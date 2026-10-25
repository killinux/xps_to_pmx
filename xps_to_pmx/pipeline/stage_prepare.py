"""Stage ③: apply the bone dispositions, fix facing, scale and ground, T→A arms, level shoulders.

Re-runnable: merged / deleted bones are gone after the first run, arms already
at the target angle are left alone, and the shoulder normalisation lands on a
factor of 1.0 the second time.
"""
from __future__ import annotations

import math
from typing import Dict, List

import bpy
import numpy as np

from .. import props
from ..blender import rigedit, snapshot
from ..core.pose import (EXPORT_SCALE, FLIP_180, distortion, down_angle, edge_lengths, forward_angle,
                         plan_arm_pose, plan_scale)
from ..core.result import StageResult

STAGE = "prepare"
ANGLE_TOLERANCE = 0.5
FOOT_SLOTS = ("left_ankle_bone", "right_ankle_bone", "left_toe_bone", "right_toe_bone")
ARM_SLOTS = {side: (f"{side}_upper_arm_bone", f"{side}_lower_arm_bone", f"{side}_hand_bone")
             for side in ("left", "right")}


def run(context: bpy.types.Context, job) -> StageResult:
    res = StageResult(STAGE)
    arm = job.armature if job is not None else None
    if arm is None or arm.name not in bpy.data.objects:
        res.error("prepare.no_armature", "当前任务没有骨架（先 ① 导入）")
        return res
    if job.stage in ("build", "morphs", "physics", "check", "export"):
        res.error("prepare.already_built", "MMD 骨架已生成；要重新预处理请先『重来』")
        return res
    if not job.slots:
        res.error("prepare.no_mapping", "还没有映射（先 ② 自动识别）")
        return res
    blocking = [c.text for c in job.checks if c.level == 'error']
    if blocking:
        res.error("prepare.mapping_errors", f"映射还有 {len(blocking)} 个错误，先在 ② 修正：{blocking[0]}")
        return res
    slot_bone = {s.name: s.bone for s in job.slots if s.bone}
    missing = [n for side in ARM_SLOTS for n in ARM_SLOTS[side] if n not in slot_bone]
    if missing:
        res.error("prepare.arm_missing", f"手臂槽位未映射：{', '.join(missing)}")
        return res

    meshes = snapshot.skinned_meshes(arm)
    counts = {o.name: (len(o.data.vertices), len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0)
              for o in meshes}

    _apply_dispositions(context, job, arm, meshes, slot_bone, res)
    plan_scale_info = _facing_and_scale(context, job, arm, meshes, slot_bone, res)
    if plan_scale_info is None:
        return res
    edges_before = _edge_snapshot(meshes)
    arm_info = _apose(context, job, arm, meshes, slot_bone, res)
    _distortion(res, meshes, edges_before)
    if job.level_shoulders:
        _level_shoulders(context, arm, slot_bone, res)
    _verify(res, job, arm, meshes, slot_bone, counts, plan_scale_info)
    res.data.update({"arms": arm_info})
    res.info("prepare.done",
             f"预处理完成：缩放 ×{plan_scale_info['factor']:.4f}，肩高 {res.data.get('shoulder_pmx', 0):.2f}，"
             f"上臂 {res.data.get('arm_left_deg', 0):.1f}°/{res.data.get('arm_right_deg', 0):.1f}°")
    job.record(res)
    return res


# ---------------------------------------------------------------------------

def _apply_dispositions(context, job, arm, meshes, slot_bone, res: StageResult) -> None:
    merges: Dict[str, str] = {}
    pending: List[str] = []
    for plan in job.bones:
        if plan.action == 'merge':
            target = slot_bone.get(plan.slot_id)
            if target and target != plan.name and plan.name in arm.data.bones:
                merges[plan.name] = target
            elif plan.name in arm.data.bones:
                pending.append(plan.name)
    deletes = [p.name for p in job.bones if p.action == 'delete' and p.name in arm.data.bones]
    groups = sum(rigedit.merge_vertex_groups(obj, merges) for obj in meshes)
    deleted = rigedit.delete_bones(context, arm, list(merges) + deletes, meshes)
    gone = set(deleted)
    with props.programmatic_writes(context):
        for i in range(len(job.bones) - 1, -1, -1):
            if job.bones[i].name in gone:
                job.bones.remove(i)
    res.data["merged_bones"] = len(merges)
    res.data["deleted_bones"] = len(deleted)
    if merges or deletes:
        res.info("prepare.dispositions",
                 f"并入 {len(merges)} 根辅助骨（{groups} 个顶点组），删除 {len(deleted)} 根骨")
    if pending:
        res.info("prepare.pending_merges",
                 f"{len(pending)} 根骨要并入的槽位将在 ④ 生成，届时再合并：{', '.join(pending[:5])}")


