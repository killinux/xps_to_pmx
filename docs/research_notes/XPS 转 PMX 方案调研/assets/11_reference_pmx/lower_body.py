# -*- coding: utf-8 -*-
"""下半身 construction and weight-boundary analysis, PMX (18 series + owner's) and XPS sources."""
import sys, os, json, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pmxlib, models
from anal import *
from anal2 import *
from scale_pairs import load_xps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = []
def P(*a):
    OUT.append(" ".join(str(x) for x in a))

BINS = np.arange(-2.5, 2.51, 0.25)

def pmx_groups(m):
    idx = {b.name: i for i, b in enumerate(m.bones)}
    ch = children_map(m)
    def chain(name):
        if name not in idx: return set()
        i = idx[name]
        return {i} | set(descendants(m, i, ch))
    up = set()
    for n in ["上半身"]:
        up |= chain(n)
    # remove arms/head? keep whole upper chain but report separately spine vs others
    spine = {idx[n] for n in ["上半身", "上半身1", "上半身2", "上半身3"] if n in idx}
    lower = {idx["下半身"]} if "下半身" in idx else set()
    legs = set()
    for n in ["左足", "右足", "左足D", "右足D", "腰キャンセル左", "腰キャンセル右"]:
        legs |= chain(n)
    lower_children = set(descendants(m, idx["下半身"], ch)) - legs if "下半身" in idx else set()
    return idx, spine, up, lower, legs, lower_children

def profile(co, wsets, y0, y1, names, mask=None, title=""):
    """weights vs normalized height t=(y-y0)/(y1-y0)."""
    t = (co[:, 1] - y0) / (y1 - y0)
    any_w = np.zeros(len(co), dtype=bool)
    for w in wsets: any_w |= w > 0
    if mask is not None: any_w &= mask
    P(f"\n{title}  (t=0 at 足 head Y={y0:.3f}, t=1 at 上半身 head Y={y1:.3f}); vertices considered = those with weight on any listed group")
    P("| t bin | Y range | nV | " + " | ".join(f"mean w {n}" for n in names) + " | nV with 0<w(" + names[0] + ")<1 |")
    P("|---|---|---|" + "---|" * len(names) + "---|")
    rows = []
    for a, b in zip(BINS[:-1], BINS[1:]):
        sel = any_w & (t >= a) & (t < b)
        n = int(sel.sum())
        if n == 0: continue
        means = [float(w[sel].mean()) for w in wsets]
        partial = int(((wsets[0][sel] > 0.001) & (wsets[0][sel] < 0.999)).sum())
        P(f"| {a:+.3f}..{b:+.3f} | {y0+a*(y1-y0):.2f}..{y0+b*(y1-y0):.2f} | {n} | " + " | ".join(f"{x:.3f}" for x in means) + f" | {partial} |")
        rows.append((a, b, n, means, partial))
    return rows

