"""client 单测:multipart 编码、cookie 解析、信封/会话过期处理。"""
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from scripts.client import (
    AUTH_FAILED_MARKER,
    ApiClient,
    ApiError,
    encode_multipart,
    file_part,
    parse_set_cookie,
)


class MultipartTest(unittest.TestCase):
    def test_encode_multipart_text_and_file(self):
        body, headers = encode_multipart(
            {
                "grade": "大二",
                "resume": ("resume.pdf", b"%PDF-1.4 hello", "application/pdf"),
                "is_quick": "true",
            }
        )
        text = body.decode("utf-8", errors="replace")
        self.assertIn('name="grade"', text)
        self.assertIn('name="resume"; filename="resume.pdf"', text)
        self.assertIn("content-type: application/pdf", text)
        self.assertIn(b"%PDF-1.4 hello", body)
        boundary = headers["content-type"].split("boundary=")[1]
        self.assertIn(f"--{boundary}", text)
        self.assertTrue(text.rstrip().endswith(f"--{boundary}--"))

    def test_file_part_missing(self):
        with self.assertRaises(ApiError):
            file_part("/nonexistent/path/file.pdf")

    def test_file_part_content_type_from_extension(self):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(b"data")
            name = fh.name
        try:
            filename, data, ctype = file_part(name)
            self.assertEqual(ctype, "application/pdf")
            self.assertEqual(data, b"data")
        finally:
            import os

            os.unlink(name)


class ParseSetCookieTest(unittest.TestCase):
    def test_extract_sso_session(self):
        headers = {
            "set-cookie": "SSO_SESSION=mock-session-1; Path=/; HttpOnly",
            "content-type": "application/json",
        }
        self.assertEqual(parse_set_cookie(headers), "mock-session-1")

    def test_no_cookie(self):
        self.assertIsNone(parse_set_cookie({"content-type": "text/html"}))


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/user/me":
            body = (
                '{"code":401,"data":null,"msg":"'
                + AUTH_FAILED_MARKER
                + '"}'
            ).encode("utf-8")
            self.send_response(401)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/recruitments/pending":
            body = b'{"code":200,"data":{"uid":"rec-1","name":"R"},"msg":"ok"}'
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = b'{"code":404,"data":null,"msg":"no"}'
            self.send_response(404)
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):
        pass


class EnvelopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_hr_ok_envelope(self):
        client = ApiClient(self.base, cookie="c")
        pending = client.hr_recruitment_pending()
        self.assertEqual(pending["uid"], "rec-1")

    def test_hr_expired_401(self):
        client = ApiClient(self.base, cookie="stale")
        with self.assertRaises(ApiError) as ctx:
            client.hr_me()
        self.assertTrue(ctx.exception.expired)

    def test_hr_business_error(self):
        client = ApiClient(self.base, cookie="c")
        with self.assertRaises(ApiError):
            client.hr_recruitment_by_id("rec-404")


if __name__ == "__main__":
    unittest.main()