def _facing_and_scale(context, job, arm, meshes, slot_bone, res: StageResult):
    rig = snapshot.rig_from_blender(arm)
    if rig.skin is None:
        res.error("prepare.no_skin", "骨架没有蒙皮网格")
        return None
    shoulders = [rig.bones[rig.by_name[slot_bone[f"{s}_upper_arm_bone"]]].head[2] for s in ("left", "right")]
    foot = [rig.by_name[slot_bone[s]] for s in FOOT_SLOTS if slot_bone.get(s) in rig.by_name]
    ground = rig.floor
    if foot:
        w = np.max([rig.skin.bone_weight_column(b) for b in foot], axis=0)
        if (w >= 0.5).any():
            ground = float(rig.skin.positions[w >= 0.5, 2].min())
    top = float(rig.skin.positions[:, 2].max())
    try:
        sp = plan_scale(job.scale_mode, float(np.mean(shoulders)), ground, top, job.shoulder_target)
    except ValueError as exc:
        res.error("prepare.scale_failed", f"无法计算缩放：{exc}")
        return None
    g = sp.matrix()
    flipped = job.facing == "+Y"
    if flipped:
        g = g @ FLIP_180
    if not np.allclose(g, np.eye(4), atol=1e-9):
        rigedit.transform_rig(context, arm, meshes, global_matrix=g)
    if flipped:
        job.facing = "-Y"
        res.info("prepare.facing_fixed", "模型原本背朝前方，已绕 Z 轴旋转 180°")
    res.info("prepare.scaled", f"缩放方式 {job.scale_mode}：×{sp.factor:.4f}，地面 {ground:+.3f} → 0，"
                               f"导出后身高 {sp.height_pmx:.2f}、肩高 {sp.shoulder_pmx:.2f}")
    res.data.update({"scale_mode": job.scale_mode, "scale_factor": sp.factor, "ground_before": ground,
                     "height_pmx": sp.height_pmx})
    return {"factor": sp.factor, "height_pmx": sp.height_pmx}


def _apose(context, job, arm, meshes, slot_bone, res: StageResult):
    rig = snapshot.rig_from_blender(arm, with_skin=False)
    parents = [b.parent for b in rig.bones]
    heads = np.array([b.head for b in rig.bones])
    arms = [(side, *(rig.by_name[slot_bone[n]] for n in ARM_SLOTS[side])) for side in ("left", "right")]
    plan = plan_arm_pose(parents, heads, arms, job.apose_upper_deg, job.apose_fore_extra_deg)
    info = {a.side: {"before_upper": round(a.before_upper_deg, 2), "before_fore": round(a.before_fore_deg, 2),
                     "planned_upper": round(a.after_upper_deg, 2), "planned_fore": round(a.after_fore_deg, 2)}
            for a in plan.arms}
    if plan.transforms:
        rigedit.transform_rig(context, arm, meshes,
                              bone_transforms={rig.bones[i].name: m for i, m in plan.transforms.items()})
        res.info("prepare.apose",
                 "手臂姿态：" + "；".join(f"{'左' if a.side == 'left' else '右'} {a.before_upper_deg:.1f}° → "
                                       f"{a.after_upper_deg:.1f}°（前臂 {a.after_fore_deg:.1f}°）" for a in plan.arms))
    else:
        res.info("prepare.apose_skipped", f"手臂已在目标角度 {job.apose_upper_deg:.1f}° 附近，未改动")
    return info


def _edge_snapshot(meshes):
    snap = {}
    for obj in meshes:
        me = obj.data
        if not len(me.edges):
            continue
        edges = np.empty(len(me.edges) * 2, dtype=np.int32)
        me.edges.foreach_get("vertices", edges)
        edges = edges.reshape(-1, 2)
        snap[obj.name] = (edges, edge_lengths(rigedit.get_coords(me.vertices, len(me.vertices)), edges))
    return snap


