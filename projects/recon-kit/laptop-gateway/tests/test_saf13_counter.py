"""SAF-13 regression: the RX replay counter survives a bridge restart."""
import importlib.util, logging, os, stat, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
logging.disable(logging.CRITICAL)


def load():
    spec = importlib.util.spec_from_file_location("lora_saf13", os.path.join(HERE, "..", "jarvis_lora_bridge.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


class Counter(unittest.TestCase):
    def setUp(self):
        os.environ["JV_LORA_KEY"] = "example-test-key-not-real"
        os.environ.pop("JV_LORA_CTR_FILE", None)
        os.environ["XDG_STATE_HOME"] = tempfile.mkdtemp()

    def test_default_path_is_posix_state_dir(self):
        b = load()
        self.assertTrue(b.CTR_FILE.startswith(os.environ["XDG_STATE_HOME"]), b.CTR_FILE)

    def test_replay_after_restart_dropped(self):
        b = load()
        frame = b.build_frame("m1", "Q", 0, 1, "hello", ctr=5)
        self.assertIsNotNone(b.parse_frame(frame))
        self.assertEqual(stat.S_IMODE(os.stat(b.CTR_FILE).st_mode), 0o600)
        b2 = load()                          # restart
        self.assertEqual(b2._RX_CTR, 5)
        self.assertIsNone(b2.parse_frame(frame))

    def test_unpersistable_counter_fails_closed(self):
        os.environ["JV_LORA_CTR_FILE"] = "/proc/no-such-dir/counters.json"
        b = load()
        self.assertIsNone(b.parse_frame(b.build_frame("m2", "Q", 0, 1, "hi", ctr=7)))


if __name__ == "__main__":
    unittest.main()
