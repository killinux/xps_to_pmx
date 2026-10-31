"""Fix-list plumbing (design doc §15.3–§15.4).

* Fix files: written next to the PMX and under ``<user data dir>/fixes/<sha1>.fixes.json`` so the
  same XPS file finds its fixes again wherever it was exported; read back when that file is imported.
* Remembered options travel with the fixes.
* ``split_side`` fixes change source weights, so they run right after ① (before ②), once each.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Optional

import bpy
import numpy as np

from .. import prefs, props
from ..blender import rigedit, snapshot
from ..core import fixes as fx
from ..core.checks.cause import SPLIT_BLEND
from ..core.result import StageResult

STAGE = "fixes"


def sha1_of(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def user_fixes_path(context: bpy.types.Context, sha1: str) -> str:
    return os.path.join(prefs.user_data_dir(context), "fixes", f"{sha1}.fixes.json")


def pmx_fixes_path(pmx_path: str) -> str:
    return os.path.splitext(pmx_path)[0] + ".fixes.json"


def remembered_path(context: bpy.types.Context, job) -> Optional[str]:
    """The fix file remembered for this job's XPS: user data folder first, then next to the default PMX."""
    from . import stage_export  # late: stage_export imports stage_identify, which imports this module
    if job.source_sha1:
        path = user_fixes_path(context, job.source_sha1)
        if os.path.isfile(path):
            return path
    path = pmx_fixes_path(stage_export.default_path(context, job))
    return path if os.path.isfile(path) else None


def option_values(job) -> Dict[str, object]:
    return {name: getattr(job, name) for name in fx.OPTION_TYPES}


def apply_options(job, options: Dict[str, object], res: StageResult) -> None:
    for name, value in options.items():
        try:
            setattr(job, name, value)
        except (TypeError, ValueError) as exc:
            res.warning("fixes.option_rejected", f"修正单里的选项 {name}={value!r} 无法使用：{exc}")


def load_remembered(context: bpy.types.Context, job) -> StageResult:
    """After ①: hash the XPS file and, when a fix file for exactly this file exists, use it."""
    res = StageResult(STAGE)
    if not job.source_sha1 and os.path.isfile(job.source_path):
        job.source_sha1 = sha1_of(job.source_path)
    path = remembered_path(context, job)
    if path is None:
        return res
    res.extend(load_file(context, job, path, remembered=True))
    return res


def load_file(context: bpy.types.Context, job, path: str, remembered: bool = False) -> StageResult:
    res = StageResult(STAGE)
    try:
        with open(path, encoding="utf-8") as f:
            ff = fx.parse_fixes(f.read())
    except (OSError, fx.FixFileError) as exc:
        res.warning("fixes.unreadable", f"修正单文件读不了，没有套用：{exc}", path)
        return res
    if job.source_sha1 and ff.source_sha1 and ff.source_sha1 != job.source_sha1:
        if remembered:
            res.warning("fixes.other_file", f"{path} 是为另一个版本的 XPS 文件记的，没有套用", path)
            return res
        res.warning("fixes.other_file", f"{path} 是为另一个版本的 XPS 文件记的，按骨名套用，请核对", path)
    with props.programmatic_writes(context):
        current = job.fix_list()
        for fix in ff.fixes:
            fx.upsert(current, fix)
        job.set_fix_list(current)
        apply_options(job, ff.options, res)
    what = "套用了上次的修正单" if remembered else "导入了修正单"
    res.info("fixes.loaded", f"{what}（{len(ff.fixes)} 条）：{path}", path, count=len(ff.fixes))
    return res


def save(context: bpy.types.Context, job, pmx_path: str = "") -> StageResult:
    """Write the fix list next to the PMX and into the user data folder (keyed by the XPS file's SHA-1)."""
    res = StageResult(STAGE)
    if not job.source_sha1 and os.path.isfile(job.source_path):
        job.source_sha1 = sha1_of(job.source_path)
    fixes, skipped = [], []
    for fix in job.fix_list():
        (skipped if fx.validate_fix(fix) else fixes).append(fix)
    for fix in skipped:
        res.warning("fixes.invalid", f"修正单里这一条不完整，没有写进文件：{fix.describe()}")
    ff = fx.FixFile(job.model_name, job.source_path, job.source_sha1, option_values(job), fixes)
    text = fx.write_fixes(ff)
    targets = [user_fixes_path(context, job.source_sha1)] if job.source_sha1 else []
    if pmx_path:
        targets.append(pmx_fixes_path(pmx_path))
    written = []
    for path in targets:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            written.append(path)
        except OSError as exc:
            res.warning("fixes.write_failed", f"修正单写不进 {path}：{exc}", path)
    res.data.update({"paths": written, "count": len(fixes)})
    return res


