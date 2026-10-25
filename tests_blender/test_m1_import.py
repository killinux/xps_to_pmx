"""M1 acceptance: stage ① import on the regression set (design doc §13).

Checks per model: stage result, counts, bone heads, weights (sum 1, <=4),
UVs, custom normals, material manifests, a second import into the same
scene, and bone heads against the XNALaraMesh importer installed in 3.6.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

import addon_utils  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402

harness.register_addon()
from xps_to_pmx.core.xps import load_xps  # noqa: E402
from xps_to_pmx.core.xps.convert import build_import_data, xna_to_blender  # noqa: E402
from xps_to_pmx.pipeline import stage_import  # noqa: E402

XNALARA_MODULE = "XNALaraMesh-master"


def check_model(entry):
    c = harness.Checker(entry["id"])
    path = entry["path"]
    if not os.path.isfile(path):
        c.check("sample file exists", False, path)
        return c
    harness.reset_scene()
    model = load_xps(path)
    data = build_import_data(model)

    t0 = time.perf_counter()
    res, job = stage_import.run(bpy.context, path)
    elapsed = time.perf_counter() - t0
    c.check("stage result ok", res.ok, [m.text for m in res.messages if m.level == "error"])
    c.check("job recorded", job is not None and job.stage == "import")
    if job is None:
        return c
    c.check("import time", True, f"{elapsed:.2f}s")
    arm = job.armature
    meshes = sorted((o for o in job.collection.all_objects if o.type == 'MESH'),
                    key=lambda o: o["xps2pmx_mesh_index"])
    c.check("mesh object count", len(meshes) == len(model.meshes), f"{len(meshes)} vs {len(model.meshes)}")

    # bones
    if model.bones:
        c.check("bone count", len(arm.data.bones) == len(model.bones))
        expected = xna_to_blender(np.array([b.position for b in model.bones]))
        worst = 0.0
        for bone in arm.data.bones:
            idx = bone["xps2pmx_index"]
            worst = max(worst, float(np.abs(np.array(bone.head_local) - expected[idx]).max()))
        c.check("bone heads match file (<1e-5)", worst < 1e-5, f"max diff {worst:.2e}")
        c.check("bone source names kept",
                all(bone["xps2pmx_src"] == model.bones[bone["xps2pmx_index"]].name for bone in arm.data.bones))

    # per mesh
    count_bad, uv_bad, normal_low, weight_bad, sample_bad = [], [], [], [], []
    for obj, im in zip(meshes, data.meshes):
        me = obj.data
        if len(me.vertices) != im.vertex_count or len(me.polygons) != im.face_count:
            count_bad.append(obj.name)
        loops = im.faces.reshape(-1)
        if im.uvs and len(loops):
            got = np.empty(len(me.loops) * 2, dtype=np.float32)
            me.uv_layers[0].data.foreach_get("uv", got)
            if not np.allclose(got.reshape(-1, 2), im.uvs[0][loops], atol=1e-6):
                uv_bad.append(obj.name)
        if len(loops):
            me.calc_normals_split()
            normals = np.empty(len(me.loops) * 3, dtype=np.float32)
            me.loops.foreach_get("normal", normals)
            dots = np.einsum("ij,ij->i", normals.reshape(-1, 3), im.normals[loops])
            valid = np.linalg.norm(im.normals[loops], axis=1) > 0.5
            frac = float((dots[valid] > 0.999).mean()) if valid.any() else 1.0
            if frac < 0.99:
                normal_low.append(f"{obj.name}:{frac:.3f}")
        if model.bones:
            names = {vg.index: vg.name for vg in obj.vertex_groups}
            bone_name = {b["xps2pmx_index"]: b.name for b in arm.data.bones}
            weighted = im.weight_bones[:, 0] >= 0
            for i, v in enumerate(me.vertices):
                gs = [g for g in v.groups if g.weight > 0]
                total = sum(g.weight for g in gs)
                if len(gs) > 4 or (weighted[i] and abs(total - 1.0) > 1e-4):
                    weight_bad.append(f"{obj.name}#{i}")
                    break
            for i in range(0, im.vertex_count, 97):
                got = {names[g.group]: round(g.weight, 5) for g in me.vertices[i].groups if g.weight > 0}
                want = {bone_name[int(b)]: round(float(w), 5)
                        for b, w in zip(im.weight_bones[i], im.weight_values[i]) if b >= 0}
                if got != want:
                    sample_bad.append(f"{obj.name}#{i}")
                    break
    c.check("vertex/face counts per mesh", not count_bad, count_bad[:5])
    c.check("UVs match (v flipped)", not uv_bad, uv_bad[:5])
    c.check("custom normals kept (>=99% loops)", not normal_low, normal_low[:5])
    if model.bones:
        c.check("weights sum to 1 and <=4 per vertex", not weight_bad, weight_bad[:5])
        c.check("sampled weights equal conversion", not sample_bad, sample_bad[:5])

    # materials and manifests
    manifest_bad, diffuse_bad = [], []
    for obj, xm in zip(meshes, model.meshes):
        mat = obj.data.materials[0] if obj.data.materials else None
        man = mat.get("xps2pmx") if mat else None
        if man is None or len(man["textures"]) != len(xm.textures):
            manifest_bad.append(obj.name)
            continue
        diffuse = next((t for t in man["textures"] if t["role"] == "diffuse"), None)
        if diffuse and diffuse["path"]:
            node = mat.node_tree.nodes.get("xps_diffuse")
            if node is None or node.image is None or \
                    os.path.normcase(bpy.path.abspath(node.image.filepath)) != os.path.normcase(diffuse["path"]):
                diffuse_bad.append(obj.name)
    c.check("material manifests complete", not manifest_bad, manifest_bad[:5])
    c.check("diffuse textures wired", not diffuse_bad, diffuse_bad[:5])
    missing = [m.text for m in res.messages if m.code == "import.texture_missing"]
    c.check("missing textures reported (info)", True, f"{len(missing)} missing")

    # second import into the same scene stays separate
    res2, job2 = stage_import.run(bpy.context, path)
    c.check("second import ok and separate", res2.ok and job2 is not None and job2.armature != arm
            and len(bpy.context.scene.xps2pmx.jobs) == 2)

    # compare with the XNALaraMesh importer
    c.run("XNALaraMesh comparison", compare_with_xnalara, c, path, arm)
    return c


def compare_with_xnalara(c, path, arm):
    mod = addon_utils.enable(XNALARA_MODULE, default_set=False)
    if mod is None:
        c.check("XNALaraMesh available", False, "addon not found")
        return
    before = set(bpy.data.objects)
    bpy.ops.xps_tools.import_model(filepath=path)
    new_arms = [o for o in set(bpy.data.objects) - before if o.type == 'ARMATURE']
    if not new_arms:
        c.check("XNALaraMesh imported an armature", False)
        return
    ref = new_arms[0]
    ours = {b["xps2pmx_src"]: b for b in arm.data.bones}
    worst, compared = 0.0, 0
    ref_mat = np.array(ref.matrix_world)
    for b in ref.data.bones:
        mine = ours.get(b.name)
        if mine is None:
            continue
        head_ref = (ref_mat @ np.append(np.array(b.head_local), 1.0))[:3]
        worst = max(worst, float(np.abs(head_ref - np.array(mine.head_local)).max()))
        compared += 1
    c.check("bone heads equal XNALaraMesh (<1e-4)", compared > 0 and worst < 1e-4,
            f"{compared} bones compared, max diff {worst:.2e}")


def main():
    args = harness.parse_args()
    checkers = [check_model(m) for m in harness.regression_models(args.models)]
    report = harness.write_report(args.out, "m1_import", checkers)
    harness.finish(report)


main()
