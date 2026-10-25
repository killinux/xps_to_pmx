"""M4 acceptance: stages ④ and ⑧ in Blender on the regression set.

import → identify → prepare → build → export, then: the mmd_tools model
structure, standard bones, D-bone / twist weights, mesh integrity (vertex and
shape-key counts), the exported PMX read back with ``pmx.load`` (bone order,
parents, 付与, IK, weights, frames, textures), and the report JSON.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

import bpy  # noqa: E402

harness.register_addon()
from xps_to_pmx.blender import mmdtools_bridge as bridge  # noqa: E402
from xps_to_pmx.blender import snapshot  # noqa: E402
from xps_to_pmx.pipeline import stage_build, stage_export, stage_identify, stage_import, stage_prepare  # noqa: E402

STANDARD = ["全ての親", "センター", "グルーブ", "腰", "上半身", "上半身2", "下半身", "首", "頭"]
for _s in "左右":
    STANDARD += [f"{_s}{n}" for n in ("肩P", "肩", "肩C", "腕", "腕捩", "腕捩1", "腕捩2", "腕捩3", "ひじ", "手捩",
                                       "手捩1", "手捩2", "手捩3", "手首", "ダミー", "親指１", "人指１", "足", "ひざ",
                                       "足首", "つま先", "足D", "ひざD", "足首D", "足先EX", "足IK親", "足ＩＫ",
                                       "つま先ＩＫ")]
    STANDARD.append(f"腰キャンセル{_s}")


def _errors(res):
    return [m.text for m in res.messages if m.level == 'error']


def _group_weight(meshes, name):
    total = 0.0
    for obj in meshes:
        vg = obj.vertex_groups.get(name)
        if vg is None:
            continue
        for v in obj.data.vertices:
            for g in v.groups:
                if g.group == vg.index:
                    total += g.weight
    return total


def check_model(entry, out_dir):
    c = harness.Checker(entry["id"])
    path = entry["path"]
    if not os.path.isfile(path):
        c.check("sample file exists", False, path)
        return c
    harness.reset_scene()
    times = {}
    t = time.time()
    res, job = stage_import.run(bpy.context, path)
    res = stage_identify.run(bpy.context, job)
    res = stage_prepare.run(bpy.context, job)
    times["import+identify+prepare"] = round(time.time() - t, 1)
    if not c.check("stages ①-③ without errors", res.ok, _errors(res)[:3]):
        return c
    arm = job.armature
    meshes = snapshot.skinned_meshes(arm)
    counts = {o.get("xps2pmx_mesh_index"): (len(o.data.vertices),
                                            len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0)
              for o in meshes}

    t = time.time()
    res = stage_build.run(bpy.context, job)
    times["build"] = round(time.time() - t, 1)
    c.check("build without errors", res.ok, _errors(res)[:5])
    warnings = [f"{m.code}: {m.text}" for m in res.messages if m.level == 'warning']
    c.check("build warnings listed", True, warnings[:8])
    if not res.ok:
        return c
    root = bridge.find_root(arm)
    c.check("armature adopted by an mmd_tools root", root is not None and arm.parent == root,
            root.name if root else None)
    c.check("job stage is build", job.stage == "build", job.stage)
    names = set(arm.data.bones.keys())
    missing = [n for n in STANDARD if n not in names]
    c.check("standard + semi-standard bones present", not missing, missing)
    has_eyes = any(s.name in ("left_eye_bone", "right_eye_bone") and s.bone for s in job.slots)
    if has_eyes:
        c.check("両目 generated for a rig with eyes", "両目" in names)
    meshes = snapshot.skinned_meshes(arm)
    fk = {n: _group_weight(meshes, n) for n in ("左足", "右ひざ", "左足首")}
    c.check("FK leg bones carry no weight", all(v == 0 for v in fk.values()), fk)
    d = {n: round(_group_weight(meshes, n), 1) for n in ("左足D", "右足D", "左ひざD", "左足首D", "左足先EX")}
    c.check("D bones and 足先EX carry the leg weights", all(v > 0 for v in d.values()), d)
    tw = {n: round(_group_weight(meshes, n), 1) for n in ("左腕捩1", "左腕捩2", "左腕捩", "右手捩3")}
    c.check("twist bones carry weight", all(v > 0 for v in tw.values()), tw)
    lb = round(_group_weight(meshes, "下半身"), 1)
    c.check("下半身 has weights", lb > 0, lb)
    now = {o.get("xps2pmx_mesh_index"): (len(o.data.vertices),
                                         len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0)
           for o in meshes}
    c.check("vertex and shape-key counts unchanged", now == counts,
            {k: (counts.get(k), now.get(k)) for k in now if counts.get(k) != now.get(k)})
    pb = arm.pose.bones
    c.check("付与 constraints built (腕捩1, 左目/肩C)",
            any(con.name == "mmd_additional_rotation" for con in pb["左腕捩1"].constraints)
            and any(con.name == "mmd_additional_rotation" for con in pb["左肩C"].constraints))
    knee = pb["左ひざ"]
    ik = next((con for con in knee.constraints if con.type == 'IK'), None)
    c.check("足ＩＫ constraint on 左ひざ", ik is not None and ik.subtarget == "左足ＩＫ" and ik.chain_count == 2,
            None if ik is None else (ik.subtarget, ik.chain_count, ik.iterations))

    out = os.path.join(out_dir, entry["id"], f"{entry['id']}.pmx")
    t = time.time()
    res = stage_export.run(bpy.context, job, out)
    times["export+readback"] = round(time.time() - t, 1)
    c.check("export + read-back checks without errors", res.ok, _errors(res)[:8])
    exp_warn = [f"{m.code}: {m.text}" for m in res.messages if m.level == 'warning']
    c.check("export warnings listed", True, exp_warn[:8])
    c.check("PMX written", os.path.isfile(out), out)
    report = os.path.splitext(out)[0] + ".report.json"
    c.check("report JSON written", os.path.isfile(report), report)
    if os.path.isfile(report):
        with open(report, encoding="utf-8") as f:
            data = json.load(f)
        c.check("report has all stages", all(s in data["stages"] for s in ("import", "identify", "prepare", "build",
                                                                          "export")), list(data["stages"]))
    info = job.summary().get("export", {})
    c.check("feet on the ground (PMX min y)", abs(info.get("min_y", 1.0)) < 0.05, info.get("min_y"))
    c.check("height plausible (18-series 19-23.5)", 17.0 < info.get("height_pmx", 0) < 26.0, info.get("height_pmx"))
    c.check("timings", True, times)
    return c


def check_redo(entry):
    """『重来』keeps options and hand-edited slots and rebuilds to the same stage."""
    from xps_to_pmx.pipeline import redo
    c = harness.Checker(entry["id"] + " (redo)")
    harness.reset_scene()
    res, job = stage_import.run(bpy.context, entry["path"])
    stage_identify.run(bpy.context, job)
    job.twist_mode = 'SMOOTH'
    job.ik_preset = 'S18'
    slot = job.slot("left_toe_bone")
    original = slot.bone
    slot.bone = ""          # a hand edit: no toe bone on the left → generated
    stage_identify.recheck(bpy.context, job)
    stage_prepare.run(bpy.context, job)
    res = stage_build.run(bpy.context, job)
    c.check("first build ok", res.ok, _errors(res)[:3])
    res, new = redo.run(bpy.context, job)
    c.check("redo ok", res.ok, _errors(res)[:3])
    if new is None:
        return c
    c.check("one job left", len(bpy.context.scene.xps2pmx.jobs) == 1, len(bpy.context.scene.xps2pmx.jobs))
    c.check("stage reached again", new.stage == "build", new.stage)
    c.check("options kept", (new.twist_mode, new.ik_preset) == ('SMOOTH', 'S18'), (new.twist_mode, new.ik_preset))
    toe = new.slot("left_toe_bone")
    c.check("hand edit kept (left toe unmapped)", toe.bone == "" and original != "", (toe.bone, toe.origin))
    arm = new.armature
    ik = arm.pose.bones["左足ＩＫ"]
    knee = arm.pose.bones["左ひざ"]
    con = next((x for x in knee.constraints if x.type == 'IK'), None)
    c.check("S18 IK preset applied", con is not None and con.iterations == 40
            and abs(knee.mmd_bone.ik_rotation_constraint - 1.0) < 1e-6, None if con is None else con.iterations)
    c.check("old objects removed", sum(1 for o in bpy.data.objects if o.type == 'ARMATURE') == 1)
    return c


def main():
    args = harness.parse_args()
    out_dir = os.path.join(args.out, "m4")
    models = harness.regression_models(args.models)
    checkers = [check_model(m, out_dir) for m in models]
    if models and os.path.isfile(models[0]["path"]):
        checkers.append(check_redo(models[0]))
    report = harness.write_report(args.out, "m4_build", checkers)
    harness.finish(report)


main()
