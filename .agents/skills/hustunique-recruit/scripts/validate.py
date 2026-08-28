"""表单校验。

学院/专业必须对照 DEPARTMENTS.json(Record<学院, 专业[]>),
该文件在每次校验时**动态 fetch**(urllib),fetch 失败则校验失败关闭 (fail-closed)。
枚举值来自 src/config/const.ts:GRADE/RANK/Group/DeprecatedGroups。
"""
import json
import urllib.request
from typing import Any, Dict, List

GRADE = ["大一", "大二", "大三", "大四", "研究生"]
RANK = ["暂无", "10%", "25%", "50%", "100%"]
REGULAR_GROUPS = ["web", "lab", "ai", "game", "pm", "design", "mobile"]
BLOCKCHAIN_GROUP = "blockchain"
VALID_GROUPS = REGULAR_GROUPS + [BLOCKCHAIN_GROUP]
DEPRECATED_GROUPS = ["android", "ios"]
EDIT_FIELDS = [
    "grade",
    "institute",
    "major",
    "rank",
    "intro",
    "referrer",
    "is_quick",
    "qq_account",
]


class ValidationError(Exception):
    pass


def fetch_departments(url: str) -> Dict[str, List[str]]:
    """动态 fetch DEPARTMENTS.json 并断言结构 Record<学院, 专业[]>。"""
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise ValidationError(f"无法获取学院专业列表 ({url}): {exc}")
    if not isinstance(data, dict):
        raise ValidationError(f"DEPARTMENTS.json 格式错误 (应为对象): {url}")
    for college, majors in data.items():
        if not isinstance(majors, list) or not all(isinstance(m, str) for m in majors):
            raise ValidationError(f"DEPARTMENTS.json 中学院 {college} 的专业列表格式错误")
    return data


def validate_form(
    fields: Dict[str, Any],
    departments: Dict[str, List[str]],
    require_groups: bool = True,
) -> List[str]:
    """返回错误信息列表;空列表 = 通过。"""
    errors: List[str] = []

    groups = fields.get("groups") or []
    if not groups and require_groups:
        errors.append("请至少选择一个组")
    elif groups:
        for g in groups:
            if g in DEPRECATED_GROUPS:
                errors.append(f"组 {g} 已废弃,不能报名")
            elif g not in VALID_GROUPS:
                errors.append(f"未知组 {g},可选组: {', '.join(VALID_GROUPS)}")
        regular = [g for g in groups if g in REGULAR_GROUPS]
        blockchain = BLOCKCHAIN_GROUP in groups
        if len(regular) > 1:
            errors.append(f"常规组只能选择一个,当前选了: {', '.join(regular)}")
        if regular and not blockchain:
            pass  # 1 常规组,合法
        if regular and len(regular) == 1 and blockchain:
            pass  # 1 常规 + blockchain,合法
        if not regular and not blockchain and groups:
            pass  # 只有废弃组的情况已在上方报错

    grade = fields.get("grade")
    if grade is None or str(grade) == "":
        errors.append("请选择年级 (grade)")
    elif grade not in GRADE:
        errors.append(f"年级 {grade} 无效,可选: {', '.join(GRADE)}")

    rank = fields.get("rank")
    if rank is None or str(rank) == "":
        errors.append("请选择专业排名 (rank)")
    elif rank not in RANK:
        errors.append(f"专业排名 {rank} 无效,可选: {', '.join(RANK)}")

    is_quick = fields.get("is_quick")
    if is_quick is not None and str(is_quick) not in ("true", "false"):
        errors.append("is_quick 只能为 true 或 false")

    institute = fields.get("institute")
    if institute is None or str(institute) == "":
        errors.append("请填写学院 (institute)")
    elif str(institute) not in departments:
        errors.append(f'学院 "{institute}" 不在 DEPARTMENTS.json 中')

    major = fields.get("major")
    if major is None or str(major) == "":
        errors.append("请填写专业 (major)")
    elif str(institute) in departments and str(major) not in departments[str(institute)]:
        majors_joined = ", ".join(departments[str(institute)])
        errors.append(f'专业 "{major}" 不属于学院 "{institute}" (可选: {majors_joined})')

    intro = fields.get("intro")
    if intro is None or str(intro) == "":
        errors.append("请填写自我介绍 (intro)")

    return errors