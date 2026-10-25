# Blender 3.6 headless, read-only: dump objects / materials / node trees of the opened .blend (never saves)
import bpy, sys, json, os
argv = sys.argv[sys.argv.index("--") + 1:]
outp = argv[0]
res = {"file": bpy.data.filepath, "objects": [], "materials": [], "images": [], "node_groups": []}
for o in bpy.data.objects:
    d = dict(name=o.name, type=o.type, parent=o.parent.name if o.parent else None,
             mods=[(m.type, m.name) for m in getattr(o, "modifiers", [])],
             mmd_type=getattr(o, "mmd_type", None) if hasattr(o, "mmd_type") else None,
             hide=o.hide_get() if hasattr(o, "hide_get") else None,
             materials=[s.material.name for s in getattr(o, "material_slots", []) if s.material])
    if o.type == 'MESH':
        d["nverts"] = len(o.data.vertices)
        d["shape_keys"] = [k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []
        d["vgroups"] = len(o.vertex_groups)
    if o.type == 'ARMATURE':
        d["nbones"] = len(o.data.bones)
        d["bones_sample"] = [b.name for b in o.data.bones][:40]
    res["objects"].append(d)

def sock_val(s):
    try:
        v = s.default_value
        if hasattr(v, "__len__"):
            return [round(float(x), 4) for x in v]
        return round(float(v), 4)
    except Exception:
        return None

for m in bpy.data.materials:
    md = dict(name=m.name, users=m.users, use_nodes=m.use_nodes, blend=getattr(m, "blend_method", None),
              shadow=getattr(m, "shadow_method", None), backface=getattr(m, "use_backface_culling", None))
    mm = getattr(m, "mmd_material", None)
    if mm is not None:
        try:
            md["mmd"] = dict(name_j=mm.name_j, name_e=mm.name_e, diffuse=list(mm.diffuse_color), alpha=mm.alpha,
                             specular=list(mm.specular_color), shininess=mm.shininess, ambient=list(mm.ambient_color),
                             is_double_sided=mm.is_double_sided, enabled_drop_shadow=mm.enabled_drop_shadow,
                             enabled_self_shadow_map=mm.enabled_self_shadow_map, enabled_self_shadow=mm.enabled_self_shadow,
                             enabled_toon_edge=mm.enabled_toon_edge, edge_weight=mm.edge_weight,
                             sphere_texture_type=mm.sphere_texture_type, is_shared_toon_texture=mm.is_shared_toon_texture,
                             shared_toon_texture=mm.shared_toon_texture, toon_texture=mm.toon_texture, comment=mm.comment)
        except Exception as e:
            md["mmd_err"] = repr(e)
    if m.use_nodes and m.node_tree:
        nodes = []
        for n in m.node_tree.nodes:
            nd = dict(name=n.name, type=n.type, label=n.label)
            if n.type == 'TEX_IMAGE' and n.image:
                nd["image"] = n.image.filepath; nd["colorspace"] = n.image.colorspace_settings.name
                nd["interp"] = n.interpolation
            if n.type == 'GROUP' and n.node_tree:
                nd["group"] = n.node_tree.name
            if n.type in ('BSDF_PRINCIPLED', 'GROUP', 'NORMAL_MAP', 'MIX_SHADER', 'BUMP', 'BSDF_DIFFUSE', 'EMISSION', 'MIX_RGB', 'MATH', 'SEPRGB', 'SEPARATE_COLOR'):
                ins = {}
                for s in n.inputs:
                    if not s.is_linked:
                        v = sock_val(s)
                        if v is not None: ins[s.name] = v
                    else:
                        ins[s.name] = "<linked>"
                nd["inputs"] = ins
            if n.type == 'NORMAL_MAP':
                nd["space"] = n.space
            nodes.append(nd)
        links = [f"{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}" for l in m.node_tree.links]
        md["nodes"] = nodes; md["links"] = links
    res["materials"].append(md)
for im in bpy.data.images:
    res["images"].append(dict(name=im.name, filepath=im.filepath, colorspace=im.colorspace_settings.name, size=list(im.size), packed=bool(im.packed_file)))
for g in bpy.data.node_groups:
    res["node_groups"].append(dict(name=g.name, users=g.users, nodes=[(n.type, n.name) for n in g.nodes][:60],
                                   inputs=[s.name for s in getattr(g, "inputs", [])]))
with open(outp, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("BLENDDUMP OK", bpy.data.filepath, len(res["objects"]), len(res["materials"]))
