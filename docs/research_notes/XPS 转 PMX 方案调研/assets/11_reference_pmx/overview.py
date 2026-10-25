# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pmxlib, models
out = []
for key, path in models.ALL:
    try:
        m = pmxlib.load(path)
    except Exception as e:
        out.append(f"{key}\tERROR {e!r}")
        continue
    mt = {}
    for mo in m.morphs:
        mt[mo.type_idx] = mt.get(mo.type_idx, 0) + 1
    out.append(f"{key}\tname={m.name!r}/{m.name_e!r}\tV={len(m.np_co)}\tF={len(m.faces)}\tTex={len(m.textures)}\tMat={len(m.materials)}\tBone={len(m.bones)}\tMorph={len(m.morphs)} {mt}\tDisp={len(m.display)}\tRB={len(m.rigids)}\tJ={len(m.joints)}\tUVadd={m.header.additional_uvs}\tenc={m.header.encoding.charset}\tver={m.header.version}")
print("\n".join(out))
