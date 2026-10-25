# -*- coding: utf-8 -*-
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scale_pairs import load_xps
from anal import angle_below_horizontal, angle_between

def seg_angles(b, a, c):
    v = b[c]["head"] - b[a]["head"]
    return angle_below_horizontal(v), math.degrees(math.atan2(-v[2], abs(v[0])))

def pose_report(name, chains):
    J, co, mesh, g, w, b = load_xps(name)
    print(f"== {name}: nbones={len(b)} H={co[:,1].max()-co[:,1].min():.4f} minY={co[:,1].min():.4f}")
    for lab, a, c in chains:
        if a in b and c in b:
            d, f = seg_angles(b, a, c)
            print(f"   {lab:28s} {a}->{c}: below-horiz {d:7.2f}  fwd {f:7.2f}")
    return b

def diff(n1, n2):
    _, _, _, _, _, b1 = load_xps(n1)
    _, _, _, _, _, b2 = load_xps(n2)
    mx = 0; worst = None
    for k in b1:
        if k in b2:
            d = np.linalg.norm(b1[k]["head"] - b2[k]["head"])
            if d > mx: mx, worst = d, k
    print(f"   max head diff {n1} vs {n2}: {mx:.5f} ({worst})")

DAZ = [("shoulder 肩→腕", "lCollar", "lShldrBend"), ("upper arm 腕→ひじ", "lShldrBend", "lForearmBend"), ("forearm ひじ→手首", "lForearmBend", "lHand"),
       ("R upper arm", "rShldrBend", "rForearmBend"), ("R forearm", "rForearmBend", "rHand"),
       ("thigh 足→ひざ", "lThighBend", "lShin"), ("shin ひざ→足首", "lShin", "lFoot"), ("foot 足首→toe", "lFoot", "lToe"),
       ("hand→mid1", "lHand", "lMid1"), ("index1→3", "lIndex1", "lIndex3"), ("thumb2→3", "lThumb2", "lThumb3")]
for n in ["inase_xps", "inase_np", "reika_xps", "reika_np"]:
    pose_report(n, DAZ)
diff("inase_xps", "inase_np"); diff("reika_xps", "reika_np"); diff("tifa_xps", "tifa_np"); diff("inase_xps", "inase_xps_defpose")
# tifa / reikaG: list bone names to find arm chain
for n in ["tifa_xps", "reikaG_xps"]:
    J, co, mesh, g, w, b = load_xps(n)
    print(n, list(b.keys())[:140])
