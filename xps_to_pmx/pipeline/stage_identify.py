"""Stage ②: identify the skeleton, store the mapping in the job, run the mapping checks.

Also: re-check after manual edits (rebuilding the identification from the job
state, not re-identifying), and import / export of per-model mapping CSV files.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

import bpy

from .. import prefs, props
from ..blender import snapshot
from ..core.checks.mapping import CheckItem, check_mapping
from ..core.mapping_io import MappingRow, parse_mapping, write_mapping
from ..core.result import StageResult
from ..core.rig.classify import Disposition
from ..core.rig.identify import Identification, SlotMatch, identify
from ..core.rig.lower_body import LowerBodyDiagnosis
from ..core.rig.rigdata import RigData
from ..core.rig.topology import TopologyResult
from ..core.spec import BoneSpec, SpecError, load_bone_spec
from ..core.spec.bone_slots import DEFAULT_PATH

STAGE = "identify"
USER_SPEC_NAME = "bone_slots.csv"


def load_spec(context: bpy.types.Context) -> BoneSpec:
    """Default table, overridden by ``<user data dir>/bone_slots.csv`` when present."""
    user = os.path.join(prefs.user_data_dir(context), USER_SPEC_NAME)
    return load_bone_spec(DEFAULT_PATH, [user])


BUILT_STAGES = ("build", "morphs", "physics", "check", "export")


def _require_armature(res: StageResult, job) -> Optional[bpy.types.Object]:
    arm = job.armature if job is not None else None
    if arm is None or arm.type != 'ARMATURE' or arm.name not in bpy.data.objects:
        res.error("identify.no_armature", "当前任务没有骨架（先 ① 导入 XPS）")
        return None
    if job.stage in BUILT_STAGES:
        res.error("identify.already_built", "MMD 骨架已生成，骨名已改成日文；要改映射请先『重来』")
        return None
    return arm


def run(context: bpy.types.Context, job, keep_user: bool = True) -> StageResult:
    res = StageResult(STAGE)
    arm = _require_armature(res, job)
    if arm is None:
        return res
    try:
        spec = load_spec(context)
    except SpecError as exc:
        res.error("identify.spec_invalid", f"骨骼规格表有错误：{exc.problems[0]}（共 {len(exc.problems)} 处）")
        return res
    rig = snapshot.rig_from_blender(arm)
    fixed = {}
    if keep_user:
        for s in job.slots:
            if s.origin != 'user':
                continue
            if not s.bone:
                fixed[s.name] = -1          # explicitly left empty → generated
            elif s.bone in rig.by_name:
                fixed[s.name] = rig.by_name[s.bone]
    ident = identify(rig, spec, fixed=fixed)
    _store(context, job, spec, rig, ident)
    items = check_mapping(rig, spec, ident)
    _store_checks(context, job, items)
    _fill_result(res, spec, ident, items)
    job.record(res)
    return res


def recheck(context: bpy.types.Context, job) -> StageResult:
    """Run the mapping checks on the job's current (possibly hand-edited) mapping."""
    res = StageResult(STAGE)
    arm = _require_armature(res, job)
    if arm is None:
        return res
    spec = load_spec(context)
    rig = snapshot.rig_from_blender(arm)
    sync_plans_with_slots(context, job)
    ident, problems = identification_from_job(job, spec, rig)
    for text in problems:
        res.warning("identify.stale_mapping", text)
    items = check_mapping(rig, spec, ident)
    _store_checks(context, job, items)
    _fill_result(res, spec, ident, items)
    props.state(context).mapping_dirty = False
    job.record(res)
    return res


def sync_plans_with_slots(context: bpy.types.Context, job) -> None:
    """After manual slot edits: slot primaries get action ``map``; bones that lost their slot are kept."""
    primary = {s.bone: s.name for s in job.slots if s.bone}
    with props.programmatic_writes(context):
        for plan in job.bones:
            slot_id = primary.get(plan.name)
            if slot_id is not None:
                if plan.action != "map" or plan.slot_id != slot_id:
                    plan.action, plan.slot_id, plan.origin = "map", slot_id, 'user'
                    plan.reason = "槽位主骨（手动）"
            elif plan.action == "map":
                plan.action, plan.slot_id = "keep", ""
                plan.reason = "原槽位已改用其他骨，保留原名"


