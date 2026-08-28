"""端到端测试:在扩展后的 mock-api.mjs 上驱动完整 CLI 流程。

测试自动拉起 mock(随机空闲端口,不占用 8788),所有 CLI 调用指向该 mock;
HUST_RECRUIT_DIR 用临时目录隔离,不碰真实主目录库。
"""
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.request
from contextlib import contextmanager
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from scripts import storage

def _find_repo_root():
    """沿目录向上找包含 scripts/mock-api.mjs 的仓库根,不依赖固定层级。"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "scripts" / "mock-api.mjs").exists():
            return parent
    raise RuntimeError("找不到仓库根目录 (scripts/mock-api.mjs)")


REPO_ROOT = _find_repo_root()
MOCK_SCRIPT = REPO_ROOT / "scripts" / "mock-api.mjs"

PHONE = "13800138000"
EMAIL = "mock@example.com"
PASSWORD = "123456"
RID = "rec-1"


def run_cli(argv, extra_env=None):
    """进程内运行 CLI,返回 (退出码, stdout, stderr)。"""
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    old = os.environ.copy()
    os.environ.clear()
    os.environ.update(env)
    stdout, stderr = StringIO(), StringIO()
    try:
        from scripts import cli

        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = cli.main(argv)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
    finally:
        os.environ.clear()
        os.environ.update(old)
    return code, stdout.getvalue(), stderr.getvalue()


def mock_request(mock_url, path, method="GET"):
    req = urllib.request.Request(mock_url + path, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        data = json.loads(exc.read().decode("utf-8"))
    if isinstance(data, dict) and "code" in data and "data" in data:
        return data["data"]
    return data


def mock_mutate(mock_url, field, value):
    req = urllib.request.Request(
        mock_url + "/__mock__/mutate",
        data=json.dumps({"field": field, "value": value}).encode("utf-8"),
        method="POST",
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_mock(mock_url, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(mock_url + "/__mock__/state", timeout=2).read()
            return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("mock 未就绪")


@unittest.skipUnless(shutil.which("node"), "需要 node 运行 mock-api.mjs")
class CliE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            cls._port = sock.getsockname()[1]
        cls._mock_url = f"http://127.0.0.1:{cls._port}"
        mock_env = dict(os.environ)
        mock_env["MOCK_API_PORT"] = str(cls._port)
        cls._mock = subprocess.Popen(
            ["node", str(MOCK_SCRIPT)],
            env=mock_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_mock(cls._mock_url)

    @classmethod
    def tearDownClass(cls):
        cls._mock.terminate()
        try:
            cls._mock.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls._mock.kill()

    def setUp(self):
        mock_request(self._mock_url, "/__mock__/reset?scenario=authed", method="POST")
        self._tmp = tempfile.TemporaryDirectory()
        self._env = {
            "HUST_RECRUIT_DIR": self._tmp.name,
            "HUST_SSO_BASE": self._mock_url + "/api",
            "HUST_HR_BASE": self._mock_url,
            "HUST_DEPARTMENTS_URL": self._mock_url + "/DEPARTMENTS.json",
        }

    def tearDown(self):
        self._tmp.cleanup()

    def _cli(self, argv, env=None):
        payload = dict(self._env)
        if env:
            payload.update(env)
        return run_cli(argv, extra_env=payload)

    # ---- 流程 ----

    @contextmanager
    def _env_ctx(self, env=None):
        """让 storage 等库调用也指向本测试的临时目录。"""
        payload = dict(self._env)
        if env:
            payload.update(env)
        old = os.environ.copy()
        os.environ.clear()
        os.environ.update(payload)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_not_logged_in(self):
        code, _, stderr = self._cli(["status"])
        self.assertEqual(code, 4)
        self.assertIn("未登录", stderr)

    def test_login_wrong_password(self):
        code, _, stderr = self._cli(
            ["login", "--method", "phone", "--phone", PHONE],
            env={"HUST_PASSWORD": "bad"},
        )
        self.assertEqual(code, 1)
        self.assertIn("wrong password", stderr)

    def test_credentials_file_login_and_wipe(self):
        # 初始化模板
        code, stdout, _ = self._cli(["credentials", "--init"])
        self.assertEqual(code, 0, stdout)
        with self._env_ctx():
            cred_path = storage.data_dir() / "credentials.json"
            self.assertTrue(cred_path.exists())
            self.assertIn("username", cred_path.read_text(encoding="utf-8"))
        # 未填写 → 登录报错并提示
        code, _, stderr = self._cli(["login"])
        self.assertEqual(code, 1)
        self.assertIn("凭据文件", stderr)
        # 填写 mock 测试账号后直接 login
        with self._env_ctx():
            cred_path.write_text(
                json.dumps({"username": PHONE, "password": PASSWORD}),
                encoding="utf-8",
            )
        code, stdout, _ = self._cli(["login"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("登录成功", stdout)
        self.assertIn("删除", stdout)  # 登录成功后的删除提醒
        # wipe 删除凭据文件
        code, stdout, _ = self._cli(["credentials", "--wipe"])
        self.assertEqual(code, 0, stdout)
        with self._env_ctx():
            self.assertFalse(cred_path.exists())

    def test_full_flow(self):
        # login
        code, stdout, _ = self._cli(
            ["login", "--method", "phone", "--phone", PHONE],
            env={"HUST_PASSWORD": PASSWORD},
        )
        self.assertEqual(code, 0, stdout)
        self.assertNotIn("mock-session", stdout)

        # status:注册场景已有 application
        code, stdout, _ = self._cli(["status"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("Mock User", stdout)
        self.assertIn("app-1", stdout)

        # apply(带简历文件)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(b"%PDF-1.4 hello resume")
            resume_path = fh.name
        try:
            code, stdout, _ = self._cli(
                [
                    "apply",
                    "--recruitment-id", RID,
                    "--group", "web",
                    "--grade", "大一",
                    "--institute", "计算机学院",
                    "--major", "计算机科学与技术",
                    "--rank", "暂无",
                    "--intro", "e2e intro",
                    "--qq", "8888",
                    "--is-quick",
                    "--resume", resume_path,
                ]
            )
            self.assertEqual(code, 0, stdout)
        finally:
            os.unlink(resume_path)

        state = mock_request(self._mock_url, "/__mock__/state")
        posts = [
            m for m in state["mutations"]
            if m["method"] == "POST" and m["path"] == "/applications/"
        ]
        self.assertEqual(len(posts), 1)
        fields = posts[0]["fields"]
        self.assertEqual(fields["group"], "web")
        self.assertEqual(fields["grade"], "大一")
        self.assertEqual(fields["institute"], "计算机学院")
        self.assertEqual(fields["is_quick"], "true")
        self.assertEqual(state["application"]["grade"], "大一")
        self.assertFalse("is_project_c" in fields)

        # applications 列出
        code, stdout, _ = self._cli(["applications"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("web", stdout)
        self.assertIn("大一", stdout)

        # 面试时间 + 单选 + 多选
        code, stdout, _ = self._cli(["interview-times", "--rid", RID, "--name", "web"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("slot-1", stdout)
        code, _, _ = self._cli(
            ["interview-select", "--aid", "app-1", "--type", "group", "--iid", "slot-1"]
        )
        self.assertEqual(code, 0)
        code, _, _ = self._cli(
            ["interview-slots", "--aid", "app-1", "--type", "team", "--iids", "slot-1,slot-2"]
        )
        self.assertEqual(code, 0)
        state = mock_request(self._mock_url, "/__mock__/state")
        self.assertEqual(state["application"]["interview_allocations_group"]["uid"], "slot-1")
        self.assertEqual(state["application"]["interview_selections"][0]["uid"], "slot-2")

        # 笔试(type=2 → URL)
        code, stdout, _ = self._cli(["written-test", "--rid", RID, "--group", "web"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("https://example.test/written-test", stdout)

        # 简历下载
        code, stdout, _ = self._cli(["resume-download", "--aid", "app-1"])
        self.assertEqual(code, 0, stdout)
        saved = Path("resume-app-1.pdf")
        self.assertTrue(saved.exists())
        self.assertEqual(saved.read_bytes(), b"mock resume")
        saved.unlink()

        # 更新资料 → 服务端字段变化
        code, stdout, _ = self._cli(
            [
                "update",
                "--grade", "大三",
                "--institute", "计算机学院",
                "--major", "计算机科学与技术",
                "--rank", "25%",
                "--intro", "updated intro",
            ]
        )
        self.assertEqual(code, 0, stdout)
        state = mock_request(self._mock_url, "/__mock__/state")
        self.assertEqual(state["application"]["grade"], "大三")
        self.assertEqual(state["application"]["rank"], "25%")

        # 冲突:mock 服务端改字段 → 读命令退出码 2 且 diff 含 grade
        mock_mutate(self._mock_url, "grade", "研究生")
        code, stdout, stderr = self._cli(["applications"])
        self.assertEqual(code, 2)
        self.assertIn("grade", stdout)
        self.assertIn("服务端", stdout)

        # sync server → 冲突消除,草稿与缓存同步为服务端值
        code, _, _ = self._cli(["sync", "--strategy", "server"])
        self.assertEqual(code, 0)
        code, stdout, _ = self._cli(["applications"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("研究生", stdout)

        # sync local 行为:冲突后保留本地草稿,但缓存刷新
        mock_mutate(self._mock_url, "rank", "100%")
        code, _, _ = self._cli(["applications"])
        self.assertEqual(code, 2)
        code, _, _ = self._cli(["sync", "--strategy", "local"])
        self.assertEqual(code, 0)
        code, stdout, _ = self._cli(["applications"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("100%", stdout)
        with self._env_ctx():
            draft = storage.load_draft()
            self.assertEqual(draft["fields"]["rank"], "25%")

        # 过期会话 → 退出码 3
        with self._env_ctx():
            storage.save_session("bogus-cookie")
        code, _, _ = self._cli(["applications"])
        self.assertEqual(code, 3)

        # 重新登录后放弃申请
        code, _, _ = self._cli(
            ["login", "--method", "phone", "--phone", PHONE],
            env={"HUST_PASSWORD": PASSWORD},
        )
        self.assertEqual(code, 0)
        code, _, _ = self._cli(["abandon", "--aid", "app-1"])
        self.assertEqual(code, 0)
        state = mock_request(self._mock_url, "/__mock__/state")
        self.assertTrue(state["application"]["abandoned"])

        # logout → 未登录
        code, _, _ = self._cli(["logout"])
        self.assertEqual(code, 0)
        code, _, stderr = self._cli(["status"])
        self.assertEqual(code, 4)
        self.assertIn("未登录", stderr)

    def test_validate_bad_institute(self):
        code, stdout, stderr = self._cli(
            [
                "validate",
                "--group", "web",
                "--grade", "大二",
                "--institute", "不存在的学院",
                "--major", "计算机科学与技术",
                "--rank", "10%",
                "--intro", "x",
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("学院", stdout)
        self.assertIn("校验未通过", stderr)

    def test_validate_ok(self):
        code, stdout, _ = self._cli(
            [
                "validate",
                "--group", "web",
                "--grade", "大二",
                "--institute", "计算机学院",
                "--major", "计算机科学与技术",
                "--rank", "10%",
                "--intro", "x",
            ]
        )
        self.assertEqual(code, 0, stdout)
        self.assertIn("校验通过", stdout)

    def test_sms_login(self):
        code, _, _ = self._cli(
            ["login", "--method", "sms", "--phone", PHONE, "--email", EMAIL],
            env={"HUST_CODE": "123456"},
        )
        self.assertEqual(code, 0)

    def test_me_and_config(self):
        code, _, _ = self._cli(
            ["login", "--method", "phone", "--phone", PHONE],
            env={"HUST_PASSWORD": PASSWORD},
        )
        self.assertEqual(code, 0)
        code, stdout, _ = self._cli(["me"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("Mock User", stdout)
        self.assertIn("mock@example.com", stdout)
        code, _, _ = self._cli(["me", "--edit", "name=New Name"])
        self.assertEqual(code, 0)
        code, stdout, _ = self._cli(["me"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("New Name", stdout)

        code, stdout, _ = self._cli(["config"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("sso_base", stdout)
        code, _, _ = self._cli(["config", "--set", "sso_base=http://example.test/api"])
        self.assertEqual(code, 0)
        code, stdout, _ = self._cli(
            ["config"],
            env={"HUST_SSO_BASE": "", "HUST_HR_BASE": "", "HUST_DEPARTMENTS_URL": ""},
        )
        self.assertEqual(code, 0, stdout)
        self.assertIn("http://example.test/api", stdout)

    def test_apply_invalid_major(self):
        code, _, _ = self._cli(
            [
                "login",
                "--method", "phone",
                "--phone", PHONE,
            ],
            env={"HUST_PASSWORD": PASSWORD},
        )
        self.assertEqual(code, 0)
        code, stdout, stderr = self._cli(
            [
                "apply",
                "--recruitment-id", RID,
                "--group", "web",
                "--grade", "大二",
                "--institute", "计算机学院",
                "--major", "航天工程",
                "--rank", "10%",
                "--intro", "x",
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("专业", stdout)
        self.assertIn("校验未通过", stderr)

    def test_update_preserves_unset_fields(self):
        # 与网页 saveApplicationInfo 一致:update 不传的字段保留服务端原值
        code, _, _ = self._cli(
            ["login", "--method", "phone", "--phone", PHONE],
            env={"HUST_PASSWORD": PASSWORD},
        )
        self.assertEqual(code, 0)
        code, _, _ = self._cli(
            [
                "apply",
                "--recruitment-id", RID,
                "--group", "web",
                "--grade", "大二",
                "--institute", "计算机学院",
                "--major", "计算机科学与技术",
                "--rank", "10%",
                "--intro", "x",
                "--qq", "6666",
                "--is-quick",
            ]
        )
        self.assertEqual(code, 0)
        state = mock_request(self._mock_url, "/__mock__/state")
        self.assertTrue(state["application"]["is_quick"])
        self.assertEqual(state["application"]["qq_account"], "6666")
        # 只改 grade/rank,不传 is_quick/qq → 它们必须保留
        code, _, _ = self._cli(
            [
                "update",
                "--grade", "大三",
                "--institute", "计算机学院",
                "--major", "计算机科学与技术",
                "--rank", "25%",
                "--intro", "x",
            ]
        )
        self.assertEqual(code, 0)
        state = mock_request(self._mock_url, "/__mock__/state")
        self.assertEqual(state["application"]["grade"], "大三")
        self.assertEqual(state["application"]["rank"], "25%")
        self.assertTrue(state["application"]["is_quick"])
        self.assertEqual(state["application"]["qq_account"], "6666")
        # 显式传 --is-quick 关闭 → 才改为 false
        code, _, _ = self._cli(
            [
                "update",
                "--grade", "大四",
                "--institute", "计算机学院",
                "--major", "计算机科学与技术",
                "--rank", "25%",
                "--intro", "x",
                "--qq", "7777",
            ]
        )
        self.assertEqual(code, 0)
        state = mock_request(self._mock_url, "/__mock__/state")
        self.assertEqual(state["application"]["grade"], "大四")
        self.assertEqual(state["application"]["qq_account"], "7777")
        self.assertTrue(state["application"]["is_quick"])

    def test_departments_command(self):
        # 无需登录即可用(供用户选学院/专业)
        code, stdout, _ = self._cli(["departments", "--colleges"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("计算机学院", stdout)
        self.assertIn("软件学院", stdout)

        code, stdout, _ = self._cli(["departments", "--college", "计算机学院"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("计算机科学与技术", stdout)
        self.assertNotIn("软件工程", stdout)

        code, stdout, _ = self._cli(["departments", "--search", "软件"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("软件学院", stdout)
        self.assertIn("软件工程", stdout)

        code, stdout, _ = self._cli(["departments", "--search", "不存在的专业"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("未找到", stdout)

        code, stdout, _ = self._cli(["departments", "--json"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("计算机科学与技术", stdout)

        code, _, stderr = self._cli(["departments", "--college", "不存在的学院"])
        self.assertEqual(code, 1)
        self.assertIn("不存在", stderr)


if __name__ == "__main__":
    unittest.main()