"""Motion smoke test: import PMX files with mmd_tools, play a VMD, sample frames, flag gross failures.

    blender -b --factory-startup --python scripts/motion_smoke.py -- --vmd <motion.vmd> <a.pmx> [<b.pmx> ...]
            [--step 15] [--frames 0:1800] [--out out/motion_smoke.json]

Per sampled frame (evaluated mesh, Blender units ×12.5 = PMX units):
* lowest foot vertex (penetration below the floor),
* knees bending backwards (knee behind the hip→ankle line w.r.t. the pelvis' forward axis),
* exploded vertices (farther than 1.5 × model height from the 下半身 bone).
mmd_tools' Blender playback only approximates MMD (IK via Blender IK, 付与 via
constraints); this catches broken rigs, not subtle differences.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import addon_utils
import bpy
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCALE = 0.08


def args_after_dashes():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def import_pmx(path):
    before = set(bpy.data.objects)
    bpy.ops.mmd_tools.import_model(filepath=path, scale=SCALE, types={'MESH', 'ARMATURE', 'DISPLAY', 'MORPHS'},
                                   clean_model=False, rename_bones=False, log_level='ERROR')
    new = [o for o in bpy.data.objects if o not in before]
    root = next(o for o in new if o.mmd_type == 'ROOT')
    arm = next(o for o in new if o.type == 'ARMATURE')
    meshes = [o for o in new if o.type == 'MESH' and len(o.data.vertices)]
    return root, arm, meshes


def import_vmd(root, arm, vmd):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    root.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.mmd_tools.import_vmd(filepath=vmd, scale=SCALE, margin=0, update_scene_settings=True)


def evaluated_positions(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3) @ np.array(o.matrix_world)[:3, :3].T + np.array(o.matrix_world)[:3, 3]
        out.append(co)
        ev.to_mesh_clear()
    return np.concatenate(out) if out else np.zeros((0, 3))


def foot_mask(arm, meshes):
    names = {"左足首", "右足首", "左足首D", "右足首D", "左つま先", "右つま先", "左足先EX", "右足先EX"}
    masks = []
    for o in meshes:
        m = np.zeros(len(o.data.vertices), dtype=bool)
        groups = {vg.index for vg in o.vertex_groups if vg.name in names}
        if groups:
            for v in o.data.vertices:
                if sum(g.weight for g in v.groups if g.group in groups) >= 0.5:
                    m[v.index] = True
        masks.append(m)
    return np.concatenate(masks) if masks else np.zeros(0, dtype=bool)


def knee_backwards(arm):
    pb = arm.pose.bones
    mw = np.array(arm.matrix_world)
    bad = []
    lower = pb.get("下半身")
    if lower is None:
        return bad
    fwd = (mw[:3, :3] @ np.array(lower.matrix)[:3, :3]) @ np.array([0.0, -1.0, 0.0])
    for side in "左右":
        try:
            hip = mw @ np.append(np.array(pb[f"{side}足"].head), 1.0)
            knee = mw @ np.append(np.array(pb[f"{side}ひざ"].head), 1.0)
            ankle = mw @ np.append(np.array(pb[f"{side}足首"].head), 1.0)
        except KeyError:
            continue
        hip, knee, ankle = hip[:3], knee[:3], ankle[:3]
        line = ankle - hip
        t = float(np.dot(knee - hip, line) / max(np.dot(line, line), 1e-12))
        d = knee - (hip + t * line)
        if np.linalg.norm(d) > 0.01 and float(np.dot(d, fwd)) < -0.005:
            bad.append(side)
    return bad


def run_model(path, vmd, frames, step):
    bpy.ops.wm.read_homefile(use_empty=True, use_factory_startup=True)
    root, arm, meshes = import_pmx(path)
    rest = evaluated_positions(meshes)
    height = float(rest[:, 2].max() - rest[:, 2].min())
    feet = foot_mask(arm, meshes)
    import_vmd(root, arm, vmd)
    scene = bpy.context.scene
    start, end = frames
    end = min(end, scene.frame_end) if scene.frame_end > scene.frame_start else end
    result = {"pmx": path, "height_m": round(height, 3), "frames": [], "worst_floor": 0.0, "knee_back_frames": 0,
              "exploded_frames": 0, "samples": 0}
    for f in range(start, end + 1, step):
        scene.frame_set(f)
        pos = evaluated_positions(meshes)
        lb = arm.pose.bones.get("下半身")
        centre = (np.array(arm.matrix_world) @ np.append(np.array(lb.head), 1.0))[:3] if lb else pos.mean(axis=0)
        floor = float(pos[feet, 2].min()) if feet.any() else float(pos[:, 2].min())
        far = int((np.linalg.norm(pos - centre, axis=1) > 1.5 * height).sum())
        knees = knee_backwards(arm)
        result["samples"] += 1
        result["worst_floor"] = min(result["worst_floor"], floor)
        result["knee_back_frames"] += 1 if knees else 0
        result["exploded_frames"] += 1 if far else 0
        if knees or far or floor < -0.03:
            result["frames"].append({"frame": f, "floor_m": round(floor, 3), "knees_back": knees, "exploded": far})
    result["frames"] = result["frames"][:40]
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pmx", nargs="+")
    ap.add_argument("--vmd", required=True)
    ap.add_argument("--step", type=int, default=15)
    ap.add_argument("--frames", default="0:1800")
    ap.add_argument("--out", default=os.path.join(REPO, "out", "motion_smoke.json"))
    args = ap.parse_args(args_after_dashes())
    addon_utils.enable("mmd_tools", default_set=False)
    a, b = (int(x) for x in args.frames.split(":"))
    results = []
    for path in args.pmx:
        r = run_model(path, args.vmd, (a, b), args.step)
        results.append(r)
        print(f"== {os.path.basename(path)}: height {r['height_m']} m, samples {r['samples']}, "
              f"lowest foot {r['worst_floor']:+.3f} m, knees backwards in {r['knee_back_frames']} samples, "
              f"exploded in {r['exploded_frames']}")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"vmd": args.vmd, "results": results}, f, ensure_ascii=False, indent=2)
    print("written", args.out)


main()
