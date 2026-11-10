"""SAF-14 regression: oversized or negative Content-Length is refused before any read."""
import importlib.util, os, socket, tempfile, threading, unittest
from http.server import ThreadingHTTPServer
HERE = os.path.dirname(os.path.abspath(__file__))


class BodyCap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("orch_saf14", os.path.join(HERE, "..", "orchestrator.py"))
        cls.o = importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.o)
        cls.o.LOG_PATH = os.path.join(tempfile.mkdtemp(), "verdicts.log")
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), cls.o.Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def post(self, path, length, body=b"{}"):
        s = socket.create_connection(self.srv.server_address, timeout=5)
        s.sendall(b"POST %s HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Type: application/json\r\n"
                  b"Content-Length: %s\r\n\r\n" % (path.encode(), str(length).encode()) + body)
        try:
            return s.recv(64).split(b" ")[1]
        finally:
            s.close()

    def test_huge_length_refused_without_reading(self):
        for path in ("/verdict", "/jarvis"):
            self.assertEqual(self.post(path, 100 * 1024 * 1024), b"400")

    def test_negative_length_refused(self):
        for path in ("/verdict", "/jarvis"):
            self.assertEqual(self.post(path, -1), b"400")

    def test_helper_limits(self):
        self.assertEqual(self.o._body_len({"Content-Length": "12"}), 12)
        with self.assertRaises(ValueError):
            self.o._body_len({"Content-Length": str(self.o.MAX_BODY + 1)})


class GpuBody(unittest.TestCase):
    def test_invalid_length_does_not_swap(self):
        import io
        import types
        spec = importlib.util.spec_from_file_location(
            "gpu_saf14", os.path.join(HERE, "..", "gpu-orchestrator", "gpu_orchestrator.py"))
        g = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(g)
        called = []
        g.ensure_llm = lambda *a, **k: called.append(a)
        g.ensure_comfy = lambda *a, **k: called.append(a)

        class F:
            def __init__(self, n):
                self.headers = {"Content-Length": str(n)}
                self.close_connection = False
                self.path = "/acquire"
                self.rfile = io.BytesIO(b"")
                self.sent = None

            def _send(self, status, payload):
                self.sent = (status, payload)

        for n in (-1, 300 * 1024):
            fake = F(n)
            fake._read_json = types.MethodType(g.Handler._read_json, fake)
            g.Handler.do_POST(fake)
            self.assertEqual(fake.sent[0], 413, n)
            self.assertTrue(fake.close_connection)
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
