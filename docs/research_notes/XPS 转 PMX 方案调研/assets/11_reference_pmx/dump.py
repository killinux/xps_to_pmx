# -*- coding: utf-8 -*-
import sys, os, math, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pmxlib, models
from anal import *
from anal2 import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

def md_table(rows, header):
    s = "| " + " | ".join(header) + " |\n|" + "|".join(["---"] * len(header)) + "|\n"
    for r in rows:
        s += "| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |\n"
    return s

def dump(key, path):
    m = pmxlib.load(path)
    L = []
    S = {"key": key, "path": path}
    L.append(f"# {key}\n\n{path}\n\n")
    L.append(f"name={m.name!r} name_e={m.name_e!r}\n\ncomment:\n~~~\n{m.comment[:1500]}\n~~~\ncomment_e:\n~~~\n{m.comment_e[:600]}\n~~~\n")
    L.append(f"V={len(m.np_co)} F={len(m.faces)} Tex={len(m.textures)} Mat={len(m.materials)} Bone={len(m.bones)} Morph={len(m.morphs)} Disp={len(m.display)} RB={len(m.rigids)} J={len(m.joints)} addUV={m.header.additional_uvs} idx(v,t,m,b,mo,r)={m.header.vertex_index_size},{m.header.texture_index_size},{m.header.material_index_size},{m.header.bone_index_size},{m.header.morph_index_size},{m.header.rigid_index_size}\n")
    S.update(name=m.name, name_e=m.name_e, comment=m.comment, V=len(m.np_co), F=len(m.faces), Tex=len(m.textures), Mat=len(m.materials), Bone=len(m.bones), Morph=len(m.morphs), RB=len(m.rigids), J=len(m.joints), addUV=m.header.additional_uvs)
    co = m.np_co
    ch = children_map(m)
    cnt, sm, ymin, ymax = weights_per_bone2(m)

    # ---------------- 1. scale
    L.append("\n## 1. Scale\n")
    mn, mx = co.min(0), co.max(0)
    H = mx[1] - mn[1]
    L.append(f"bbox min={fmtv(mn)} max={fmtv(mx)} size={fmtv(mx-mn)} height={H:.3f} ground(minY)={mn[1]:.4f}\n\n")
    S.update(height=float(H), minY=float(mn[1]), maxY=float(mx[1]), bbox_min=mn.tolist(), bbox_max=mx.tolist())
    rows = []
    bones_y = {}
    for n in ["全ての親", "センター", "グルーブ", "腰", "下半身", "上半身", "上半身1", "上半身2", "上半身3", "首", "首1", "頭", "両目", "左目", "右目",
              "左肩", "左腕", "左ひじ", "左手首", "左足", "左ひざ", "左足首", "左つま先", "左足ＩＫ", "左つま先ＩＫ", "左足D", "左ひざD", "左足首D", "左足先EX"]:
        p = bpos(m, n)
        if p is not None:
            rows.append([n, fmtv(p), f"{(p[1]-mn[1])/H:.3f}"])
            bones_y[n] = p.tolist()
    S["bones_pos"] = bones_y
    L.append(md_table(rows, ["bone", "pos", "Y/height (from ground)"]))

    # ---------------- 2. rest pose
    L.append("\n## 2. Rest pose angles\n")
    pose = {}
    def P(n): return bpos(m, n)
    rows = []
    for side in ["左", "右"]:
        sgn = 1 if side == "左" else -1
        def seg(a, b):
            pa, pb = P(side + a), P(side + b)
            if pa is None or pb is None: return None
            return pb - pa
        r = {}
        for lab, a, b in [("肩→腕", "肩", "腕"), ("腕→ひじ", "腕", "ひじ"), ("ひじ→手首", "ひじ", "手首"), ("腕→手首", "腕", "手首")]:
            v = seg(a, b)
            if v is None: continue
            down = angle_below_horizontal(v)
            fwd = math.degrees(math.atan2(-v[2], abs(v[0])))  # +: toward -Z (front)
            r[lab] = (down, fwd)
        v1, v2 = seg("腕", "ひじ"), seg("ひじ", "手首")
        elbow = angle_between(v1, v2) if v1 is not None and v2 is not None else float('nan')
        t1, t2 = seg("足", "ひざ"), seg("ひざ", "足首")
        knee = angle_between(t1, t2) if t1 is not None and t2 is not None else float('nan')
        kneez = None
        if t1 is not None and t2 is not None:
            pa, pk, pf = P(side + "足"), P(side + "ひざ"), P(side + "足首")
            kneez = float(pk[2] - (pa[2] + (pf[2] - pa[2]) * (pk[1] - pa[1]) / (pf[1] - pa[1]))) if abs(pf[1]-pa[1]) > 1e-6 else None
        legspread = None
        if t1 is not None and P(side + "足首") is not None:
            vv = P(side + "足首") - P(side + "足")
            legspread = math.degrees(math.atan2(vv[0] * sgn, -vv[1]))
        f = seg("足首", "つま先")
        foot = None
        if f is not None:
            toe_out = math.degrees(math.atan2(f[0] * sgn, -f[2]))
            pitch = angle_below_horizontal(f)
            foot = (toe_out, pitch)
        fing = {}
        def fdir(a, b):
            pa, pb = P(side + a), P(side + b)
            if pa is None or pb is None: return None
            v = pb - pa
            return angle_below_horizontal(v), math.degrees(math.atan2(-v[2], abs(v[0])))
        for lab, a, b in [("手首→中指１", "手首", "中指１"), ("人指１→人指３", "人指１", "人指３"), ("中指１→中指３", "中指１", "中指３"),
                          ("小指１→小指３", "小指１", "小指３"), ("親指１→親指２", "親指１", "親指２"), ("親指０→親指２", "親指０", "親指２")]:
            d = fdir(a, b)
            if d is not None: fing[lab] = d
        pose[side] = dict(segs=r, elbow=elbow, knee=knee, kneez=kneez, legspread=legspread, foot=foot, fingers=fing)
        for lab, (down, fwd) in r.items():
            rows.append([side, lab, f"{down:.2f}", f"{fwd:.2f}"])
        rows.append([side, "elbow bend(3D)", f"{elbow:.2f}", ""])
        rows.append([side, "knee bend(3D)", f"{knee:.2f}", f"kneeZ-offset={kneez:.3f}" if kneez is not None else ""])
        rows.append([side, "leg spread (足→足首 from vertical, +outward)", f"{legspread:.2f}" if legspread is not None else "-", ""])
        if foot: rows.append([side, "足首→つま先 toe-out / pitch-down", f"{foot[0]:.2f}", f"{foot[1]:.2f}"])
        for lab, (d, fw) in fing.items():
            rows.append([side, lab, f"{d:.2f}", f"{fw:.2f}"])
    L.append(md_table(rows, ["side", "segment", "deg below horizontal (or angle)", "deg forward(-Z)"]))
    S["pose"] = pose

    # ---------------- 3. bones full dump
    L.append("\n## 3. Bones (full)\n")
    rows = []
    for i, b in enumerate(m.bones):
        add = f"{bname(m, b.additionalTransform[0])}×{b.additionalTransform[1]:.3f}" if b.additionalTransform else ""
        dc = bname(m, b.displayConnection) if isinstance(b.displayConnection, int) else fmtv(b.displayConnection, 2)
        lc = ""
        if b.localCoordinate is not None:
            lc = f"x{fmtv(b.localCoordinate.x_axis,3)} z{fmtv(b.localCoordinate.z_axis,3)}"
        ik = ""
        if b.isIK:
            links = []
            for l in b.ik_links:
                if l.minimumAngle is not None:
                    links.append(f"{bname(m,l.target)}[{','.join(f'{a*DEG:.1f}' for a in l.minimumAngle)}~{','.join(f'{a*DEG:.1f}' for a in l.maximumAngle)}]")
                else:
                    links.append(bname(m, l.target))
            ik = f"T={bname(m,b.target)} loop={b.loopCount} unit={b.rotationConstraint*DEG:.2f}° links: " + "; ".join(links)
        rows.append([i, b.name, b.name_e, bname(m, b.parent), fmtv(b.location, 3), flags_str(b), b.transform_order, dc, add,
                     fmtv(b.axis, 3) if b.axis is not None else "", lc, ik, int(cnt[i]), f"{sm[i]:.0f}"])
    L.append(md_table(rows, ["#", "name_j", "name_e", "parent", "pos", "flags", "層", "tail", "付与", "軸", "ローカル軸", "IK", "nV", "Σw"]))
    S["bones"] = [dict(i=i, name=b.name, name_e=b.name_e, parent=b.parent, pos=list(b.location), flags=flags_str(b), layer=b.transform_order,
                       add=(b.additionalTransform[0], b.additionalTransform[1]) if b.additionalTransform else None,
                       axis=list(b.axis) if b.axis is not None else None,
                       local=(list(b.localCoordinate.x_axis), list(b.localCoordinate.z_axis)) if b.localCoordinate is not None else None,
                       ik=(b.target, b.loopCount, b.rotationConstraint, [(l.target, l.minimumAngle, l.maximumAngle) for l in b.ik_links]) if b.isIK else None,
                       nV=int(cnt[i]), sw=float(sm[i]), ymin=float(ymin[i]) if cnt[i] else None, ymax=float(ymax[i]) if cnt[i] else None,
                       tail=b.displayConnection if isinstance(b.displayConnection, int) else list(b.displayConnection))
                  for i, b in enumerate(m.bones)]

    present = {}
    for n in STD_BONES:
        present[n] = find_bone(m, n) is not None
    for base in SIDE_BONES:
        for side in ["左", "右"]:
            nm = side_name(side, base)
            present[nm] = find_bone(m, nm) is not None
    S["present"] = present
    L.append("\nStandard/semi-standard presence: " + ", ".join(f"{k}:{'Y' if v else '-'}" for k, v in present.items()) + "\n")

    # ---------------- 5. weights summary
    L.append("\n## 5. Weights\n")
    wt = collections.Counter(m.np_wtype.tolist())
    infl = influences_per_vertex(m)
    ih = collections.Counter(infl.tolist())
    s4 = m.np_bw.sum(1)
    bad = int(np.sum(np.abs(s4 - 1) > 1e-3))
    neg = int(np.sum(m.np_bw < -1e-6))
    L.append(f"weight types: BDEF1={wt.get(0,0)} BDEF2={wt.get(1,0)} BDEF4={wt.get(2,0)} SDEF={wt.get(3,0)}; distinct influences/vertex: {dict(sorted(ih.items()))}; sum!=1: {bad}; negative: {neg}\n\n")
    S["wtypes"] = {"BDEF1": wt.get(0, 0), "BDEF2": wt.get(1, 0), "BDEF4": wt.get(2, 0), "SDEF": wt.get(3, 0)}
    S["influences"] = dict(sorted((int(k), int(v)) for k, v in ih.items()))
    S["wsum_bad"] = bad
    rows = []
    for i in np.argsort(-cnt):
        if cnt[i] == 0: break
        rows.append([i, m.bones[i].name, int(cnt[i]), f"{sm[i]:.1f}", f"{ymin[i]:.2f}", f"{ymax[i]:.2f}"])
    L.append(md_table(rows, ["#", "bone", "nV(w>0)", "Σw", "ymin", "ymax"]))

    # ---------------- 6. morphs
    L.append("\n## 6. Morphs\n")
    PANEL = {0: "システム", 1: "眉", 2: "目", 3: "口", 4: "その他"}
    TYPE = {0: "group", 1: "vertex", 2: "bone", 3: "uv", 4: "uv1", 5: "uv2", 6: "uv3", 7: "uv4", 8: "material", 9: "flip", 10: "impulse"}
    rows = []
    mlist = []
    for i, mo in enumerate(m.morphs):
        t = mo.type_idx
        det = ""
        info = dict(i=i, name=mo.name, name_e=mo.name_e, panel=mo.category, type=TYPE[t], n=len(mo.offsets))
        if t == 2:
            parts = []
            for o in mo.offsets:
                ang, ax = quat_to_axis_angle(o.rotation_offset)
                eu = quat_to_euler_yxz(o.rotation_offset)
                loc = o.location_offset
                s = f"{bname(m,o.index)}: rot {ang:.1f}° eulerXYZ({eu[0]:.1f},{eu[1]:.1f},{eu[2]:.1f})"
                if any(abs(x) > 1e-6 for x in loc): s += f" loc{fmtv(loc,3)}"
                parts.append(s)
            det = "; ".join(parts)
            info["offsets"] = [(bname(m, o.index), list(o.location_offset), list(o.rotation_offset)) for o in mo.offsets]
        elif t == 1:
            offs = np.array([o.offset for o in mo.offsets]) if mo.offsets else np.zeros((0, 3))
            idx = np.array([o.index for o in mo.offsets], dtype=np.int64) if mo.offsets else np.zeros(0, dtype=np.int64)
            mag = np.linalg.norm(offs, axis=1) if len(offs) else np.zeros(0)
            nz = int(np.sum(mag > 1e-5))
            topb = ""
            yr = None
            if len(idx):
                bb = m.np_bidx[idx, 0]
                c = collections.Counter(bb.tolist()).most_common(3)
                topb = ",".join(f"{bname(m,k)}:{v}" for k, v in c)
                yr = (float(m.np_co[idx, 1].min()), float(m.np_co[idx, 1].max()))
            det = f"nOff={len(mo.offsets)} nonzero={nz} max|d|={mag.max() if len(mag) else 0:.4f} mean|d|={mag[mag>1e-5].mean() if nz else 0:.4f} Yrange={fmtv(yr,2) if yr else '-'} topBone={topb}"
            info.update(nonzero=nz, maxd=float(mag.max()) if len(mag) else 0.0, topb=topb)
        elif t == 0:
            det = "; ".join(f"{m.morphs[o.morph].name if 0 <= o.morph < len(m.morphs) else o.morph}×{o.factor:.2f}" for o in mo.offsets)
            info["offsets"] = [(o.morph, o.factor) for o in mo.offsets]
        elif t == 8:
            parts = []
            for o in mo.offsets:
                mname = m.materials[o.index].name if 0 <= o.index < len(m.materials) else ("ALL" if o.index == -1 else o.index)
                parts.append(f"{mname} op={'mul' if o.offset_type==0 else 'add'} diff{fmtv(o.diffuse_offset,2)}")
            det = "; ".join(parts)
        elif t in (3, 4, 5, 6, 7):
            det = f"nOff={len(mo.offsets)}"
        elif t == 9:
            det = "; ".join(f"{m.morphs[o.morph].name}×{o.factor:.2f}" for o in mo.offsets)
        rows.append([i, mo.name, mo.name_e, PANEL.get(mo.category, mo.category), TYPE[t], len(mo.offsets), det])
        mlist.append(info)
    S["morphs"] = mlist
    L.append(md_table(rows, ["#", "name", "name_e", "panel", "type", "nOff", "detail"]))

    # ---------------- 7. physics
    L.append("\n## 7. Rigid bodies\n")
    SHAPE = {0: "sphere", 1: "box", 2: "capsule"}
    MODE = {0: "static", 1: "dynamic", 2: "dyn+bone"}
    rows = []
    rbl = []
    for i, r in enumerate(m.rigids):
        bpos_ = np.array(m.bones[r.bone].location) if r.bone is not None and 0 <= r.bone < len(m.bones) else None
        rel = (np.array(r.location) - bpos_) if bpos_ is not None else None
        noncoll = [g + 1 for g in range(16) if not (r.collision_group_mask >> g) & 1]
        rows.append([i, r.name, r.name_e, bname(m, r.bone), SHAPE[r.type], fmtv(r.size, 3), fmtv(r.location, 3), fmtv(rel, 3) if rel is not None else "-",
                     fmtv([a * DEG for a in r.rotation], 1), f"{r.mass:g}", f"{r.velocity_attenuation:g}", f"{r.rotation_attenuation:g}", f"{r.bounce:g}", f"{r.friction:g}",
                     MODE.get(r.mode, r.mode), r.collision_group_number + 1, ",".join(map(str, noncoll)), f"0x{r.collision_group_mask:04x}"])
        rbl.append(dict(i=i, name=r.name, name_e=r.name_e, bone=bname(m, r.bone), bone_i=r.bone, shape=SHAPE[r.type], size=list(r.size), loc=list(r.location),
                        rel=rel.tolist() if rel is not None else None, rot=[a * DEG for a in r.rotation], mass=r.mass, ld=r.velocity_attenuation,
                        ad=r.rotation_attenuation, rest=r.bounce, fric=r.friction, mode=MODE.get(r.mode, r.mode), group=r.collision_group_number + 1,
                        noncoll=noncoll, mask=r.collision_group_mask))
    S["rigids"] = rbl
    L.append(md_table(rows, ["#", "name", "name_e", "bone", "shape", "size", "pos", "pos-bone", "rot°", "mass", "linD", "angD", "rest", "fric", "mode", "grp", "non-coll", "mask"]))
    L.append("\n### Joints\n")
    rows = []
    jl = []
    for i, j in enumerate(m.joints):
        ra = m.rigids[j.src_rigid].name if j.src_rigid is not None and 0 <= j.src_rigid < len(m.rigids) else "-"
        rb = m.rigids[j.dest_rigid].name if j.dest_rigid is not None and 0 <= j.dest_rigid < len(m.rigids) else "-"
        rows.append([i, j.name, j.name_e, j.mode, ra, rb, fmtv(j.location, 3), fmtv([a * DEG for a in j.rotation], 1),
                     fmtv(j.minimum_location, 2) + "~" + fmtv(j.maximum_location, 2),
                     fmtv([a * DEG for a in j.minimum_rotation], 1) + "~" + fmtv([a * DEG for a in j.maximum_rotation], 1),
                     fmtv(j.spring_constant, 1), fmtv(j.spring_rotation_constant, 1)])
        jl.append(dict(i=i, name=j.name, a=j.src_rigid, b=j.dest_rigid, aname=ra, bname=rb, loc=list(j.location), rot=[a * DEG for a in j.rotation],
                       tmin=list(j.minimum_location), tmax=list(j.maximum_location), rmin=[a * DEG for a in j.minimum_rotation],
                       rmax=[a * DEG for a in j.maximum_rotation], st=list(j.spring_constant), sr=list(j.spring_rotation_constant)))
    S["joints"] = jl
    L.append(md_table(rows, ["#", "name", "name_e", "type", "A", "B", "pos", "rot°", "move min~max", "rot min~max (deg)", "spring T", "spring R"]))

    # ---------------- 8. materials
    L.append("\n## 8. Materials\n")
    rows = []
    ml = []
    tex = [t.raw_path for t in m.textures]
    base = os.path.dirname(path)
    L.append("textures: " + "; ".join(f"[{i}]{t}{'' if os.path.exists(os.path.join(base, t)) else ' (MISSING)'}" for i, t in enumerate(tex)) + "\n\n")
    SPH = {0: "off", 1: "mul", 2: "add", 3: "subtex"}
    for i, mt in enumerate(m.materials):
        toon = (f"shared toon{mt.toon_texture+1:02d}" if mt.is_shared_toon_texture else (tex[mt.toon_texture] if 0 <= mt.toon_texture < len(tex) else f"#{mt.toon_texture}"))
        flags = "".join(["D" if mt.is_double_sided else "-", "G" if mt.enabled_drop_shadow else "-", "M" if mt.enabled_self_shadow_map else "-", "S" if mt.enabled_self_shadow else "-", "E" if mt.enabled_toon_edge else "-"])
        rows.append([i, mt.name, mt.name_e, tex[mt.texture] if 0 <= mt.texture < len(tex) else "-",
                     (tex[mt.sphere_texture] if 0 <= mt.sphere_texture < len(tex) else "-") + f" ({SPH.get(mt.sphere_texture_mode, mt.sphere_texture_mode)})",
                     toon, fmtv(mt.diffuse, 2), fmtv(mt.specular, 2), f"{mt.shininess:g}", fmtv(mt.ambient, 2), flags, f"{mt.edge_size:g}", fmtv(mt.edge_color, 2),
                     mt.vertex_count // 3, mt.comment.replace("\n", " ")[:60]])
        ml.append(dict(i=i, name=mt.name, name_e=mt.name_e, tex=tex[mt.texture] if 0 <= mt.texture < len(tex) else None,
                       sphere=tex[mt.sphere_texture] if 0 <= mt.sphere_texture < len(tex) else None, sphere_mode=mt.sphere_texture_mode,
                       toon=toon, diffuse=list(mt.diffuse), specular=list(mt.specular), shininess=mt.shininess, ambient=list(mt.ambient),
                       flags=flags, edge_size=mt.edge_size, edge_color=list(mt.edge_color), faces=mt.vertex_count // 3, memo=mt.comment))
    S["materials"] = ml
    S["textures"] = tex
    L.append(md_table(rows, ["#", "name", "name_e", "tex", "sphere(mode)", "toon", "diffuse", "specular", "shin", "ambient", "flags D/G/M/S/E", "edge", "edge color", "faces", "memo"]))

    # ---------------- 9. display frames
    L.append("\n## 9. Display frames\n")
    dl = []
    for d in m.display:
        items = []
        for t, idx in d.data:
            items.append(bname(m, idx) if t == 0 else ("morph:" + (m.morphs[idx].name if 0 <= idx < len(m.morphs) else str(idx))))
        L.append(f"- **{d.name}** / {d.name_e} special={d.isSpecial} n={len(items)}: " + ", ".join(items) + "\n")
        dl.append(dict(name=d.name, name_e=d.name_e, special=d.isSpecial, items=items))
    S["display"] = dl

    # ---------------- 10. validation smells
    L.append("\n## 10. Validation smells\n")
    def dups(names):
        c = collections.Counter(names)
        return {k: v for k, v in c.items() if v > 1}
    val = {}
    val["dup_bones"] = dups([b.name for b in m.bones])
    val["dup_morphs"] = dups([x.name for x in m.morphs])
    val["dup_mats"] = dups([x.name for x in m.materials])
    val["dup_rigids"] = dups([x.name for x in m.rigids])
    val["dup_joints"] = dups([x.name for x in m.joints])
    val["bone_gt15"] = [(b.name, cp932_len(b.name)) for b in m.bones if (cp932_len(b.name) or 99) > 15]
    val["morph_gt15"] = [(x.name, cp932_len(x.name)) for x in m.morphs if (cp932_len(x.name) or 99) > 15]
    val["non_cp932_bones"] = [(b.name, "".join(non_cp932_chars(b.name))) for b in m.bones if non_cp932_chars(b.name)]
    val["non_cp932_morphs"] = [(x.name, "".join(non_cp932_chars(x.name))) for x in m.morphs if non_cp932_chars(x.name)]
    val["non_cp932_mats"] = [(x.name, "".join(non_cp932_chars(x.name))) for x in m.materials if non_cp932_chars(x.name)]
    val["empty_name_e_bones"] = sum(1 for b in m.bones if not b.name_e)
    ref = set()
    for i, b in enumerate(m.bones):
        if b.parent is not None and b.parent >= 0: ref.add(b.parent)
        if b.additionalTransform: ref.add(b.additionalTransform[0])
        if b.isIK:
            ref.add(b.target)
            for l in b.ik_links: ref.add(l.target)
        if isinstance(b.displayConnection, int) and b.displayConnection >= 0: ref.add(b.displayConnection)
    for r in m.rigids:
        if r.bone is not None and r.bone >= 0: ref.add(r.bone)
    for mo in m.morphs:
        if mo.type_idx == 2:
            for o in mo.offsets: ref.add(o.index)
    val["unused_leaf_bones_noweight"] = [b.name for i, b in enumerate(m.bones) if cnt[i] == 0 and i not in ref and not b.isIK and not ch.get(i)]
    val["weighted_but_nonrot"] = [b.name for i, b in enumerate(m.bones) if cnt[i] > 0 and not b.isRotatable]
    val["weighted_bones"] = int(np.sum(cnt > 0))
    val["wsum_bad"] = bad
    val["rigid_no_bone"] = [r.name for r in m.rigids if r.bone is None or r.bone < 0]
    val["joint_bad"] = [j.name for j in m.joints if j.src_rigid is None or j.dest_rigid is None or j.src_rigid == j.dest_rigid]
    val["missing_textures"] = [t for t in tex if not os.path.exists(os.path.join(base, t))]
    val["parent_after_child"] = [b.name for i, b in enumerate(m.bones) if b.parent is not None and b.parent > i]
    in_disp = set()
    for d in m.display:
        for t, idx in d.data:
            if t == 0: in_disp.add(idx)
    val["ctrl_visible_not_in_frames"] = [b.name for i, b in enumerate(m.bones) if b.visible and b.isControllable and i not in in_disp and i != 0]
    S["validation"] = val
    for k, v in val.items():
        L.append(f"- {k}: {v if not isinstance(v, list) or len(v) < 60 else (str(v[:60]) + f' ... ({len(v)})')}\n")

    with open(os.path.join(OUT, key + ".md"), "w", encoding="utf-8") as f:
        f.write("".join(L))
    with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))
    return m, S

if __name__ == "__main__":
    keys = sys.argv[1:] or [k for k, _ in models.ALL]
    for k in keys:
        dump(k, models.PATHS[k])
        print("done", k)
