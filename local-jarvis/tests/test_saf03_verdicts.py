"""SAF-03 regression: verdicts must answer the open card; strangers on the public broker are ignored."""
import importlib.util, json, os, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))


class Msg:
    def __init__(self, topic, payload):
        self.topic, self.payload = topic, json.dumps(payload).encode()


def load(node=""):
    os.environ["JARVIS_WATCH_NODE"] = node
    spec = importlib.util.spec_from_file_location("orch_saf03", os.path.join(HERE, "..", "orchestrator.py"))
    o = importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
    o.LOG_PATH = os.path.join(tempfile.mkdtemp(), "verdicts.log")
    o.mqtt_publish_brief = lambda card: None
    o._draft_brief = lambda: ("t", "b")
    return o


class Verdicts(unittest.TestCase):
    def test_wrong_id_refused(self):
        o = load(); card = o.get_brief()
        with self.assertRaises(o.StaleVerdict):
            o.record_verdict(str(int(card["id"]) + 99), "approve")
        self.assertEqual(o._state["verdicts"], 0)
        o.record_verdict(card["id"], "deny")
        self.assertEqual(o._state["verdicts"], 1)

    def test_mesh_off_without_pinned_node(self):
        o = load("")
        self.assertFalse(o.mqtt_start())

    def test_stranger_node_ignored(self):
        o = load("!a1b2c3d4"); o.get_brief()
        o._state["mqtt"]["ok"] = True
        o._mqtt_on_message(None, None, Msg("msh/US/2/json/mqtt/!0badc0de", {"type": "text", "payload": {"text": "APPROVE"}}))
        self.assertEqual(o._state["verdicts"], 0)
        self.assertIsNone(o._state["mqtt"]["watch_id"])
        o._mqtt_on_message(None, None, Msg("msh/US/2/json/mqtt/!a1b2c3d4", {"type": "text", "payload": {"text": "APPROVE"}}))
        self.assertEqual(o._state["verdicts"], 1)


if __name__ == "__main__":
    unittest.main()
