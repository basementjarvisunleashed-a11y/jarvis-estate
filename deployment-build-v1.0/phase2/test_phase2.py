"""Phase 2 tests — Orchestral layers.

Covers, exactly per the normative spec:
  * per-surface contracts enforced AT THE PULL: for EVERY surface, for EVERY
    item in its NEVER-PULLS list, the pull is refused with a sealed denial
    (both seals verify; the denial is logged);
  * for every allowed PULLS item: the pull succeeds with a sealed response;
  * enrollment ceremony: happy path (phone-initiated, pairing codes match,
    exact contract terms, first pull = Watchtower status, enrollment sealed
    in the log) and refusal paths (self-enrollment, non-phone initiator,
    pairing-code mismatch, non-exact terms);
  * attention budget: exact spend accounting (5 watch pulls -> 6th queued;
    tv/headset system-initiated refused; remaining exposed; unspent-budget
    success metric; day rollover);
  * plane enforcement: direct cross-plane calls raise PlaneViolation.

Keys: TEST ONLY, via common/keys.py ceremony (CEREMONY-TEST marker).

Writes the evidence log with exact counts to
~/workspace/jarvis-deploy/tests/evidence/phase2-2026-10-21.log.
"""
import os
import secrets
import shutil
import sys
import tempfile
import unittest

BUILD_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BUILD_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import seal, planes
from common import keys as key_ceremony
from common.clock import FakeClock
from common.log import IntentLog
from common.planes import Plane, PlaneViolation

import contracts
from contracts import (PullServer, DataStore, KeyService, SurfaceClient,
                       CONTRACTS, SURFACES, VALID_STATES)
from enrollment import EnrollmentCeremony
from budget import BudgetTracker, BUDGETS


H = {}
COUNTS = {
    "refusal": {s: 0 for s in SURFACES},
    "allowance": {s: 0 for s in SURFACES},
    "fail_closed": 0,
    "bypass_refused": 0,
    "enrollment_ok": 0,
    "enrollment_refusal": {"self": 0, "wrong_initiator": 0,
                           "mismatch": 0, "wrong_terms": 0},
    "budget_verdicts": 0,
    "budget_integration": {"allowed": 0, "queued": 0, "refused": 0},
    "keys_governance": 0,
    "plane_violations": 0,
    "plane_ok": 0,
    "handshake_state": None,
}


def setUpModule():
    tmp = tempfile.mkdtemp(prefix="phase2-")
    H["tmp"] = tmp
    kd = os.path.join(tmp, "keys")
    # TEST keys only, via the common ceremony.
    key_ceremony.ceremony_generate(kd, surfaces=SURFACES)
    assert key_ceremony.is_test_keyset(kd)
    keyset = key_ceremony.load_keys(kd)
    H["key_dir"] = kd
    H["keyset"] = keyset
    H["MASTER"] = keyset["master"]
    H["TRANSPORT"] = secrets.token_bytes(32)  # pull-protocol transport only

    clock = FakeClock(start=1_760_000_000)
    H["clock"] = clock
    log = IntentLog(os.path.join(tmp, "intent.log"), H["MASTER"],
                    origin="phase2", clock=clock)
    H["log"] = log

    gw = planes.PlaneGateway(clock)
    H["gw"] = gw

    ks = KeyService("key-service", keyset, clock)
    ds = DataStore("data-store", clock)
    bt = BudgetTracker("attention-budget", clock)
    cer = EnrollmentCeremony("enrollment-ceremony", log, clock)
    srv = PullServer("pull-server", cer, bt, log, H["TRANSPORT"])

    gw.serve(Plane.GOVERNANCE, ks)
    gw.serve(Plane.DATA, ds)
    gw.serve(Plane.CONTROL, srv)
    for comp in (ks, ds, bt, cer, srv):
        comp.wire(gw)

    cer.bootstrap([(s + "-01", s) for s in SURFACES])

    clients = {}
    for s in SURFACES:
        cl = SurfaceClient(s, s, s + "-01")
        cl.wire(gw)
        clients[s] = cl
    H["clients"] = clients

    H["key_service"] = ks
    H["data_store"] = ds
    H["budget"] = bt
    H["ceremony"] = cer
    H["server"] = srv


