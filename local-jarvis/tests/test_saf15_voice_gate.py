"""SAF-15 regression: the voice gate is off only when chosen, and fails closed when on."""
import ast, json, os, subprocess, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "jarvis_voice.py")


def gate_ns(env):
    """Load only the gate settings and class (the module loads Whisper at import)."""
    with open(SRC, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    keep = [n for n in tree.body if (isinstance(n, ast.Assign) and any(
        getattr(t, "id", "") in ("GATE_PY", "GATE", "GATE_MODE") for t in n.targets))
        or (isinstance(n, ast.ClassDef) and n.name == "Gate")]
    old = dict(os.environ); os.environ.update(env)
    try:
        ns = {"subprocess": subprocess, "json": json, "os": os, "sys": sys, "__file__": SRC}
        exec(compile(ast.Module(body=keep, type_ignores=[]), SRC, "exec"), ns)
        return ns
    finally:
        os.environ.clear(); os.environ.update(old)


class VoiceGate(unittest.TestCase):
    def test_no_windows_paths(self):
        ns = gate_ns({})
        self.assertNotIn("\\", ns["GATE_PY"] + ns["GATE"])
        self.assertTrue(ns["GATE"].endswith(os.sep + "voice_gate.py"))

    def test_off_is_explicit_pass_through(self):
        g = gate_ns({"JARVIS_VOICE_GATE": "off"})["Gate"]()
        self.assertEqual(g.info["gate"], "off"); self.assertEqual(g.check("x.wav"), (True, 1.0))

    def test_on_but_broken_refuses_everyone(self):
        g = gate_ns({"JARVIS_VOICE_GATE": "on", "JARVIS_GATE_PY": "/nonexistent/python"})["Gate"]()
        self.assertEqual(g.check("stranger.wav"), (False, 0.0))


if __name__ == "__main__":
    unittest.main()