def export_file(context: bpy.types.Context, job, path: str) -> StageResult:
    res = StageResult(STAGE)
    ff = fx.FixFile(job.model_name, job.source_path, job.source_sha1, option_values(job),
                    [f for f in job.fix_list() if not fx.validate_fix(f)])
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(fx.write_fixes(ff))
    res.info("fixes.exported", f"已导出修正单（{len(ff.fixes)} 条）：{path}", path)
    return res


# ---------------------------------------------------------------------------
# applying split_side before stage ②

def splits_done(job) -> List[str]:
    try:
        return list(json.loads(job.splits_done_json or "[]"))
    except ValueError:
        return []


def apply_splits(context: bpy.types.Context, job) -> StageResult:
    """Apply enabled ``split_side`` fixes that were not applied yet (only before ③ changes the skeleton)."""
    res = StageResult(STAGE)
    pending = [f for f in fx.split_fixes(job.fix_list()) if f.key not in splits_done(job)]
    if not pending:
        return res
    arm = job.armature
    if arm is None or job.stage not in ("", "import", "identify"):
        res.warning("fixes.split_late", f"{len(pending)} 条拆分权重修正要从头重做才能生效")
        return res
    names = {b.name for b in arm.data.bones}
    rig = snapshot.rig_from_blender(arm, with_skin=False)
    blend = SPLIT_BLEND * rig.height
    to_arm = np.array(arm.matrix_world.inverted())
    done = splits_done(job)
    for fix in pending:
        if fix.bone not in names or fix.twin not in names:
            res.warning("fixes.split_missing", f"拆分权重：骨架里没有 {fix.bone} 或 {fix.twin}，跳过", fix.bone)
            continue
        twin_x = float(arm.data.bones[fix.twin].head_local[0])
        side = 1.0 if twin_x > 0 else -1.0
        changed = sum(rigedit.split_group_by_side(obj, fix.bone, fix.twin, side, blend,
                                                  to_arm @ np.array(obj.matrix_world))
                      for obj in snapshot.skinned_meshes(arm))
        done.append(fix.key)
        res.info("fixes.split_applied", f"已按左右拆分 {fix.bone} 的权重：{changed} 个顶点改给 {fix.twin}", fix.bone,
                 vertices=changed)
    job.splits_done_json = json.dumps(done, ensure_ascii=False)
    return res


# ---------------------------------------------------------------------------
# panel actions on findings and fixes

def toggle_finding_fix(context: bpy.types.Context, job, index: int) -> str:
    """Put a finding's suggested fix into the fix list, or switch it on / off."""
    if not 0 <= index < len(job.findings) or not job.findings[index].fix_json:
        return ""
    fix = fx.Fix(**json.loads(job.findings[index].fix_json))
    item = job.fix_item(fix.key)
    if item is None:
        fix.enabled, fix.auto = True, False
        job.upsert_fix(fix)
        text = f"已记入修正单：{fix.describe()}"
    else:
        item.enabled = not item.enabled
        text = ("已启用：" if item.enabled else "已撤销：") + fix.describe()
    if job.stage in props.BUILT_STAGES:
        job.fixes_pending = True
    return text


def ignore_finding(context: bpy.types.Context, job, index: int) -> str:
    if not 0 <= index < len(job.findings):
        return ""
    f = job.findings[index]
    job.upsert_fix(fx.Fix("ignore", finding=f.key, origin="user", note=f.text[:80]))
    job.findings.remove(index)
    job.findings_index = min(job.findings_index, len(job.findings) - 1)
    return f"以后不再报：{f.text[:40]}"


def remove_fix(context: bpy.types.Context, job, index: int) -> str:
    """Remove a fix; automatic ones are only switched off, so the checkup does not add them back."""
    if not 0 <= index < len(job.fixes):
        return ""
    item = job.fixes[index]
    text = item.to_fix().describe()
    if item.origin == "checkup" and item.auto:
        item.enabled = False
        text = f"已撤销（保留记录，不会再自动加回）：{text}"
    else:
        job.fixes.remove(index)
        job.fixes_index = min(job.fixes_index, len(job.fixes) - 1)
        text = f"已删除：{text}"
    if job.stage in props.BUILT_STAGES:
        job.fixes_pending = True
    return text

