"""skill CLI 入口:python3 -m scripts.cli <子命令> ...(stdlib only)。

退出码:0 成功 | 1 校验/业务错误 | 2 服务端与本地缓存冲突 | 3 会话过期 | 4 未登录。
密码/验证码只能从环境变量 (HUST_PASSWORD / HUST_CODE) 或交互输入读取,禁止出现在 argv。
SSO_SESSION cookie 永不打印。
"""
import argparse
import getpass
import json
import os
import sys
from typing import Any, Dict, List, Optional

if __package__ in (None, ""):
    # 支持直接运行: python3 scripts/cli.py
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import client as client_mod  # noqa: E402
from scripts import storage, validate as validate_mod  # noqa: E402
from scripts.client import ApiClient, ApiError  # noqa: E402

DEFAULT_SSO_BASE = "https://dev.back.sso.hustunique.com/api"
DEFAULT_HR_BASE = "https://dev.back.recruitment2023.hustunique.com"
DEFAULT_DEPARTMENTS_URL = "https://join2024.hustunique.com/DEPARTMENTS.json"

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_CONFLICT = 2
EXIT_EXPIRED = 3
EXIT_NOT_LOGGED_IN = 4

EDIT_FIELDS = validate_mod.EDIT_FIELDS
REQUIRED_ARG_FIELDS = ["grade", "institute", "major", "rank", "intro"]
CREDENTIALS_FILENAME = "credentials.json"


# ---- 基础 ----

def out(text: str = "") -> None:
    print(text)


def fail(message: str, code: int = EXIT_ERROR) -> "None":
    print(message, file=sys.stderr)
    sys.exit(code)


def resolve_config() -> tuple:
    sso = os.environ.get("HUST_SSO_BASE") or storage.get_config("sso_base") or DEFAULT_SSO_BASE
    hr = os.environ.get("HUST_HR_BASE") or storage.get_config("hr_base") or DEFAULT_HR_BASE
    dep = (
        os.environ.get("HUST_DEPARTMENTS_URL")
        or storage.get_config("departments_url")
        or DEFAULT_DEPARTMENTS_URL
    )
    return sso, hr, dep


def make_hr_client() -> ApiClient:
    _, hr, _ = resolve_config()
    return ApiClient(hr, cookie=storage.load_session())


def make_sso_client() -> ApiClient:
    sso, _, _ = resolve_config()
    return ApiClient(sso, cookie=storage.load_session())


def require_session() -> None:
    if not storage.load_session():
        fail(
            "未登录。请先运行: python3 -m scripts.cli login --method phone --phone <手机号>",
            EXIT_NOT_LOGGED_IN,
        )


def read_secret(prompt: str, env_name: str) -> str:
    value = os.environ.get(env_name)
    if value:
        return value
    if env_name == "HUST_PASSWORD":
        return getpass.getpass(f"请输入{prompt} (可用环境变量 {env_name} 提供): ")
    return input(f"请输入{prompt} (可用环境变量 {env_name} 提供): ").strip()


def load_credentials() -> tuple:
    """读取用户填写的凭据文件 (username/password),返回 (dict, 路径)。"""
    path = storage.data_dir() / CREDENTIALS_FILENAME
    if not path.exists():
        return {}, path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"凭据文件无法解析 ({path}): {exc}")
    return (data if isinstance(data, dict) else {}), path


# ---- 冲突检测 ----

