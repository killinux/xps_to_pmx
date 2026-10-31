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
from ..blender import posetest as bpt
from ..blender import snapshot
from ..core import fixes as fx
from ..core.checks import posetest
from ..core.checks.checkup import (INFO, Finding, diff_findings, joint_findings, joint_leaks, joint_specs,
                                   part_of_category, part_of_slot, side_findings, side_leaks, sort_findings,
                                   summarize)
from ..core.result import StageResult
from . import stage_identify, views

STAGE = "checkup"
REPORT_STAGES = ("import", "prepare", "build", "export")
#: ② explanations that are not problems and would only make the report longer.
QUIET_CODES = ("mapping.disagreement",)
#: Stage warnings that describe routine clean-up rather than problems: shown as 提示.  A renamed bone
#: keeps its original name in a property; when the rename hides a real problem the duplicate check says so.
INFO_CODES = ("import.weights_renormalized", "import.weights_truncated", "import.bone_renamed")
SEVERITY = {"info": 0, "warning": 1, "error": 2}
#: Pose-test regions that show the 下半身 reaching into the belly (lower_body.high is about the same thing).
BELLY = (("hip_twist", "腹部"), ("waist_bend", "腹部"))


def snapshot_findings(job) -> Dict[str, Dict]:
    """The last checkup as ``key → {level, text, part, code, state, view}`` (for the before / after diff)."""
    return {f.key: {"level": f.level, "text": f.text, "part": f.part, "code": f.code, "state": f.state,
                    "view": f.view()} for f in job.findings}


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
    job.checkup_run += 1
    fixes = job.fix_list()
    bones = set(arm.data.bones.keys())
    category_of_src = {plan.src or plan.name: plan.category for plan in job.bones}
    source_of = {pb.name: pb.mmd_bone.name_e for pb in arm.pose.bones}

    def part_of_bone(name: str) -> str:
        slot = spec.by_name_j.get(name)
        if slot is not None:
            return part_of_slot(spec, slot.slot_id)
        return part_of_category(category_of_src.get(source_of.get(name, ""), ""))

    twins = {d.get("twin") for d in _load(job.duplicates_json)} | {f.twin for f in fx.split_fixes(fixes)}
    findings = [f for f in _stage_messages(job, bones, part_of_bone)
                if not (f.code == "import.bone_renamed" and f.subject in twins)]  # explained by the duplicate
    findings += _mapping_checks(job, spec, bones, category_of_src)
    meshes = snapshot.skinned_meshes(arm)
    rig = snapshot.rig_from_blender(arm, meshes=meshes)
    if rig.skin is not None:
        prig = bpt.pose_rig(arm, rig, views.body_names(context))
        bpt.remember(job.job_id, arm, meshes, prig, rig.skin.mesh_slices)
        bm = posetest.body_map(prig)
        issues = posetest.run_tests(prig, bm=bm)
        findings += _symptoms(job, spec, rig, fixes, source_of, part_of_bone, prig, issues)
        findings = _lower_body(findings, prig, bm, issues)
    findings = _merge_duplicates(findings)
    ignored = fx.ignored(fixes)
    shown = [f for f in findings if f.key not in ignored]
    final = sort_findings(diff_findings(prev, shown))
    _store(context, job, final)
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


def _symptoms(job, spec, rig, fixes, source_of, part_of_bone, prig, issues) -> List[Finding]:
    """Joint and side leaks on the final weights, then the pose tests (design doc §15.5, §16)."""
    index = rig.by_name
    n = rig.skin.count

    def column(names) -> np.ndarray:
        cols = [rig.skin.bone_weight_column(index[nm]) for nm in names if nm in index]
        return np.sum(cols, axis=0) if cols else np.zeros(n)

    heads = {b.name: np.asarray(b.head, float) for b in rig.bones}
    leaks = joint_leaks(rig.skin.positions, column, joint_specs(spec, heads))
    analysis = _load(job.merge_analysis_json)
    found = joint_findings(leaks, spec, analysis, fx.user_decided(fixes))
    _joint_views(found, leaks, prig)
    weighted = [b for b in rig.bones if b.weighted]
    sides = side_leaks([b.name for b in weighted], np.array([b.head for b in weighted]) if weighted else np.zeros((0, 3)),
                       rig.skin.positions, lambda k: rig.skin.bone_weight_column(weighted[k].index), rig.height)
    duplicates = _load(job.duplicates_json)
    side_found = side_findings(sides, source_of, duplicates, part_of_bone)
    centre_y = float(np.mean(rig.skin.positions[:, 1])) if n else 0.0
    for f, leak in zip(side_found, sides):  # one finding per leak, in order
        back = heads[leak.bone][1] > centre_y if leak.bone in heads else True
        f.view = posetest.make_view(prig, leak.idx, bone=leak.bone, axis=(0.0, -leak.side, 0.0), angle=30.0,
                                    direction=(0.0, 1.0 if back else -1.0, 0.0))
    found += side_found
    belly = [i for i in issues if (i.test.id, i.region) in BELLY]
    return _with_pose(found, [i for i in issues if not i.quiet and i not in belly], prig, source_of, duplicates)


def _joint_views(found: List[Finding], leaks, prig) -> None:
    """A joint leak is shown in the knee / elbow test with its leaking vertices selected."""
    by = {(leak.spec.side, leak.spec.joint): leak for leak in leaks}
    for f in found:
        if f.code != "checkup.joint_leak":
            continue
        side, joint, direction = f.subject.split(":")[0].split("_")
        leak = by.get((side, joint))
        test = posetest.find_test(prig, f"{joint}_{'L' if side == 'left' else 'R'}")
        if leak is not None and test is not None:
            f.view = posetest.make_view(prig, leak.down_idx if direction == "down" else leak.up_idx, test)


