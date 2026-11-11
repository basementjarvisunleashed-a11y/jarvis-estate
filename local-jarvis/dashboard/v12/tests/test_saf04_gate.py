"""SAF-04 regression: the dashboard answers loopback and tailnet peers only,
refuses rebinding Host headers and cross-site simple POSTs."""
import http.client
import importlib.util
import os
import threading
import unittest
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("dash_saf04", os.path.join(HERE, "..", "server.py"))
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)


class Gate(unittest.TestCase):
    def test_peers(self):
        # 100.64.0.1 and fd7a:115c:a1e0::/48 are the documentation ranges
        # for the tailnet, not an address of a real node.
        for ok in ("127.0.0.1", "::1", "100.64.0.1", "fd7a:115c:a1e0::1", "::ffff:127.0.0.1"):
            self.assertTrue(d.peer_allowed(ok), ok)
        for bad in ("192.168.1.50", "10.0.0.7", "172.16.0.9", "192.0.2.1", "fe80::1", "garbage"):
            self.assertFalse(d.peer_allowed(bad), bad)

    def test_hosts(self):
        for ok in ("127.0.0.1:8899", "localhost:8899", "100.64.0.1:8899",
                   "example.ts.net:8899", "[::1]:8899"):
            self.assertTrue(d.host_allowed(ok), ok)
        for bad in ("attacker.example:8899", "", None, "127.0.0.1.attacker.example",
                    "192.168.1.50:8899", "192.0.2.1", "10.0.0.7:8899"):
            self.assertFalse(d.host_allowed(bad), bad)

    def test_handler_refuses_rebinding_and_simple_post(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), d.Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        port = srv.server_address[1]
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            c.request("GET", "/no-such", headers={"Host": "attacker.example:%d" % port})
            resp = c.getresponse(); resp.read()
            self.assertEqual(resp.status, 403)

            c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            c.request("POST", "/api/play", body=b"{}", headers={
                "Host": "127.0.0.1:%d" % port,
                "Content-Type": "text/plain",
            })
            resp = c.getresponse(); resp.read()
            self.assertEqual(resp.status, 415)

            c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            c.request("GET", "/no-such", headers={"Host": "127.0.0.1:%d" % port})
            resp = c.getresponse(); resp.read()
            self.assertEqual(resp.status, 404)
        finally:
            srv.shutdown()


if __name__ == "__main__":
    unittest.main()
