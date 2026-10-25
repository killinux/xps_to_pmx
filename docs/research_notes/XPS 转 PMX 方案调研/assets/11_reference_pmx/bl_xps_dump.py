# Blender 3.6 headless: import an XPS with XNALaraMesh and dump bones / weights (read-only on source).
# usage: blender --background --python bl_xps_dump.py -- <xps path> <out prefix> [impDefPose 0/1]
import bpy, sys, json, os
import numpy as np
import addon_utils

argv = sys.argv[sys.argv.index("--") + 1:]
src, outp = argv[0], argv[1]
imp_def_pose = (len(argv) > 2 and argv[2] == "1")
join_rips = not (len(argv) > 3 and argv[3] == "0")

for mod in addon_utils.modules():
    if mod.__name__.startswith("XNALaraMesh"):
        addon_utils.enable(mod.__name__, default_set=False)

# clean scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.xps_tools.import_model(filepath=src, impDefPose=imp_def_pose, joinMeshRips=join_rips, joinMeshParts=True,
                               markSeams=False, vColors=False, connectBones=False, autoIk=False, importNormals=False)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE']
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
res = {"src": src, "impDefPose": imp_def_pose, "joinRips": join_rips, "armatures": [a.name for a in arm], "meshes": []}
bones = []
if arm:
    a = arm[0]
    mw = a.matrix_world
    for b in a.data.bones:
        h = mw @ b.head_local
        t = mw @ b.tail_local
        bones.append(dict(name=b.name, parent=b.parent.name if b.parent else None, head=list(h), tail=list(t),
                          matrix=[list(r) for r in (mw @ b.matrix_local)]))
    # pose-mode: if a default pose was applied, record posed heads as well
    pb = []
    for p in a.pose.bones:
        m = mw @ p.matrix
        pb.append(dict(name=p.name, head=list(m.translation), rot_q=list(p.rotation_quaternion), loc=list(p.location)))
    res["pose_bones"] = pb
res["bones"] = bones
bone_index = {b["name"]: i for i, b in enumerate(bones)}

all_co = []; all_mesh = []; all_g = []; all_w = []
MAXG = 8
for mi, o in enumerate(meshes):
    me = o.data
    n = len(me.vertices)
    co = np.zeros(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    M = np.array(o.matrix_world)
    co = (co @ M[:3, :3].T) + M[:3, 3]
    gnames = [g.name for g in o.vertex_groups]
    G = np.full((n, MAXG), -1, dtype=np.int32); W = np.zeros((n, MAXG), dtype=np.float64)
    over = 0
    for v in me.vertices:
        gs = sorted(((g.weight, g.group) for g in v.groups if g.weight > 0), reverse=True)
        if len(gs) > MAXG: over += 1
        for k, (w, gi) in enumerate(gs[:MAXG]):
            G[v.index, k] = bone_index.get(gnames[gi], -2)
            W[v.index, k] = w
    mats = [s.material.name for s in o.material_slots if s.material]
    # texture images used by the material
    texs = []
    for s in o.material_slots:
        if s.material and s.material.use_nodes:
            for nd in s.material.node_tree.nodes:
                if nd.type == 'TEX_IMAGE' and nd.image:
                    texs.append(nd.image.filepath)
    res["meshes"].append(dict(name=o.name, nverts=n, materials=mats, textures=texs, over8=over,
                              bbox_min=co.min(0).tolist() if n else None, bbox_max=co.max(0).tolist() if n else None,
                              groups_missing=[g for g in gnames if g not in bone_index]))
    all_co.append(co); all_mesh.append(np.full(n, mi, dtype=np.int32)); all_g.append(G); all_w.append(W)

co = np.concatenate(all_co) if all_co else np.zeros((0, 3))
np.savez_compressed(outp + ".npz", co=co, mesh=np.concatenate(all_mesh), g=np.concatenate(all_g), w=np.concatenate(all_w))
res["nverts"] = int(len(co))
res["bbox_min"] = co.min(0).tolist(); res["bbox_max"] = co.max(0).tolist()
with open(outp + ".json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("XPSDUMP OK", src, len(bones), len(co))
