# -*- coding: utf-8 -*-
import sys, os, math, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pmxlib, models

DEG = 180.0 / math.pi

STD_BONES = ["全ての親", "センター", "グルーブ", "腰", "上半身", "上半身1", "上半身2", "上半身3", "下半身",
             "首", "首1", "頭", "両目", "左目", "右目", "操作中心"]
SIDE_BONES = ["肩P", "肩", "肩C", "腕", "腕捩", "腕捩1", "腕捩2", "腕捩3", "ひじ", "手捩", "手捩1", "手捩2", "手捩3",
              "手首", "ダミー", "親指０", "親指１", "親指２", "人指１", "人指２", "人指３", "中指１", "中指２", "中指３",
              "薬指１", "薬指２", "薬指３", "小指１", "小指２", "小指３",
              "足", "ひざ", "足首", "つま先", "足D", "ひざD", "足首D", "足先EX", "腰キャンセル", "足IK親", "足ＩＫ", "つま先ＩＫ"]

def bname(m, i):
    if i is None or i < 0 or i >= len(m.bones):
        return "-" if (i is None or i < 0) else f"#{i}?"
    return m.bones[i].name

def find_bone(m, name):
    for i, b in enumerate(m.bones):
        if b.name == name:
            return i
    return None

def side_name(side, base):
    # 腰キャンセル uses suffix: 腰キャンセル左 ; others prefix
    if base == "腰キャンセル":
        return base + side
    return side + base

def bpos(m, name):
    i = find_bone(m, name)
    if i is None:
        return None
    return np.array(m.bones[i].location, dtype=float)

def flags_str(b):
    f = []
    f.append("R" if b.isRotatable else "-")
    f.append("M" if b.isMovable else "-")
    f.append("V" if b.visible else "-")
    f.append("C" if b.isControllable else "-")
    s = "".join(f)
    extra = []
    if b.isIK: extra.append("IK")
    if b.hasAdditionalRotate: extra.append("付R")
    if b.hasAdditionalLocation: extra.append("付M")
    if b.axis is not None: extra.append("軸")
    if b.localCoordinate is not None: extra.append("ロ")
    if b.transAfterPhis: extra.append("物後")
    if b.externalTransKey is not None: extra.append("外")
    return s + ("," + ",".join(extra) if extra else "")

def fmtv(v, n=3):
    if v is None: return "-"
    return "(" + ", ".join(f"{x:.{n}f}" for x in v) + ")"

def children_map(m):
    ch = collections.defaultdict(list)
    for i, b in enumerate(m.bones):
        if b.parent is not None and b.parent >= 0:
            ch[b.parent].append(i)
    return ch

def descendants(m, i, ch=None):
    ch = ch or children_map(m)
    out = []
    st = [i]
    while st:
        x = st.pop()
        for c in ch.get(x, []):
            out.append(c); st.append(c)
    return out

def quat_to_axis_angle(q):
    x, y, z, w = q
    w = max(-1.0, min(1.0, w))
    ang = 2 * math.acos(abs(w)) * DEG
    s = math.sqrt(max(0.0, 1 - w * w))
    if s < 1e-8:
        return ang, (0.0, 0.0, 0.0)
    sg = 1 if w >= 0 else -1
    return ang, (sg * x / s, sg * y / s, sg * z / s)

def quat_to_euler_yxz(q):
    # PMX/MMD convention: R = Ry * Rx * Rz (PMXE displays X,Y,Z deg). Use standard extraction.
    x, y, z, w = q
    # rotation matrix (right-handed math on given components)
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    m00 = 1 - 2 * (yy + zz); m01 = 2 * (xy - wz); m02 = 2 * (xz + wy)
    m10 = 2 * (xy + wz); m11 = 1 - 2 * (xx + zz); m12 = 2 * (yz - wx)
    m20 = 2 * (xz - wy); m21 = 2 * (yz + wx); m22 = 1 - 2 * (xx + yy)
    # YXZ: R = Ry Rx Rz -> m12 = -sin(x)
    sx = -m12
    sx = max(-1.0, min(1.0, sx))
    ax = math.asin(sx)
    if abs(sx) < 0.9999:
        ay = math.atan2(m02, m22)
        az = math.atan2(m10, m11)
    else:
        ay = math.atan2(-m20, m00); az = 0.0
    return (ax * DEG, ay * DEG, az * DEG)

def angle_below_horizontal(v):
    return math.degrees(math.atan2(-v[1], math.hypot(v[0], v[2])))

def angle_between(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9: return float('nan')
    c = float(np.dot(a, b) / (na * nb))
    return math.degrees(math.acos(max(-1, min(1, c))))

def cp932_len(s):
    try:
        return len(s.encode('cp932'))
    except UnicodeEncodeError:
        return None

def non_cp932_chars(s):
    bad = []
    for ch in s:
        try:
            ch.encode('cp932')
        except UnicodeEncodeError:
            bad.append(ch)
    return bad

# ----------------------------------------------------------------------------------
def weights_per_bone(m):
    """returns dict bone -> (count_vertices_w>0, sum_w, ymin, ymax) and per-vertex nonzero influence count"""
    bidx, bw, co = m.np_bidx, m.np_bw, m.np_co
    nb = len(m.bones)
    cnt = np.zeros(nb + 1, dtype=np.int64); sm = np.zeros(nb + 1)
    ymin = np.full(nb + 1, np.inf); ymax = np.full(nb + 1, -np.inf)
    for k in range(4):
        b = bidx[:, k]; w = bw[:, k]
        mask = (b >= 0) & (w > 0)
        bb = b[mask]; ww = w[mask]; yy = co[mask, 1]
        np.add.at(cnt, bb, 1)
        np.add.at(sm, bb, ww)
        np.minimum.at(ymin, bb, yy)
        np.maximum.at(ymax, bb, yy)
    return cnt[:nb], sm[:nb], ymin[:nb], ymax[:nb]

def vertex_weight_of(m, bone_set):
    """per-vertex total weight of bones in bone_set"""
    bidx, bw = m.np_bidx, m.np_bw
    s = np.zeros(len(bidx))
    arr = np.array(sorted(bone_set), dtype=np.int64) if bone_set else np.zeros(0, dtype=np.int64)
    for k in range(4):
        s += np.where(np.isin(bidx[:, k], arr), bw[:, k], 0.0)
    return s
