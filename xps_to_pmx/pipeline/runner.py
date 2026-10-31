"""Whole-pipeline entry points (design doc §15.2): one-click, continue, redo from scratch.

* ``one_click``: ① → remembered fix list → ② ③ ④ ⑧ ⑨.
* ``continue_job``: from the job's current stage to ⑨ (e.g. after 分步重做 stopped at ②).
* ``redo``: delete what the job generated, re-import the same XPS with the same options and fix
  list, and run to ② (分步重做) or to ⑨ (按修正从头重做), comparing with the previous checkup.

They call the same stage functions as the step buttons (hard constraint 1); the batch script
calls ``one_click`` too.  Automatic fixes are applied inside ② (no extra round is needed).
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

import bpy

from .. import props
from ..blender import importer
from ..core import fixes as fx
from ..core.result import StageResult
from . import fixlist, stage_build, stage_checkup, stage_export, stage_identify, stage_import, stage_prepare

STAGE = "run"
OPTIONS = tuple(fx.OPTION_TYPES) + ("export_path",)
STEPS = (("identify", "② 识别"), ("prepare", "③ 预处理"), ("build", "④ 生成骨架"), ("export", "⑧ 导出"),
         ("checkup", "⑨ 体检"))
#: stage reached → index of the next step in STEPS
NEXT = {"": 0, "import": 0, "identify": 1, "prepare": 2, "build": 3, "morphs": 3, "physics": 3, "export": 4,
        "checkup": 5}


def one_click(context: bpy.types.Context, path: str, remember: bool = True, fixes_file: str = ""
              ) -> Tuple[StageResult, Optional[object]]:
    """``remember``: use the fix list remembered for this XPS; ``fixes_file``: use this fix file instead."""
    res = StageResult(STAGE)
    imp, job = stage_import.run(context, path)
    _step(res, "① 导入", imp)
    if not imp.ok or job is None:
        res.error("run.import_failed", next((m.text for m in imp.messages if m.level == "error"), "导入失败"))
        return res, None
    if fixes_file:
        job.source_sha1 = fixlist.sha1_of(job.source_path)
        loaded = fixlist.load_file(context, job, fixes_file)
    elif remember:
        loaded = fixlist.load_remembered(context, job)
    else:
        loaded = StageResult(fixlist.STAGE)
    res.messages.extend(m for m in loaded.messages if m.level != "info" or m.code == "fixes.loaded")
    _run_to_end(context, job, res, previous={})
    return res, job


def continue_job(context: bpy.types.Context, job) -> StageResult:
    res = StageResult(STAGE)
    if job is None:
        res.error("run.no_job", "没有活动任务")
        return res
    if job.findings:
        previous = stage_checkup.snapshot_findings(job)
    else:  # 分步重做 left the last checkup here
        previous = json.loads(job.previous_findings_json or "{}")
    _run_to_end(context, job, res, previous)
    return res


def redo(context: bpy.types.Context, job, stop_after: str = "checkup") -> Tuple[StageResult, Optional[object]]:
    """Re-import and run again with the job's options and fix list; ``stop_after`` is "identify" or "checkup"."""
    res = StageResult(STAGE)
    if job is None:
        res.error("run.no_job", "没有活动任务")
        return res, None
    path = job.source_path
    options = {name: getattr(job, name) for name in OPTIONS}
    fixes = job.fix_list()
    previous = stage_checkup.snapshot_findings(job)
    sha1 = job.source_sha1
    remove_job(context, job)
    imp, new = stage_import.run(context, path)
    _step(res, "① 导入", imp)
    if not imp.ok or new is None:
        res.error("run.reimport_failed", "重新导入失败，任务未恢复")
        return res, None
    with props.programmatic_writes(context):
        for name, value in options.items():
            setattr(new, name, value)
        new.set_fix_list(fixes)
        new.source_sha1 = sha1
        new.previous_findings_json = json.dumps(previous, ensure_ascii=False)
    if stop_after == "identify":
        r = stage_identify.run(context, new)
        _step(res, "② 识别", r)
        res.info("run.at_identify", "已从头重做到 ②：展开「分步模式」改映射，改完点「继续」"
                 + ("" if r.ok else f"（② 还有 {r.count('error')} 个错误）"))
        return res, new
    _run_to_end(context, new, res, previous)
    return res, new


def _run_to_end(context, job, res: StageResult, previous: Dict[str, Dict]) -> None:
    for name, label in STEPS[NEXT.get(job.stage, 0):]:
        if name == "identify":
            r = stage_identify.run(context, job)
        elif name == "prepare":
            r = stage_prepare.run(context, job)
        elif name == "build":
            r = stage_build.run(context, job)
        elif name == "export":
            r = stage_export.run(context, job, "")
        else:
            r = stage_checkup.run(context, job, previous)
        _step(res, label, r)
        if not r.ok:
            errors = [m.text for m in r.messages if m.level == "error"]
            hint = "在「分步模式」里修改后点「继续」" if name == "identify" else "详见报告"
            res.error("run.stage_failed", f"{label} 有 {len(errors)} 个错误：{errors[0] if errors else ''}（{hint}）")
            return
        if name == "export":
            saved = fixlist.save(context, job, r.data.get("path", ""))
            res.messages.extend(m for m in saved.messages if m.level != "info")
            res.data["fix_files"] = saved.data.get("paths", [])
    job.fixes_pending = False
    done = next((m.text for m in job.reports if m.code == "checkup.done"), "完成")
    res.info("run.done", done)


def _step(res: StageResult, label: str, r: StageResult) -> None:
    steps: List[Dict] = res.data.setdefault("steps", [])
    steps.append({"label": label, "ok": r.ok,
                  "errors": [m.text for m in r.messages if m.level == "error"],
                  "warnings": [m.text for m in r.messages if m.level == "warning"]})


def remove_job(context: bpy.types.Context, job) -> None:
    """Delete everything a job generated and the job itself."""
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
