"""Stage ⑧: export the PMX (×12.5, REST pose, textures copied), read it back and check it (design doc §4, §12.1).

Writes ``<name>.pmx``, ``<name>.report.json`` (all stage reports + read-back
checks) next to it.  Expectations for the read-back checks come from the
Blender model and the bone spec, never from the exported file.
"""
from __future__ import annotations

import json
import math
import os
import re
from typing import Dict, List

import bpy

from .. import prefs, props
from ..blender import mmdtools_bridge as bridge
from ..core.checks.export import check_pmx
from ..core.pose import EXPORT_SCALE
from ..core.result import StageResult
from . import stage_identify

STAGE = "export"
DEFAULT_ROOT = r"D:\xps_exports"
READY_STAGES = props.BUILT_STAGES
_BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(name: str) -> str:
    cleaned = _BAD_CHARS.sub("_", name).strip().rstrip(".")
    return cleaned or "model"


def default_path(context: bpy.types.Context, job) -> str:
    root = prefs.export_root(context, DEFAULT_ROOT)
    name = safe_name(job.model_name)
    return os.path.join(root, name, f"{name}.pmx")


def run(context: bpy.types.Context, job, filepath: str = "") -> StageResult:
    res = StageResult(STAGE)
    arm = job.armature if job is not None else None
    if arm is None or arm.name not in bpy.data.objects:
        res.error("export.no_armature", "当前任务没有骨架")
        return res
    if job.stage not in READY_STAGES:
        res.error("export.not_built", "先完成 ④ 生成 MMD 骨架")
        return res
    try:
        root = bridge.find_root(arm)
    except bridge.MMDToolsError as exc:
        res.error("export.mmd_tools", str(exc))
        job.record(res)
        return res
    if root is None:
        res.error("export.no_root", "骨架不在 mmd_tools 模型里（④ 没有成功）")
        job.record(res)
        return res
    path = bpy.path.abspath(filepath or job.export_path) if (filepath or job.export_path) else default_path(context, job)
    if not path.lower().endswith(".pmx"):
        path = os.path.join(path, f"{safe_name(job.model_name)}.pmx")
    expected = expectations(context, arm, job)
    try:
        bridge.export_pmx(context, root, path, scale=EXPORT_SCALE, copy_textures=True)
    except Exception as exc:  # noqa: BLE001 - the user must see any exporter failure
        res.error("export.failed", f"mmd_tools 导出失败：{exc}")
        job.record(res)
        return res
    summary = bridge.read_pmx(path)
    items = check_pmx(summary, expected, path)
    for it in items:
        res.add(it.level, it.code, it.text, it.bone)
    res.data.update({"path": path, "bones": len(summary["bones"]), "vertices": summary["vertices"],
                     "faces": summary["faces"], "materials": len(summary["materials"]),
                     "textures": len(summary["textures"]), "frames": len(summary["frames"]),
                     "min_y": summary["min_y"], "max_y": summary["max_y"],
                     "height_pmx": summary["max_y"] - summary["min_y"]})
    errors = sum(1 for it in items if it.level == "error")
    warnings = sum(1 for it in items if it.level == "warning")
    if not errors:
        res.info("export.done", f"已导出 {path}（{len(summary['bones'])} 骨、{summary['vertices']} 顶点、"
                                f"{len(summary['materials'])} 材质）；读回检查 {warnings} 条警告")
    job.last_export = path
    job.record(res)
    _write_report(path, job, res, summary)
    return res


def expectations(context: bpy.types.Context, arm: bpy.types.Object, job) -> Dict:
    """What the PMX must contain, read from the Blender model (bone order mesh, constraints, mmd_bone)."""
    order_obj = next((o for o in arm.children if bridge.BONE_ORDER_MODIFIER in o.modifiers), None)
    pbs = arm.pose.bones
    names = [vg.name for vg in order_obj.vertex_groups] if order_obj is not None else \
        [b.name for b in arm.data.bones if not pbs[b.name].is_mmd_shadow_bone]
    bones: List[Dict] = []
    for name in names:
        pb = pbs[name]
        mb = pb.mmd_bone
        entry = {"name": mb.name_j or name, "parent": "", "transform_order": mb.transform_order,
                 "visible": not pb.bone.hide, "controllable": mb.is_controllable,
                 "movable": not all(pb.lock_location)}
        parent = pb.parent
        while parent is not None and parent.is_mmd_shadow_bone:
            parent = parent.parent
        entry["parent"] = (parent.mmd_bone.name_j or parent.name) if parent is not None else ""
        if mb.has_additional_rotation or mb.has_additional_location:
            target = mb.additional_transform_bone
            entry["grant"] = [pbs[target].mmd_bone.name_j or target if target in pbs else "",
                              float(mb.additional_transform_influence)]
        bones.append(entry)
    by_name = {e["name"]: e for e in bones}
    spec = stage_identify.load_spec(context)
    for pb in pbs:
        for c in pb.constraints:
            if c.type != 'IK' or c.mute or c.subtarget not in pbs:
                continue
            ik_bone = pbs[c.subtarget]
            chain = []
            cur = pb
            for _ in range(c.chain_count):
                chain.append(cur)
                cur = cur.parent
            target = next((ch for ch in pb.children
                           if ch.constraints.get("mmd_ik_target_override") is not None), None)
            ik_name = ik_bone.mmd_bone.name_j or ik_bone.name
            ik_spec = spec.by_name_j.get(ik_name)
            limits = [None] * len(chain)
            if ik_spec is not None and len(ik_spec.ik_links) == len(chain):
                limits = [[[math.radians(l.limit_min_deg), 0.0, 0.0], [math.radians(l.limit_max_deg), 0.0, 0.0]]
                          if l.limited else None for l in ik_spec.ik_links]
            entry = by_name.get(ik_name)
            if entry is not None:
                entry["ik"] = {"target": (target.mmd_bone.name_j or target.name) if target else "",
                               "links": [l.mmd_bone.name_j or l.name for l in chain],
                               "loop": int(c.iterations), "unit": float(pb.mmd_bone.ik_rotation_constraint),
                               "limits": limits}
    no_weight, need_weight = [], []
    for e in bones:
        s = spec.by_name_j.get(e["name"])
        if s is None:
            continue
        if not s.deform:
            no_weight.append(e["name"])
    # FK leg bones carry nothing when the D bones exist (design doc §8.2)
    for s in spec:
        if s.recipe == "d_bone" and s.name_j in by_name:
            src = spec.get(s.recipe_args.get("source", ""))
            if src is not None:
                no_weight.append(src.name_j)
                need_weight.append(s.name_j)
    heights = {}
    if job.scale_mode == 'SHOULDER':
        for sid in ("left_upper_arm_bone", "right_upper_arm_bone"):
            heights[spec[sid].name_j] = float(job.shoulder_target)
    return {"bones": bones, "no_weight": no_weight, "need_weight": need_weight, "heights": heights,
            "vertices": True, "ground_tolerance": 0.05}


def _write_report(path: str, job, res: StageResult, summary: Dict) -> None:
    report = {
        "model": job.model_name, "source": job.source_path, "pmx": path,
        "stages": job.summary(),
        "reports": [{"stage": r.stage, "level": r.level, "code": r.code, "text": r.text, "target": r.target}
                    for r in job.reports],
        "readback": {k: v for k, v in summary.items() if k not in ("bones", "weight_counts")},
        "bones": [{"name": b["name"], "name_e": b["name_e"], "parent": b["parent"],
                   "grant": b["grant"], "ik": b["ik"]} for b in summary["bones"]],
    }
    base = os.path.splitext(path)[0]
    with open(base + ".report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