def tearDownModule():
    shutil.rmtree(H["tmp"], ignore_errors=True)


def pull_as(client, query):
    """Pull through the gateway; verify BOTH seals; return the body.

    Outer seal: transport credential (pull-protocol hop). Inner seal: the
    governance KeyService with the ceremony master key — the proof the
    response/denial is authentic.
    """
    outer = H["gw"].pull(client, Plane.CONTROL, query, H["TRANSPORT"])
    content, _o, _t = seal.open_envelope(H["TRANSPORT"], outer)
    body, origin, _ts = seal.open_envelope(H["MASTER"], content["sealed"])
    assert origin == "pull-server", origin
    return body


def data_pull(surface, category, device=None, initiated="principal", **kw):
    q = {"query": "pull", "surface": surface,
         "device": device or (surface + "-01"),
         "category": category, "initiated": initiated}
    q.update(kw)
    return pull_as(H["clients"][surface], q)


# ---------------------------------------------------------------------------
# Contract enforcement at the pull.


class TestContractRefusals(unittest.TestCase):
    """Every NEVER-PULLS item, for every surface: sealed denial + logged."""

    def check_refused(self, surface, category):
        n0 = len(H["log"])
        body = data_pull(surface, category)
        self.assertTrue(body.get("denial"), (surface, category))
        self.assertIn(category, body.get("reason", ""), (surface, category))
        self.assertEqual(body.get("rule"), "surface-contract")
        # The denial is logged.
        self.assertEqual(len(H["log"]), n0 + 1)
        self.assertEqual(H["log"].entries[-1]["content"]["type"], "DENIAL")
        COUNTS["refusal"][surface] += 1

    def test_phone_never(self):
        for cat in CONTRACTS["phone"]["never"]:
            with self.subTest(category=cat):
                self.check_refused("phone", cat)

    def test_watch_never(self):
        for cat in CONTRACTS["watch"]["never"]:
            with self.subTest(category=cat):
                self.check_refused("watch", cat)

    def test_tablet_never(self):
        for cat in CONTRACTS["tablet"]["never"]:
            with self.subTest(category=cat):
                self.check_refused("tablet", cat)

    def test_tv_never(self):
        for cat in CONTRACTS["tv"]["never"]:
            with self.subTest(category=cat):
                self.check_refused("tv", cat)

    def test_headset_never(self):
        for cat in CONTRACTS["headset"]["never"]:
            with self.subTest(category=cat):
                self.check_refused("headset", cat)


class TestContractAllowances(unittest.TestCase):
    """Every PULLS item, for every surface: succeeds, sealed."""

    def check_allowed(self, surface, category, key):
        body = data_pull(surface, category)
        self.assertNotIn("denial", body, (surface, category))
        self.assertIn(key, body, (surface, category))
        COUNTS["allowance"][surface] += 1

    def test_phone(self):
        for cat, key in (("briefs", "briefs"), ("decisions", "decisions"),
                         ("blocks", "blocks"), ("packets", "packets")):
            with self.subTest(category=cat):
                self.check_allowed("phone", cat, key)

    def test_watch(self):
        self.check_allowed("watch", "approvals_5s", "approvals")
        self.check_allowed("watch", "critical_alerts", "alerts")

    def test_tablet(self):
        self.check_allowed("tablet", "full_evidence_packets",
                           "evidence_packets")

    def test_tv(self):
        body = data_pull("tv", "state")
        self.assertNotIn("denial", body)
        self.assertIn(body["state"], VALID_STATES)
        COUNTS["allowance"]["tv"] += 1

    def test_headset(self):
        self.check_allowed("headset", "role_artifact_evidence_relationships",
                           "relationships")


