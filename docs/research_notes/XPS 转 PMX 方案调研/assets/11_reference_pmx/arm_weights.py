# -*- coding: utf-8 -*-
"""Arm twist split profiles (PMX) vs XPS bend/twist, plus spine split and influences."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pmxlib, models
from anal import *
from anal2 import *
from scale_pairs import load_xps

OUT = []
def P(s=""): OUT.append(s)

def arm_profile_pmx(key, side="左"):
    m = pmxlib.load(models.PATHS[key])
    idx = {b.name: i for i, b in enumerate(m.bones)}
    pa = np.array(m.bones[idx[side + "腕"]].location); pe = np.array(m.bones[idx[side + "ひじ"]].location); pw = np.array(m.bones[idx[side + "手首"]].location)
    co = m.np_co
    groups = [[side + "肩"], [side + "腕"], [side + "腕捩"], [side + "腕捩1"], [side + "腕捩2"], [side + "腕捩3"], [side + "ひじ"], [side + "手捩"], [side + "手捩1"], [side + "手捩2"], [side + "手捩3"], [side + "手首"]]
    groups = [g for g in groups if all(n in idx for n in g)]
    W = [vertex_weight_of(m, {idx[n] for n in g}) for g in groups]
    tot = sum(W)
    # param s: 0 at 腕, 1 at ひじ, 2 at 手首 (projection onto segments)
    def proj(p0, p1):
        d = p1 - p0; L2 = d @ d
        return ((co - p0) @ d) / L2
    s1 = proj(pa, pe); s2 = proj(pe, pw)
    s = np.where(s1 <= 1.0, s1, 1.0 + s2)
    sel = tot > 0.5
    P(f"\n### {key} {side} arm: weights vs position s (0=腕 head, 1=ひじ head, 2=手首 head); twist bone positions:")
    for n in [side + "腕捩", side + "腕捩1", side + "腕捩2", side + "腕捩3", side + "手捩", side + "手捩1", side + "手捩2", side + "手捩3"]:
        if n in idx:
            p = np.array(m.bones[idx[n]].location)
            ss = (p - pa) @ (pe - pa) / ((pe - pa) @ (pe - pa)) if "腕" in n else 1 + (p - pe) @ (pw - pe) / ((pw - pe) @ (pw - pe))
            P(f"- {n}: s={ss:.3f}")
    names = ["/".join(g) for g in groups]
    P("| s bin | nV | " + " | ".join(names) + " |")
    P("|---|---|" + "---|" * len(names))
    for a in np.arange(-0.25, 2.25, 0.125):
        b = a + 0.125
        q = sel & (s >= a) & (s < b)
        n = int(q.sum())
        if n == 0: continue
        P(f"| {a:.3f}..{b:.3f} | {n} | " + " | ".join(f"{w[q].mean():.2f}" for w in W) + " |")

def arm_profile_xps(name, f, c, side="l"):
    J, co, mesh, g, w, xb = load_xps(name)
    names = [b["name"] for b in J["bones"]]
    co = co.copy(); co[:, 1] = (co[:, 1] + c) * f; co[:, 0] *= f; co[:, 2] *= f
    def H(n):
        h = xb[n]["head"].copy(); return np.array([h[0] * f, (h[1] + c) * f, h[2] * f])
    pa, pe, pw = H(side + "ShldrBend"), H(side + "ForearmBend"), H(side + "Hand")
    groups = [side + "Collar", side + "ShldrBend", side + "ShldrTwist", side + "ForearmBend", side + "ForearmTwist", side + "Hand"]
    W = []
    for n in groups:
        i = names.index(n); W.append(np.where(g == i, w, 0).sum(1))
    tot = sum(W)
    def proj(p0, p1):
        d = p1 - p0; L2 = d @ d
        return ((co - p0) @ d) / L2
    s1 = proj(pa, pe); s2 = proj(pe, pw)
    s = np.where(s1 <= 1.0, s1, 1.0 + s2)
    sel = tot > 0.5
    P(f"\n### XPS {name} {side} arm (T-pose source): weights vs s; twist bone heads: ShldrTwist s={((H(side+'ShldrTwist')-pa)@(pe-pa))/((pe-pa)@(pe-pa)):.3f}, ForearmTwist s={1+((H(side+'ForearmTwist')-pe)@(pw-pe))/((pw-pe)@(pw-pe)):.3f}")
    P("| s bin | nV | " + " | ".join(groups) + " |")
    P("|---|---|" + "---|" * len(groups))
    for a in np.arange(-0.25, 2.25, 0.125):
        b = a + 0.125
        q = sel & (s >= a) & (s < b)
        n = int(q.sum())
        if n == 0: continue
        P(f"| {a:.3f}..{b:.3f} | {n} | " + " | ".join(f"{x[q].mean():.2f}" for x in W) + " |")

def spine_profile(key):
    m = pmxlib.load(models.PATHS[key])
    idx = {b.name: i for i, b in enumerate(m.bones)}
    names = [n for n in ["下半身", "上半身", "上半身1", "上半身2", "上半身3", "首", "首1", "頭", "左乳奶", "右乳奶", "左肩", "右肩"] if n in idx]
    W = [vertex_weight_of(m, {idx[n]}) for n in names]
    co = m.np_co
    sel = (np.abs(co[:, 0]) < 1.0) & (sum(W) > 0.5)
    P(f"\n### {key} torso (|x|<1.0) weights vs Y; bone heads: " + ", ".join(f"{n}={m.bones[idx[n]].location[1]:.2f}" for n in names[:8]))
    P("| Y bin | nV | " + " | ".join(names) + " |")
    P("|---|---|" + "---|" * len(names))
    y0 = m.bones[idx["下半身"]].location[1] - 1.5
    for a in np.arange(y0, y0 + 8.0, 0.5):
        q = sel & (co[:, 1] >= a) & (co[:, 1] < a + 0.5)
        n = int(q.sum())
        if n == 0: continue
        P(f"| {a:.2f}..{a+0.5:.2f} | {n} | " + " | ".join(f"{w[q].mean():.2f}" for w in W) + " |")

if __name__ == "__main__":
    arm_profile_pmx("Inase18_None")
    arm_profile_xps("inase_xps", 10.9376, 0.0847)
    arm_profile_pmx("Reika18_None")
    arm_profile_pmx("Bunny18_None")
    arm_profile_pmx("Lucy18_None")
    spine_profile("Inase18_None")
    spine_profile("Bunny18_None")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "arm_spine.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))
