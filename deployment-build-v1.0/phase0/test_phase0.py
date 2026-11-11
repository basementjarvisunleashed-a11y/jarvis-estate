"""Phase 0 — Ground: key ceremony, intent log, seal verification.

Done when the chain verifies end-to-end (§6.1).
"""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import seal, keys
from common.log import IntentLog
from common.clock import FakeClock
from common.seal import SealError


class TestKeyCeremony(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.kd = os.path.join(self.tmp, "keys")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ceremony_marks_test_keys(self):
        ks = keys.ceremony_generate(self.kd, surfaces=("phone", "watch"))
        self.assertTrue(keys.is_test_keyset(self.kd))
        self.assertIn("master", ks)
        self.assertIn("surface:phone", ks)
        self.assertIn("surface:watch", ks)
        for v in ks.values():
            self.assertEqual(len(v), 32)

    def test_load_refuses_without_marker(self):
        os.makedirs(self.kd, exist_ok=True)
        with self.assertRaises(keys.KeyError):
            keys.load_keys(self.kd)

    def test_load_roundtrip(self):
        keys.ceremony_generate(self.kd, surfaces=("phone",))
        ks = keys.load_keys(self.kd)
        self.assertEqual(set(ks), {"master", "surface:phone"})

    def test_keys_never_leave_key_dir(self):
        keys.ceremony_generate(self.kd)
        names = os.listdir(self.kd)
        self.assertTrue(all(n.endswith((".key",)) or n == keys.MARKER
                           for n in names))


class TestSeal(unittest.TestCase):
    KEY = b"0" * 32

    def test_roundtrip(self):
        env = seal.make_envelope(self.KEY, {"a": 1}, "origin", 100)
        content, origin, ts = seal.open_envelope(self.KEY, env)
        self.assertEqual((content, origin, ts), ({"a": 1}, "origin", 100))

    def test_tamper_content_fails(self):
        env = seal.make_envelope(self.KEY, {"a": 1}, "origin", 100)
        env["content"] = {"a": 2}
        self.assertFalse(seal.verify_envelope(self.KEY, env))
        with self.assertRaises(SealError):
            seal.open_envelope(self.KEY, env)

    def test_tamper_origin_fails(self):
        env = seal.make_envelope(self.KEY, {"a": 1}, "origin", 100)
        env["origin"] = "evil"
        self.assertFalse(seal.verify_envelope(self.KEY, env))

    def test_tamper_ts_fails(self):
        env = seal.make_envelope(self.KEY, {"a": 1}, "origin", 100)
        env["ts"] = 101
        self.assertFalse(seal.verify_envelope(self.KEY, env))

    def test_wrong_key_fails(self):
        env = seal.make_envelope(self.KEY, {"a": 1}, "origin", 100)
        self.assertFalse(seal.verify_envelope(b"1" * 32, env))

    def test_missing_fields_fail_closed(self):
        self.assertFalse(seal.verify_envelope(self.KEY, {}))
        self.assertFalse(seal.verify_envelope(self.KEY, {"seal": "x"}))

    def test_canonical_stable(self):
        a = seal.canonical({"b": 1, "a": [1, 2]})
        b = seal.canonical({"a": [1, 2], "b": 1})
        self.assertEqual(a, b)

    def test_intent_digest_binds_content(self):
        d1 = seal.intent_digest({"action": "send", "to": ["a"]})
        d2 = seal.intent_digest({"action": "send", "to": ["a", "b"]})
        self.assertNotEqual(d1, d2)
        self.assertEqual(len(d1), 64)


class TestIntentLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.clock = FakeClock()
        self.log = IntentLog(os.path.join(self.tmp, "log.jsonl"),
                             b"2" * 32, clock=self.clock)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_chain_verifies_end_to_end(self):
        for i in range(5):
            self.clock.advance(1)
            self.log.append("INTENT", {"i": i})
        self.assertTrue(self.log.verify_chain())
        self.assertEqual(len(self.log), 5)

    def test_chain_links_prev(self):
        self.log.append("INTENT", {"i": 0})
        self.log.append("INTENT", {"i": 1})
        self.assertEqual(self.log.entries[1]["content"]["prev"],
                         self.log.entries[0]["seal"])

    def test_tampered_log_fails(self):
        self.log.append("INTENT", {"i": 0})
        self.log.entries[0]["content"]["content"] = {"i": 999}
        self.assertFalse(self.log.verify_chain())

    def test_checkpoint_and_rollback(self):
        self.log.append("INTENT", {"i": 0})
        self.log.checkpoint("phase0-done")
        self.log.append("INTENT", {"i": 1})
        self.log.rollback("phase0-done")
        self.assertTrue(self.log.verify_chain())
        types = [e["content"]["type"] for e in self.log.entries]
        self.assertEqual(types, ["INTENT", "CHECKPOINT", "INTENT", "ROLLBACK"])

    def test_rollback_unknown_label_fails(self):
        with self.assertRaises(SealError):
            self.log.rollback("nope")

    def test_reload_verifies(self):
        self.log.append("EVIDENCE", {"ok": True})
        again = IntentLog(self.log.path, b"2" * 32)
        self.assertTrue(again.verify_chain())
        self.assertEqual(len(again), 1)



class TestKeyFileModes(unittest.TestCase):
    """SAF-08: ceremony key files are owner-only regardless of umask."""

    def test_modes(self):
        import stat
        # umask 0 would leave a normal open() world-writable. The ceremony
        # must still produce 0700/0600, and must not follow a key symlink.
        old = os.umask(0)
        parent = tempfile.mkdtemp()
        try:
            d = os.path.join(parent, "keys")
            keys.ceremony_generate(d, surfaces=("watch",))
            self.assertEqual(stat.S_IMODE(os.stat(d).st_mode), 0o700)
            saw_key = False
            for fn in os.listdir(d):
                if fn.endswith(".key"):
                    saw_key = True
                    self.assertEqual(
                        stat.S_IMODE(os.stat(os.path.join(d, fn)).st_mode),
                        0o600, fn)
            self.assertTrue(saw_key)
            outside = os.path.join(parent, "stolen.key")
            master = os.path.join(d, "master.key")
            os.remove(master)
            os.symlink(outside, master)
            with self.assertRaises(OSError):
                keys.ceremony_generate(d, surfaces=("watch",))
            self.assertFalse(os.path.exists(outside))
        finally:
            os.umask(old)
            shutil.rmtree(parent, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