def _with_pose(found: List[Finding], issues, prig, source_of, duplicates) -> List[Finding]:
    """Add the pose-test findings; a knee / elbow issue that a joint leak already explains becomes its evidence."""
    out = list(found)
    for issue in issues:
        joint = issue.test.id.split("_")[0]
        if issue.kind == "follow" and joint in ("knee", "elbow"):
            side = "left" if issue.test.id.endswith("_L") else "right"
            prefix = f"{side}_{joint}_{'down' if issue.expect == 'move' else 'up'}"
            same = [f for f in out if f.code == "checkup.joint_leak" and f.subject.split(":")[0] == prefix]
            if same:
                how = "跟不上" if issue.expect == "move" else "被带着动"
                for f in same:
                    f.detail = (f.detail + "；" if f.detail else "") + \
                        f"姿势测试：{issue.test.label}时 {len(issue.vertices)} 个顶点{how}，最多约 {posetest.length_text(issue.worst)}"
                    if not f.view:
                        f.view = posetest.issue_view(prig, issue)
                continue
        out.append(posetest.issue_finding(prig, issue, source_of, duplicates))
    return out


def _lower_body(findings: List[Finding], prig, bm, issues) -> List[Finding]:
    """「下半身 reaches above the waist」 is judged by the hip twist and the waist bend.

    The belly of the 18-series reference models follows the hips by up to 3.4 % of the height, so a
    drag within that is not reported on its own.  Above it, the warning stays and shows the pose;
    within it (or with no drag at all), the warning drops to a 提示 that says so.
    """
    belly = [i for i in issues if (i.test.id, i.region) in BELLY]
    loud = [i for i in belly if not i.quiet]
    worst = max(loud or belly, key=lambda i: i.worst) if belly else None
    warning = next((f for f in findings if f.code == "lower_body.high"), None)
    if warning is None:
        if worst is not None and not worst.quiet:  # no static warning, but the pose shows it
            findings.append(posetest.issue_finding(prig, worst, {}, []))
        return findings
    text = "；".join(f"{i.test.label}时{i.region}{len(i.vertices)} 个顶点被带着动，最多约 "
                    f"{posetest.length_text(i.worst)}" for i in belly)
    if worst is not None and not worst.quiet:
        warning.detail = (warning.detail + "；" if warning.detail else "") + f"姿势测试：{text}"
        warning.view = posetest.issue_view(prig, worst)
        return findings
    warning.level = INFO
    warning.detail = (warning.detail + "；" if warning.detail else "") + (
        f"姿势测试：{text}；18 系列成品也是这样（最多约身高的 {posetest.BELLY_LIMIT:.1%}），不算问题" if belly else
        "姿势测试：下半身扭转 30°、上半身前屈 45° 时，腹部没有明显被带着动")
    if worst is not None:
        warning.view = posetest.issue_view(prig, worst)
        return findings
    test = posetest.find_test(prig, "hip_twist")
    lower = prig.by_name.get("下半身")
    if test is not None and lower is not None:
        weight = np.where(prig.skin_bones == lower, prig.skin_weights, 0.0).sum(axis=1)
        region = bm.region("spine", posetest.belly_start(prig), 0.45) & (weight > 0.05)
        warning.view = posetest.make_view(prig, np.nonzero(region)[0], test)
    return findings


def _merge_duplicates(findings: List[Finding]) -> List[Finding]:
    """A symptom whose fix equals a cause finding's fix is the same problem: keep the cause, add the evidence.

    The cause also takes the symptom's view (a pose test's view first) and its pose-test evidence.
    """
    by_fix = {}
    out = []
    for f in findings:
        key = f.fix.key if f.fix is not None else None
        if key is not None and key in by_fix and f.code.startswith(("checkup.", "pose.")):
            first = by_fix[key]
            first.detail = (first.detail + "；" if first.detail else "") + f"体检：{f.text}"
            first.detail += "".join(f"；{part}" for part in f.detail.split("；") if part.startswith("姿势测试"))
            if f.view and (not first.view or f.code.startswith("pose.")):
                first.view = f.view
            if SEVERITY[f.level] > SEVERITY[first.level]:
                first.level = f.level  # the symptom shows the problem is real
            continue
        if key is not None and key not in by_fix:
            by_fix[key] = f
        out.append(f)
    return out


def _store(context, job, findings: List[Finding]) -> None:
    job.findings.clear()
    for f in findings:
        item = job.findings.add()
        item.level, item.code, item.part, item.text = f.level, f.code, f.part, f.text
        item.target, item.subject, item.key, item.detail = f.target, f.subject, f.key, f.detail
        item.fix_json = json.dumps(f.fix.to_dict(), ensure_ascii=False) if f.fix is not None else ""
        item.fix_key = f.fix.key if f.fix is not None else ""
        item.state = f.state
        item.view_json = json.dumps(f.view, ensure_ascii=False) if f.view else ""
        item.image_before = views.earlier_image(context, job, f.key) if f.view else ""
        item.image_after = ""
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
                      "fix": f.fix.to_dict() if f.fix is not None else None,
                      "pose": ({"view": f.view.get("test") or f.view.get("bone", ""),
                                "vertices": len(f.view.get("vertices", []))} if f.view else None)}
                     for f in findings],
        "fixes": [fix.to_dict() for fix in job.fix_list()],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