def normalize_is_quick(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def snapshot_applications(user: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    snap: Dict[str, Dict[str, str]] = {}
    for app in user.get("applications") or []:
        rid = app.get("recruitment_id")
        if not rid:
            continue
        fields: Dict[str, str] = {}
        for key in EDIT_FIELDS:
            value = app.get(key)
            fields[key] = normalize_is_quick(value) if key == "is_quick" else (
                "" if value is None else str(value)
            )
        snap[rid] = fields
    return snap


def diff_snapshots(cache: Dict[str, Dict[str, str]], current: Dict[str, Dict[str, str]]) -> list:
    diffs = []
    for rid, cur in current.items():
        old = cache.get(rid)
        if old is None:
            diffs.append((rid, "(整体)", "(无)", "存在报名"))
            continue
        for key in EDIT_FIELDS:
            if old.get(key) != cur.get(key):
                diffs.append((rid, key, old.get(key), cur.get(key)))
    for rid in cache:
        if rid not in current:
            diffs.append((rid, "(整体)", "存在报名", "(无)"))
    return diffs


def print_diffs(diffs: list) -> None:
    out("检测到服务端状态与本地缓存不一致:")
    for rid, field, old, new in diffs:
        out(f"  [{rid}] {field}: 缓存={old!r} → 服务端={new!r}")


def check_conflict(client: ApiClient) -> Dict[str, Any]:
    """读命令前置:先拉服务端状态;与缓存不一致 → 打印 diff 并退出码 2。"""
    user = client.hr_me()
    current = snapshot_applications(user)
    cache = storage.load_cache()
    if cache is None:
        storage.save_cache(current)
        return user
    diffs = diff_snapshots(cache, current)
    if diffs:
        print_diffs(diffs)
        fail(
            "请先询问用户合并策略,再运行: "
            "python3 -m scripts.cli sync --strategy server|local|fields=<字段名,...>",
            EXIT_CONFLICT,
        )
    storage.save_cache(current)
    return user


def refresh_cache(client: ApiClient) -> None:
    storage.save_cache(snapshot_applications(client.hr_me()))


# ---- 表单 ----

def collect_fields(args) -> Dict[str, Any]:
    fields = {}
    for name in REQUIRED_ARG_FIELDS + ["referrer", "qq_account"]:
        value = getattr(args, name, None)
        if value is not None:
            fields[name] = value
    return fields


def validate_or_fail(fields: Dict[str, Any], groups: List[str], require_groups: bool) -> None:
    sso, hr, dep = resolve_config()
    try:
        departments = validate_mod.fetch_departments(dep)
    except validate_mod.ValidationError as exc:
        fail(f"校验失败: {exc}")
    errors = validate_mod.validate_form(
        {**fields, "groups": groups}, departments, require_groups=require_groups
    )
    if errors:
        for error in errors:
            out(f"- {error}")
        fail("校验未通过", EXIT_ERROR)


def current_application_uid(client: ApiClient) -> str:
    pending = client.hr_recruitment_pending()
    rid = pending.get("uid", "")
    if not rid:
        fail("没有进行中的招募")
    return rid


# ---- 子命令 ----
def cmd_login(args) -> int:
    if args.method:
        if args.method == "phone":
            if not args.phone:
                fail("缺少 --phone")
            data = {"phone": args.phone, "password": read_secret("密码", "HUST_PASSWORD")}
        elif args.method == "email":
            if not args.email:
                fail("缺少 --email")
            data = {"email": args.email, "password": read_secret("密码", "HUST_PASSWORD")}
        else:
            if not args.phone or not args.email:
                fail("sms 登录需要 --phone 与 --email")
            data = {
                "phone": args.phone,
                "email": args.email,
                "validate_code": read_secret("短信验证码", "HUST_CODE"),
            }
    else:
        # 无参数 → 从凭据文件读取 (推荐用法)
        creds, path = load_credentials()
        username = str(creds.get("username") or "").strip()
        password = str(creds.get("password") or "")
        if not username or not password:
            fail(
                f"凭据文件未填写或不存在: {path}\n"
                "请运行 credentials init 生成模板,再编辑填入 username(手机号或邮箱) 与 password",
                EXIT_ERROR,
            )
        method = str(creds.get("method") or ("phone" if username.isdigit() else "email"))
        if method == "phone":
            data = {"phone": username, "password": password}
        elif method == "email":
            data = {"email": username, "password": password}
        else:
            fail(f"凭据文件 method 字段无效: {method} (可选 phone|email)")
    client = make_sso_client()
    resp, cookie = client.sso_login(data)
    if not cookie:
        fail("登录响应未携带 SSO_SESSION cookie")
    storage.save_session(cookie, email=data.get("email") or data.get("phone", ""))
    out("登录成功")
    if not args.method:
        _, cred_path = load_credentials()
        out(
            f"提醒:凭据文件 {cred_path} 含明文密码,登录完成后请删除: "
            "python3 -m scripts.cli credentials --wipe"
        )
    return EXIT_OK


def cmd_credentials(args) -> int:
    path = storage.data_dir() / CREDENTIALS_FILENAME
    if args.wipe:
        if path.exists():
            path.unlink()
            out(f"已删除凭据文件: {path}")
        else:
            out("凭据文件不存在,无需删除")
        return EXIT_OK
    if args.init:
        if path.exists():
            out(f"凭据文件已存在: {path}")
        else:
            path.write_text(
                json.dumps(
                    {"username": "", "password": ""}, ensure_ascii=False, indent=2
                )
                + "\n",
                encoding="utf-8",
            )
            if os.name != "nt":
                os.chmod(str(path), 0o600)
            out(f"已创建凭据文件: {path}")
        out("请填入 username(手机号或邮箱) 与 password,然后直接运行 login")
        return EXIT_OK
    out(f"凭据文件: {path}")
    creds, _ = load_credentials()
    out(f"username: {'已填写' if creds.get('username') else '(空)'}")
    out(f"password: {'已填写' if creds.get('password') else '(空)'}")
    out("修改:直接编辑该文件;或运行 credentials init 重新生成模板")
    return EXIT_OK


def cmd_register(args) -> int:
    password = read_secret("密码", "HUST_PASSWORD")
    code = read_secret("短信验证码", "HUST_CODE")
    data = {
        "name": args.name,
        "gender": args.gender,
        "phone": args.phone,
        "password": password,
        "validate_code": code,
        "email": args.email,
        "qq_account": args.qq or "",
    }
    make_sso_client().sso_register(data)
    out("注册成功,请运行 login 登录")
    return EXIT_OK


def cmd_code(args) -> int:
    make_sso_client().sso_send_code(args.phone, args.email)
    out("验证码已发送")
    return EXIT_OK


def cmd_logout(args) -> int:
    try:
        make_sso_client().sso_logout()
    except ApiError:
        pass
    storage.clear_session()
    out("已退出登录")
    return EXIT_OK


def cmd_ping(args) -> int:
    try:
        resp = make_sso_client().sso_ping()
        out(f"pong: {resp.get('data')}")
    except ApiError as exc:
        fail(f"ping 失败: {exc.message}")
    return EXIT_OK


def cmd_me(args) -> int:
    client = make_sso_client()
    if args.edit:
        fields = {}
        for kv in args.edit:
            key, _, value = kv.partition("=")
            if not key:
                fail(f"无效的编辑项: {kv} (格式 key=value)")
            if key == "password":
                value = read_secret("新密码", "HUST_PASSWORD")
            fields[key] = value
        client.sso_edit(fields)
        out("资料已更新")
        return EXIT_OK
    me = client.sso_me()
    out(f"uid: {me.get('uid', '')}")
    out(f"姓名: {me.get('name', '')}")
    out(f"手机: {me.get('phone', '')}")
    out(f"邮箱: {me.get('email', '')}")
    out(f"性别: {me.get('gender', '')} (1男 2女 3其他)")
    out(f"QQ: {me.get('qq_account', '')}")
    out(f"角色: {', '.join(me.get('roles') or [])}")
    out(f"加入时间: {me.get('join_time', '')}")
    return EXIT_OK


def print_application(app: Dict[str, Any]) -> None:
    intro = str(app.get("intro") or "")
    out(
        f"  [{app.get('uid', '')}] 组={app.get('group', '')} 流程={app.get('step', '')} "
        f"放弃={bool(app.get('abandoned'))} 淘汰={bool(app.get('rejected'))}"
    )
    out(
        f"      年级={app.get('grade', '')} 学院={app.get('institute', '')} "
        f"专业={app.get('major', '')} 排名={app.get('rank', '')} "
        f"快速通道={app.get('is_quick', '')} 推荐人={app.get('referrer') or '-'} "
        f"QQ={app.get('qq_account') or '-'}"
    )
    if intro:
        out(f"      简介: {intro[:60]}{'...' if len(intro) > 60 else ''}")


def cmd_status(args) -> int:
    client = make_hr_client()
    user = client.hr_me()
    pending = client.hr_recruitment_pending()
    out(f"用户: {user.get('name', '')} ({user.get('email', '') or user.get('phone', '')})")
    out(
        f"最新招募: {pending.get('name', '')} [{pending.get('uid', '')}] "
        f"截止 {pending.get('deadline', '')}"
    )
    apps = user.get("applications") or []
    if not apps:
        out("当前无报名记录")
    else:
        out(f"报名记录 ({len(apps)}):")
        for app in apps:
            print_application(app)
    current = snapshot_applications(user)
    cache = storage.load_cache()
    if cache is not None:
        diffs = diff_snapshots(cache, current)
        if diffs:
            print_diffs(diffs)
            fail(
                "请先询问用户合并策略,再运行: "
                "python3 -m scripts.cli sync --strategy server|local|fields=<字段名,...>",
                EXIT_CONFLICT,
            )
    storage.save_cache(current)
    return EXIT_OK


def cmd_sync(args) -> int:
    client = make_hr_client()
    cache = storage.load_cache()
    if cache is None:
        fail("没有缓存,无需合并。请先运行 status。")
    user = client.hr_me()
    current = snapshot_applications(user)
    draft_info = storage.load_draft()
    draft = dict(draft_info["fields"]) if draft_info else {}
    strategy = args.strategy
    if strategy == "server":
        new_draft = {}
        for _, fields in current.items():
            new_draft.update(fields)
        if new_draft:
            draft.update({k: v for k, v in new_draft.items()})
    elif strategy == "local":
        pass
    elif strategy.startswith("fields="):
        names = [n.strip() for n in strategy.split("=", 1)[1].split(",") if n.strip()]
        invalid = [n for n in names if n not in EDIT_FIELDS]
        if invalid:
            fail(f"未知字段: {', '.join(invalid)};可选: {', '.join(EDIT_FIELDS)}")
        for name in names:
            if name not in draft:
                continue
            for _, fields in current.items():
                if name in fields:
                    draft[name] = fields.get(name, draft[name])
    else:
        fail(f"未知策略: {strategy};可选 server|local|fields=k1,k2")
    rid = draft_info["recruitment_id"] if draft_info else (
        list(current.keys())[0] if current else ""
    )
    storage.save_draft(rid, draft)
    storage.save_cache(current)
    out("合并完成,缓存已刷新")
    return EXIT_OK


def cmd_apply(args) -> int:
    client = make_hr_client()
    groups = args.group
    fields = collect_fields(args)
    missing = [name for name in REQUIRED_ARG_FIELDS if not getattr(args, name, None)]
    if missing:
        fail("缺少必填字段: " + ", ".join(missing))
    validate_or_fail(fields, groups, require_groups=True)
    base = {
        "recruitment_id": args.recruitment_id,
        "grade": args.grade,
        "rank": args.rank,
        "major": args.major,
        "qq_account": args.qq or "",
        "institute": args.institute,
        "intro": args.intro,
        "referrer": args.referrer or "",
        "is_quick": "true" if args.is_quick else "false",
    }
    if args.resume:
        base["resume"] = client_mod.file_part(args.resume)
    ok_groups: List[str] = []
    for group in groups:
        try:
            client.hr_create_application({**base, "group": group})
            ok_groups.append(group)
        except ApiError as exc:
            if exc.expired:
                fail(f"{exc.message}", EXIT_EXPIRED)
            failed = [g for g in groups if g not in ok_groups]
            out(f"以下组报名失败: {', '.join(failed)},原因: {exc.message}")
            out("可能部分成功,请运行 status 查看服务端真值")
            fail("报名未完全成功", EXIT_ERROR)
    storage.save_draft(
        args.recruitment_id, {**{k: v for k, v in fields.items()}, "groups": groups}
    )
    refresh_cache(client)
    out(f"报名成功: {', '.join(groups)}")
    return EXIT_OK


def cmd_update(args) -> int:
    client = make_hr_client()
    fields = collect_fields(args)
    missing = [name for name in REQUIRED_ARG_FIELDS if not getattr(args, name, None)]
    if missing:
        fail("缺少必填字段: " + ", ".join(missing))
    validate_or_fail(fields, [], require_groups=False)
    rid = current_application_uid(client)
    user = client.hr_me()
    apps = [app for app in (user.get("applications") or []) if app.get("recruitment_id") == rid]
    if not apps:
        fail("尚未报名当前招募,请先运行 apply")
    # 与网页 saveApplicationInfo 一致:以服务端当前值(已加载的 form 状态)为底,
    # 仅覆盖用户本次显式传入的字段,避免未传字段被重置为空。
    first = apps[0]
    form = {
        "recruitment_id": rid,
        "grade": str(first.get("grade") or ""),
        "rank": str(first.get("rank") or ""),
        "major": str(first.get("major") or ""),
        "qq_account": str(first.get("qq_account") or ""),
        "institute": str(first.get("institute") or ""),
        "intro": str(first.get("intro") or ""),
        "referrer": str(first.get("referrer") or ""),
        "is_quick": "true" if first.get("is_quick") else "false",
    }
    for key in ("grade", "rank", "major", "institute", "intro", "referrer"):
        if key in fields:
            form[key] = fields[key]
    if args.qq is not None:
        form["qq_account"] = args.qq
    if args.is_quick is not None:
        form["is_quick"] = "true" if args.is_quick else "false"
    if args.resume:
        form["resume"] = client_mod.file_part(args.resume)
    for app in apps:
        client.hr_update_application(app["uid"], form)
    draft_info = storage.load_draft()
    groups = draft_info["fields"].get("groups", []) if draft_info else []
    final_fields = {
        key: value for key, value in form.items() if key not in ("recruitment_id", "resume")
    }
    storage.save_draft(rid, {**final_fields, "groups": groups})
    refresh_cache(client)
    out(f"更新成功 ({len(apps)} 条申请)")
    return EXIT_OK


def cmd_applications(args) -> int:
    client = make_hr_client()
    user = check_conflict(client)
    apps = user.get("applications") or []
    if not apps:
        out("当前无报名记录")
        return EXIT_OK
    out(f"报名记录 ({len(apps)}):")
    for app in apps:
        print_application(app)
    return EXIT_OK


def _extension_from_content_type(content_type: str) -> str:
    ctype = (content_type or "").split(";")[0].strip().lower()
    return {".pdf": ".pdf", "application/pdf": ".pdf"}.get(ctype, "")


def cmd_written_test(args) -> int:
    client = make_hr_client()
    check_conflict(client)
    test_type = client.hr_written_test_type(args.rid, args.group)
    if test_type == 2:
        url = client.hr_written_test_url(args.rid, args.group)
        out(f"在线问卷链接: {url}")
    elif test_type == 1:
        data, headers = client.hr_written_test_file(args.rid, args.group)
        name = f"WrittenTest-{args.group}-{args.rid}"
        name += _extension_from_content_type(headers.get("content-type", ""))
        with open(name, "wb") as fh:
            fh.write(data)
        out(f"笔试文件已保存: {name}")
    else:
        out("该组暂无笔试")
    return EXIT_OK


def cmd_written_test_upload(args) -> int:
    client = make_hr_client()
    client.hr_upload_written_test(args.aid, args.file)
    out("笔试作答已上传")
    return EXIT_OK


def cmd_resume_download(args) -> int:
    client = make_hr_client()
    check_conflict(client)
    data, headers = client.hr_resume(args.aid)
    name = args.out or f"resume-{args.aid}"
    name += _extension_from_content_type(headers.get("content-type", ""))
    with open(name, "wb") as fh:
        fh.write(data)
    out(f"简历已保存: {name}")
    return EXIT_OK


def cmd_interview_times(args) -> int:
    client = make_hr_client()
    check_conflict(client)
    times = client.hr_interview_times(args.rid, args.name)
    times = sorted(times, key=lambda t: t.get("start") or "")
    if not times:
        out("暂无可用时间")
        return EXIT_OK
    for t in times:
        remaining = t.get("slot_number", 0) - t.get("select_number", 0)
        status = "已满" if remaining <= 0 else f"剩余 {remaining}"
        out(
            f"  {t.get('uid', '')} {t.get('date', '')} {t.get('period', '')} "
            f"{t.get('start', '')} - {t.get('end', '')} [{status}]"
        )
    return EXIT_OK


def cmd_interview_select(args) -> int:
    client = make_hr_client()
    client.hr_allocate_interview(args.aid, args.type, args.iid)
    out("已选定该面试时间")
    return EXIT_OK


def cmd_interview_slots(args) -> int:
    client = make_hr_client()
    iids = [i.strip() for i in args.iids.split(",") if i.strip()]
    if not iids:
        fail("--iids 至少需要一个时间 id")
    client.hr_set_slots(args.aid, args.type, iids)
    out(f"已设置候补时间: {', '.join(iids)}")
    return EXIT_OK


def cmd_abandon(args) -> int:
    client = make_hr_client()
    client.hr_abandon(args.aid)
    out("已放弃该申请")
    return EXIT_OK


def cmd_validate_command(args) -> int:
    fields = {}
    for name in REQUIRED_ARG_FIELDS + ["referrer", "qq_account"]:
        value = getattr(args, name, None)
        if value is not None:
            fields[name] = value
    if args.is_quick:
        fields["is_quick"] = "true"
    require_groups = bool(args.group)
    validate_or_fail(fields, args.group or [], require_groups=require_groups)
    out("校验通过")
    return EXIT_OK


def cmd_config(args) -> int:
    if args.set:
        key, _, value = args.set.partition("=")
        allowed = ("sso_base", "hr_base", "departments_url")
        if key not in allowed:
            fail(f"未知配置项: {key};可选: {', '.join(allowed)}")
        storage.set_config(key, value)
        out(f"{key} 已设置")
        return EXIT_OK
    sso, hr, dep = resolve_config()
    out(f"sso_base        = {sso}")
    out(f"hr_base         = {hr}")
    out(f"departments_url = {dep}")
    out("设置: config --set <key>=<value>;env HUST_SSO_BASE/HUST_HR_BASE/HUST_DEPARTMENTS_URL 优先级更高")
    return EXIT_OK


def cmd_departments(args) -> int:
    """提前动态 fetch DEPARTMENTS.json,列出/搜索学院与专业,供用户选择、AI 纠错匹配。"""
    _, _, dep = resolve_config()
    try:
        departments = validate_mod.fetch_departments(dep)
    except validate_mod.ValidationError as exc:
        fail(f"获取失败: {exc}")
    if args.json:
        out(json.dumps(departments, ensure_ascii=False))
        return EXIT_OK
    if args.college:
        college = args.college
        if college not in departments:
            hint = [c for c in departments if college in c or c in college]
            if hint:
                fail(
                    f'学院 "{college}" 不存在。相近的学院: {", ".join(hint)}。'
                    '确认后: departments --college "<学院名>"'
                )
            fail(f'学院 "{college}" 不在 DEPARTMENTS.json 中。先运行 departments --colleges 查看全部学院')
        out(f"学院: {college}")
        for major in departments[college]:
            out(f"  - {major}")
        return EXIT_OK
    if args.search:
        keyword = args.search
        college_hits = [c for c in departments if keyword in c]
        major_hits = [
            (c, m) for c, majors in departments.items() for m in majors if keyword in m
        ]
        if not college_hits and not major_hits:
            out(f'未找到包含 "{keyword}" 的学院或专业')
            return EXIT_OK
        for c in college_hits:
            out(f"[学院] {c}")
        for c, m in major_hits:
            out(f"{c}: {m}")
        return EXIT_OK
    if args.colleges:
        out("可选学院 (来源: " + dep + "):")
        for college, majors in departments.items():
            out(f"  {college} ({len(majors)} 个专业)")
        return EXIT_OK
    out("学院与专业 (来源: " + dep + "):")
    for college, majors in departments.items():
        out(f"{college} ({len(majors)} 个专业):")
        for major in majors:
            out(f"  - {major}")
    return EXIT_OK


# ---- 主入口 ----

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hustunique-recruit",
        description="HUST 联创团队招新 skill 命令行 (stdlib only)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("login", help="SSO 登录 (默认读凭据文件;也可 --method 走 env/getpass)")
    p.add_argument("--method", choices=["phone", "email", "sms"])
    p.add_argument("--phone")
    p.add_argument("--email")
    p.set_defaults(func=cmd_login)

    p = sub.add_parser("credentials", help="查看/初始化凭据文件 (username+password)")
    p.add_argument("--init", action="store_true", help="生成模板文件")
    p.add_argument("--wipe", action="store_true", help="删除凭据文件 (登录后建议执行)")
    p.set_defaults(func=cmd_credentials)

    p = sub.add_parser("register", help="SSO 注册 (先运行 code 获取验证码)")
    p.add_argument("--name", required=True)
    p.add_argument("--gender", required=True, help="1男 2女 3其他")
    p.add_argument("--phone", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--qq")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("code", help="发送短信验证码")
    p.add_argument("--phone", required=True)
    p.add_argument("--email", required=True)
    p.set_defaults(func=cmd_code)

    sub.add_parser("logout", help="退出登录").set_defaults(func=cmd_logout)
    sub.add_parser("ping", help="SSO 连通性检查").set_defaults(func=cmd_ping)

    p = sub.add_parser("me", help="查看/修改个人资料")
    p.add_argument("--edit", action="append", help="格式 key=value;password 走 env HUST_PASSWORD")
    p.set_defaults(func=cmd_me)

    sub.add_parser("status", help="拉取服务端状态并做冲突检测").set_defaults(func=cmd_status)

    p = sub.add_parser("sync", help="按策略合并服务端状态到本地")
    p.add_argument("--strategy", required=True, help="server | local | fields=k1,k2")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("apply", help="报名 (每个组一次 POST)")
    p.add_argument("--recruitment-id", required=True)
    p.add_argument("--group", action="append", required=True, help="可多次传入")
    _add_form_args(p)
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("update", help="更新当前招募的申请资料 (无 --group)")
    _add_form_args(p)
    p.set_defaults(func=cmd_update)

    sub.add_parser("applications", help="列出我的报名记录").set_defaults(func=cmd_applications)

    p = sub.add_parser("written-test", help="查询笔试类型/链接/文件")
    p.add_argument("--rid", required=True)
    p.add_argument("--group", required=True)
    p.set_defaults(func=cmd_written_test)

    p = sub.add_parser("written-test-upload", help="上传笔试作答")
    p.add_argument("--aid", required=True)
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_written_test_upload)

    p = sub.add_parser("resume-download", help="下载简历")
    p.add_argument("--aid", required=True)
    p.add_argument("--out")
    p.set_defaults(func=cmd_resume_download)

    p = sub.add_parser("interview-times", help="查看面试可选时间")
    p.add_argument("--rid", required=True)
    p.add_argument("--name", default="unique", help="组面传组名 (如 web),群面用 unique")
    p.set_defaults(func=cmd_interview_times)

    p = sub.add_parser("interview-select", help="选定单个面试时间 (单选分配)")
    p.add_argument("--aid", required=True)
    p.add_argument("--type", choices=["group", "team"], required=True)
    p.add_argument("--iid", required=True)
    p.set_defaults(func=cmd_interview_select)

    p = sub.add_parser("interview-slots", help="设置候补时间列表 (多选)")
    p.add_argument("--aid", required=True)
    p.add_argument("--type", choices=["group", "team"], required=True)
    p.add_argument("--iids", required=True, help="逗号分隔")
    p.set_defaults(func=cmd_interview_slots)

    p = sub.add_parser("abandon", help="放弃报名")
    p.add_argument("--aid", required=True)
    p.set_defaults(func=cmd_abandon)

    p = sub.add_parser("validate", help="只校验表单字段 (动态拉取 DEPARTMENTS.json)")
    _add_form_args(p, groups_optional=True)
    p.set_defaults(func=cmd_validate_command)

    p = sub.add_parser("config", help="查看/设置端点配置")
    p.add_argument("--set", help="key=value;可选 sso_base/hr_base/departments_url")
    p.set_defaults(func=cmd_config)

    p = sub.add_parser(
        "departments",
        help="列出/搜索学院专业 (动态 fetch DEPARTMENTS.json,供用户选择与纠错)",
    )
    p.add_argument("--colleges", action="store_true", help="只列学院名+专业数")
    p.add_argument("--college", help="列出指定学院的全部专业")
    p.add_argument("--search", help="按关键词搜索学院/专业")
    p.add_argument("--json", action="store_true", help="输出原始 JSON")
    p.set_defaults(func=cmd_departments)
    return parser


def _add_form_args(parser: argparse.ArgumentParser, groups_optional: bool = False) -> None:
    if not groups_optional:
        parser.add_argument("--grade", help="大一|大二|大三|大四|研究生")
        parser.add_argument("--institute", help="学院 (须在 DEPARTMENTS.json 中)")
        parser.add_argument("--major", help="专业 (须属于所选学院)")
        parser.add_argument("--rank", help="暂无|10%|25%|50%|100%")
        parser.add_argument("--intro", help="自我介绍")
    else:
        parser.add_argument("--group", action="append", help="可多次传入 (可选)")
        parser.add_argument("--grade")
        parser.add_argument("--institute")
        parser.add_argument("--major")
        parser.add_argument("--rank")
        parser.add_argument("--intro")
    parser.add_argument("--referrer")
    parser.add_argument("--qq")
    parser.add_argument("--is-quick", action="store_true", default=None, help="快速通道")
    parser.add_argument("--resume", help="简历文件路径 (可选)")


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command not in (
        "login", "register", "code", "ping", "config", "validate", "credentials",
        "departments",
    ):
        require_session()
    try:
        return args.func(args)
    except ApiError as exc:
        if exc.expired:
            print(f"会话已过期: {exc.message}", file=sys.stderr)
            return EXIT_EXPIRED
        print(f"错误: {exc.message}", file=sys.stderr)
        return EXIT_ERROR
    except validate_mod.ValidationError as exc:
        print(f"校验失败: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())