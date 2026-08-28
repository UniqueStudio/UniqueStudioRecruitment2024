"""HTTP 客户端 (stdlib urllib only)。

- 显式携带 `Cookie: SSO_SESSION=<value>`,不依赖 cookiejar 域名匹配。
- HR 信封 `{code, data, msg}`;SSO 信封 `{message, data}`。
- 会话过期 (msg 含 "authentication failed could not get uid") 抛 ApiError(expired=True)。
"""
import json
import mimetypes
import ssl
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SESSION_COOKIE = "SSO_SESSION"
AUTH_FAILED_MARKER = "authentication failed could not get uid"
DEFAULT_ACCEPT = "application/json, text/plain, */*"


class ApiError(Exception):
    def __init__(self, message: str, code: Optional[int] = None, expired: bool = False):
        self.message = message
        self.code = code
        self.expired = expired
        super().__init__(message)


def encode_multipart(fields: Dict[str, Any]) -> Tuple[bytes, Dict[str, str]]:
    """手写 multipart/form-data。文件字段值为 (filename, bytes, content_type)。"""
    boundary = "----hustrecruit" + uuid.uuid4().hex
    parts: List[bytes] = []
    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, tuple):
            filename, content, ctype = value
            parts.append(
                (
                    f"--{boundary}\r\n"
                    f'content-disposition: form-data; name="{key}"; filename="{filename}"\r\n'
                    f"content-type: {ctype}\r\n\r\n"
                ).encode("utf-8")
                + content
                + b"\r\n"
            )
        else:
            parts.append(
                (
                    f"--{boundary}\r\n"
                    f'content-disposition: form-data; name="{key}"\r\n\r\n'
                    f"{value}\r\n"
                ).encode("utf-8")
            )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    headers = {"content-type": f"multipart/form-data; boundary={boundary}"}
    return b"".join(parts), headers


def file_part(path: str) -> Tuple[str, bytes, str]:
    p = Path(path)
    if not p.exists():
        raise ApiError(f"文件不存在: {path}")
    data = p.read_bytes()
    ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return (p.name, data, ctype)


def parse_set_cookie(headers: Dict[str, str]) -> Optional[str]:
    """从响应头提取 SSO_SESSION cookie 值。"""
    for name, value in headers.items():
        if name.lower() == "set-cookie":
            first = value.split(";", 1)[0].strip()
            if first.startswith(SESSION_COOKIE + "="):
                return first[len(SESSION_COOKIE) + 1 :].strip()
    return None


