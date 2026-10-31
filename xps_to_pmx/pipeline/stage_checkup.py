"""Stage ⑨ 体检 (design doc §15.5–§15.6): one report for the converted model.

Collects what the stages reported (① import warnings, ② mapping checks including the
cause checks, ③ ④ ⑧ warnings and read-back checks), adds the symptom checks on the MMD
model's final weights, drops ignored findings, compares with the previous checkup and
stores the result in the job and in ``<name>.report.json``.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

import bpy
import numpy as np

from .. import props
from ..blender import snapshot
from ..core import fixes as fx
from ..core.checks.checkup import (INFO, Finding, diff_findings, joint_findings, joint_leaks, joint_specs,
                                   part_of_category, part_of_slot, side_findings, side_leaks, sort_findings,
                                   summarize)
from ..core.result import StageResult
from . import stage_identify

STAGE = "checkup"
REPORT_STAGES = ("import", "prepare", "build", "export")
#: ② explanations that are not problems and would only make the report longer.
QUIET_CODES = ("mapping.disagreement",)
#: Stage warnings that describe routine clean-up rather than problems: shown as 提示.
INFO_CODES = ("import.weights_renormalized", "import.weights_truncated")
SEVERITY = {"info": 0, "warning": 1, "error": 2}


def snapshot_findings(job) -> Dict[str, Dict]:
    """The last checkup as ``key → {level, text, part, code, state}`` (for the before / after diff)."""
    return {f.key: {"level": f.level, "text": f.text, "part": f.part, "code": f.code, "state": f.state}
            for f in job.findings}


def run(context: bpy.types.Context, job, previous: Optional[Dict[str, Dict]] = None) -> StageResult:
    res = StageResult(STAGE)
    arm = job.armature if job is not None else None
    if arm is None or arm.name not in bpy.data.objects:
        res.error("checkup.no_armature", "当前任务没有骨架")
        return res
    if job.stage not in props.BUILT_STAGES:
        res.error("checkup.not_built", "先完成 ④ 生成 MMD 骨架")
        return res
    spec = stage_identify.load_spec(context)
    prev = snapshot_findings(job) if previous is None else previous
    fixes = job.fix_list()
    bones = set(arm.data.bones.keys())
    category_of_src = {plan.src or plan.name: plan.category for plan in job.bones}
    source_of = {pb.name: pb.mmd_bone.name_e for pb in arm.pose.bones}

    def part_of_bone(name: str) -> str:
        slot = spec.by_name_j.get(name)
        if slot is not None:
            return part_of_slot(spec, slot.slot_id)
        return part_of_category(category_of_src.get(source_of.get(name, ""), ""))

    twins = {d.get("twin") for d in _load(job.duplicates_json)}
    findings = [f for f in _stage_messages(job, bones, part_of_bone)
                if not (f.code == "import.bone_renamed" and f.subject in twins)]  # explained by the duplicate
    findings += _mapping_checks(job, spec, bones, category_of_src)
    rig = snapshot.rig_from_blender(arm)
    if rig.skin is not None:
        findings += _symptoms(job, spec, rig, fixes, source_of, part_of_bone)
    findings = _merge_duplicates(findings)
    ignored = fx.ignored(fixes)
    shown = [f for f in findings if f.key not in ignored]
    final = sort_findings(diff_findings(prev, shown))
    _store(job, final)
    counts = summarize({"level": f.level, "state": f.state} for f in final)
    res.data.update({"counts": counts, "ignored": len(findings) - len(shown), "findings": len(final)})
    parts = [f"{counts['error']} 错误", f"{counts['warning']} 警告", f"{counts['info']} 提示"]
    if counts["auto_fixed"]:
        parts.append(f"已自动修正 {counts['auto_fixed']} 项")
    if counts["fixed"]:
        parts.append(f"比上次修好 {counts['fixed']} 项")
    res.info("checkup.done", "体检：" + "、".join(parts))
    job.record(res)
    write_report_section(job, final, counts, len(findings) - len(shown))
    return res


def _stage_messages(job, bones, part_of_bone) -> List[Finding]:
    out = []
    for r in job.reports:
        if r.stage not in REPORT_STAGES or r.level == INFO:
            continue
        target = r.target if r.target in bones else ""
        part = part_of_bone(target) if target else "global"
        level = INFO if r.code in INFO_CODES else r.level
        out.append(Finding(r.code, level, r.text, part, target, r.target or r.text[:48]))
    return out


def _mapping_checks(job, spec, bones, category_of_src) -> List[Finding]:
    out = []
    for c in job.checks:
        if c.code in QUIET_CODES:
            continue
        slot = spec.get(c.slot_id) if c.slot_id else None
        if slot is not None:
            part = part_of_slot(spec, c.slot_id)
        else:
            part = part_of_category(category_of_src.get(c.target, "")) if c.target else "global"
        target = slot.name_j if slot is not None and slot.name_j in bones else (c.target if c.target in bones else "")
        f = Finding(c.code, c.level, c.text, part, target, c.target or c.slot_id, c.detail,
                    stage_identify.fix_from_json(c.fix_json))
        if c.code == "mapping.auto_fixed":
            f.state = "auto_fixed"
        out.append(f)
    return out


def _symptoms(job, spec, rig, fixes, source_of, part_of_bone) -> List[Finding]:
    index = rig.by_name
    n = rig.skin.count

    def column(names) -> np.ndarray:
        cols = [rig.skin.bone_weight_column(index[nm]) for nm in names if nm in index]
        return np.sum(cols, axis=0) if cols else np.zeros(n)

    heads = {b.name: np.asarray(b.head, float) for b in rig.bones}
    leaks = joint_leaks(rig.skin.positions, column, joint_specs(spec, heads))
    analysis = _load(job.merge_analysis_json)
    found = joint_findings(leaks, spec, analysis, fx.user_decided(fixes))
    weighted = [b for b in rig.bones if b.weighted]
    sides = side_leaks([b.name for b in weighted], np.array([b.head for b in weighted]) if weighted else np.zeros((0, 3)),
                       rig.skin.positions, lambda k: rig.skin.bone_weight_column(weighted[k].index), rig.height)
    found += side_findings(sides, source_of, _load(job.duplicates_json), part_of_bone)
    return found


def _merge_duplicates(findings: List[Finding]) -> List[Finding]:
    """A symptom whose fix equals a cause finding's fix is the same problem: keep the cause, add the evidence."""
    by_fix = {}
    out = []
    for f in findings:
        key = f.fix.key if f.fix is not None else None
        if key is not None and key in by_fix and f.code.startswith("checkup."):
            first = by_fix[key]
            first.detail = (first.detail + "；" if first.detail else "") + f"体检：{f.text}"
            if SEVERITY[f.level] > SEVERITY[first.level]:
                first.level = f.level  # the symptom shows the problem is real
            continue
        if key is not None and key not in by_fix:
            by_fix[key] = f
        out.append(f)
    return out


