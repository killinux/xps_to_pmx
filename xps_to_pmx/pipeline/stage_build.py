"""Stage ④: build the MMD skeleton and adopt the model into mmd_tools (design doc §4, §8).

analyse (snapshot) → plan (core.rig.skeleton) → execute (blender.skeleton_apply,
blender.mmdtools_bridge) → self-check (read the Blender data back against the plan).
Not re-runnable on its own output: bones are renamed and generated, so a second
build needs "重来" (re-import with the same mapping and options).
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

import bpy
import numpy as np

from ..blender import mmdtools_bridge as bridge
from ..blender import skeleton_apply, snapshot
from ..blender.importer import PROP_MANIFEST
from ..core import mmd_material
from ..core.checks.lower_body import check_lower_body, lower_body_metrics
from ..core.result import StageResult
from ..core.rig.skeleton import BuildOptions, ExtraBone, SkeletonPlan, plan_skeleton
from . import stage_identify

STAGE = "build"
DONE_STAGES = ("build", "morphs", "physics", "check", "export")


def run(context: bpy.types.Context, job) -> StageResult:
    res = StageResult(STAGE)
    arm = job.armature if job is not None else None
    if arm is None or arm.name not in bpy.data.objects:
        res.error("build.no_armature", "当前任务没有骨架（先 ① 导入）")
        return res
    if job.stage in DONE_STAGES:
        res.error("build.already_built", "这个模型已经生成过 MMD 骨架；要按新设置重新生成，请用『重来』")
        return res
    if job.stage != "prepare":
        res.error("build.not_prepared", "先完成 ③ 预处理（缩放、A 姿势）")
        return res
    try:
        bridge.ensure_mmd_tools()
        ver = bridge.version()
    except bridge.MMDToolsError as exc:
        res.error("build.mmd_tools", str(exc))
        job.record(res)
        return res
    if ver not in bridge.SUPPORTED:
        res.warning("build.mmd_tools_version", f"mmd_tools 版本是 {ver}，本插件按 1.0.2 编写，导出前请仔细检查")

    spec = stage_identify.load_spec(context)
    rig = snapshot.rig_from_blender(arm)
    if rig.skin is None:
        res.error("build.no_skin", "骨架没有蒙皮网格")
        job.record(res)
        return res
    slot_bones = {s.name: s.bone for s in job.slots if s.bone}
    extra = {p.name: ExtraBone(p.action, p.slot_id, p.category or "other") for p in job.bones
             if p.action in ("keep", "merge")}
    options = BuildOptions(tier2=job.gen_tier2, tier3=job.gen_tier3, twist_mode=job.twist_mode,
                           ik_preset=job.ik_preset)
    plan = plan_skeleton(rig, spec, slot_bones, extra, job.lower_body(), options)
    res.messages.extend(plan.messages)
    if not plan.ok:
        res.error("build.plan_failed", "骨架计划有错误，未修改场景")
        job.record(res)
        return res

    res.data["lower_body"] = _lower_body_checks(res, plan, rig.skin.positions)
    bone_stats = skeleton_apply.apply_bones(context, arm, plan)
    weight_stats = skeleton_apply.apply_weights(plan, rig.skin.mesh_slices)
    meshes = snapshot.skinned_meshes(arm)
    collection = job.collection
    root = bridge.create_model(context, arm, job.model_name, job.model_name, collection)
    problems = bridge.setup_bones(arm, plan)
    bridge.build_bone_order(arm, plan, collection)
    problems += bridge.setup_ik(arm, plan)
    bridge.apply_axes_and_grants(context, arm)
    frames = bridge.setup_display_frames(root, arm, plan)
    mat_notes = _materials(meshes)
    order = _draw_order(meshes, job.model_name)
    bridge.set_model_info(root, job.model_name, job.model_name,
                          f"Converted from XPS by xps_to_pmx\n{os.path.basename(job.source_path)}")
    for p in problems:
        res.error("build.mmd_setup", p)
    for n in mat_notes:
        res.warning("build.material", n)

    _verify(res, arm, root, plan, meshes)
    res.data.update({
        "bones": len(plan.bones), "renamed": bone_stats["renamed"], "created": bone_stats["created"],
        "deleted": bone_stats["deleted"], "weights_rewritten": weight_stats["vertices"],
        "generated": plan.stats.get("generated", []), "frames": frames, "draw_order": order,
        "plan": {k: v for k, v in plan.stats.items() if k not in ("generated",)},
        "root": root.name,
    })
    if res.ok:
        res.info("build.done", f"MMD 骨架完成：{len(plan.bones)} 根骨（生成 {bone_stats['created']}，"
                               f"改名 {bone_stats['renamed']}），重写 {weight_stats['vertices']} 个顶点的权重")
    job.record(res)
    return res


def _lower_body_checks(res: StageResult, plan: SkeletonPlan, positions) -> Dict:
    by_slot = plan.by_slot()
    idx = plan.index()

    def column(slot_ids) -> np.ndarray:
        ids = [idx[by_slot[s].name] for s in slot_ids if s in by_slot]
        return np.where(np.isin(plan.skin_bones, ids), plan.skin_weights, 0.0).sum(axis=1)

    lb = by_slot.get("lower_body_bone")
    if lb is None or plan.skin_bones is None:
        return {}
    upper = column([s for s in by_slot if s.startswith("upper_body")])
    legs = column(["left_thigh_bone", "right_thigh_bone", "left_leg_d_bone", "right_leg_d_bone"])
    thigh_z = float(np.mean([by_slot[f"{s}_thigh_bone"].head[2] for s in ("left", "right")]))
    metrics = lower_body_metrics(np.asarray(positions, float), column(["lower_body_bone"]), upper, legs, thigh_z,
                                 float(by_slot["upper_body_bone"].head[2]),
                                 abs(float(by_slot["left_thigh_bone"].head[0])))
    for item in check_lower_body(metrics, lb.name):
        res.add(item.level, item.code, item.text, item.bone)
    return metrics


def _materials(meshes) -> List[str]:
    notes: List[str] = []
    seen = set()
    for obj in meshes:
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None or mat.name in seen:
                continue
            seen.add(mat.name)
            manifest = _manifest(mat)
            notes += bridge.setup_material(mat, mmd_material.material_name(manifest, mat.name),
                                           mmd_material.material_memo(manifest), "xps_diffuse", "xps_bump")
    return notes


def _manifest(mat) -> Dict:
    raw = mat.get(PROP_MANIFEST)
    if raw is None:
        return {}
    try:
        return raw.to_dict()
    except AttributeError:
        return dict(raw)


def _draw_order(meshes, model_name: str) -> List[str]:
    """Rename mesh objects so mmd_tools' name sort gives opaque first, alpha render groups last (design doc §9)."""
    items = []
    for obj in meshes:
        mat = obj.material_slots[0].material if obj.material_slots else None
        manifest = _manifest(mat) if mat is not None else {}
        manifest.setdefault("mesh_index", obj.get("xps2pmx_mesh_index", 0))
        items.append((obj.name, manifest))
    order = mmd_material.draw_order(items)
    width = max(3, len(str(len(order))))
    temp = {}
    for k, name in enumerate(order):
        obj = bpy.data.objects[name]
        temp[k] = obj
        obj.name = f"__x2p_mesh_{k:0{width}d}"
    final = []
    for k, obj in temp.items():
        manifest = dict(items)[order[k]]
        base = manifest.get("base_name") or order[k]
        obj.name = f"{model_name}_{k:0{width}d}_{base}"[:63]
        final.append(obj.name)
    return final