def identification_from_job(job, spec: BoneSpec, rig: RigData) -> Tuple[Identification, List[str]]:
    problems: List[str] = []
    slots: Dict[str, SlotMatch] = {}
    for s in spec:
        item = job.slot(s.slot_id)
        m = SlotMatch(s.slot_id)
        if item is not None and item.bone:
            if item.bone in rig.by_name:
                m.bone = rig.by_name[item.bone]
                m.origin = item.origin
                m.confidence = item.confidence
                m.reason = item.reason
            else:
                problems.append(f"{s.name_j} 映射的骨 {item.bone} 已不存在")
        elif item is not None and item.origin == 'user':  # explicitly left empty by the user
            m.origin, m.reason = item.origin, item.reason or "用户指定留空（由补骨生成）"
        slots[s.slot_id] = m
    dispositions: Dict[int, Disposition] = {}
    for plan in job.bones:
        idx = rig.by_name.get(plan.name)
        if idx is None:
            continue
        dispositions[idx] = Disposition(idx, plan.action, plan.slot_id, plan.category, plan.reason, plan.origin)
        if plan.action == "merge" and plan.slot_id in slots:
            slots[plan.slot_id].merges.append(idx)
    diag_data = job.lower_body()
    diag = LowerBodyDiagnosis(case=diag_data.get("case", ""), text=diag_data.get("text", ""),
                              primary=rig.by_name.get(diag_data.get("primary", ""), -1))
    disagreements = []
    try:
        for slot_id, a, b in json.loads(job.disagreements_json or "[]"):
            if a in rig.by_name and b in rig.by_name:
                disagreements.append((slot_id, rig.by_name[a], rig.by_name[b]))
    except ValueError:
        pass
    ident = Identification(job.convention, [], slots, dispositions, diag, TopologyResult(), disagreements)
    return ident, problems


def _store(context, job, spec: BoneSpec, rig: RigData, ident: Identification) -> None:
    with props.programmatic_writes(context):
        job.convention = ident.convention
        job.facing = ident.facing
        job.slots.clear()
        for s in spec.ordered():
            m = ident.slots[s.slot_id]
            item = job.slots.add()
            item.name = s.slot_id
            item.name_j, item.group, item.row_type = s.name_j, s.group, s.row_type
            item.side, item.mirror, item.required, item.tier = s.side, s.mirror, s.required, s.tier
            item.bone = rig.bones[m.bone].name if m.bone >= 0 else ""
            item.origin = m.origin if (m.bone >= 0 or m.origin == 'user') and m.origin else 'NONE'
            item.confidence = m.confidence
            item.reason = m.reason
        job.bones.clear()
        for b in rig.bones:
            disp = ident.bones.get(b.index)
            plan = job.bones.add()
            plan.name = b.name
            plan.src = b.src_name
            plan.weighted = b.weighted
            if disp is None:
                continue
            plan.action = disp.action
            plan.slot_id = disp.slot_id
            plan.category = disp.category
            plan.reason = disp.reason
            plan.origin = disp.origin if disp.origin in {o[0] for o in props.ORIGIN_ITEMS} else 'classifier'
        diag = ident.lower_body
        job.lower_body_json = json.dumps({
            "case": diag.case, "text": diag.text,
            "primary": rig.bones[diag.primary].name if diag.primary >= 0 else "",
            "split_bone": rig.bones[diag.split_bone].name if diag.split_bone >= 0 else "",
            "merges": [rig.bones[b].name for b in diag.merges],
            "waist_z": diag.waist_z, "thigh_z": diag.thigh_z, "seg_l": diag.seg_l,
            "candidates": [c.as_dict() for c in diag.candidates],
        }, ensure_ascii=False)
        job.disagreements_json = json.dumps(
            [(s, rig.bones[a].name, rig.bones[b].name) for s, a, b in ident.disagreements], ensure_ascii=False)
    props.state(context).mapping_dirty = False


