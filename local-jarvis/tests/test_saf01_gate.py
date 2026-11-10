"""SAF-01 regression: /jarvis and /verdict are not open to the network or to cross-site requests."""
import importlib.util, json, os, sys, threading, unittest, http.client
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    spec = importlib.util.spec_from_file_location("orch_saf01", os.path.join(HERE, "..", "orchestrator.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


class Gate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = load()
        cls.o.jarvis_ask = lambda text: ("ok", [])   # no Ollama needed
        cls.o.record_verdict = lambda *a, **k: {"id": "1", "decision": "approve"}
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), cls.o.Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.port = cls.srv.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def post(self, path, ctype="application/json", host=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        h = {"Content-Type": ctype}
        if host:
            h["Host"] = host
        c.request("POST", path, json.dumps({"text": "hi", "id": "1", "decision": "approve"}), h)
        r = c.getresponse(); r.read(); return r.status

    def test_default_bind_is_loopback(self):
        self.assertEqual(self.o.HOST, "127.0.0.1")

    def test_local_json_still_works(self):
        self.assertEqual(self.post("/jarvis"), 200)

    def test_cross_site_text_plain_refused(self):
        self.assertEqual(self.post("/jarvis", "text/plain"), 403)
        self.assertEqual(self.post("/verdict", "text/plain"), 403)

    def test_dns_rebinding_host_refused(self):
        self.assertEqual(self.post("/jarvis", host="attacker.example:8080"), 403)

    def test_remote_peer_needs_token(self):
        # RFC 5737 documentation address. Not a host on this network.
        err = self.o.request_gate(_Fake("192.0.2.10", "127.0.0.1"), True)
        self.assertIn("JARVIS_TOKEN", err)
        # Hex-form IPv4-mapped loopback is still loopback.
        self.assertIsNone(self.o.request_gate(
            _Fake("::ffff:7f00:1", "localhost"), True))

    def test_remote_token_and_host_case(self):
        # JARVIS_TOKEN is read at import. JARVIS_ALLOWED_HOSTS is read
        # per request, so it has to stay set for the calls below.
        os.environ["JARVIS_TOKEN"] = "example-token"
        os.environ["JARVIS_ALLOWED_HOSTS"] = "Watch.Example"
        try:
            o = load()
            self.assertIsNone(o.request_gate(
                _Fake("192.0.2.10", "watch.example:8080",
                      authorization="Bearer example-token"), True))
            self.assertEqual(
                o.request_gate(_Fake("192.0.2.10", "watch.example",
                                     authorization="Bearer wrong"), True),
                "unauthorized")
            self.assertEqual(
                o.request_gate(_Fake("192.0.2.10", "attacker.example",
                                     authorization="Bearer example-token"), True),
                "host not allowed")
        finally:
            os.environ.pop("JARVIS_TOKEN", None)
            os.environ.pop("JARVIS_ALLOWED_HOSTS", None)


class _Fake:
    def __init__(self, peer, host, content_type="application/json", authorization=""):
        self.client_address = (peer, 9)
        self.headers = {
            "Host": host,
            "Content-Type": content_type,
            "Authorization": authorization,
        }


if __name__ == "__main__":
    unittest.main()