class TestFailClosed(unittest.TestCase):
    def test_unknown_category_refused(self):
        n0 = len(H["log"])
        body = data_pull("phone", "teleport")
        self.assertTrue(body.get("denial"))
        self.assertEqual(len(H["log"]), n0 + 1)
        COUNTS["fail_closed"] += 1

    def test_unenrolled_device_refused(self):
        n0 = len(H["log"])
        body = data_pull("watch", "critical_alerts", device="watch-99")
        self.assertTrue(body.get("denial"))
        self.assertIn("not enrolled", body["reason"])
        self.assertEqual(len(H["log"]), n0 + 1)
        COUNTS["fail_closed"] += 1

    def test_direct_data_plane_bypass_refused(self):
        # The data plane serves only via the pull server: a fetch without
        # the pull server's authorization is refused — no side door around
        # the contract. (Requested here from the control plane, since a
        # surface client is itself data-plane and may not address the data
        # plane over the gateway at all.)
        outer = H["gw"].pull(H["ceremony"], Plane.DATA,
                             {"query": "fetch", "category": "briefs"},
                             H["TRANSPORT"])
        body, _o, _t = seal.open_envelope(H["TRANSPORT"], outer)
        self.assertTrue(body.get("denial"))
        self.assertIn("pull server", body["reason"])
        COUNTS["bypass_refused"] += 1


# ---------------------------------------------------------------------------
# Enrollment ceremony.


class TestEnrollmentHappy(unittest.TestCase):
    def test_full_ceremony(self):
        cer = H["ceremony"]
        phone = H["clients"]["phone"]

        # (1) begins on the trusted surface (the phone).
        b = pull_as(phone, {"query": "enroll", "step": "begin",
                            "initiator": "phone",
                            "initiator_device": "phone-01",
                            "new_device": "watch-02", "surface": "watch",
                            "req_id": "enr-happy-1"})
        self.assertNotIn("denial", b)
        eid, code = b["enrollment_id"], b["pairing_code"]
        self.assertEqual(len(code), 6)

        # (2) both screens show the pairing code; the principal confirms.
        b = pull_as(phone, {"query": "enroll", "step": "confirm",
                            "enrollment_id": eid, "surface_code": code,
                            "req_id": "enr-happy-2"})
        self.assertEqual(b.get("pairing"), "matched")

        # (3) the phone displays the contract; the principal enrolls the
        # surface into its exact terms.
        b = pull_as(phone, {"query": "enroll", "step": "contract",
                            "enrollment_id": eid, "req_id": "enr-happy-3"})
        self.assertEqual(b["terms"], contracts.terms("watch"))
        b = pull_as(phone, {"query": "enroll", "step": "accept",
                            "enrollment_id": eid,
                            "terms": contracts.terms("watch"),
                            "req_id": "enr-happy-4"})
        self.assertTrue(b.get("enrolled_into_contract"))

        # (4) the surface's first pull is the Watchtower status — the
        # handshake rendered as state.
        w2 = SurfaceClient("watch-02", "watch", "watch-02")
        w2.wire(H["gw"])
        body = pull_as(w2, {"query": "pull", "surface": "watch",
                            "device": "watch-02",
                            "category": "watchtower_status",
                            "handshake": True, "enrollment_id": eid,
                            "req_id": "enr-happy-5"})
        self.assertIn(body["watchtower"]["state"], VALID_STATES)
        COUNTS["handshake_state"] = body["watchtower"]["state"]

        # Enrollment sealed in the log; chain verifies.
        self.assertTrue(cer.is_enrolled("watch-02"))
        found = [e for e in H["log"].entries
                 if e["content"]["type"] == "DECISION"
                 and e["content"]["content"].get("enrollment", {}).get(
                     "device") == "watch-02"]
        self.assertEqual(len(found), 1)
        self.assertTrue(H["log"].verify_chain())
        COUNTS["enrollment_ok"] += 1