class ApiClient:
    def __init__(self, base_url: str, cookie: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.cookie = cookie
        self.timeout = timeout
        self.context = ssl.create_default_context()

    # ---- 底层 ----

    def _headers(self, json_body: bool = True) -> Dict[str, str]:
        headers = {"accept": DEFAULT_ACCEPT}
        if json_body:
            headers["content-type"] = "application/json"
        if self.cookie:
            headers["cookie"] = f"{SESSION_COOKIE}={self.cookie}"
        return headers

    def _request(
        self, method: str, path: str, body: Optional[bytes] = None, headers=None, raw: bool = False
    ) -> Tuple[int, bytes, Dict[str, str]]:
        req = urllib.request.Request(
            self.base_url + path, data=body, method=method, headers=headers or {}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.context) as resp:
                return resp.status, resp.read(), dict(resp.headers.items())
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), dict(exc.headers.items())
        except urllib.error.URLError as exc:
            raise ApiError(f"网络错误: {exc.reason}")

    @staticmethod
    def _parse_json(data: bytes) -> Any:
        try:
            return json.loads(data.decode("utf-8") or "null")
        except ValueError:
            return None

    # ---- HR (信封 {code, data, msg}) ----

    def _hr(self, method: str, path: str, data: Optional[dict] = None,
            form: Optional[Dict[str, Any]] = None) -> Any:
        if form is not None:
            body, headers = encode_multipart(form)
            headers = {**self._headers(json_body=False), **headers}
            status, raw, _ = self._request(method, path, body=body, headers=headers)
        else:
            payload = json.dumps(data).encode("utf-8") if data is not None else None
            status, raw, _ = self._request(
                method, path, body=payload, headers=self._headers(json_body=data is not None)
            )
        parsed = self._parse_json(raw)
        msg = ""
        if isinstance(parsed, dict):
            msg = str(parsed.get("msg") or parsed.get("message") or "")
        if AUTH_FAILED_MARKER in msg:
            raise ApiError("会话已过期,请重新运行 login 登录", code=status, expired=True)
        if status >= 400:
            raise ApiError(msg or f"HTTP {status}", code=status)
        if isinstance(parsed, dict) and "code" in parsed:
            code = parsed.get("code")
            if code not in (200, 0):
                raise ApiError(str(parsed.get("msg") or f"业务错误 code={code}"), code=code)
            return parsed.get("data")
        return parsed

    def _hr_raw_json(self, method: str, path: str) -> Any:
        status, raw, _ = self._request(method, path, headers=self._headers(json_body=False))
        parsed = self._parse_json(raw)
        msg = str(parsed.get("msg") or "") if isinstance(parsed, dict) else ""
        if AUTH_FAILED_MARKER in msg:
            raise ApiError("会话已过期,请重新运行 login 登录", code=status, expired=True)
        if status >= 400:
            raise ApiError(msg or f"HTTP {status}", code=status)
        return parsed

    def _hr_raw_bytes(self, method: str, path: str) -> Tuple[bytes, Dict[str, str]]:
        status, raw, headers = self._request(
            method, path, headers=self._headers(json_body=False), raw=True
        )
        if status >= 400:
            parsed = self._parse_json(raw)
            msg = str(parsed.get("msg") or "") if isinstance(parsed, dict) else ""
            if AUTH_FAILED_MARKER in msg:
                raise ApiError("会话已过期,请重新运行 login 登录", code=status, expired=True)
            raise ApiError(msg or f"HTTP {status}", code=status)
        return raw, headers

    # ---- SSO (信封 {message, data}) ----

    def _sso(self, method: str, path: str, data: Optional[dict] = None) -> Dict[str, Any]:
        payload = json.dumps(data).encode("utf-8") if data is not None else None
        status, raw, _ = self._request(
            method, path, body=payload, headers=self._headers(json_body=data is not None)
        )
        parsed = self._parse_json(raw)
        if status >= 400 or not isinstance(parsed, dict) or "message" not in parsed:
            message = parsed.get("message") if isinstance(parsed, dict) else ""
            raise ApiError(message or f"HTTP {status}", code=status)
        return parsed

    # ---- SSO 接口 ----

    def sso_login(self, data: dict) -> Tuple[Dict[str, Any], Optional[str]]:
        payload = json.dumps(data).encode("utf-8")
        status, raw, headers = self._request(
            "POST", "/v1/login", body=payload, headers=self._headers(), raw=True
        )
        parsed = self._parse_json(raw)
        if status >= 400 or not isinstance(parsed, dict) or "message" not in parsed:
            message = parsed.get("message") if isinstance(parsed, dict) else ""
            raise ApiError(message or f"HTTP {status}", code=status)
        return parsed, parse_set_cookie(headers)

    def sso_register(self, data: dict) -> Dict[str, Any]:
        return self._sso("POST", "/v1/register", data)

    def sso_send_code(self, phone: str, email: str) -> Dict[str, Any]:
        return self._sso("POST", "/v1/code/sms", {"phone": phone, "email": email})

    def sso_logout(self) -> Dict[str, Any]:
        return self._sso("POST", "/v1/logout")

    def sso_ping(self) -> Dict[str, Any]:
        return self._sso("GET", "/v1/ping")

    def sso_me(self) -> Dict[str, Any]:
        parsed = self._sso("GET", "/v1/user/my")
        return parsed.get("data") if isinstance(parsed.get("data"), dict) else {}

    def sso_edit(self, fields: dict) -> Dict[str, Any]:
        return self._sso("PUT", "/v1/user/my", fields)

    # ---- HR 接口 ----

    def hr_me(self) -> Dict[str, Any]:
        data = self._hr("GET", "/user/me")
        return data if isinstance(data, dict) else {}

    def hr_recruitment_pending(self) -> Dict[str, Any]:
        data = self._hr("GET", "/recruitments/pending")
        return data if isinstance(data, dict) else {}

    def hr_recruitment_by_id(self, rid: str) -> Dict[str, Any]:
        data = self._hr("GET", f"/recruitments/{rid}")
        return data if isinstance(data, dict) else {}

    def hr_interview_times(self, rid: str, name: str) -> List[Dict[str, Any]]:
        data = self._hr("GET", f"/recruitments/{rid}/interviews/{name}")
        return data if isinstance(data, list) else []

    def hr_written_test_type(self, rid: str, group: str) -> int:
        parsed = self._hr_raw_json("GET", f"/recruitments/{rid}/written-test-type/{group}")
        value = parsed.get("data") if isinstance(parsed, dict) else parsed
        if value is None:
            raise ApiError("written-test-type 响应格式异常")
        return int(value)

    def hr_written_test_url(self, rid: str, group: str) -> str:
        parsed = self._hr_raw_json("GET", f"/recruitments/{rid}/written-test-url/{group}")
        value = parsed.get("data") if isinstance(parsed, dict) else parsed
        if value is None:
            raise ApiError("written-test-url 响应格式异常")
        return str(value)

    def hr_written_test_file(self, rid: str, group: str) -> Tuple[bytes, Dict[str, str]]:
        return self._hr_raw_bytes("GET", f"/recruitments/{rid}/file/{group}/WrittenTest")

    def hr_create_application(self, form: Dict[str, Any]) -> Any:
        return self._hr("POST", "/applications/", form=form)

    def hr_update_application(self, aid: str, form: Dict[str, Any]) -> Any:
        return self._hr("PUT", f"/applications/{aid}", form=form)

    def hr_upload_written_test(self, aid: str, file_path: str) -> Any:
        return self._hr(
            "PUT", f"/applications/{aid}/file/WrittenTest",
            form={"file": file_part(file_path)},
        )

    def hr_allocate_interview(self, aid: str, type_: str, iid: str) -> Any:
        return self._hr(
            "PUT", f"/applications/{aid}/interview/{type_}/self", data={"interview_id": iid}
        )

    def hr_set_slots(self, aid: str, type_: str, iids: List[str]) -> Any:
        return self._hr("PUT", f"/applications/{aid}/slots/{type_}", data={"iids": iids})

    def hr_abandon(self, aid: str) -> Any:
        return self._hr("PUT", f"/applications/{aid}/abandoned")

    def hr_resume(self, aid: str) -> Tuple[bytes, Dict[str, str]]:
        return self._hr_raw_bytes("GET", f"/applications/{aid}/resume")