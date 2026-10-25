"""『重来』: delete what a job generated, re-import the same XPS and re-run up to the stage it had reached.

Kept: every option of the job and the user's own decisions (slots and bone
dispositions marked 'user').  Everything automatic is recomputed, so fixes to
identification or to the skeleton rules apply to the redone model too.
Export is not repeated automatically.
"""
from __future__ import annotations

from typing import Dict, Tuple

import bpy

from .. import props
from ..blender import importer
from ..core.result import StageResult
from . import stage_build, stage_identify, stage_import, stage_prepare

STAGE = "redo"
OPTIONS = ("scale_mode", "shoulder_target", "apose_preset", "apose_upper_deg", "apose_fore_extra_deg",
           "level_shoulders", "gen_tier2", "gen_tier3", "twist_mode", "ik_preset", "export_path")
ORDER = ("import", "identify", "prepare", "build")


def run(context: bpy.types.Context, job) -> Tuple[StageResult, object]:
    res = StageResult(STAGE)
    if job is None:
        res.error("redo.no_job", "没有活动任务")
        return res, None
    path = job.source_path
    reached = job.stage if job.stage in ORDER else ("build" if job.stage else "import")
    options = {name: getattr(job, name) for name in OPTIONS}
    user_slots: Dict[str, str] = {s.name: s.bone for s in job.slots if s.origin == 'user'}
    user_plans: Dict[str, Tuple[str, str]] = {p.name: (p.action, p.slot_id) for p in job.bones if p.origin == 'user'}

    _remove_job(context, job)

    imp, new = stage_import.run(context, path)
    res.messages.extend(imp.messages)
    if not imp.ok or new is None:
        res.error("redo.import_failed", "重新导入失败，任务未恢复")
        return res, None
    with props.programmatic_writes(context):
        for name, value in options.items():
            setattr(new, name, value)
        for slot_id, bone in user_slots.items():
            item = new.slots.add()
            item.name, item.bone, item.origin = slot_id, bone, 'user'
    steps = []
    if ORDER.index(reached) >= ORDER.index("identify"):
        r = stage_identify.run(context, new, keep_user=True)
        if r.ok and user_plans:
            with props.programmatic_writes(context):
                for name, (action, slot_id) in user_plans.items():
                    plan = new.bones.get(name)
                    if plan is not None:
                        plan.action, plan.slot_id, plan.origin = action, slot_id, 'user'
            r = stage_identify.recheck(context, new)
        steps.append(("② 识别", r))
    if steps and steps[-1][1].ok and ORDER.index(reached) >= ORDER.index("prepare"):
        steps.append(("③ 预处理", stage_prepare.run(context, new)))
    if steps and steps[-1][1].ok and ORDER.index(reached) >= ORDER.index("build"):
        steps.append(("④ 生成骨架", stage_build.run(context, new)))
    failed = next(((label, r) for label, r in steps if not r.ok), None)
    if failed:
        res.error("redo.stage_failed", f"重来时 {failed[0]} 出错：" +
                  next((m.text for m in failed[1].messages if m.level == 'error'), ""))
    else:
        res.info("redo.done", f"已重来到 {props.STAGE_LABELS.get(reached, reached)}"
                              f"（保留 {len(user_slots)} 个手改槽位、{len(user_plans)} 个手改处置）")
    return res, new


def _remove_job(context: bpy.types.Context, job) -> None:
    st = props.state(context)
    if context.view_layer.objects.active is not None and context.view_layer.objects.active.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    coll = job.collection
    roots = [o for o in (coll.all_objects if coll else []) if o.type == 'EMPTY']
    for root in roots:
        text = bpy.data.texts.get(f"{root.name}_comment")
        if text is not None:
            bpy.data.texts.remove(text)
    if coll is not None:
        importer.remove_collection_objects(coll)
    for i, j in enumerate(st.jobs):
        if j.job_id == job.job_id:
            st.jobs.remove(i)
            break
    st.active_job_index = min(st.active_job_index, len(st.jobs) - 1)