class TestEnrollmentRefusals(unittest.TestCase):
    def enroll_begin(self, **kw):
        q = {"query": "enroll", "step": "begin", "initiator": "phone",
             "initiator_device": "phone-01", "surface": "headset"}
        q.update(kw)
        return pull_as(H["clients"]["phone"], q)

    def test_self_enrollment_rejected(self):
        n0 = len(H["log"])
        b = self.enroll_begin(new_device="phone-01",
                              initiator_device="phone-01", surface="phone")
        self.assertTrue(b.get("denial"))
        self.assertIn("itself", b["reason"])
        self.assertEqual(len(H["log"]), n0 + 1)
        COUNTS["enrollment_refusal"]["self"] += 1

    def test_non_phone_initiator_rejected(self):
        n0 = len(H["log"])
        b = pull_as(H["clients"]["watch"],
                    {"query": "enroll", "step": "begin", "initiator": "watch",
                     "initiator_device": "watch-01",
                     "new_device": "headset-03", "surface": "headset"})
        self.assertTrue(b.get("denial"))
        self.assertIn("trusted surface", b["reason"])
        self.assertFalse(H["ceremony"].is_enrolled("headset-03"))
        self.assertEqual(len(H["log"]), n0 + 1)
        COUNTS["enrollment_refusal"]["wrong_initiator"] += 1

    def test_pairing_mismatch_rejected(self):
        n0 = len(H["log"])
        b = self.enroll_begin(new_device="tablet-02", surface="tablet")
        eid = b["enrollment_id"]
        wrong = "000000" if b["pairing_code"] != "000000" else "000001"
        b = pull_as(H["clients"]["phone"],
                    {"query": "enroll", "step": "confirm",
                     "enrollment_id": eid, "surface_code": wrong})
        self.assertTrue(b.get("denial"))          # sealed denial
        self.assertIn("match", b["reason"])
        self.assertFalse(H["ceremony"].is_enrolled("tablet-02"))
        self.assertIsNone(H["ceremony"].get_pending(eid))  # aborted
        self.assertEqual(len(H["log"]), n0 + 1)   # denial logged
        COUNTS["enrollment_refusal"]["mismatch"] += 1

    def test_non_exact_terms_rejected(self):
        n0 = len(H["log"])
        b = self.enroll_begin(new_device="tv-02", surface="tv")
        eid = b["enrollment_id"]
        pull_as(H["clients"]["phone"],
                {"query": "enroll", "step": "confirm",
                 "enrollment_id": eid, "surface_code": b["pairing_code"]})
        t = contracts.terms("tv")
        tampered = dict(t)
        tampered["pulls"] = t["pulls"] + ["approvals"]
        b = pull_as(H["clients"]["phone"],
                    {"query": "enroll", "step": "accept",
                     "enrollment_id": eid, "terms": tampered})
        self.assertTrue(b.get("denial"))          # sealed denial
        self.assertIn("exact terms", b["reason"])
        self.assertFalse(H["ceremony"].is_enrolled("tv-02"))
        self.assertEqual(len(H["log"]), n0 + 1)   # denial logged
        COUNTS["enrollment_refusal"]["wrong_terms"] += 1


# ---------------------------------------------------------------------------
# Attention budget.