def _store(job, findings: List[Finding]) -> None:
    job.findings.clear()
    for f in findings:
        item = job.findings.add()
        item.level, item.code, item.part, item.text = f.level, f.code, f.part, f.text
        item.target, item.subject, item.key, item.detail = f.target, f.subject, f.key, f.detail
        item.fix_json = json.dumps(f.fix.to_dict(), ensure_ascii=False) if f.fix is not None else ""
        item.fix_key = f.fix.key if f.fix is not None else ""
        item.state = f.state
    job.findings_index = 0


def _load(text: str) -> list:
    try:
        return list(json.loads(text or "[]"))
    except ValueError:
        return []


def write_report_section(job, findings: List[Finding], counts: Dict[str, int], ignored: int) -> None:
    """Add the checkup to ``<name>.report.json`` next to the last export (if there is one)."""
    if not job.last_export:
        return
    path = os.path.splitext(job.last_export)[0] + ".report.json"
    if not os.path.isfile(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            report = json.load(f)
    except (OSError, ValueError):
        return
    report["checkup"] = {
        "counts": counts, "ignored": ignored,
        "findings": [{"level": f.level, "state": f.state, "part": f.part, "code": f.code, "text": f.text,
                      "detail": f.detail, "target": f.target, "key": f.key,
                      "fix": f.fix.to_dict() if f.fix is not None else None} for f in findings],
        "fixes": [fix.to_dict() for fix in job.fix_list()],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