def _verify(res: StageResult, arm, root, plan: SkeletonPlan, meshes) -> None:
    bones = arm.data.bones
    pbs = arm.pose.bones
    real = [b for b in bones if not pbs[b.name].is_mmd_shadow_bone]
    planned = {b.name: b for b in plan.bones}
    missing = [n for n in planned if n not in bones]
    extra = [b.name for b in real if b.name not in planned]
    if missing or extra:
        res.error("build.verify_bones", f"骨架与计划不符：缺 {missing[:5]}，多 {extra[:5]}")
    for name, b in planned.items():
        if name not in bones:
            continue
        parent = bones[name].parent.name if bones[name].parent else ""
        if parent != b.parent:
            res.error("build.verify_parent", f"{name} 的父骨是 {parent or '无'}，计划为 {b.parent or '无'}", name)
        if b.grant_parent and pbs[name].mmd_bone.additional_transform_bone != b.grant_parent:
            res.error("build.verify_grant", f"{name} 的付与源读回为 {pbs[name].mmd_bone.additional_transform_bone!r}",
                      name)
        if pbs[name].mmd_bone.name_j != name:
            res.error("build.verify_name", f"{name} 的 mmd 名为 {pbs[name].mmd_bone.name_j!r}", name)
    order_obj = next((o for o in arm.children if bridge.BONE_ORDER_MODIFIER in o.modifiers), None)
    if order_obj is None:
        res.error("build.verify_order", "没有骨序网格")
    elif [vg.name for vg in order_obj.vertex_groups] != [b.name for b in plan.bones]:
        res.error("build.verify_order", "骨序网格的顶点组顺序与计划不符")
    carriers = [o for o in bpy.data.objects if o.type == 'MESH' and bridge.BONE_ORDER_MODIFIER in o.modifiers
                and o.parent == arm]
    if len(carriers) != 1:
        res.error("build.verify_order", f"带 {bridge.BONE_ORDER_MODIFIER} 修改器的网格有 {len(carriers)} 个")
    if bridge.find_root(arm) != root:
        res.error("build.verify_root", "骨架不在 mmd_tools 模型里")
    if not np.allclose(np.array(root.matrix_world), np.eye(4), atol=1e-6):
        res.warning("build.verify_root_matrix", "MMD 根对象有变换，导出时会被烘焙进 PMX")
    for b in plan.bones:
        if b.ik is None:
            continue
        chain0 = pbs[b.ik.links[0].bone]
        if not any(c.type == 'IK' and c.subtarget == b.name and not c.mute for c in chain0.constraints):
            res.error("build.verify_ik", f"{b.name} 的 IK 约束没有建在 {chain0.name} 上", b.name)
    bone_names = {b.name for b in plan.bones}
    over, stray = 0, set()
    for obj in meshes:
        groups = {vg.index: vg.name for vg in obj.vertex_groups}
        stray |= {n for n in groups.values() if n not in bone_names and not n.startswith("mmd_")}
        verts = obj.data.vertices
        for k in range(0, len(verts), 97):
            v = verts[k]
            if sum(1 for g in v.groups if g.weight > 0) > 4:
                over += 1
    if stray:
        res.error("build.verify_groups", f"网格上有不对应任何骨的顶点组：{sorted(stray)[:5]}")
    if over:
        res.error("build.verify_influences", f"抽样发现 {over} 个顶点超过 4 个影响骨")
    rewired = [m.name for o in meshes for m in (s.material for s in o.material_slots)
               if m is not None and bridge.material_output_is_mmd_shader(m)]
    if rewired:
        res.warning("build.material_rewired", f"{len(rewired)} 个材质的输出被改接到 mmd_shader：{rewired[:3]}")