class TestAttentionBudget(unittest.TestCase):
    def test_watch_five_then_queued(self):
        bt = BudgetTracker("t", FakeClock(1000))
        for i in range(5):
            v = bt.request("watch", initiated="system")
            self.assertEqual(v["verdict"], "allowed")
            self.assertTrue(v["counted"])
            self.assertEqual(v["remaining"], 4 - i)
            COUNTS["budget_verdicts"] += 1
        v = bt.request("watch", initiated="system")
        self.assertEqual(v["verdict"], "queued")
        self.assertFalse(v["counted"])
        self.assertEqual(bt.spent("watch"), 5)   # never silently spent
        self.assertEqual(bt.remaining("watch"), 0)
        COUNTS["budget_verdicts"] += 1

    def test_phone_three_then_queued(self):
        bt = BudgetTracker("t", FakeClock(1000))
        for _ in range(3):
            self.assertEqual(bt.request("phone", initiated="system")
                             ["verdict"], "allowed")
            COUNTS["budget_verdicts"] += 1
        v = bt.request("phone", initiated="system")
        self.assertEqual(v["verdict"], "queued")
        self.assertEqual(bt.spent("phone"), 3)
        COUNTS["budget_verdicts"] += 1

    def test_tv_headset_zero(self):
        bt = BudgetTracker("t", FakeClock(1000))
        for s in ("tv", "headset"):
            v = bt.request(s, initiated="system")
            self.assertEqual(v["verdict"], "refused")
            self.assertEqual(bt.spent(s), 0)
            COUNTS["budget_verdicts"] += 1

    def test_tablet_system_initiated_refused(self):
        bt = BudgetTracker("t", FakeClock(1000))
        v = bt.request("tablet", initiated="system")
        self.assertEqual(v["verdict"], "refused")
        self.assertIn("principal-initiated only", v["reason"])
        self.assertEqual(bt.remaining("tablet"), "unbounded")
        COUNTS["budget_verdicts"] += 1

    def test_principal_initiated_uncounted(self):
        bt = BudgetTracker("t", FakeClock(1000))
        for _ in range(3):
            v = bt.request("watch", initiated="principal")
            self.assertEqual(v["verdict"], "allowed")
            self.assertFalse(v["counted"])
        self.assertEqual(bt.spent("watch"), 0)
        self.assertEqual(bt.remaining("watch"), 5)

    def test_remaining_and_report(self):
        bt = BudgetTracker("t", FakeClock(1000))
        bt.request("watch", initiated="system")
        bt.request("watch", initiated="system")
        bt.request("phone", initiated="system")
        self.assertEqual(bt.remaining("watch"), 3)
        self.assertEqual(bt.remaining("phone"), 2)
        self.assertEqual(bt.remaining("tablet"), "unbounded")
        rep = bt.report()
        self.assertEqual(rep["surfaces"]["watch"],
                         {"budget": 5, "spent": 2, "remaining": 3,
                          "unspent": 3})
        # Unspent budget is the success metric: (5-2)+(3-1)+0+0 = 5 of 8.
        self.assertEqual(rep["attention_success"]["unspent"], 5)
        self.assertEqual(rep["attention_success"]["of_budget"], 8)
        self.assertAlmostEqual(rep["attention_success"]["unspent_ratio"],
                               0.625)

    def test_day_rollover_resets(self):
        clock = FakeClock(1000)
        bt = BudgetTracker("t", clock)
        for _ in range(5):
            bt.request("watch", initiated="system")
        self.assertEqual(bt.request("watch", initiated="system")
                         ["verdict"], "queued")
        clock.advance(86401)
        v = bt.request("watch", initiated="system")
        self.assertEqual(v["verdict"], "allowed")
        self.assertEqual(v["remaining"], 4)


class TestBudgetIntegration(unittest.TestCase):
    """Budget enforced at the pull, through the pull server."""

    def test_watch_budget_enforced_at_pull(self):
        bt = H["budget"]
        for i in range(5):
            body = data_pull("watch", "critical_alerts", initiated="system",
                             req_id="bq-%d" % i)
            self.assertNotIn("denial", body)
            self.assertIn("alerts", body)
            COUNTS["budget_integration"]["allowed"] += 1
        body = data_pull("watch", "critical_alerts", initiated="system",
                         req_id="bq-5")
        self.assertTrue(body.get("queued"))
        self.assertNotIn("denial", body)
        self.assertEqual(bt.spent("watch"), 5)
        self.assertEqual(bt.remaining("watch"), 0)
        COUNTS["budget_integration"]["queued"] += 1

    def test_tv_system_initiated_refused(self):
        n0 = len(H["log"])
        body = data_pull("tv", "state", initiated="system", req_id="bq-tv")
        self.assertTrue(body.get("denial"))
        self.assertIn("budget", body["reason"].lower())
        self.assertEqual(len(H["log"]), n0 + 1)
        COUNTS["budget_integration"]["refused"] += 1


# ---------------------------------------------------------------------------
# Keys stay in governance; planes enforced.


