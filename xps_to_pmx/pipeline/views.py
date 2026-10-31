"""定位 and 看图 for checkup findings (design doc §16.4–§16.5).

* 定位: show the model posed for the finding's view with its vertices selected (a preview of
  copies; the converted model itself is hidden, never posed), or select the finding's bone when
  it has no view.  「复位」 removes the preview.
* 看图: render a thumbnail of the view into ``<user data>/checkup_images/<SHA-1>/``.  File names
  carry the checkup run, so after 「按修正从头重做」 the image of the previous run is shown as
  「上次」 next to the new one.  Before redoing, findings whose fix is ticked are rendered
  automatically, so their before/after pair exists even if 看图 was not clicked.
"""
from __future__ import annotations

import glob
import hashlib
import os
import re
from typing import Optional

import bpy

from .. import prefs
from ..blender import posetest as bpt
from ..core.checks import posetest
from ..core.result import StageResult
from . import stage_identify

STAGE = "view"
_RUN_RE = re.compile(r"@(\d+)\.png$")


def body_names(context: bpy.types.Context) -> set:
    return {s.name_j for s in stage_identify.load_spec(context).slots if s.name_j}


def image_dir(context: bpy.types.Context, job) -> str:
    return os.path.join(prefs.user_data_dir(context), "checkup_images", job.source_sha1 or job.job_id)


def _slug(key: str) -> str:
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def image_path(context: bpy.types.Context, job, key: str, run: Optional[int] = None) -> str:
    return os.path.join(image_dir(context, job), f"{_slug(key)}@{job.checkup_run if run is None else run}.png")


def earlier_image(context: bpy.types.Context, job, key: str) -> str:
    """The newest image of ``key`` from a checkup before the current one, or ""."""
    best, best_run = "", -1
    for path in glob.glob(os.path.join(image_dir(context, job), f"{_slug(key)}@*.png")):
        m = _RUN_RE.search(path)
        if m and best_run < int(m.group(1)) < job.checkup_run:
            best, best_run = path, int(m.group(1))
    return best


def view_label(prig: posetest.PoseRig, view: dict) -> str:
    if view.get("test"):
        test = posetest.find_test(prig, view["test"])
        return test.label if test is not None else view["test"]
    return f"{view.get('bone', '')} 转 {view.get('angle', 0):.0f}°"


def _finding(job, index: int):
    return job.findings[index] if 0 <= index < len(job.findings) else None


def locate(context: bpy.types.Context, job, index: int) -> StageResult:
    res = StageResult(STAGE)
    item = _finding(job, index)
    view = item.view() if item is not None else {}
    if not view:
        res.error("view.no_view", "这条结果没有可以摆出来的姿势")
        return res
    prig, slices = bpt.job_rig(job, body_names(context))
    label = view_label(prig, view)
    n = bpt.show_preview(context, job, view, prig, slices, label)
    res.info("view.located", f"已摆成「{label}」，选中 {n} 个顶点（看完点「复位」）")
    return res


def reset(context: bpy.types.Context, job) -> StageResult:
    res = StageResult(STAGE)
    if bpt.clear_preview(context, job):
        res.info("view.reset", "已复位，模型回到原来的样子")
    else:
        res.info("view.nothing", "没有在预览的姿势")
    return res


def clear_preview(context: bpy.types.Context, job) -> None:
    if job is not None and bpt.preview_active(job):
        bpt.clear_preview(context, job)


def render_finding(context: bpy.types.Context, job, index: int) -> StageResult:
    res = StageResult(STAGE)
    item = _finding(job, index)
    view = item.view() if item is not None else {}
    if not view:
        res.error("view.no_view", "这条结果没有可以看的图")
        return res
    path = image_path(context, job, item.key)
    if not _render(context, job, view, path, res):
        return res
    item.image_after = path
    item.image_before = earlier_image(context, job, item.key)
    res.info("view.rendered", "已生成看图" + ("（左边是上次）" if item.image_before else ""))
    return res


def _render(context: bpy.types.Context, job, view: dict, path: str, res: StageResult) -> bool:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    prig, slices = bpt.job_rig(job, body_names(context))
    try:
        bpt.render(job, view, prig, slices, path)
    except RuntimeError as exc:  # rendering unavailable (e.g. no GPU context)
        res.error("view.render_failed", f"渲染失败：{exc}")
        return False
    return True


def capture_before(context: bpy.types.Context, job) -> int:
    """Render the findings whose fix is ticked (and that have no image of this run yet); returns the count."""
    done = 0
    for item in job.findings:
        view = item.view()
        if not view or item.state == "fixed" or not item.fix_key:
            continue
        fix = job.fix_item(item.fix_key)
        path = image_path(context, job, item.key)
        if fix is None or not fix.enabled or os.path.isfile(path):
            continue
        if _render(context, job, view, path, StageResult(STAGE)):
            done += 1
    return done