def _store_checks(context, job, items: List[CheckItem]) -> None:
    job.checks.clear()
    order = {"error": 0, "warning": 1, "info": 2}
    for it in sorted(items, key=lambda i: order[i.level]):
        c = job.checks.add()
        c.level = it.level
        c.stage = STAGE
        c.code = it.code
        c.text = it.text
        c.target = it.bone
        c.slot_id = it.slot_id


def _fill_result(res: StageResult, spec: BoneSpec, ident: Identification, items: List[CheckItem]) -> None:
    required = [s.slot_id for s in spec if s.required]
    filled = sum(1 for s in required if ident.slots[s].mapped)
    for it in items:
        res.add(it.level, it.code, it.text, it.bone or it.slot_id)
    actions: Dict[str, int] = {}
    for d in ident.bones.values():
        actions[d.action] = actions.get(d.action, 0) + 1
    res.data = {"convention": ident.convention, "required_filled": filled, "required_total": len(required),
                "lower_body_case": ident.lower_body.case, "actions": actions,
                "errors": sum(1 for i in items if i.level == "error"),
                "warnings": sum(1 for i in items if i.level == "warning")}
    res.info("identify.summary",
             f"约定 {ident.convention or '（仅拓扑）'}；必需骨 {filled}/{len(required)}；下半身 情形{ident.lower_body.case or '?'}；"
             f"映射 {actions.get('map', 0)}、并入 {actions.get('merge', 0)}、保留 {actions.get('keep', 0)}、"
             f"删除 {actions.get('delete', 0)}")


# ---------------------------------------------------------------------------
# CSV import / export

def export_csv(context: bpy.types.Context, job, path: str) -> StageResult:
    res = StageResult(STAGE)
    spec = load_spec(context)
    rows: List[MappingRow] = []
    for plan in job.bones:
        slot = spec.get(plan.slot_id) if plan.slot_id else None
        conf = 1.0
        if plan.action == "map" and plan.slot_id and job.slot(plan.slot_id) is not None:
            conf = job.slot(plan.slot_id).confidence
        rows.append(MappingRow(plan.src or plan.name, plan.action, plan.slot_id, slot.name_j if slot else "",
                               plan.origin, conf, plan.reason))
    text = write_mapping(rows, source=job.source_path, convention=job.convention)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    res.info("identify.csv_exported", f"已导出映射 {len(rows)} 行：{path}", path)
    return res


def import_csv(context: bpy.types.Context, job, path: str) -> StageResult:
    res = StageResult(STAGE)
    arm = _require_armature(res, job)
    if arm is None:
        return res
    spec = load_spec(context)
    with open(path, encoding="utf-8-sig") as f:
        parsed = parse_mapping(f.read(), spec)
    for text in parsed.problems:
        res.warning("identify.csv_problem", text, path)
    by_src = {plan.src or plan.name: plan.name for plan in job.bones}
    by_name = {plan.name: plan.name for plan in job.bones}
    resolved = 0
    with props.programmatic_writes(context):
        for row in parsed.rows:
            bone = by_src.get(row.source_bone) or by_name.get(row.source_bone)
            if bone is None:
                res.warning("identify.csv_unknown_bone", f"映射文件里的骨 {row.source_bone} 不在当前骨架里")
                continue
            plan = job.bones.get(bone)
            if row.action == "map":
                for other in job.slots:  # a bone fills at most one slot
                    if other.bone == bone and other.name != row.slot_id:
                        other.bone, other.origin = "", 'NONE'
                slot = job.slot(row.slot_id)
                slot.bone, slot.origin, slot.reason, slot.confidence = bone, 'user', "映射文件", 1.0
            plan.action, plan.slot_id, plan.origin = row.action, row.slot_id, 'user'
            if row.note:
                plan.reason = row.note
            resolved += 1
    res.info("identify.csv_imported", f"已导入 {resolved} 行映射（标记为手动）", path)
    res.extend(recheck(context, job))
    return res