def pmx_lower(key):
    m = pmxlib.load(models.PATHS[key])
    idx, spine, up, lower, legs, lower_children = pmx_groups(m)
    P(f"\n## {key}")
    if not lower:
        P("no 下半身"); return
    lb = m.bones[idx["下半身"]]
    ub = m.bones[idx["上半身"]] if "上半身" in idx else None
    lh = np.array(lb.location)
    tail = lb.displayConnection
    tail_pos = (np.array(m.bones[tail].location) if isinstance(tail, int) and tail >= 0 else lh + np.array(tail))
    legL = np.array(m.bones[idx["左足"]].location); legR = np.array(m.bones[idx["右足"]].location)
    uh = np.array(ub.location) if ub else None
    ch = children_map(m)
    P(f"下半身 head={fmtv(lh)} tail={fmtv(tail_pos)} (tail-head={fmtv(tail_pos-lh)}) parent={bname(m, lb.parent)} flags={flags_str(lb)}")
    if ub is not None:
        P(f"上半身 head={fmtv(uh)} parent={bname(m, ub.parent)}; 下半身-上半身 head ΔY={lh[1]-uh[1]:+.4f} ΔZ={lh[2]-uh[2]:+.4f}")
    P(f"左足 head={fmtv(legL)} 右足 head={fmtv(legR)}; 下半身 head − 足 head ΔY={lh[1]-legL[1]:+.3f} (= {(lh[1]-legL[1])/ (m.np_co[:,1].max()-m.np_co[:,1].min())*100:.2f}% of H); 下半身 tail Y − 足 Y = {tail_pos[1]-legL[1]:+.3f}")
    P("children of 下半身: " + ", ".join(bname(m, c) for c in ch.get(idx["下半身"], [])))
    cnt, sm, ymin, ymax = weights_per_bone2(m)
    i = idx["下半身"]
    P(f"下半身 weights: nV={cnt[i]} Σw={sm[i]:.1f} Y range {ymin[i]:.3f}..{ymax[i]:.3f}; Σw/nV={sm[i]/max(cnt[i],1):.3f}")
    wl = vertex_weight_of(m, lower)
    ws = vertex_weight_of(m, spine)
    wleg = vertex_weight_of(m, legs)
    wother = vertex_weight_of(m, lower_children)
    # histogram of 下半身 weight values
    h = np.histogram(wl[wl > 0], bins=[0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.999, 1.001])[0]
    P("下半身 weight-value histogram (0-.1,.1-.25,.25-.5,.5-.75,.75-.9,.9-.999,=1): " + ", ".join(map(str, h)))
    # Y quantiles of vertices with 下半身 weight > 0.5
    yy = m.np_co[wl > 0.5, 1]
    if len(yy):
        q = np.quantile(yy, [0, 0.05, 0.5, 0.95, 1])
        P("Y quantiles (0,5,50,95,100%) of vertices with w(下半身)>0.5: " + ", ".join(f"{x:.2f}" for x in q))
    other_names = ", ".join(sorted(m.bones[c].name for c in lower_children))
    names4 = ["下半身", "上半身..3", "足系(足/足D/腰キャンセル+子)", "下半身の他の子"]
    P("下半身の他の子 = " + other_names[:300])
    body = wother <= 0
    rows = profile(m.np_co, [wl, ws, wleg, wother], legL[1], uh[1], names4, mask=body, title=f"{key} weight profile, excluding vertices weighted to 下半身's other children (genitals/butt/etc.)")
    ax = np.abs(m.np_co[:, 0])
    halfw = abs(legL[0])
    profile(m.np_co, [wl, ws, wleg, wother], legL[1], uh[1], names4, mask=body & (ax < 0.35 * halfw), title=f"{key} CENTER strip |x|<0.35*足X({0.35*halfw:.2f})")
    profile(m.np_co, [wl, ws, wleg, wother], legL[1], uh[1], names4, mask=body & (ax > 1.2 * halfw), title=f"{key} SIDE |x|>1.2*足X({1.2*halfw:.2f})")
    return dict(key=key, lh=lh.tolist(), uh=uh.tolist(), leg=legL.tolist(), tail=tail_pos.tolist(), rows=rows)

