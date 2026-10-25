# -*- coding: utf-8 -*-
import json, os, tempfile, traceback
import bpy

OUT = {}
def section(name):
    def deco(fn):
        try:
            OUT[name] = fn()
        except Exception:
            OUT[name] = {'ERROR': traceback.format_exc()}
        return fn
    return deco

@section('K_enum_idprop_and_toon_idprop')
def _():
    from mmd_tools.core.model import Model
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.armatures, bpy.data.materials):
        for it in list(coll):
            coll.remove(it)
    rig = Model.create('E', 'E', scale=0.08, obj_name='E', add_root_bone=True)
    root, arm = rig.rootObject(), rig.armature()
    res = {}
    mats = []
    for val in (1, 2, 3, 4):
        mat = bpy.data.materials.new('M%d' % val); mat.use_nodes = True
        mat.mmd_material['sphere_texture_type'] = val
        mat.mmd_material['is_shared_toon_texture'] = True
        mat.mmd_material['shared_toon_texture'] = 3
        mat.mmd_material['name_j'] = '材質%d' % val
        out = next(n for n in mat.node_tree.nodes if n.bl_idname == 'ShaderNodeOutputMaterial')
        res['M%d' % val] = {'rna_sphere_type': mat.mmd_material.sphere_texture_type,
                            'rna_is_shared': mat.mmd_material.is_shared_toon_texture,
                            'rna_shared_toon': mat.mmd_material.shared_toon_texture,
                            'surface_src': out.inputs['Surface'].links[0].from_node.bl_idname,
                            'nodes': sorted(n.bl_idname for n in mat.node_tree.nodes)}
        mats.append(mat)
    me = bpy.data.meshes.new('m'); me.from_pydata([(0,0,0),(1,0,0),(0,1,0),(1,1,0)], [], [(0,1,2),(1,3,2)])
    for mt in mats[:2]:
        me.materials.append(mt)
    me.polygons[1].material_index = 1
    ob = bpy.data.objects.new('mesh', me); bpy.context.collection.objects.link(ob); ob.parent = arm
    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_enum.pmx')
    pmx_exporter.export(filepath=out, scale=12.5, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    m = pmx.load(out)
    res['exported_materials'] = [(x.name, x.sphere_texture_mode, x.is_shared_toon_texture, x.toon_texture) for x in m.materials]
    res['has_vertex_group_sort_op'] = 'vertex_group_sort' in dir(bpy.ops.object)
    res['vertex_group_sort_types'] = [i.identifier for i in bpy.ops.object.vertex_group_sort.get_rna_type().properties['sort_type'].enum_items]
    return res

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify_live3_102.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1, default=str)
print('WROTE', out_path)
