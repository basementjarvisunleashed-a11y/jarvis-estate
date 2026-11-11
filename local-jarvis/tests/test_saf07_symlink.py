"""SAF-07 regression: a symlink inside an allowed root cannot escape it."""
import importlib.util, os, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))


class Symlink(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.docs = os.path.join(self.base, "Documents"); os.makedirs(self.docs)
        out = os.path.join(self.base, "outside"); os.makedirs(out)
        with open(os.path.join(out, "secret.txt"), "w") as fh:
            fh.write("DUMMY")
        with open(os.path.join(self.docs, "ok.txt"), "w") as fh:
            fh.write("fine")
        os.symlink(out, os.path.join(self.docs, "link"))
        os.environ["JARVIS_ROOTS"] = self.docs
        spec = importlib.util.spec_from_file_location("orch_saf07", os.path.join(HERE, "..", "orchestrator.py"))
        self.o = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.o)

    def test_link_escape_refused_every_form(self):
        for p in ("Documents/link/secret.txt", os.path.join(self.docs, "link", "secret.txt"), "link/secret.txt"):
            ap, err = self.o._safe_path(p)
            self.assertIsNone(ap, p); self.assertIn("refused", err)
        self.assertTrue(self.o.tool_file_read({"path": "Documents/link/secret.txt"}).startswith("ERROR"))

    def test_normal_paths_still_work(self):
        self.assertIn("fine", self.o.tool_file_read({"path": "Documents/ok.txt"}))
        self.assertEqual(self.o._safe_path("Documents")[1], None)

    def test_search_and_list_do_not_follow_link(self):
        sub = os.path.join(self.docs, "notes")
        os.makedirs(sub)
        with open(os.path.join(sub, "note.txt"), "w") as fh:
            fh.write("n")
        found = self.o.tool_file_search({"dir": "Documents", "pattern": "*"})
        self.assertIn("ok.txt", found)
        self.assertIn("notes/note.txt", found)
        self.assertNotIn("secret.txt", found)
        listed = self.o.tool_file_list({"dir": "Documents"})
        self.assertIn("ok.txt", listed)
        self.assertNotIn("secret.txt", listed)
        self.assertNotIn("DUMMY", listed)


if __name__ == "__main__":
    unittest.main()
