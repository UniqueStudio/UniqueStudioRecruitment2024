"""validate 单测:动态 fetch DEPARTMENTS.json(fail-closed) + 表单字段校验。"""
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from scripts import validate
from scripts.validate import ValidationError, fetch_departments, validate_form

DEPARTMENTS = {"计算机学院": ["计算机科学与技术"], "软件学院": ["软件工程"]}

VALID = {
    "groups": ["web"],
    "grade": "大二",
    "rank": "10%",
    "institute": "计算机学院",
    "major": "计算机科学与技术",
    "intro": "hello",
    "is_quick": "true",
}


class DepartmentsServer:
    """本地 HTTP 服务,用于测试 fetch_departments 的成败路径。"""

    def __init__(self, payload):
        self._payload = payload

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/DEPARTMENTS.json":
                    body = json.dumps(self.server._payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("content-type", "application/json")
                    self.send_header("content-length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    body = b"not found"
                    self.send_response(404)
                    self.send_header("content-length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

            def log_message(self, *args):
                pass

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server._payload = self._payload
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def url(self):
        host, port = self._server.server_address
        return f"http://{host}:{port}/DEPARTMENTS.json"

    def close(self):
        self._server.shutdown()
        self._server.server_close()


class FetchDepartmentsTest(unittest.TestCase):
    def test_fetch_ok(self):
        server = DepartmentsServer(DEPARTMENTS)
        try:
            result = fetch_departments(server.url())
            self.assertEqual(result, DEPARTMENTS)
        finally:
            server.close()

    def test_fetch_fail_closed(self):
        server = DepartmentsServer({"bad": "shape"})
        try:
            with self.assertRaises(ValidationError):
                fetch_departments(server.url() + "404")
        finally:
            server.close()

    def test_fetch_malformed_shape(self):
        server = DepartmentsServer({"学园": "不是列表"})
        try:
            with self.assertRaises(ValidationError):
                fetch_departments(server.url())
        finally:
            server.close()

    def test_fetch_connection_error(self):
        with self.assertRaises(ValidationError):
            fetch_departments("http://127.0.0.1:1/DEPARTMENTS.json")


class ValidateFormTest(unittest.TestCase):
    def test_valid_form(self):
        self.assertEqual(validate_form(dict(VALID), DEPARTMENTS), [])

    def test_valid_blockchain_only(self):
        fields = dict(VALID, groups=["blockchain"])
        self.assertEqual(validate_form(fields, DEPARTMENTS), [])

    def test_valid_regular_plus_blockchain(self):
        fields = dict(VALID, groups=["web", "blockchain"])
        self.assertEqual(validate_form(fields, DEPARTMENTS), [])

    def test_invalid_institute(self):
        fields = dict(VALID, institute="不存在的学院")
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("学院" in e for e in errors))

    def test_invalid_major(self):
        fields = dict(VALID, major="航天工程")
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("专业" in e for e in errors))

    def test_deprecated_group(self):
        fields = dict(VALID, groups=["android"])
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("废弃" in e for e in errors))

    def test_two_regular_groups(self):
        fields = dict(VALID, groups=["web", "pm"])
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("常规组只能选择一个" in e for e in errors))

    def test_unknown_group(self):
        fields = dict(VALID, groups=["hacker"])
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("未知组" in e for e in errors))

    def test_empty_groups(self):
        fields = dict(VALID, groups=[])
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("组" in e for e in errors))

    def test_bad_grade_and_rank(self):
        fields = dict(VALID, grade="博后", rank="7%")
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("年级" in e for e in errors))
        self.assertTrue(any("排名" in e for e in errors))

    def test_bad_is_quick(self):
        fields = dict(VALID, is_quick="yes")
        errors = validate_form(fields, DEPARTMENTS)
        self.assertTrue(any("is_quick" in e for e in errors))

    def test_missing_required(self):
        errors = validate_form({}, DEPARTMENTS)
        self.assertTrue(any("组" in e for e in errors))
        self.assertTrue(any("年级" in e for e in errors))
        self.assertTrue(any("学院" in e for e in errors))
        self.assertTrue(any("专业" in e for e in errors))
        self.assertTrue(any("自我介绍" in e for e in errors))

    def test_require_groups_false_skips_groups(self):
        fields = {k: v for k, v in VALID.items() if k != "groups"}
        errors = validate_form(fields, DEPARTMENTS, require_groups=False)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()