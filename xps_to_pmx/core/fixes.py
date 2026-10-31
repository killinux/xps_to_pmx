"""Fix list (修正单) and its file format (design doc §15.3–§15.4).

The fix list records every decision that deviates from the automatic result:
hand edits of slots and bone dispositions, mapping-CSV rows that differ, fixes
proposed by the checkup, and ignored findings.  ``Fix.key`` identifies what a
fix decides, so a later decision about the same thing replaces the earlier one.

File format: JSON with a schema name and version.  Unknown or missing keys
are errors (hard constraint 5); this module is the only parser.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set

SCHEMA = "xps_to_pmx.fixes"
VERSION = 1
KINDS = ("slot", "bone", "split_side", "ignore")
ORIGINS = ("user", "csv", "checkup", "file")
ACTIONS = ("map", "merge", "keep", "delete")
#: Per-model options remembered with the fixes (export path is machine-specific and not remembered).
OPTION_TYPES = {
    "scale_mode": str, "shoulder_target": float, "apose_preset": str, "apose_upper_deg": float,
    "apose_fore_extra_deg": float, "level_shoulders": bool, "gen_tier2": bool, "gen_tier3": bool,
    "twist_mode": str, "ik_preset": str,
}
COMMON_KEYS = ("kind", "enabled", "origin", "auto", "finding", "note")
KIND_KEYS = {
    "slot": ("slot_id", "bone", "src"),
    "bone": ("bone", "src", "action", "slot_id", "category"),
    "split_side": ("bone", "src", "twin"),
    "ignore": (),
}
TOP_KEYS = ("schema", "version", "model", "source", "source_sha1", "options", "fixes")


class FixFileError(ValueError):
    def __init__(self, problems: List[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass
class Fix:
    kind: str
    bone: str = ""        # slot: the source bone ("" = leave the slot empty); bone / split_side: the bone
    src: str = ""         # original XPS name of ``bone`` (for people; ``bone`` is the Blender name)
    slot_id: str = ""     # slot: the slot; bone: map / merge target
    action: str = ""      # bone only
    category: str = ""    # bone only; "" keeps the classifier's category
    twin: str = ""        # split_side only: the same-named bone on the other side
    finding: str = ""     # ignore: the ignored finding's key; other kinds: the finding that proposed it
    enabled: bool = True
    origin: str = "user"
    auto: bool = False    # added automatically by the checkup
    note: str = ""

    @property
    def key(self) -> str:
        if self.kind == "slot":
            return f"slot:{self.slot_id}"
        if self.kind == "bone":
            return f"bone:{self.bone}"
        if self.kind == "split_side":
            return f"split:{self.bone}"
        return f"ignore:{self.finding}"

    def describe(self, slot_name=lambda s: s) -> str:
        """One line for the panel; ``slot_name`` turns a slot id into its MMD name."""
        if self.kind == "slot":
            return f"{slot_name(self.slot_id)} ← {self.bone}" if self.bone else f"{slot_name(self.slot_id)} 留空（生成）"
        if self.kind == "bone":
            action = {"map": "映射到", "merge": "并入", "keep": "保留", "delete": "删除"}.get(self.action, self.action)
            target = f" {slot_name(self.slot_id)}" if self.action in ("map", "merge") and self.slot_id else ""
            cat = f"（类别 {self.category}）" if self.category else ""
            return f"{self.bone}：{action}{target}{cat}"
        if self.kind == "split_side":
            return f"{self.bone} 按左右拆分权重给 {self.twin}"
        return f"忽略：{self.finding}"

    def to_dict(self) -> Dict:
        out = {"kind": self.kind}
        for k in KIND_KEYS[self.kind]:
            out[k] = getattr(self, k)
        for k in COMMON_KEYS[1:]:
            out[k] = getattr(self, k)
        return out


@dataclass
class FixFile:
    model: str = ""
    source: str = ""
    source_sha1: str = ""
    options: Dict[str, object] = field(default_factory=dict)
    fixes: List[Fix] = field(default_factory=list)


def validate_fix(fix: Fix) -> List[str]:
    problems = []
    if fix.kind not in KINDS:
        return [f"未知的修正类型 {fix.kind!r}"]
    if fix.origin not in ORIGINS:
        problems.append(f"{fix.key}: 未知的来源 {fix.origin!r}")
    if fix.kind == "slot" and not fix.slot_id:
        problems.append("slot 修正缺少 slot_id")
    if fix.kind == "bone":
        if not fix.bone:
            problems.append("bone 修正缺少 bone")
        if fix.action not in ACTIONS:
            problems.append(f"{fix.key}: 未知的处置 {fix.action!r}")
        if fix.action in ("map", "merge") and not fix.slot_id:
            problems.append(f"{fix.key}: {fix.action} 缺少目标槽位")
    if fix.kind == "split_side" and not (fix.bone and fix.twin):
        problems.append("split_side 修正缺少 bone 或 twin")
    if fix.kind == "ignore" and not fix.finding:
        problems.append("ignore 修正缺少 finding")
    return problems


def write_fixes(ff: FixFile) -> str:
    problems = [p for f in ff.fixes for p in validate_fix(f)]
    problems += _option_problems(ff.options)
    if problems:
        raise FixFileError(problems)
    data = {"schema": SCHEMA, "version": VERSION, "model": ff.model, "source": ff.source,
            "source_sha1": ff.source_sha1, "options": dict(ff.options), "fixes": [f.to_dict() for f in ff.fixes]}
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def parse_fixes(text: str) -> FixFile:
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise FixFileError([f"不是有效的 JSON：{exc}"]) from exc
    if not isinstance(data, dict):
        raise FixFileError(["顶层必须是对象"])
    problems = _key_problems("文件", data, TOP_KEYS)
    if problems:
        raise FixFileError(problems)
    if data["schema"] != SCHEMA:
        raise FixFileError([f"schema 是 {data['schema']!r}，应为 {SCHEMA!r}"])
    if data["version"] != VERSION:
        raise FixFileError([f"version 是 {data['version']!r}，本插件只读 {VERSION}"])
    for k in ("model", "source", "source_sha1"):
        if not isinstance(data[k], str):
            problems.append(f"{k} 必须是字符串")
    if not isinstance(data["options"], dict):
        problems.append("options 必须是对象")
    else:
        problems += _option_problems(data["options"])
    if not isinstance(data["fixes"], list):
        problems.append("fixes 必须是数组")
    fixes: List[Fix] = []
    for n, item in enumerate(data["fixes"] if isinstance(data["fixes"], list) else []):
        where = f"fixes[{n}]"
        if not isinstance(item, dict) or item.get("kind") not in KINDS:
            problems.append(f"{where}: 缺少或未知的 kind")
            continue
        kp = _key_problems(where, item, COMMON_KEYS + KIND_KEYS[item["kind"]])
        if kp:
            problems += kp
            continue
        bad = [k for k in item if k not in ("enabled", "auto") and not isinstance(item[k], str)]
        bad += [k for k in ("enabled", "auto") if not isinstance(item[k], bool)]
        if bad:
            problems.append(f"{where}: 类型错误 {bad}")
            continue
        fix = Fix(**item)
        problems += [f"{where}: {p}" for p in validate_fix(fix)]
        fixes.append(fix)
    if problems:
        raise FixFileError(problems)
    return FixFile(data["model"], data["source"], data["source_sha1"], dict(data["options"]), fixes)


def _key_problems(where: str, data: Dict, expected: Iterable[str]) -> List[str]:
    expected = tuple(expected)
    out = [f"{where}: 缺少 {k}" for k in expected if k not in data]
    out += [f"{where}: 未知的键 {k}" for k in data if k not in expected]
    return out


def _option_problems(options: Dict[str, object]) -> List[str]:
    out = []
    for k, v in options.items():
        t = OPTION_TYPES.get(k)
        if t is None:
            out.append(f"options: 未知的选项 {k}")
        elif t is float and (isinstance(v, bool) or not isinstance(v, (int, float))):
            out.append(f"options.{k} 必须是数字")
        elif t is not float and not isinstance(v, t):
            out.append(f"options.{k} 必须是 {t.__name__}")
    return out


# ---------------------------------------------------------------------------
# queries over a fix list (only enabled fixes take effect)

def upsert(fixes: List[Fix], fix: Fix) -> List[Fix]:
    """Replace the fix with the same key (keeping its position) or append."""
    for n, f in enumerate(fixes):
        if f.key == fix.key:
            fixes[n] = fix
            return fixes
    fixes.append(fix)
    return fixes


def by_key(fixes: Iterable[Fix]) -> Dict[str, Fix]:
    return {f.key: f for f in fixes}


def fixed_slots(fixes: Iterable[Fix]) -> Dict[str, str]:
    """Enabled slot fixes: slot id → source bone ("" = leave empty)."""
    return {f.slot_id: f.bone for f in fixes if f.enabled and f.kind == "slot"}


def bone_fixes(fixes: Iterable[Fix]) -> Dict[str, Fix]:
    return {f.bone: f for f in fixes if f.enabled and f.kind == "bone"}


def split_fixes(fixes: Iterable[Fix]) -> List[Fix]:
    return [f for f in fixes if f.enabled and f.kind == "split_side"]


def ignored(fixes: Iterable[Fix]) -> Set[str]:
    return {f.finding for f in fixes if f.enabled and f.kind == "ignore"}


def user_decided(fixes: Iterable[Fix]) -> Set[str]:
    """Keys the user decided (hand edits, CSV, files): automatic fixes never replace these."""
    return {f.key for f in fixes if f.origin in ("user", "csv", "file")}


def find(fixes: Iterable[Fix], key: str) -> Optional[Fix]:
    return next((f for f in fixes if f.key == key), None)
