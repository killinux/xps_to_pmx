"""Stage ②: identify the skeleton, store the mapping in the job, run the mapping checks.

The fix list (design doc §15.3) is applied here: ``split_side`` fixes first (they change
weights), slot fixes as fixed slots, bone fixes after identification.  The cause checks
(§15.5) then run on the source skeleton; fixes they mark automatic are added to the fix
list and applied on the spot, so no redo is needed for them.

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
from ..core import fixes as fx
from ..core.checks import cause
from ..core.checks.mapping import CheckItem, check_mapping
from ..core.fixes import Fix
from ..core.mapping_io import MappingRow, parse_mapping, write_mapping
from ..core.result import StageResult
from ..core.rig.classify import Disposition
from ..core.rig.identify import Identification, SlotMatch, identify
from ..core.rig.lower_body import LowerBodyDiagnosis
from ..core.rig.rigdata import RigData
from ..core.rig.topology import TopologyResult
from ..core.spec import BoneSpec, SpecError, load_bone_spec
from ..core.spec.bone_slots import DEFAULT_PATH
from . import fixlist

STAGE = "identify"
USER_SPEC_NAME = "bone_slots.csv"


def load_spec(context: bpy.types.Context) -> BoneSpec:
    """Default table, overridden by ``<user data dir>/bone_slots.csv`` when present."""
    user = os.path.join(prefs.user_data_dir(context), USER_SPEC_NAME)
    return load_bone_spec(DEFAULT_PATH, [user])


BUILT_STAGES = props.BUILT_STAGES
#: Cause-check codes; after ③ the source skeleton is gone, so re-checks keep the last results of these.
CAUSE_CODES = ("mapping.merge_segment", "mapping.duplicate_name", "mapping.auto_fixed")
PRE_PREPARE = ("", "import", "identify")


def _require_armature(res: StageResult, job) -> Optional[bpy.types.Object]:
    arm = job.armature if job is not None else None
    if arm is None or arm.type != 'ARMATURE' or arm.name not in bpy.data.objects:
        res.error("identify.no_armature", "当前任务没有骨架（先 ① 导入 XPS）")
        return None
    if job.stage in BUILT_STAGES:
        res.error("identify.already_built", "MMD 骨架已生成，骨名已改成日文；要改映射请用「分步重做」")
        return None
    return arm


def run(context: bpy.types.Context, job, keep_user: bool = True) -> StageResult:
    """Identify; ``keep_user=False`` first drops the user's slot / bone fixes (「清除手动修改」)."""
    res = StageResult(STAGE)
    arm = _require_armature(res, job)
    if arm is None:
        return res
    try:
        spec = load_spec(context)
    except SpecError as exc:
        res.error("identify.spec_invalid", f"骨骼规格表有错误：{exc.problems[0]}（共 {len(exc.problems)} 处）")
        return res
    if not keep_user:
        _drop_user_mapping_fixes(context, job)
    res.extend(fixlist.apply_splits(context, job))      # they change weights: before anything looks at them
    rig = snapshot.rig_from_blender(arm)
    fixes = job.fix_list()
    fixed: Dict[str, int] = {}
    for slot_id, bone in fx.fixed_slots(fixes).items():
        if not bone:
            fixed[slot_id] = -1                           # explicitly left empty → generated
        elif bone in rig.by_name:
            fixed[slot_id] = rig.by_name[bone]
        else:
            res.warning("identify.fix_stale", f"修正单：槽位 {slot_id} 指定的骨 {bone} 不在骨架里，没有套用", bone)
    for fix in fx.bone_fixes(fixes).values():             # "map" in the bone list = choosing a slot's bone
        if fix.action == "map" and fix.slot_id and fix.slot_id not in fixed and fix.bone in rig.by_name:
            fixed[fix.slot_id] = rig.by_name[fix.bone]
    ident = identify(rig, spec, fixed=fixed)
    apply_bone_fixes(rig, ident, [f for f in fx.bone_fixes(fixes).values() if f.action != "map"], res)
    cause_items = _cause_checks(context, job, spec, rig, ident, auto=True)
    _store(context, job, spec, rig, ident)
    items = check_mapping(rig, spec, ident) + cause_items
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
    if job.stage in PRE_PREPARE:
        cause_items = _cause_checks(context, job, spec, rig, ident, auto=False)
    else:
        cause_items = [_item_from_report(c) for c in job.checks if c.code in CAUSE_CODES]
    items = check_mapping(rig, spec, ident) + cause_items
    _store_checks(context, job, items)
    _fill_result(res, spec, ident, items)
    props.state(context).mapping_dirty = False
    job.record(res)
    return res


