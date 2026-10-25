# -*- coding: utf-8 -*-
"""Generate markdown tables for the report from out/*.json"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models
HERE = os.path.dirname(os.path.abspath(__file__))
DEG = 180 / math.pi

def L(k):
    return json.load(open(os.path.join(HERE, "out", k + ".json"), encoding="utf-8"))

def f3(v):
    return "(" + ", ".join(f"{x:.3f}" for x in v) + ")"

def bone_table(key, include):
    S = L(key); B = S["bones"]
    name = lambda i: B[i]["name"] if i is not None and 0 <= i < len(B) else "-"
    out = ["| # | name_j | name_e | 親 | 位置 | flags | 層 | 付与(親×率) | 軸固定 / ローカル軸 | IK | nV |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in B:
        if not include(b): continue
        add = f"{name(b['add'][0])}×{b['add'][1]:.2f}" if b["add"] else ""
        ax = ""
        if b["axis"]: ax = "軸" + f3(b["axis"])
        if b["local"]: ax += ("; " if ax else "") + "x" + f3(b["local"][0]) + " z" + f3(b["local"][1])
        ik = ""
        if b["ik"]:
            t, loop, unit, links = b["ik"]
            ls = []
            for (lt, mn, mx) in links:
                if mn is not None:
                    ls.append(f"{name(lt)}[X {mn[0]*DEG:.1f}~{mx[0]*DEG:.1f}]")
                else:
                    ls.append(name(lt))
            ik = f"T={name(t)} loop={loop} 単位角={unit*DEG:.1f}° links: " + ", ".join(ls)
        out.append(f"| {b['i']} | {b['name']} | {b['name_e']} | {name(b['parent'])} | {f3(b['pos'])} | {b['flags']} | {b['layer']} | {add} | {ax} | {ik} | {b['nV']} |")
    return "\n".join(out)

def rigid_table(key):
    S = L(key)
    out = ["| # | 名称 | 骨 | 形状 | 尺寸 | 位置−骨 | 旋转° | 质量 | 移动衰减 | 旋转衰减 | 反弹 | 摩擦 | 模式 | 组 | 非碰撞组 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in S["rigids"]:
        sz = f"r={r['size'][0]:.3f}" if r["shape"] == "sphere" else (f"r={r['size'][0]:.3f} h={r['size'][1]:.3f}" if r["shape"] == "capsule" else f"{r['size'][0]:.3f}×{r['size'][1]:.3f}×{r['size'][2]:.3f}")
        rel = f3(r["rel"]) if r["rel"] else "-"
        rot = "(" + ", ".join(f"{x:.1f}" for x in r["rot"]) + ")"
        nc = r["noncoll"]
        ncs = "全部(1-16)" if len(nc) == 16 else ",".join(map(str, nc))
        out.append(f"| {r['i']} | {r['name']} | {r['bone']} | {r['shape']} | {sz} | {rel} | {rot} | {r['mass']:g} | {r['ld']:g} | {r['ad']:g} | {r['rest']:g} | {r['fric']:g} | {r['mode']} | {r['group']} | {ncs} |")
    return "\n".join(out)

def joint_table(key):
    S = L(key)
    out = ["| # | 名称 | 刚体A | 刚体B | 位置 | 移动限制 min~max | 旋转限制 min~max (°) | 弹簧(移动) | 弹簧(旋转) |", "|---|---|---|---|---|---|---|---|---|"]
    for j in S["joints"]:
        mv = f3(j["tmin"]) + "~" + f3(j["tmax"])
        rt = "(" + ", ".join(f"{x:.0f}" for x in j["rmin"]) + ")~(" + ", ".join(f"{x:.0f}" for x in j["rmax"]) + ")"
        out.append(f"| {j['i']} | {j['name']} | {j['aname']} | {j['bname']} | {f3(j['loc'])} | {mv} | {rt} | {f3(j['st'])} | {f3(j['sr'])} |")
    return "\n".join(out)

if __name__ == "__main__":
    what = sys.argv[1]
    if what == "bones_inase":
        S = L("Inase18_V1")
        std = set(["操作中心", "全ての親", "センター", "グルーブ", "腰", "下半身", "上半身", "上半身1", "上半身2", "上半身3", "首", "首1", "頭", "両目", "左目", "右目",
                   "左乳奶", "右乳奶", "腰キャンセル左", "腰キャンセル右", "左足", "左ひざ", "左足首", "左足IK親", "左足ＩＫ", "左つま先", "左つま先ＩＫ",
                   "右足", "右ひざ", "右足首", "右足IK親", "右足ＩＫ", "右つま先", "右つま先ＩＫ", "左肩P", "左肩", "左肩C", "左腕", "左腕捩", "左腕捩1", "左腕捩2", "左腕捩3",
                   "左ひじ", "左手捩", "左手捩1", "左手捩2", "左手捩3", "左手首", "左ダミー", "左親指０", "左親指１", "左親指２", "左人指０", "左人指１", "左人指２", "左人指３",
                   "Teeth Upper", "Jaw Bone", "Teeth Lower", "Tongue 1", "QQ26", "QQ12", "QQ7", "lEar", "hair front left 1", "hair front left 2", "Anus", "Genitals", "lSmallToe4", "lBigToe",
                   "右足D", "右ひざD", "右足首D", "右足先EX", "左足D", "左ひざD", "左足首D", "左足先EX"])
        print(bone_table("Inase18_V1", lambda b: b["name"] in std))
    elif what == "rigid":
        print(rigid_table(sys.argv[2]))
    elif what == "joint":
        print(joint_table(sys.argv[2]))
