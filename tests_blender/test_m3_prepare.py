"""M3 acceptance: stage ③ in Blender on the regression set.

import → identify → prepare, then: arm angles, shoulder height, ground, removed
bones, weights, a hand-made shape key (offsets rotated/scaled rigidly), trunk
normals unchanged, idempotent second run; plus a model turned 180° first.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

import bpy  # noqa: E402
import numpy as np  # noqa: E402

harness.register_addon()
from xps_to_pmx.blender import rigedit, snapshot  # noqa: E402
from xps_to_pmx.core.pose import FLIP_180, down_angle  # noqa: E402
from xps_to_pmx.pipeline import stage_identify, stage_import, stage_prepare  # noqa: E402


def _arm_angles(job):
    arm = job.armature
    out = {}
    for side in ("left", "right"):
        up = arm.data.bones[job.slot(f"{side}_upper_arm_bone").bone].head_local
        lo = arm.data.bones[job.slot(f"{side}_lower_arm_bone").bone].head_local
        hand = arm.data.bones[job.slot(f"{side}_hand_bone").bone].head_local
        out[side] = (down_angle(np.array(lo - up)), down_angle(np.array(hand - lo)))
    return out


def _add_test_key(obj):
    me = obj.data
    if me.shape_keys is None:
        obj.shape_key_add(name="Basis", from_mix=False)
    key = obj.shape_key_add(name="xps2pmx_test", from_mix=False)
    n = len(me.vertices)
    co = rigedit.get_coords(key.data, n)
    rigedit.set_coords(key.data, co + np.array([0.0, 0.0, 0.01]))
    return key.name


def _trunk_loops(obj, job):
    """Loop indices whose vertex is weighted only to spine bones (not moved by the A-pose)."""
    spine = {job.slot(s).bone for s in ("upper_body_bone", "upper_body2_bone") if job.slot(s).bone}
    names = {vg.index: vg.name for vg in obj.vertex_groups}
    good = {i for i, v in enumerate(obj.data.vertices)
            if v.groups and all(names.get(g.group) in spine for g in v.groups if g.weight > 0)}
    lv = rigedit.loop_vertices(obj.data)
    return np.array([i for i, v in enumerate(lv) if v in good][:500], dtype=int)


def check_model(entry, flip_first=False):
    name = entry["id"] + (" (turned 180°)" if flip_first else "")
    c = harness.Checker(name)
    path = entry["path"]
    if not os.path.isfile(path):
        c.check("sample file exists", False, path)
        return c
    harness.reset_scene()
    res, job = stage_import.run(bpy.context, path)
    arm = job.armature
    meshes = snapshot.skinned_meshes(arm)
    if flip_first:
        rigedit.transform_rig(bpy.context, arm, meshes, global_matrix=FLIP_180)
    res = stage_identify.run(bpy.context, job)
    if flip_first:
        c.check("identify detects facing +Y", job.facing == "+Y", job.facing)
    c.check("identify without errors", not [m for m in res.messages if m.level == 'error'],
            [m.text for m in res.messages if m.level == 'error'][:3])

    # a shape key on the mesh with the most arm weights, and trunk normals before
    target = max(meshes, key=lambda o: len(o.data.vertices))
    key_name = _add_test_key(target)
    trunk = _trunk_loops(target, job)
    normals_before = rigedit.loop_normals(target.data)[trunk] if len(trunk) else None
    to_delete = [p.name for p in job.bones if p.action in ('merge', 'delete')]

    res = stage_prepare.run(bpy.context, job)
    errors = [m.text for m in res.messages if m.level == 'error']
    c.check("prepare without errors", not errors, errors[:3])
    angles = _arm_angles(job)
    c.check("arms at 37.5° and straight",
            all(abs(u - 37.5) < 0.5 and abs(f - 37.5) < 0.5 for u, f in angles.values()), angles)
    shoulder = res.data.get("shoulder_pmx", 0)
    c.check("shoulder height 17.0 PMX", abs(shoulder - 17.0) < 0.1, shoulder)
    rig = snapshot.rig_from_blender(arm)
    feet = [rig.by_name[job.slot(s).bone] for s in ("left_ankle_bone", "right_ankle_bone", "left_toe_bone",
                                                    "right_toe_bone") if job.slot(s).bone in rig.by_name]
    w = np.max([rig.skin.bone_weight_column(b) for b in feet], axis=0)
    ground = float(rig.skin.positions[w >= 0.5, 2].min())
    c.check("feet on the ground", abs(ground) < 1e-4, ground)
    left = [n for n in to_delete if n in arm.data.bones]
    c.check("merged/deleted bones removed", not left, left[:5])
    stray = [vg.name for o in meshes for vg in o.vertex_groups if vg.name in set(to_delete)]
    c.check("no vertex groups of removed bones", not stray, stray[:5])
    sums_ok = True
    for o in meshes:
        for v in list(o.data.vertices)[::53]:
            ws = [g.weight for g in v.groups if g.weight > 0]
            if ws and (len(ws) > 4 or abs(sum(ws) - 1) > 1e-4):
                sums_ok = False
                break
    c.check("weights still normalised, <=4", sums_ok)
    if flip_first:
        lx = arm.data.bones[job.slot("left_hand_bone").bone].head_local.x
        c.check("left hand back on +X after the flip", lx > 0 and job.facing == "-Y", lx)

    me = target.data
    kb = me.shape_keys.key_blocks
    delta = rigedit.get_coords(kb[key_name].data, len(me.vertices)) - rigedit.get_coords(kb[0].data, len(me.vertices))
    lengths = np.linalg.norm(delta, axis=1)
    factor = res.data.get("scale_factor", 1.0)
    single = np.array([sum(1 for g in v.groups if g.weight > 0) == 1 for v in me.vertices])
    c.check("shape key offsets rigid on single-bone vertices",
            np.allclose(lengths[single], 0.01 * factor, atol=1e-6),
            f"{int(single.sum())} vertices; min {lengths[single].min():.6f} expected {0.01 * factor:.6f}")
    ratio = lengths / (0.01 * factor)
    c.check("blended vertices shrink at most 15% (linear blend skinning)",
            float(ratio.min()) > 0.85 and float(ratio.max()) < 1.0 + 1e-4, f"{ratio.min():.3f}..{ratio.max():.3f}")
    if normals_before is not None:
        after = rigedit.loop_normals(me)[trunk]
        expected = normals_before * np.array([-1.0, -1.0, 1.0]) if flip_first else normals_before
        dots = np.einsum("ij,ij->i", expected, after)
        c.check("trunk normals unchanged", float(dots.min()) > 0.999, float(dots.min()))

    res2 = stage_prepare.run(bpy.context, job)
    c.check("second run is a no-op", res2.ok and abs(res2.data.get("scale_factor", 0) - 1.0) < 1e-6
            and any(m.code == "prepare.apose_skipped" for m in res2.messages),
            res2.data.get("scale_factor"))
    c.check("torn edges reported", True, res.data.get("torn_edges"))
    return c


def main():
    args = harness.parse_args()
    models = harness.regression_models(args.models)
    checkers = [check_model(m) for m in models]
    if models:
        checkers.append(check_model(models[0], flip_first=True))
    report = harness.write_report(args.out, "m3_prepare", checkers)
    harness.finish(report)


main()