def _distortion(res: StageResult, meshes, before) -> None:
    lows, highs = [], []
    for obj in meshes:
        co = rigedit.get_coords(obj.data.vertices, len(obj.data.vertices))
        if len(co):
            lows.append(co.min(axis=0))
            highs.append(co.max(axis=0))
    size = float(np.linalg.norm(np.max(highs, axis=0) - np.min(lows, axis=0))) if lows else 1.0
    torn_total, worst = 0, (1.0, "")
    for obj in meshes:
        snap = before.get(obj.name)
        if snap is None:
            continue
        edges, old = snap
        new = edge_lengths(rigedit.get_coords(obj.data.vertices, len(obj.data.vertices)), edges)
        d = distortion(old, new, size)
        torn_total += d["torn"]
        if d["worst_ratio"] > worst[0]:
            worst = (d["worst_ratio"], obj.name)
    res.data["torn_edges"] = torn_total
    if torn_total:
        res.warning("prepare.torn", f"A 姿势后有 {torn_total} 条边被拉裂（最严重 ×{worst[0]:.1f}，{worst[1]}），"
                                    "检查腋下/手腕权重", worst[1])


def _level_shoulders(context, arm, slot_bone, res: StageResult) -> None:
    moved = []
    for side in ("left", "right"):
        sh, up = slot_bone.get(f"{side}_shoulder_bone"), slot_bone.get(f"{side}_upper_arm_bone")
        if not sh or not up or sh not in arm.data.bones:
            continue
        sh_head = arm.data.bones[sh].head_local
        up_head = arm.data.bones[up].head_local
        target = (sh_head.x, up_head.y, up_head.z)
        if (sh_head - type(sh_head)(target)).length > 1e-5:
            rigedit.edit_bone_head(context, arm, sh, target)
            moved.append(sh)
    if moved:
        res.info("prepare.shoulders_levelled", f"肩骨已摆平（只改骨）：{', '.join(moved)}")


def _verify(res: StageResult, job, arm, meshes, slot_bone, counts, scale_info) -> None:
    rig = snapshot.rig_from_blender(arm)
    for side in ("left", "right"):
        up, lo, hand = (rig.bones[rig.by_name[slot_bone[n]]] for n in ARM_SLOTS[side])
        angle = down_angle(lo.head - up.head)
        fore = down_angle(hand.head - lo.head)
        res.data[f"arm_{side}_deg"] = angle
        res.data[f"forearm_{side}_deg"] = fore
        target_fore = job.apose_upper_deg + job.apose_fore_extra_deg
        if abs(angle - job.apose_upper_deg) > ANGLE_TOLERANCE or abs(fore - target_fore) > ANGLE_TOLERANCE:
            res.error("prepare.arm_angle", f"{'左' if side == 'left' else '右'}臂角度 {angle:.2f}°/{fore:.2f}°，"
                                           f"目标 {job.apose_upper_deg:.2f}°/{target_fore:.2f}°")
        if abs(forward_angle(lo.head - up.head)) > 1.0:
            res.warning("prepare.arm_forward", f"{side} 上臂仍有 {forward_angle(lo.head - up.head):.1f}° 前倾")
    shoulder_z = float(np.mean([rig.bones[rig.by_name[slot_bone[f'{s}_upper_arm_bone']]].head[2]
                                for s in ("left", "right")]))
    res.data["shoulder_pmx"] = shoulder_z * EXPORT_SCALE
    if job.scale_mode == 'SHOULDER' and abs(shoulder_z * EXPORT_SCALE - job.shoulder_target) > 0.1:
        res.error("prepare.shoulder_height", f"肩高 {shoulder_z * EXPORT_SCALE:.2f}，目标 {job.shoulder_target:.2f}")
    for obj in meshes:
        n, keys = counts.get(obj.name, (None, None))
        now = (len(obj.data.vertices), len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0)
        if n is not None and now != (n, keys):
            res.error("prepare.mesh_changed", f"{obj.name} 顶点/形态键数变了：{(n, keys)} → {now}", obj.name)