def xps_lower(name, f, c, lower_names, spine_names, leg_names, other_names, title):
    J, co, mesh, g, w, xb = load_xps(name)
    names = [b["name"] for b in J["bones"]]
    nidx = {n: i for i, n in enumerate(names)}
    def wsum(ns):
        s = np.zeros(len(co))
        ids = [nidx[n] for n in ns if n in nidx]
        for k in range(g.shape[1]):
            s += np.where(np.isin(g[:, k], ids), w[:, k], 0.0)
        return s
    co2 = co.copy(); co2[:, 1] = (co2[:, 1] + c) * f; co2[:, 0] *= f; co2[:, 2] *= f
    P(f"\n## XPS {name} ({title}); coordinates scaled ×{f} and grounded like the PMX")
    for n in ["hip", "pelvis", "abdomenLower", "abdomenUpper", "lThighBend", "rThighBend", "lThighTwist"]:
        if n in xb:
            h = xb[n]["head"]; t = xb[n]["tail"]
            P(f"{n}: head=({h[0]*f:.3f},{(h[1]+c)*f:.3f},{h[2]*f:.3f}) tail=({t[0]*f:.3f},{(t[1]+c)*f:.3f},{t[2]*f:.3f}) parent={xb[n]['parent']}")
    # per bone weight stats for relevant groups
    for n in lower_names + spine_names[:2] + ["lThighBend", "lThighTwist", "rThighBend"]:
        if n in nidx:
            s = wsum([n])
            sel = s > 0
            if sel.sum():
                P(f"  group {n}: nV={int(sel.sum())} Σw={s.sum():.1f} Y {co2[sel,1].min():.3f}..{co2[sel,1].max():.3f}")
            else:
                P(f"  group {n}: nV=0")
    leg_y = (xb["lThighBend"]["head"][1] + c) * f
    up_y = (xb["abdomenLower"]["head"][1] + c) * f
    wl = wsum(lower_names); ws = wsum(spine_names); wleg = wsum(leg_names); wo = wsum(other_names)
    h = np.histogram(wl[wl > 0], bins=[0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.999, 1.001])[0]
    P(f"  {'+'.join(lower_names)} weight-value histogram (0-.1,.1-.25,.25-.5,.5-.75,.75-.9,.9-.999,=1): " + ", ".join(map(str, h)))
    nm = ["+".join(lower_names), "+".join(spine_names), "+".join(leg_names)[:40], "+".join(other_names)[:40]]
    body = wo <= 0
    profile(co2, [wl, ws, wleg, wo], leg_y, up_y, nm, mask=body, title=f"XPS {name} weight profile (excluding genital groups)")
    halfw = abs(xb["lThighBend"]["head"][0] * f)
    ax = np.abs(co2[:, 0])
    profile(co2, [wl, ws, wleg, wo], leg_y, up_y, nm, mask=body & (ax < 0.35 * halfw), title=f"XPS {name} CENTER strip |x|<{0.35*halfw:.2f}")
    profile(co2, [wl, ws, wleg, wo], leg_y, up_y, nm, mask=body & (ax > 1.2 * halfw), title=f"XPS {name} SIDE |x|>{1.2*halfw:.2f}")
    # pelvis-only (without hip) and abdomenLower-only stats
    for n in ["pelvis", "abdomenLower", "hip"]:
        if n in nidx:
            s1 = wsum([n]); sel = s1 > 0
            if sel.sum():
                q = np.quantile(co2[s1 > 0.5, 1], [0, 0.05, 0.5, 0.95, 1]) if (s1 > 0.5).sum() else []
                P(f"  {n}: nV={int(sel.sum())} Σw={s1.sum():.1f}; Y quantiles of w>0.5: " + ", ".join(f"{x:.2f}" for x in q))

if __name__ == "__main__":
    for k in ["Inase18_None", "Inase18_V1", "Reika18_None", "Bunny18_None", "Czern18_None", "Lucy18_None", "Own_TifaGantz", "Own_inaseCleanIK", "Own_inase430"]:
        try:
            pmx_lower(k)
        except Exception as e:
            P(f"\n## {k}: ERROR {e!r}")
    xps_lower("inase_xps", 10.9376, 0.0847, ["hip", "pelvis"], ["abdomenLower", "abdomenUpper", "chestLower", "chestUpper"],
              ["lThighBend", "lThighTwist", "rThighBend", "rThighTwist", "lShin", "rShin"], ["Genitals", "Anus"], "Inase source")
    xps_lower("reika_xps", 11.4247, 0.0196, ["hip", "pelvis"], ["abdomenLower", "abdomenUpper", "chestLower", "chestUpper"],
              ["lThighBend", "lThighTwist", "rThighBend", "rThighTwist", "lShin", "rShin"], ["Genitals", "Anus", "Rectum", "Colon", "Vagina"], "Reika source")
    open(os.path.join(HERE, "out", "lower_body.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))