def apply_bone_fixes(rig: RigData, ident: Identification, fixes, res: StageResult) -> None:
    """Set the dispositions the fix list asks for (merge targets, keep / delete, categories)."""
    for fix in fixes:
        i = rig.by_name.get(fix.bone)
        d = ident.bones.get(i) if i is not None else None
        if d is None:
            res.warning("identify.fix_stale", f"修正单：骨 {fix.bone} 不在骨架里，没有套用", fix.bone)
            continue
        if d.action == "map":
            res.warning("identify.fix_conflict",
                        f"修正单要求 {fix.bone} {fix.action}，但它是槽位主骨；要换主骨请改槽位", fix.bone)
            continue
        old = ident.slots.get(d.slot_id) if d.action == "merge" else None
        if old is not None and i in old.merges:
            old.merges.remove(i)
        d.action = fix.action
        d.slot_id = fix.slot_id if fix.action in ("map", "merge") else ""
        if fix.category:
            d.category = fix.category
        d.origin = "checkup" if fix.origin == "checkup" else "user"
        d.reason = f"修正单：{fix.note}" if fix.note else "修正单"
        if fix.action == "merge" and fix.slot_id in ident.slots:
            ident.slots[fix.slot_id].merges.append(i)


def _cause_checks(context, job, spec: BoneSpec, rig: RigData, ident: Identification, auto: bool
                  ) -> List[CheckItem]:
    """Merge-segment and duplicate-name checks; automatic fixes go into the fix list and apply now."""
    fixes = job.fix_list()
    known = {f.key for f in fixes}              # never re-add a fix the user unticked or decided otherwise
    analysis = cause.merge_analysis(rig, ident.slot_bones(), ident.bones)
    items: List[CheckItem] = []
    applied: List[Fix] = []
    for it in cause.check_merge_segments(rig, spec, analysis, fx.user_decided(fixes)):
        if auto and it.fix is not None and it.fix.auto and it.fix.key not in known:
            applied.append(it.fix)
        else:
            items.append(it)
    if applied:
        with props.programmatic_writes(context):
            for fix in applied:
                job.upsert_fix(fix)
        apply_bone_fixes(rig, ident, applied, StageResult(STAGE))
        analysis = cause.merge_analysis(rig, ident.slot_bones(), ident.bones)
    items += [cause.auto_fixed_item(f, spec) for f in job.fix_list() if f.auto and f.enabled and f.kind == "bone"]
    pairs = cause.find_duplicates(rig)
    items += cause.check_duplicates(rig, pairs)
    job.merge_analysis_json = json.dumps([a.as_dict(rig) for a in analysis], ensure_ascii=False)
    job.duplicates_json = json.dumps([p.as_dict(rig) for p in pairs], ensure_ascii=False)
    return items


def _drop_user_mapping_fixes(context, job) -> None:
    keep = [f for f in job.fix_list() if not (f.kind in ("slot", "bone") and f.origin in ("user", "csv", "file"))]
    with props.programmatic_writes(context):
        job.set_fix_list(keep)


def fix_from_json(text: str) -> Optional[Fix]:
    if not text:
        return None
    try:
        return Fix(**json.loads(text))
    except (TypeError, ValueError):
        return None


def _item_from_report(c) -> CheckItem:
    return CheckItem(c.level, c.code, c.text, c.slot_id, c.target, c.detail, fix_from_json(c.fix_json))

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
        c.detail = it.detail
        c.fix_json = json.dumps(it.fix.to_dict(), ensure_ascii=False) if it.fix is not None else ""


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
    """Apply a mapping CSV; rows that differ from the current mapping go into the fix list (origin csv)."""
    res = StageResult(STAGE)
    arm = _require_armature(res, job)
    if arm is None:
        return res
    if not job.bones:
        res.error("identify.csv_before_identify", "先点「② 自动识别」，再导入映射 CSV")
        return res
    spec = load_spec(context)
    with open(path, encoding="utf-8-sig") as f:
        parsed = parse_mapping(f.read(), spec)
    for text in parsed.problems:
        res.warning("identify.csv_problem", text, path)
    by_src = {plan.src or plan.name: plan.name for plan in job.bones}
    by_name = {plan.name: plan.name for plan in job.bones}
    resolved = changed = 0
    with props.programmatic_writes(context):
        for row in parsed.rows:
            bone = by_src.get(row.source_bone) or by_name.get(row.source_bone)
            if bone is None:
                res.warning("identify.csv_unknown_bone", f"映射文件里的骨 {row.source_bone} 不在当前骨架里")
                continue
            plan = job.bones.get(bone)
            resolved += 1
            if row.action == "map":
                slot = job.slot(row.slot_id)
                if slot is None or slot.bone == bone:
                    continue
                for other in job.slots:  # a bone fills at most one slot
                    if other.bone == bone and other.name != row.slot_id:
                        other.bone, other.origin = "", 'NONE'
                slot.bone, slot.origin, slot.reason, slot.confidence = bone, 'user', "映射文件", 1.0
                job.upsert_fix(Fix("slot", slot_id=row.slot_id, bone=bone, src=plan.src, origin="csv",
                                   note="映射 CSV"))
                changed += 1
                continue
            target = row.slot_id if row.action in ("map", "merge") else ""
            if plan.action == row.action and (plan.slot_id == target or not target):
                continue
            plan.action, plan.slot_id, plan.origin = row.action, target, 'user'
            if row.note:
                plan.reason = row.note
            job.upsert_fix(Fix("bone", bone=bone, src=plan.src, action=row.action, slot_id=target, origin="csv",
                               note=row.note[:80]))
            changed += 1
    res.info("identify.csv_imported", f"已导入 {resolved} 行映射，其中 {changed} 行与当前结果不同，已记入修正单", path)
    res.extend(recheck(context, job))
    return res

