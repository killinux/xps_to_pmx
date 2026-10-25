# -*- coding: utf-8 -*-
"""Classify rigid bodies/joints into body / breast / butt / clothing / hair / other and summarise parameters."""
import sys, os, json, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pmxlib, models
from anal import *
from scale_pairs import pmx_material_vertices

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = []
def P(s=""): OUT.append(s)

BODY_BONES = {"頭", "首", "首1", "上半身", "上半身1", "上半身2", "上半身3", "下半身", "左足", "右足", "左ひざ", "右ひざ",
              "左肩", "右肩", "左腕", "右腕", "左ひじ", "右ひじ", "上半身b", "上半身2b", "左手首", "右手首", "左足首", "右足首"}

def classify_bone(m, bi, mat_hits):
    n = m.bones[bi].name if bi is not None and bi >= 0 else ""
    ne = m.bones[bi].name_e if bi is not None and bi >= 0 else ""
    low = (n + " " + ne).lower()
    if n in BODY_BONES:
        return "body"
    if "乳" in n or "胸" in n or "pectoral" in low or "breast" in low:
        return "breast"
    if "屁股" in n or "尻" in n or "butt" in low or "ass." in low:
        return "butt"
    if "hair" in low or "髪" in n or "side" in low:
        # verify by materials: Bunny DEF-ult_hair weights helmet
        if mat_hits and not any("hair" in k.lower() for k in mat_hits):
            return "hair?(weights:" + ",".join(list(mat_hits)[:2]) + ")"
        return "hair"
    if mat_hits:
        if any("hair" in k.lower() for k in mat_hits):
            return "hair"
        return "clothing(" + ",".join(list(mat_hits)[:2]) + ")"
    return "other"

def bone_material_hits(m, pm, bi, cache):
    if bi in cache: return cache[bi]
    w = vertex_weight_of(m, {bi} | set(descendants(m, bi)))
    hits = collections.OrderedDict()
    for name, ids in sorted(pm, key=lambda x: -int((w[x[1]] > 0).sum())):
        c = int((w[ids] > 0).sum())
        if c > 0: hits[name] = c
    cache[bi] = hits
    return hits

def summarize(key, full=False):
    m = pmxlib.load(models.PATHS[key])
    pm = pmx_material_vertices(m)
    cache = {}
    cats = []
    for r in m.rigids:
        bi = r.bone if r.bone is not None and r.bone >= 0 else None
        hits = bone_material_hits(m, pm, bi, cache) if bi is not None and m.bones[bi].name not in BODY_BONES else {}
        c = classify_bone(m, bi, hits)
        cats.append(c)
    P(f"\n## {key}: {len(m.rigids)} rigid bodies, {len(m.joints)} joints")
    cc = collections.Counter(c.split("(")[0] for c in cats)
    P("category counts: " + ", ".join(f"{k}={v}" for k, v in cc.items()))
    # collision groups per category
    grp = collections.defaultdict(collections.Counter)
    for r, c in zip(m.rigids, cats):
        noncoll = tuple(g + 1 for g in range(16) if not (r.collision_group_mask >> g) & 1)
        grp[c.split("(")[0]][(r.collision_group_number + 1, noncoll)] += 1
    for c, d in grp.items():
        P(f"- {c}: group/non-collide sets: " + "; ".join(f"g{g} nc={list(nc)} ×{n}" for (g, nc), n in d.items()))
    SHAPE = {0: "sphere", 1: "box", 2: "capsule"}; MODE = {0: "static", 1: "dynamic", 2: "dyn+bone"}
    # per-category parameter table
    P("\n| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    bycat = collections.defaultdict(list)
    for r, c in zip(m.rigids, cats):
        bycat[c.split("(")[0]].append(r)
    def rng(vals):
        vals = list(vals)
        if not vals: return "-"
        a, b = min(vals), max(vals)
        return f"{a:g}" if abs(a - b) < 1e-6 else f"{a:.3g}~{b:.3g}"
    for c, rs in bycat.items():
        shapes = collections.Counter(SHAPE[r.type] for r in rs)
        modes = collections.Counter(MODE[r.mode] for r in rs)
        sz0 = rng(r.size[0] for r in rs); sz1 = rng(r.size[1] for r in rs if r.type != 0); sz2 = rng(r.size[2] for r in rs if r.type == 1)
        P(f"| {c} | {len(rs)} | {dict(shapes)} | {dict(modes)} | r/w {sz0}; h {sz1}; d {sz2} | {rng(r.mass for r in rs)} | {rng(r.velocity_attenuation for r in rs)} | {rng(r.rotation_attenuation for r in rs)} | {rng(r.bounce for r in rs)} | {rng(r.friction for r in rs)} |")
    # joints by category of B body
    P("\n| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |")
    P("|---|---|---|---|---|---|")
    jby = collections.defaultdict(list)
    for j in m.joints:
        cb = cats[j.dest_rigid].split("(")[0] if j.dest_rigid is not None and 0 <= j.dest_rigid < len(cats) else "?"
        jby[cb].append(j)
    for c, js in jby.items():
        mv = collections.Counter((tuple(round(x, 3) for x in j.minimum_location), tuple(round(x, 3) for x in j.maximum_location)) for j in js)
        rt = collections.Counter((tuple(round(x * DEG, 1) for x in j.minimum_rotation), tuple(round(x * DEG, 1) for x in j.maximum_rotation)) for j in js)
        st = collections.Counter(tuple(round(x, 2) for x in j.spring_constant) for j in js)
        sr = collections.Counter(tuple(round(x, 2) for x in j.spring_rotation_constant) for j in js)
        P(f"| {c} | {len(js)} | {dict(mv)} | {dict(rt)} | {dict(st)} | {dict(sr)} |")
    # chains
    adj = collections.defaultdict(list)
    for j in m.joints:
        if j.src_rigid is not None and j.dest_rigid is not None:
            adj[j.src_rigid].append(j.dest_rigid)
    has_parent = {j.dest_rigid for j in m.joints}
    P("\nchains (root → … ; mode letters s=static d=dynamic b=dyn+bone):")
    seen = set()
    for i, r in enumerate(m.rigids):
        if i in has_parent and m.rigids[i].mode != 0: continue
        if i not in adj: continue
        for c0 in adj[i]:
            chain = [i, c0]; cur = c0
            while len(adj.get(cur, [])) == 1:
                cur = adj[cur][0]; chain.append(cur)
            branch = len(adj.get(cur, [])) > 1
            P(f"- [{cats[c0].split('(')[0]}] " + " → ".join(f"{m.rigids[k].name}({'sdb'[m.rigids[k].mode]})" for k in chain) + (" …(branches)" if branch else "") + f"  segments(dynamic)={sum(1 for k in chain if m.rigids[k].mode != 0)}")
    return m, cats

if __name__ == "__main__":
    allcats = {}
    for k in ["Inase18_V1", "Reika18_None", "Bunny18_None", "Czern18_V1", "Lucy18_V1", "Own_TifaGantz", "Own_inase430"]:
        m, cats = summarize(k)
        allcats[k] = cats
    open(os.path.join(HERE, "out", "physics.md"), "w", encoding="utf-8").write("\n".join(OUT))
    json.dump(allcats, open(os.path.join(HERE, "out", "physics_cats.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("\n".join(OUT))
