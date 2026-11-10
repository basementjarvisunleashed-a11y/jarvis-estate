#!/usr/bin/env python3
"""test_crackme_v9.py — simulated verification for the crackme-v9 v1 package.

Nothing here touches the Acer, the vault, wabt, Node, or the 27B. All
vault / tool / 27B behaviour is simulated with fake files and fake
output. Run:
    python3 test_crackme_v9.py
Exits 0 only if every test passes.
"""
import gzip
import hashlib
import importlib.util
import os
import re
import sys
import tempfile
import unittest

BUILD_DIR = os.path.join(os.path.expanduser("~"), "workspace", "family-bot", "crackme-v9-build")
WRAPPER = os.path.join(BUILD_DIR, "crackme-v9.py")
LAUNCHER = os.path.join(BUILD_DIR, "start-crackme-v9.sh")
README = os.path.join(BUILD_DIR, "README.md")


def load_wrapper():
    spec = importlib.util.spec_from_file_location("crackme_v9", WRAPPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V9 = load_wrapper()


# ---------------------------------------------------------------- fake WASM builder
def leb(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def section(sec_id, payload):
    return bytes([sec_id]) + leb(len(payload)) + payload


def fake_wasm():
    """A minimal valid WASM module: one type, two functions, two exports
    (a func 'unlock' and a memory 'mem'), two code bodies."""
    type_sec = section(1, leb(1) + b"\x60\x00\x00")
    func_sec = section(3, leb(2) + leb(0) + leb(0))
    exp = leb(2)
    exp += leb(6) + b"unlock" + bytes([0]) + leb(0)
    exp += leb(3) + b"mem" + bytes([2]) + leb(0)
    export_sec = section(7, exp)
    code = leb(2) + leb(3) + b"\x00\x0b" + leb(3) + b"\x00\x0b"
    code_sec = section(10, code)
    return b"\x00asm" + b"\x01\x00\x00\x00" + type_sec + func_sec + export_sec + code_sec


FAKE_JS = """#!/usr/bin/env node
"use strict";
(function(){
  var __expected = "f6a1beae9ca262974122a1e31614c70375596ebbeb5ef8506b7caa64558ecec4";
  function checkKey(k) {
    if (typeof k !== "string" || k.length !== 16) return "DENIED";
    var h = require("node:crypto").createHash("sha256");
    h.update(k);
    return verifyWasm(h.digest());
  }
  function verifyWasm(digest) {
    return unlock(digest);
  }
  const unlock = (d) => { return "DENIED"; };
  module.exports = { checkKey };
})();
"""

FAKE_PY = '''"""policy ledger."""
import hashlib

class QuotaLedger:
    def __init__(self, seal):
        self.seal = seal

    def check(self, key):
        h = hashlib.sha256(key.encode()).hexdigest()
        return h == self.seal

def load_policy(path):
    return QuotaLedger("abc")
'''

FAKE_HTML = """<!doctype html>
<html><head><title>Sovereign Panel</title></head>
<body>
<script>
function onUnlockClick() { verifyKey(document.getElementById("k").value); }
function verifyKey(k) { fetch("/unlock", {method: "POST", body: k}); }
</script>
<script src="panel.js"></script>
</body></html>
"""

FAKE_WAT = """(module
  (type (;0;) (func (param i32 i32) (result i32)))
  (func $unlock (export "unlock") (param i32 i32) (result i32)
    ;; SHA-256 KDF + ARX commitment
    (local i32 i32)
    i32.const 0
    i32.const 0x6a09e667
    i32.add
    i32.const 5
    i32.rotr
    return)
  (func $decoy (export "decoy") (param i32) (result i32)
    i32.const 1
    return)
  (memory (;0;) 1)
  (export "mem" (memory 0)))
"""


class TestWasmParser(unittest.TestCase):
    def test_parse_minimal_wasm(self):
        p = V9.parse_wasm(fake_wasm())
        self.assertTrue(p["valid"], p.get("error"))
        self.assertEqual(p["function_count"], 2)
        self.assertEqual(p["code_count"], 2)
        self.assertEqual(p["import_count"], 0)
        self.assertEqual(p["imported_funcs"], 0)
        self.assertEqual(len(p["exports"]), 2)
        self.assertIn(("unlock", "func", 0), p["exports"])
        self.assertIn(("mem", "mem", 0), p["exports"])
        self.assertEqual(len(p["sections"]), 4)

    def test_parse_invalid_magic(self):
        p = V9.parse_wasm(b"NOTWASM" + b"\x00" * 20)
        self.assertFalse(p["valid"])
        self.assertIn("magic", p["error"])

    def test_parse_empty(self):
        p = V9.parse_wasm(b"")
        self.assertFalse(p["valid"])
        self.assertIsNotNone(p["error"])

    def test_parse_truncated(self):
        full = fake_wasm()
        p = V9.parse_wasm(full[:len(full) - 3])
        self.assertFalse(p["valid"])
        self.assertIsNotNone(p["error"])

    def test_parse_truncated_leb(self):
        # A section size LEB that never terminates.
        p = V9.parse_wasm(b"\x00asm\x01\x00\x00\x00\x01\x80\x80\x80")
        self.assertFalse(p["valid"])

    def test_leb_roundtrip(self):
        for n in [0, 1, 63, 64, 127, 128, 300, 16384, 6883604]:
            v, pos = V9._read_uleb(leb(n), 0)
            self.assertEqual(v, n)
            self.assertEqual(pos, len(leb(n)))

    def test_summary_text(self):
        p = V9.parse_wasm(fake_wasm())
        t = V9.wasm_summary_text(p)
        self.assertIn("unlock", t)
        self.assertIn("2 total functions", t)
        self.assertIn("Exports (2)", t)

    def test_summary_text_invalid(self):
        t = V9.wasm_summary_text(V9.parse_wasm(b"junk"))
        self.assertIn("FAILED", t)


class TestExcerpts(unittest.TestCase):
    def test_js_function_names(self):
        names = V9.js_function_names(FAKE_JS)
        self.assertIn("checkKey", names)
        self.assertIn("verifyWasm", names)
        self.assertIn("unlock", names)
        # Deduplicated.
        self.assertEqual(len(names), len(set(names)))

    def test_py_defs(self):
        defs = V9.py_defs(FAKE_PY)
        self.assertIn("QuotaLedger", defs)
        self.assertIn("check", defs)
        self.assertIn("load_policy", defs)

    def test_find_window(self):
        window, marker, line = V9.find_window(FAKE_JS, ["DENIED", "unlock"], before=2, after=2, budget=1500)
        self.assertEqual(marker, "DENIED")
        self.assertGreater(line, 0)
        self.assertIn("DENIED", window)
        self.assertIn("checkKey", window)

    def test_find_window_no_marker(self):
        window, marker, line = V9.find_window("hello\nworld\n", ["DENIED", "unlock"])
        self.assertEqual(window, "")
        self.assertIsNone(marker)
        self.assertEqual(line, -1)

    def test_find_window_case_insensitive_fallback(self):
        window, marker, line = V9.find_window("the Key is here\n", ["KEY"])
        self.assertIn("Key", window)
        self.assertEqual(marker, "KEY")

    def test_interesting_strings(self):
        strs = V9.interesting_strings(FAKE_JS, ["sha256", "DENIED", "key"])
        self.assertTrue(any("DENIED" in s for s in strs))

    def test_html_structure(self):
        s = V9.html_structure(FAKE_HTML)
        self.assertEqual(s["title"], "Sovereign Panel")
        self.assertEqual(s["script_tags"], 2)
        self.assertIn("onUnlockClick", s["functions"])
        self.assertIn("verifyKey", s["functions"])

    def test_extract_wat_excerpt_match(self):
        ex, matched = V9.extract_wat_excerpt(FAKE_WAT, ["unlock", "decoy"], budget=2000)
        self.assertEqual(matched, "unlock")
        self.assertIn("unlock", ex)
        self.assertIn("6a09e667", ex)
        self.assertLessEqual(len(ex), 2000)

    def test_extract_wat_excerpt_no_match(self):
        ex, matched = V9.extract_wat_excerpt(FAKE_WAT, ["nope"], budget=200)
        self.assertIsNone(matched)
        self.assertEqual(len(ex), 200)
        self.assertTrue(ex.startswith("(module"))


class TestPrompts(unittest.TestCase):
    def _long(self, n=4000):
        return "x = 1;\n" * (n // 7)

    def test_all_prompts_under_3500(self):
        funcs = ["checkKey", "verifyWasm", "unlock"] + ["f%d" % i for i in range(37)]
        p1 = V9.build_license_prompt(funcs, self._long(), "DENIED", 9, 201111)
        p2 = V9.build_wasm_prompt(V9.wasm_summary_text(V9.parse_wasm(fake_wasm())), '{"revision": 1}')
        p3 = V9.build_policy_prompt(["QuotaLedger", "check"], self._long(), "sha256", 5, 41561)
        p4 = V9.build_wat_prompt(self._long(3000), "unlock")
        p5 = V9.build_panel_prompt({"title": "T", "script_tags": 2, "functions": ["onUnlockClick"]},
                                   self._long(), "key", 4, 126216)
        for i, p in enumerate([p1, p2, p3, p4, p5], 1):
            self.assertLess(len(p), 3500, "prompt %d must stay under 3500 chars (got %d)" % (i, len(p)))

    def test_prompts_carry_key_candidate_instruction(self):
        for p in [
            V9.build_license_prompt(["a"], "DENIED", "DENIED", 1, 10),
            V9.build_wasm_prompt("wasm", "{}"),
            V9.build_policy_prompt(["a"], "x", "key", 1, 10),
            V9.build_wat_prompt("wat", "unlock"),
            V9.build_panel_prompt({"title": "", "script_tags": 0, "functions": []}, "x", "key", 1, 10),
        ]:
            self.assertIn("KEY-CANDIDATE", p)

    def test_fit_prompt_truncates_data_not_instruction(self):
        instruction = "INSTRUCTION-KEEP-ME " * 10
        p = V9.fit_prompt(instruction, "D" * 10000, "coverage line", limit=3400)
        self.assertLess(len(p), 3400)
        self.assertTrue(p.startswith("INSTRUCTION-KEEP-ME"))
        self.assertIn("coverage line", p)


class TestCandidates(unittest.TestCase):
    def test_extract_candidates(self):
        replies = ["The key is AbCdEfGh12345678 — quote it as KEY-CANDIDATE.\n"]
        self.assertEqual(V9.extract_candidates(replies), ["AbCdEfGh12345678"])

    def test_extract_ignores_non_key_lines(self):
        # A 16-char token on a line with no 'key' word is not a candidate.
        replies = ["The digest is AbCdEfGh12345678 in the file.\n"]
        self.assertEqual(V9.extract_candidates(replies), [])

    def test_extract_dedupes(self):
        replies = ["key: AbCdEfGh12345678\n", "the key AbCdEfGh12345678 again\n"]
        self.assertEqual(V9.extract_candidates(replies), ["AbCdEfGh12345678"])

    def test_extract_caps_at_3(self):
        replies = ["key %s\n" % k for k in
                   ["AAAAAAAAAAAAAAAA", "BBBBBBBBBBBBBBBB", "CCCCCCCCCCCCCCCC",
                    "DDDDDDDDDDDDDDDD", "EEEEEEEEEEEEEEEE"]]
        self.assertEqual(len(V9.extract_candidates(replies)), 3)

    def test_extract_ignores_short_and_long(self):
        replies = ["key SHORT1 and key AAAAAAAAAAAAAAAAAAAAAAAA and key AbCdEfGh12345678\n"]
        self.assertEqual(V9.extract_candidates(replies), ["AbCdEfGh12345678"])

    def test_verify_flag_match(self):
        flag = "FLAG{test-solve-1234}"
        digest = hashlib.sha256(flag.encode()).hexdigest()
        # Point the module at a fake commitment, verify, restore.
        orig = V9.FLAG_SHA256
        V9.FLAG_SHA256 = digest
        try:
            self.assertTrue(V9.verify_flag(flag))
            self.assertFalse(V9.verify_flag("FLAG{wrong}"))
            self.assertFalse(V9.verify_flag(""))
        finally:
            V9.FLAG_SHA256 = orig


class TestSetup(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="crackme-v9-setup-")
        self.vault = os.path.join(self.d, "vault")
        self.base = os.path.join(self.d, "base")
        os.makedirs(self.vault)
        os.makedirs(self.base)
        self.saved = {}
        for name in ["VAULT_DIR", "BASE_DIR", "WORK_DIR", "REPORT", "CALLS_LOG",
                     "LOG_PATH", "STATUS_PATH", "EXPECTED", "EXPECTED_CORE_WASM",
                     "EXPECTED_CORE_WASM_BYTES"]:
            self.saved[name] = getattr(V9, name)
        V9.VAULT_DIR = self.vault
        V9.BASE_DIR = self.base
        V9.WORK_DIR = os.path.join(self.base, "work")
        V9.REPORT = os.path.join(self.base, "report.md")
        V9.CALLS_LOG = os.path.join(self.base, "27b-calls.jsonl")
        V9.LOG_PATH = os.path.join(self.base, "crackme-v9.log")
        V9.STATUS_PATH = os.path.join(self.base, "status.txt")
        # Fake vault: five files + the gunzipped core.wasm digest.
        self.contents = {
            "license.cjs": b"node license.cjs fake\n",
            "panel.html": b"<html>fake</html>\n",
            "policy.py": b"# fake policy\n",
            "seal.json": b'{"revision": 1}\n',
        }
        self.raw_wasm = fake_wasm()
        gz_path = os.path.join(self.vault, "core.wasm.gz")
        with gzip.open(gz_path, "wb") as f:
            f.write(self.raw_wasm)
        for name, data in self.contents.items():
            with open(os.path.join(self.vault, name), "wb") as f:
                f.write(data)
        V9.EXPECTED = {name: hashlib.sha256(data).hexdigest()
                       for name, data in self.contents.items()}
        V9.EXPECTED["core.wasm.gz"] = hashlib.sha256(open(gz_path, "rb").read()).hexdigest()
        V9.EXPECTED_CORE_WASM = hashlib.sha256(self.raw_wasm).hexdigest()
        V9.EXPECTED_CORE_WASM_BYTES = len(self.raw_wasm)

    def tearDown(self):
        for name, val in self.saved.items():
            setattr(V9, name, val)

    def test_setup_copies_and_verifies(self):
        self.assertTrue(V9.setup_vault())
        for name in ["license.cjs", "panel.html", "policy.py", "core.wasm.gz", "seal.json"]:
            self.assertTrue(os.path.isfile(os.path.join(V9.WORK_DIR, name)), name)
        wasm = os.path.join(V9.WORK_DIR, "core.wasm")
        self.assertTrue(os.path.isfile(wasm))
        self.assertEqual(open(wasm, "rb").read(), self.raw_wasm)
        # Idempotent: a second run skips the copies.
        self.assertTrue(V9.setup_vault())

    def test_setup_refuses_tampered_source(self):
        with open(os.path.join(self.vault, "seal.json"), "wb") as f:
            f.write(b'{"revision": 999}\n')
        self.assertFalse(V9.setup_vault())
        self.assertFalse(os.path.exists(os.path.join(V9.WORK_DIR, "seal.json")))

    def test_setup_never_writes_to_vault(self):
        before = {n: open(os.path.join(self.vault, n), "rb").read()
                  for n in os.listdir(self.vault)}
        self.assertTrue(V9.setup_vault())
        after = {n: open(os.path.join(self.vault, n), "rb").read()
                 for n in os.listdir(self.vault)}
        self.assertEqual(before, after)
        self.assertEqual(set(before), set(after), "no new files in the vault")

    def test_vault_and_work_dirs_differ(self):
        # The real module constants (saved before setUp overrode them).
        self.assertNotEqual(self.saved["VAULT_DIR"], self.saved["WORK_DIR"])
        self.assertIn("opt/bla/challenge/v9/hardened", self.saved["VAULT_DIR"])
        self.assertIn("crackme-v9/work", self.saved["WORK_DIR"])
        # The temp dirs used by this test also differ (copies only).
        self.assertNotEqual(V9.VAULT_DIR, V9.WORK_DIR)


class TestReport(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="crackme-v9-report-")
        self.saved_report = V9.REPORT
        V9.REPORT = os.path.join(self.d, "report.md")
        V9._report_header_written[0] = False

    def tearDown(self):
        V9.REPORT = self.saved_report
        V9._report_header_written[0] = False

    def test_append_header_once(self):
        V9._report_header_written[0] = False
        out = V9.append_section("# Existing\n\nOriginal.\n", "### license.cjs (crackme-v9\n\nFindings.\n")
        self.assertTrue(out.startswith("# Existing"))
        self.assertIn("# CrackMe v9", out)
        self.assertEqual(out.count("# CrackMe v9"), 1)
        self.assertIn("Findings.", out)
        out2 = V9.append_section(out, "### policy.py (crackme-v9\n\nMore.\n")
        self.assertEqual(out2.count("# CrackMe v9"), 1)
        self.assertIn("More.", out2)
        self.assertTrue(out2.startswith(out))
        V9._report_header_written[0] = False

    def test_atomic_write_no_temp_left(self):
        with open(V9.REPORT, "w") as f:
            f.write("# Report\n\nOriginal.\n")
        size = V9.append_to_report("### license.cjs (crackme-v9\n\nOK.\n")
        self.assertIsNotNone(size)
        self.assertFalse(os.path.exists(V9.REPORT + ".tmp-crackme-v9"),
                         "no temp file must be left behind")
        data = open(V9.REPORT).read()
        self.assertIn("Original.", data)
        self.assertIn("# CrackMe v9", data)
        self.assertTrue(data.endswith("\n"))

    def test_task_done_in(self):
        self.assertTrue(V9.task_done_in("### license.cjs (crackme-v9\n\nx\n",
                                        "### license.cjs (crackme-v9"))
        self.assertFalse(V9.task_done_in("nothing here\n", "### license.cjs (crackme-v9"))
        self.assertFalse(V9.task_done_in("", "### license.cjs (crackme-v9"))


class TestWrapperSource(unittest.TestCase):
    def test_27b_settings(self):
        src = open(WRAPPER).read()
        self.assertIn("OLLAMA_TIMEOUT = 1800", src)
        self.assertIn("http://127.0.0.1:11434/api/chat", src)
        self.assertNotIn("11435", src, "the router must never be used")
        self.assertNotIn("timeout=600", src)
        self.assertNotIn("timeout = 600", src)
        self.assertIn('"think": True', src)
        self.assertIn('"num_gpu": 0', src)
        self.assertIn('"num_ctx": 4096', src)
        self.assertIn('"keep_alive": "24h"', src)

    def test_no_privilege_escalation(self):
        src = open(WRAPPER).read().lower()
        for bad in ["sudo", "modprobe", "usermod", "chmod", "chown", "setcap", "insmod"]:
            self.assertNotIn(bad, src, "wrapper must not contain %r" % bad)

    def test_no_shell(self):
        src = open(WRAPPER).read()
        self.assertNotIn("os.system", src)
        self.assertNotIn("shell=True", src)

    def test_tool_applicability_names_all_15(self):
        src = open(WRAPPER).read()
        for tool in ["Detect-It-Easy", "capa", "LIEF", "Ghidra", "GhidraMCP",
                     "angr", "Frida", "objection", "jadx", "Apktool", "ILSpy",
                     "asar", "mitmproxy", "Wireshark", "ImHex"]:
            self.assertIn(tool, src, "tool applicability must name %s" % tool)

    def test_expected_digests_match_seal(self):
        # The digests hard-coded in the runner must be the SEAL.json ones
        # (verified by the recon run on 2026-11-10).
        self.assertEqual(V9.EXPECTED["license.cjs"],
                         "a56604751015fe59c7a034dc30799c9286c45d0ae00b1f9df8e4ddc42457fec0")
        self.assertEqual(V9.EXPECTED["panel.html"],
                         "b3e6787d8029cdb6caf4e500e2333648729390c967f981d56f279d77e7c58bbf")
        self.assertEqual(V9.EXPECTED["policy.py"],
                         "a3ffe58c2dc7c1ac7d7f0605cfc1fad1fa1b20f83d4a42710051262c7a2c7e1c")
        self.assertEqual(V9.EXPECTED["core.wasm.gz"],
                         "67aacf5c86c29572df02f142804fd6a784372705f4bc20d90f67942aa903dd96")
        self.assertEqual(V9.EXPECTED["seal.json"],
                         "cbbd7a672a96170a95682d574fa6f31bfa1eb5e32ee88d2651bca471e5455085")
        self.assertEqual(V9.EXPECTED_CORE_WASM,
                         "b38e5d6b7526ca515ac196f6da6ce76d7f1c8261eab9d599f1a466152371b44c")
        self.assertEqual(V9.EXPECTED_CORE_WASM_BYTES, 6883604)
        self.assertEqual(V9.FLAG_SHA256,
                         "06772462f4ba0586ca27aaecf8fd4da5919a336b84f6855de009fc0751c5cf0e")


class TestLauncher(unittest.TestCase):
    def test_no_bang_except_shebang(self):
        lines = open(LAUNCHER).read().splitlines()
        for i, line in enumerate(lines):
            if i == 0:
                self.assertTrue(line.startswith("#!"), "first line must be the shebang")
                continue
            self.assertNotIn("!", line, "line %d must not contain '!': %r" % (i + 1, line))

    def test_launcher_starts_runner(self):
        src = open(LAUNCHER).read()
        self.assertIn("crackme-v9.py", src)
        self.assertIn("nohup", src)
        self.assertIn("</dev/null", src)


class TestReadme(unittest.TestCase):
    def test_readme_covers_run_verify_rollback(self):
        src = open(README).read()
        low = src.lower()
        for word in ["start-crackme-v9.sh", "report.md", "rollback", "verify",
                     "license.cjs", "wabt", "resumable"]:
            self.assertIn(word, low, "README must cover %r" % word)

    def test_readme_states_honest_limits(self):
        src = open(README).read()
        self.assertIn("search the key space", src)
        self.assertIn("simulated tests", src)


class TestEndToEnd(unittest.TestCase):
    """Full main() run with a fake vault, a mocked 27B, and the real Node
    binary. Proves: setup copies + verifies, recon sections land, all
    five 27B tasks append, a candidate key from a 27B reply is verified
    in the working copy, a matching FLAG is confirmed against the public
    commitment, and the status says solved. The 27B is the only mock;
    everything else (setup, recon, Node verification) is real."""

    FAKE_LICENSE_CLI = """#!/usr/bin/env node
"use strict";
const k = process.argv[2] || "";
if (k === "AbCdEfGh12345678") { console.log("FLAG{fake-test-flag}"); }
else { console.log("DENIED"); }
"""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="crackme-v9-e2e-")
        self.vault = os.path.join(self.d, "vault")
        self.base = os.path.join(self.d, "base")
        os.makedirs(self.vault)
        os.makedirs(self.base)
        self.saved = {}
        for name in ["VAULT_DIR", "BASE_DIR", "WORK_DIR", "REPORT", "CALLS_LOG",
                     "LOG_PATH", "STATUS_PATH", "EXPECTED", "EXPECTED_CORE_WASM",
                     "EXPECTED_CORE_WASM_BYTES", "FLAG_SHA256", "call_27b_item"]:
            self.saved[name] = getattr(V9, name)
        V9.VAULT_DIR = self.vault
        V9.BASE_DIR = self.base
        V9.WORK_DIR = os.path.join(self.base, "work")
        V9.REPORT = os.path.join(self.base, "report.md")
        V9.CALLS_LOG = os.path.join(self.base, "27b-calls.jsonl")
        V9.LOG_PATH = os.path.join(self.base, "crackme-v9.log")
        V9.STATUS_PATH = os.path.join(self.base, "status.txt")
        V9._report_header_written[0] = False
        # Fake vault files (the license one is a real Node CLI for the
        # verification step).
        contents = {
            "license.cjs": self.FAKE_LICENSE_CLI.encode(),
            "panel.html": FAKE_HTML.encode(),
            "policy.py": FAKE_PY.encode(),
            "seal.json": b'{"revision": 1, "certificateSha256": "abc"}\n',
        }
        raw_wasm = fake_wasm()
        gz_path = os.path.join(self.vault, "core.wasm.gz")
        with gzip.open(gz_path, "wb") as f:
            f.write(raw_wasm)
        for name, data in contents.items():
            with open(os.path.join(self.vault, name), "wb") as f:
                f.write(data)
        V9.EXPECTED = {name: hashlib.sha256(data).hexdigest()
                       for name, data in contents.items()}
        V9.EXPECTED["core.wasm.gz"] = hashlib.sha256(open(gz_path, "rb").read()).hexdigest()
        V9.EXPECTED_CORE_WASM = hashlib.sha256(raw_wasm).hexdigest()
        V9.EXPECTED_CORE_WASM_BYTES = len(raw_wasm)
        # Point the flag commitment at the fake flag so the solve path is testable.
        V9.FLAG_SHA256 = hashlib.sha256(b"FLAG{fake-test-flag}").hexdigest()
        # Mock the 27B: the license reply proposes the (fake) key; the
        # others return generic on-topic replies with the right markers.
        def fake_call(prompt, task_id, markers, min_chars=150, min_markers=1):
            if "license" in task_id:
                return ("The key is checked in checkKey: it must be a "
                        "16-character string. The key AbCdEfGh12345678 "
                        "unlocks the gate via the WASM export. DENIED otherwise.")
            if "wasm" in task_id:
                return ("The WASM exports unlock and mem. The seal binds the "
                        "revision. The unlock is a SHA-256 KDF.")
            if "policy" in task_id:
                return ("The policy ledger checks the key against the seal. "
                        "The Python ledger holds no key material.")
            if "wat" in task_id:
                return ("This WASM function is the SHA-256 KDF: it loads the "
                        "key, runs ARX rounds, and outputs a commitment.")
            return ("The panel HTML shows the unlock UI. It calls the key "
                    "check in license.cjs.")
        V9.call_27b_item = fake_call

    def tearDown(self):
        for name, val in self.saved.items():
            setattr(V9, name, val)
        V9._report_header_written[0] = False

    def test_full_run_solves(self):
        rc = V9.main()
        self.assertEqual(rc, 0)
        report = open(V9.REPORT).read()
        for marker in ["# CrackMe v9", "## Recon — files", "## Recon — WASM",
                       "## Tool applicability",
                       "### license.cjs (crackme-v9",
                       "### core.wasm + seal.json (crackme-v9",
                       "### policy.py (crackme-v9",
                       "### panel.html (crackme-v9",
                       "## Candidate keys", "## Summary — v1 findings"]:
            self.assertIn(marker, report, "report must contain %r" % marker)
        # The disassembly task depends on wabt; here it is a placeholder
        # (wabt is absent on this machine), which is the honest outcome.
        self.assertIn("### core.wasm disassembly (crackme-v9", report)
        # The candidate key was verified and solved.
        self.assertIn("AbCdEfGh12345678", report)
        self.assertIn("UNLOCKED", report)
        self.assertIn("FLAG{fake-test-flag}", report)
        status = open(V9.STATUS_PATH).read()
        self.assertIn("result: solved", status)
        self.assertIn("solved: yes", status)
        # Working copy exists, vault untouched.
        self.assertTrue(os.path.isfile(os.path.join(V9.WORK_DIR, "core.wasm")))
        self.assertEqual(len(os.listdir(self.vault)), 5)

    def test_full_run_resumable(self):
        self.assertEqual(V9.main(), 0)
        # A second run must not re-call the 27B (all sections exist) and
        # must still exit 0 with the same solved status.
        calls = {"n": 0}
        def counting_call(*a, **k):
            calls["n"] += 1
            return "should not be called"
        V9.call_27b_item = counting_call
        self.assertEqual(V9.main(), 0)
        self.assertEqual(calls["n"], 0, "no 27B call on a re-run (resumable)")
        self.assertIn("result: solved", open(V9.STATUS_PATH).read())


if __name__ == "__main__":
    unittest.main(verbosity=2)
