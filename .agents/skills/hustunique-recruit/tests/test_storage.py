"""storage 单测:加密往返、单行约束、权限、env 目录隔离。"""
import os
import sqlite3
import stat
import tempfile
import unittest

from scripts import storage

DEPARTMENTS = {"计算机学院": ["计算机科学与技术"]}


class StorageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old_env = os.environ.get("HUST_RECRUIT_DIR")
        os.environ["HUST_RECRUIT_DIR"] = self._tmp.name

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("HUST_RECRUIT_DIR", None)
        else:
            os.environ["HUST_RECRUIT_DIR"] = self._old_env
        self._tmp.cleanup()

    def test_data_dir_created(self):
        d = storage.data_dir()
        self.assertTrue(d.is_dir())
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(os.stat(d).st_mode), 0o700)

    def test_encrypt_decrypt_roundtrip(self):
        secret = "SSO_SESSION=mock-session-1234567890"
        blob = storage.encrypt(secret)
        self.assertNotIn("mock-session-1234567890", blob)
        self.assertEqual(storage.decrypt(blob), secret)

    def test_encrypt_nonce_randomness(self):
        a = storage.encrypt("same-value")
        b = storage.encrypt("same-value")
        self.assertNotEqual(a, b)
        self.assertEqual(storage.decrypt(a), storage.decrypt(b))

    def test_session_single_row_and_clear(self):
        storage.save_session("cookie-a", email="a@example.com")
        storage.save_session("cookie-b", email="b@example.com")
        self.assertEqual(storage.load_session(), "cookie-b")
        with sqlite3.connect(str(storage.db_path())) as conn:
            count = conn.execute("SELECT COUNT(*) FROM session").fetchone()[0]
        self.assertEqual(count, 1)
        storage.clear_session()
        self.assertIsNone(storage.load_session())

    def test_draft_roundtrip(self):
        storage.save_draft("rec-1", {"grade": "大二", "groups": ["web"]})
        draft = storage.load_draft()
        self.assertEqual(draft["recruitment_id"], "rec-1")
        self.assertEqual(draft["fields"]["grade"], "大二")
        self.assertEqual(draft["fields"]["groups"], ["web"])

    def test_cache_roundtrip(self):
        storage.save_cache({"rec-1": {"grade": "大二"}})
        cache = storage.load_cache()
        self.assertEqual(cache, {"rec-1": {"grade": "大二"}})

    def test_db_permissions(self):
        storage.save_session("x")
        if os.name != "nt":
            mode = stat.S_IMODE(os.stat(str(storage.db_path())).st_mode)
            self.assertEqual(mode, 0o600)


if __name__ == "__main__":
    unittest.main()