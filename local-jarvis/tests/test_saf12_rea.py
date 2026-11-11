"""SAF-12 regression: rea_analyze only reads inside the allowed folders."""
import importlib.util, os, subprocess, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))


class R:
    returncode, stdout, stderr = 0, "{}", ""


class Rea(unittest.TestCase):
    def setUp(self):
        base = tempfile.mkdtemp()
        self.root = os.path.join(base, "Documents"); os.makedirs(self.root)
        self.inside = os.path.join(self.root, "sample.bin")
        self.outside = os.path.join(base, "private.bin")
        for path in (self.inside, self.outside):
            with open(path, "wb"):
                pass
        os.environ["JARVIS_ROOTS"] = self.root; os.environ["JARVIS_REA_BIN"] = "/usr/bin/rea-agents"
        spec = importlib.util.spec_from_file_location("orch_saf12", os.path.join(HERE, "..", "orchestrator.py"))
        self.o = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.o)
        self.calls = []; self._run = subprocess.run
        subprocess.run = lambda argv, **k: (self.calls.append(argv), R())[1]

    def tearDown(self):
        subprocess.run = self._run
        os.environ.pop("JARVIS_REA_BIN", None)
        os.environ.pop("JARVIS_ROOTS", None)

    def test_outside_target_refused(self):
        r = self.o.tool_rea_analyze({"command": "analyze", "target": self.outside})
        self.assertTrue(r.startswith("ERROR"), r); self.assertEqual(self.calls, [])

    def test_inside_target_runs_without_npx(self):
        self.o.tool_rea_analyze({"command": "analyze", "target": self.inside})
        self.assertEqual(self.calls[0][0], "/usr/bin/rea-agents")
        self.assertNotIn("-y", self.calls[0])


if __name__ == "__main__":
    unittest.main()