class TestKeysInGovernance(unittest.TestCase):
    def test_only_governance_holds_ceremony_keys(self):
        master = H["MASTER"]
        for name, comp in (("pull-server", H["server"]),
                           ("ceremony", H["ceremony"]),
                           ("data-store", H["data_store"]),
                           ("budget", H["budget"])):
            blobs = [v for v in vars(comp).values()
                     if isinstance(v, (bytes, bytearray))]
            self.assertFalse(any(bytes(x) == master for x in blobs), name)
        for cl in H["clients"].values():
            blobs = [v for v in vars(cl).values()
                     if isinstance(v, (bytes, bytearray))]
            self.assertFalse(any(bytes(x) == master for x in blobs), cl.name)
        self.assertEqual(H["key_service"]._master, master)
        self.assertTrue(key_ceremony.is_test_keyset(H["key_dir"]))
        COUNTS["keys_governance"] += 1


class TestPlanes(unittest.TestCase):
    def test_direct_cross_plane_calls_raise(self):
        cases = [
            (H["clients"]["phone"], H["server"]),     # data -> control
            (H["server"], H["data_store"]),           # control -> data
            (H["ceremony"], H["key_service"]),       # control -> governance
            (H["data_store"], H["server"]),           # data -> control
        ]
        for a, b in cases:
            with self.subTest(a=a.name, b=b.name):
                with self.assertRaises(PlaneViolation):
                    a.call(b, "serve_pull", {"query": "pull"})
                COUNTS["plane_violations"] += 1

    def test_component_without_plane_rejected(self):
        class Vague(planes.Component):
            pass

        with self.assertRaises(PlaneViolation):
            Vague("vague")
        COUNTS["plane_violations"] += 1

    def test_gateway_rejects_same_plane(self):
        with self.assertRaises(PlaneViolation):
            H["gw"].pull(H["clients"]["phone"], Plane.DATA,
                         {"query": "x"}, H["TRANSPORT"])
        with self.assertRaises(PlaneViolation):
            H["gw"].pull(H["server"], Plane.CONTROL,
                         {"query": "x"}, H["TRANSPORT"])
        COUNTS["plane_violations"] += 2

    def test_sanctioned_pull_path_works(self):
        body = data_pull("phone", "briefs", req_id="plane-ok")
        self.assertIn("briefs", body)
        COUNTS["plane_ok"] += 1


# ---------------------------------------------------------------------------
# Evidence log with exact counts (runs last: classes load alphabetically).


