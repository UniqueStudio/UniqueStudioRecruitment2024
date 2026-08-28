"""本地持久化 + 简单加密 (stdlib only)。

数据目录:env HUST_RECRUIT_DIR 覆盖;默认 ~/.local/share/hustunique-recruit
(Windows: %LOCALAPPDATA%/hustunique-recruit)。目录 0700,state.db 0600。

加密定位:防随手读文件的"混淆级",非强加密。真正的登录态保护是
SKILL.md 硬规则:token 永不出现在模型/用户可见输出 + 文件权限 0600。
方案:机器指纹 PBKDF2-HMAC-SHA256 派生密钥 + 随机 nonce + XOR 流密钥
(SHA256(key||counter)),密文 base64。
"""
import base64
import datetime
import hashlib
import json
import os
import platform
import secrets
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_NAME = "state.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS session (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    cookie_enc TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS draft (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    recruitment_id TEXT NOT NULL DEFAULT '',
    fields_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cache (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    applications_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
"""
_NONCE_BYTES = 16
_PBKDF2_ITERATIONS = 200_000
_DK_LEN = 32


def data_dir() -> Path:
    override = os.environ.get("HUST_RECRUIT_DIR")
    if override:
        p = Path(override).expanduser()
    elif os.name == "nt":
        p = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hustunique-recruit"
    else:
        p = Path.home() / ".local" / "share" / "hustunique-recruit"
    p.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(str(p), 0o700)
    except OSError:
        pass
    return p


def db_path() -> Path:
    return data_dir() / DB_NAME


def _connect() -> sqlite3.Connection:
    path = db_path()
    conn = sqlite3.connect(str(path))
    conn.executescript(SCHEMA)
    conn.commit()
    if os.name != "nt":
        try:
            os.chmod(str(path), 0o600)
        except OSError:
            pass
    return conn


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


# ---- config (meta) ----

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    with _connect() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def set_config(key: str, value: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


# ---- 简单加密 (混淆级) ----

def _machine_secret() -> bytes:
    home = str(Path.home())
    return hashlib.sha256(f"{platform.node()}|{uuid.getnode()}|{home}".encode("utf-8")).digest()


def _key() -> bytes:
    salt_hex = get_config("salt")
    if not salt_hex:
        salt = secrets.token_bytes(_NONCE_BYTES)
        set_config("salt", salt.hex())
    else:
        salt = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac("sha256", _machine_secret(), salt, _PBKDF2_ITERATIONS, _DK_LEN)


def _xor_stream(key: bytes, plaintext: bytes) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < len(plaintext):
        block = hashlib.sha256(key + counter.to_bytes(8, "big")).digest()
        out.extend(block)
        counter += 1
    return bytes(a ^ b for a, b in zip(out, plaintext))[: len(plaintext)]


def encrypt(plaintext: str) -> str:
    key = _key()
    nonce = secrets.token_bytes(_NONCE_BYTES)
    ct = _xor_stream(key + nonce, plaintext.encode("utf-8"))
    return base64.b64encode(nonce + ct).decode("ascii")


def decrypt(blob: str) -> str:
    key = _key()
    raw = base64.b64decode(blob)
    nonce, ct = raw[:_NONCE_BYTES], raw[_NONCE_BYTES:]
    return _xor_stream(key + nonce, ct).decode("utf-8")


# ---- session (单行登录态) ----

def save_session(cookie_value: str, email: str = "") -> None:
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO session(id, cookie_enc, email, updated_at) VALUES(1, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET cookie_enc = excluded.cookie_enc, "
            "email = excluded.email, updated_at = excluded.updated_at",
            (encrypt(cookie_value), email, now),
        )


def load_session() -> Optional[str]:
    with _connect() as conn:
        row = conn.execute("SELECT cookie_enc FROM session WHERE id = 1").fetchone()
    if not row:
        return None
    try:
        return decrypt(row[0])
    except Exception:
        return None


def session_email() -> str:
    with _connect() as conn:
        row = conn.execute("SELECT email FROM session WHERE id = 1").fetchone()
    return row[0] if row else ""


def clear_session() -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM session WHERE id = 1")


# ---- draft (表单草稿) ----

def save_draft(recruitment_id: str, fields: Dict[str, Any]) -> None:
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO draft(id, recruitment_id, fields_json, updated_at) VALUES(1, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET recruitment_id = excluded.recruitment_id, "
            "fields_json = excluded.fields_json, updated_at = excluded.updated_at",
            (recruitment_id, json.dumps(fields, ensure_ascii=False), now),
        )


def load_draft() -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT recruitment_id, fields_json FROM draft WHERE id = 1"
        ).fetchone()
    if not row:
        return None
    try:
        return {"recruitment_id": row[0], "fields": json.loads(row[1])}
    except Exception:
        return None


# ---- cache (上次读取的服务端 application 快照,冲突检测用) ----

def save_cache(snapshot: Dict[str, Dict[str, Any]]) -> None:
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO cache(id, applications_json, fetched_at) VALUES(1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET applications_json = excluded.applications_json, "
            "fetched_at = excluded.fetched_at",
            (json.dumps(snapshot, ensure_ascii=False), now),
        )


def load_cache() -> Optional[Dict[str, Dict[str, Any]]]:
    with _connect() as conn:
        row = conn.execute("SELECT applications_json FROM cache WHERE id = 1").fetchone()
    if not row:
        return None
    try:
        value = json.loads(row[0])
        return value if isinstance(value, dict) else None
    except Exception:
        return None