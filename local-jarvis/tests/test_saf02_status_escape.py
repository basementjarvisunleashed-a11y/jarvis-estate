"""SAF-02 regression: mesh-supplied topic segments render as text on the status page."""
import importlib.util, json, os, threading, unittest, http.client
from http.server import ThreadingHTTPServer
HERE = os.path.dirname(os.path.abspath(__file__))


class Msg:
    def __init__(self, topic, payload):
        self.topic, self.payload = topic, json.dumps(payload).encode()


class Escape(unittest.TestCase):
    def test_region_from_public_broker_is_escaped(self):
        os.environ["JARVIS_WATCH_NODE"] = "!deadbeef"  # the pinned watch (SAF-03) may still be hostile-named
        spec = importlib.util.spec_from_file_location("orch_saf02", os.path.join(HERE, "..", "orchestrator.py"))
        o = importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
        o.get_brief = lambda: {"id": "1", "title": "t", "body": "b"}
        o._vlc_ping = lambda: False
        evil = "<img src=x onerror=alert(1)>"
        o._mqtt_on_message(None, None, Msg("msh/%s/2/json/mqtt/!deadbeef" % evil, {"type": "text", "payload": {"text": "READY"}}))
        srv = ThreadingHTTPServer(("127.0.0.1", 0), o.Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
            c.request("GET", "/"); page = c.getresponse().read().decode()
        finally:
            srv.shutdown()
        self.assertNotIn(evil, page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)


if __name__ == "__main__":
    unittest.main()