class TestZZEvidence(unittest.TestCase):
    def test_write_evidence_log(self):
        self.assertEqual(COUNTS["refusal"],
                         {"phone": 2, "watch": 2, "tablet": 2, "tv": 2,
                          "headset": 1})
        self.assertEqual(COUNTS["allowance"],
                         {"phone": 4, "watch": 2, "tablet": 1, "tv": 1,
                          "headset": 1})
        self.assertEqual(COUNTS["fail_closed"], 2)
        self.assertEqual(COUNTS["bypass_refused"], 1)
        self.assertEqual(COUNTS["enrollment_ok"], 1)
        self.assertEqual(COUNTS["enrollment_refusal"],
                         {"self": 1, "wrong_initiator": 1,
                          "mismatch": 1, "wrong_terms": 1})
        # 6 watch + 4 phone + 2 tv/headset + 1 tablet verdicts
        self.assertEqual(COUNTS["budget_verdicts"], 13)
        self.assertEqual(COUNTS["budget_integration"],
                         {"allowed": 5, "queued": 1, "refused": 1})
        self.assertEqual(COUNTS["keys_governance"], 1)
        self.assertEqual(COUNTS["plane_violations"], 7)
        self.assertEqual(COUNTS["plane_ok"], 1)

        log = H["log"]
        self.assertTrue(log.verify_chain())
        denials = [e for e in log.entries
                   if e["content"]["type"] == "DENIAL"]
        # 9 contract + 2 fail-closed + 4 enrollment + 1 budget(tv) = 16
        self.assertEqual(len(denials), 16)
        decisions = [e for e in log.entries
                     if e["content"]["type"] == "DECISION"]
        self.assertEqual(len(decisions), 2)  # bootstrap + enrollment complete
        self.assertEqual(len(log), 18)

        lines = []
        a = lines.append
        a("PHASE 2 EVIDENCE LOG — orchestral layers")
        a("build: ~/workspace/jarvis-deploy/phase2")
        a("date: 2026-10-21")
        a("keys: TEST ONLY (common/keys.py ceremony; CEREMONY-TEST marker "
          "present)")
        a("")
        a("CONTRACT ENFORCEMENT AT THE PULL")
        a("Every refusal below: sealed denial (governance inner seal verified")
        a("with the ceremony master key; transport outer seal verified) AND")
        a("logged as DENIAL in the intent log (chain verified end-to-end).")
        a("refusals by surface:")
        for s in SURFACES:
            a("  %s: %d — %s" % (s, COUNTS["refusal"][s],
                                 ", ".join(CONTRACTS[s]["never"])))
        a("refusals total: %d" % sum(COUNTS["refusal"].values()))
        a("allowances, sealed responses (both seals verified):")
        for s in SURFACES:
            a("  %s: %d — %s" % (s, COUNTS["allowance"][s],
                                 ", ".join(CONTRACTS[s]["pulls"])))
        a("allowances total: %d" % sum(COUNTS["allowance"].values()))
        a("")
        a("FAIL-CLOSED")
        a("unknown category refused: 1; unenrolled device refused: 1 "
          "(counter total: %d)" % COUNTS["fail_closed"])
        a("direct data-plane bypass (no pull-server authorization) refused: "
          "%d" % COUNTS["bypass_refused"])
        a("")
        a("ENROLLMENT CEREMONY (control plane)")
        a("happy path: %d — phone-initiated; pairing codes matched; exact "
          "contract terms accepted;" % COUNTS["enrollment_ok"])
        a("  first pull = Watchtower status (state=%s); enrollment sealed in "
          "the log (DECISION)" % COUNTS["handshake_state"])
        a("refusal paths (each: sealed denial, seal verified, DENIAL logged, "
          "device left unenrolled):")
        for k, v in COUNTS["enrollment_refusal"].items():
            a("  %s: %d" % (k, v))
        a("")
        a("ATTENTION BUDGET (monitored quantity; unspent budget is the "
          "success metric)")
        a("unit verdicts asserted: %d — watch 5 allowed then 6th queued "
          "(spent stays 5);" % COUNTS["budget_verdicts"])
        a("  phone 3 allowed then 4th queued; tv/headset system-initiated "
          "refused;")
        a("  tablet system-initiated refused (principal-initiated only); "
          "principal-initiated uncounted;")
        a("  remaining() exact; report() exact; attention_success unspent=5 "
          "of 8 (ratio 0.625);")
        a("  day rollover resets spend")
        bi = COUNTS["budget_integration"]
        a("integration at the pull: %d system-initiated watch pulls allowed, "
          "%d queued (spent unchanged at 5, remaining 0);" % (bi["allowed"],
                                                              bi["queued"]))
        a("  tv system-initiated pull refused with sealed denial: %d"
          % bi["refused"])
        a("")
        a("KEYS: ceremony master key held only by the governance KeyService; "
          "no control/data component")
        a("or surface client holds ceremony key bytes: %d assertion set "
          "passed" % COUNTS["keys_governance"])
        a("PLANES: %d direct cross-plane calls raised PlaneViolation; %d "
          "sanctioned gateway pull" % (COUNTS["plane_violations"],
                                       COUNTS["plane_ok"]))
        a("succeeded")
        a("INTENT LOG: %d entries (%d DECISION, %d DENIAL); chain verifies: "
          "%s" % (len(log), len(decisions), len(denials),
                  log.verify_chain()))
        path = os.path.join(BUILD_ROOT, "tests", "evidence",
                            "phase2-2026-10-21.log")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        self.assertTrue(os.path.isfile(path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
