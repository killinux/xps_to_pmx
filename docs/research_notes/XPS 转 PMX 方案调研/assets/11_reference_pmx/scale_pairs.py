# -*- coding: utf-8 -*-
"""Scale comparison PMX vs XPS (same model pairs). XPS in Blender coords -> PMX-like (x, z, y)."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pmxlib, models
from anal import *

HERE = os.path.dirname(os.path.abspath(__file__))

def load_xps(name):
    J = json.load(open(os.path.join(HERE, "xps", name + ".json"), encoding="utf-8"))
    Z = np.load(os.path.join(HERE, "xps", name + ".npz"))
    co = Z["co"][:, [0, 2, 1]]  # -> PMX-like: X, Y(up), Z(=blender Y, front=-)
    bones = {b["name"]: dict(head=np.array(b["head"])[[0, 2, 1]], tail=np.array(b["tail"])[[0, 2, 1]], parent=b["parent"]) for b in J["bones"]}
    return J, co, Z["mesh"], Z["g"], Z["w"], bones

def pmx_material_vertices(m):
    """returns list of (material name, vertex index array)"""
    out = []
    fi = 0
    F = np.array(m.faces, dtype=np.int64)
    for mt in m.materials:
        n = mt.vertex_count // 3
        idx = np.unique(F[fi:fi + n].reshape(-1)) if n else np.zeros(0, dtype=np.int64)
        out.append((mt.name, idx))
        fi += n
    return out

def strip_xps_mat(n):
    # "4_+Swimsuit_0.1_0_0" -> "+Swimsuit"
    parts = n.split("_")
    if parts[0].isdigit():
        parts = parts[1:]
    # drop trailing numeric params (3)
    while parts and all(c in "0123456789.-" for c in parts[-1]) and len(parts) > 1:
        parts = parts[:-1]
    return "_".join(parts)

def compare(pmx_key, xps_name, out):
    m = pmxlib.load(models.PATHS[pmx_key])
    J, xco, xmesh, xg, xw, xb = load_xps(xps_name)
    out.append(f"\n### {pmx_key} vs {xps_name}\n")
    pco = m.np_co
    pmin, pmax = pco.min(0), pco.max(0)
    xmin, xmax = xco.min(0), xco.max(0)
    out.append(f"PMX bbox {fmtv(pmin)}..{fmtv(pmax)} H={pmax[1]-pmin[1]:.4f}; XPS bbox {fmtv(xmin,4)}..{fmtv(xmax,4)} H={xmax[1]-xmin[1]:.4f}; ratio H={ (pmax[1]-pmin[1])/(xmax[1]-xmin[1]):.4f}\n")
    # per-material bbox ratio
    pm = pmx_material_vertices(m)
    xm = {}
    for mi, mobj in enumerate(J["meshes"]):
        nm = strip_xps_mat(mobj["name"])
        xm[nm] = np.where(xmesh == mi)[0]
    rows = []
    ratios = []
    for name, idx in pm:
        key = name
        if key not in xm:
            continue
        a = pco[idx]; b = xco[xm[key]]
        if len(a) < 10 or len(b) < 10: continue
        sa = a.max(0) - a.min(0); sb = b.max(0) - b.min(0)
        r = sa / np.where(sb == 0, np.nan, sb)
        # offset: translation of bbox center after scaling by ratio_y
        rows.append((name, len(a), len(b), r, a.min(0), b.min(0)))
    out.append("| material | nV pmx | nV xps | size ratio X | Y | Z | PMX minY | XPS minY |\n|---|---|---|---|---|---|---|---|\n")
    for name, na, nb, r, amin, bmin in rows:
        out.append(f"| {name} | {na} | {nb} | {r[0]:.4f} | {r[1]:.4f} | {r[2]:.4f} | {amin[1]:.4f} | {bmin[1]:.4f} |\n")
    # bone pair distances using name_e == xps bone name
    pmap = {}
    for i, b in enumerate(m.bones):
        if b.name_e in xb:
            pmap[b.name_e] = np.array(b.location)
    pairs = [("hip", "head"), ("lEye", "rEye"), ("lCollar", "rCollar"), ("abdomenLower", "chestUpper"), ("neckLower", "head"),
             ("lThighBend", "rThighBend"), ("lShldrBend", "rShldrBend"), ("lShldrBend", "lForearmBend"), ("lForearmBend", "lHand"),
             ("lThighBend", "lShin"), ("lShin", "lFoot"), ("lEar", "rEar"), ("chestLower", "head")]
    out.append("\n| bone pair (DAZ name = PMX name_e) | XPS dist | PMX dist | ratio |\n|---|---|---|---|\n")
    for a, b in pairs:
        if a in pmap and b in pmap and a in xb and b in xb:
            dx = np.linalg.norm(xb[a]["head"] - xb[b]["head"]); dp = np.linalg.norm(pmap[a] - pmap[b])
            out.append(f"| {a}–{b} | {dx:.4f} | {dp:.4f} | {dp/dx:.4f} |\n")
    # translation: compare head bone after scaling
    if "head" in pmap and "head" in xb:
        for f in [12.5]:
            pass
    return m, J, xco, xb, pmap

if __name__ == "__main__":
    out = []
    compare("Inase18_V1", "inase_xps", out)
    compare("Inase18_None", "inase_xps", out)
    compare("Own_inaseCleanIK", "inase_xps", out)
    compare("Own_329conv", "inase_xps", out)
    compare("Reika18_None", "reika_xps", out)
    compare("Reika18_V1", "reika_xps", out)
    compare("Own_TifaGantz", "tifa_xps", out)
    open(os.path.join(HERE, "out", "scale_pairs.md"), "w", encoding="utf-8").write("".join(out))
    print("".join(out))
