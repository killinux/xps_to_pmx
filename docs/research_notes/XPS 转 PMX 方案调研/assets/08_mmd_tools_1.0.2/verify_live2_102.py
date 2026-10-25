# -*- coding: utf-8 -*-
"""Second batch of live checks for mmd_tools 1.0.2 in Blender 3.6 (headless)."""
import json
import os
import tempfile
import traceback

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

def reset_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.armatures, bpy.data.materials, bpy.data.images, bpy.data.texts):
        for item in list(coll):
            try:
                coll.remove(item)
            except Exception:
                pass

# 1. bone order fallback (no override modifier) -> pose.bones order vs creation order vs DFS
@section('G_fallback_order')
def _():
    from mmd_tools.core.model import Model
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    reset_scene()
    rig = Model.create('O', 'O', scale=0.08, obj_name='O', add_root_bone=False)
    root, arm = rig.rootObject(), rig.armature()
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    creation = []
    def nb(n, p=None, x=0.0):
        b = eb.new(n); b.head = (x, 0, 0); b.tail = (x, 0, 0.1)
        if p: b.parent = eb[p]
        creation.append(n)
    nb('R')
    nb('X1', 'R', 0.1)
    nb('R2', None, 0.5)
    nb('X2', 'R', 0.2)
    nb('Y1', 'X1', 0.3)
    bpy.ops.object.mode_set(mode='OBJECT')
    # layer/hide visibility test
    arm.data.bones['X2'].layers = [i == 1 for i in range(32)]  # only layer 1 (armature shows only layer 0)
    arm.data.bones['Y1'].hide = True
    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_fallback.pmx')
    arm.data.pose_position = 'REST'
    pmx_exporter.export(filepath=out, scale=12.5, root=root, armature=arm, meshes=[], rigid_bodies=[], joints=[], copy_textures=False)
    m = pmx.load(out)
    return {'creation_order': creation,
            'data_bones_order': [b.name for b in arm.data.bones],
            'pose_bones_order': [b.name for b in arm.pose.bones],
            'exported_order': [b.name for b in m.bones],
            'exported_visible': {b.name: b.visible for b in m.bones},
            'root_empty_display_size_for_scale_0.08': root.empty_display_size,
            'model_name_e_comment': (m.name, m.name_e, m.comment, m.comment_e)}

# 2. Model.create(armature=existing) transform handling
@section('H_create_with_existing_armature')
def _():
    from mmd_tools.core.model import Model
    from mathutils import Matrix, Euler
    reset_scene()
    arm_data = bpy.data.armatures.new('xps_arm')
    arm = bpy.data.objects.new('Armature', arm_data)
    bpy.context.collection.objects.link(arm)
    arm.location = (1.0, 2.0, 3.0)
    arm.rotation_euler = Euler((0.0, 0.0, 1.0))
    arm.scale = (0.5, 0.5, 0.5)
    me = bpy.data.meshes.new('body'); me.from_pydata([(0,0,0),(1,0,0),(0,1,0)], [], [(0,1,2)])
    mesh = bpy.data.objects.new('Body', me); bpy.context.collection.objects.link(mesh)
    mesh.parent = arm
    mod = mesh.modifiers.new('Armature', 'ARMATURE'); mod.object = arm
    bpy.context.view_layer.update()
    arm_world_before = [list(r) for r in arm.matrix_world]
    mesh_world_before = [list(r) for r in mesh.matrix_world]
    rig = Model.create('XPS', 'XPS_e', scale=0.08, obj_name='XPSRoot', armature=arm, add_root_bone=False)
    bpy.context.view_layer.update()
    root = rig.rootObject()
    def mat_eq(a, b):
        return all(abs(x - y) < 1e-5 for ra, rb in zip(a, b) for x, y in zip(ra, rb))
    return {'root_name': root.name, 'arm_name_after': arm.name, 'arm_parent': arm.parent.name,
            'arm_world_unchanged': mat_eq(arm_world_before, [list(r) for r in arm.matrix_world]),
            'mesh_world_unchanged': mat_eq(mesh_world_before, [list(r) for r in mesh.matrix_world]),
            'arm_matrix_local_is_identity': mat_eq([list(r) for r in arm.matrix_local], [list(r) for r in Matrix.Identity(4)]),
            'root_location': list(root.location), 'root_scale': list(root.scale),
            'arm_locks': (tuple(arm.lock_location), tuple(arm.lock_rotation), tuple(arm.lock_scale)),
            'meshes_found': [o.name for o in rig.meshes()],
            'mesh_modifiers': [(md.name, md.type) for md in mesh.modifiers]}

# 3. Writing mmd_material fields on a Principled material: does it rewire the node tree?
@section('I_mmd_material_rewires_nodes')
def _():
    reset_scene()
    mat = bpy.data.materials.new('HD')
    mat.use_nodes = True
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial')
    def surface_src():
        l = out.inputs['Surface'].links
        return (l[0].from_node.bl_idname, l[0].from_node.name) if l else None
    res = {'nodes_initial': [(n.bl_idname, n.name) for n in nt.nodes], 'surface_src_initial': surface_src()}
    # (a) write via ID-property (no update callbacks)
    mat.mmd_material['diffuse_color'] = [0.9, 0.1, 0.1]
    mat.mmd_material['alpha'] = 0.5
    res['after_idprop_write'] = {'surface_src': surface_src(), 'nodes': sorted(n.name for n in nt.nodes),
                                 'rna_read_diffuse': list(mat.mmd_material.diffuse_color), 'rna_read_alpha': mat.mmd_material.alpha}
    # (b) write name_j/name_e (name_j has a custom setter but no node update)
    mat.mmd_material.name_j = '体'
    mat.mmd_material.name_e = 'body'
    res['after_name_write'] = {'surface_src': surface_src(), 'name_j': mat.mmd_material.name_j}
    # (c) write via RNA (update callback)
    mat.mmd_material.diffuse_color = (0.2, 0.3, 0.4)
    res['after_rna_write'] = {'surface_src': surface_src(), 'nodes': sorted(n.name for n in nt.nodes),
                              'principled_still_exists': any(n.bl_idname == 'ShaderNodeBsdfPrincipled' for n in nt.nodes),
                              'blend_method': mat.blend_method}
    return res

# 4. Operators: export_pmx error swallowing; apply_additional_transform via ops; legacy pose library presence
@section('J_operators_and_api_presence')
def _():
    from mmd_tools.core.model import Model
    reset_scene()
    rig = Model.create('OP', 'OP', scale=0.08, obj_name='OP', add_root_bone=True)
    root = rig.rootObject()
    bpy.context.view_layer.objects.active = root
    root.select_set(True)
    res = {'export_poll': bpy.ops.mmd_tools.export_pmx.poll()}
    bad = os.path.join('Q:\\does_not_exist_dir', 'x.pmx')
    try:
        r = bpy.ops.mmd_tools.export_pmx(filepath=bad, scale=12.5)
        res['export_to_bad_path_returned'] = sorted(r)
    except Exception as e:
        res['export_to_bad_path_raised'] = repr(e)
    res['bad_file_exists'] = os.path.exists(bad)
    try:
        r = bpy.ops.mmd_tools.apply_additional_transform()
        res['apply_additional_transform_returned'] = sorted(r)
    except Exception as e:
        res['apply_additional_transform_raised'] = repr(e)
    res['has_pose_library_attr'] = hasattr(bpy.types.Object, 'pose_library')
    res['has_poselib_apply_pose'] = 'apply_pose' in dir(bpy.ops.poselib)
    res['ops_dir_contains_fix_bone_order'] = 'fix_bone_order' in dir(bpy.ops.mmd_tools)
    res['types_has_fix_bone_order'] = getattr(bpy.types, 'MMD_TOOLS_OT_fix_bone_order', None) is not None
    res['types_has_export_pmx'] = getattr(bpy.types, 'MMD_TOOLS_OT_export_pmx', None) is not None
    import mmd_tools.bpyutils as bu
    res['bpyutils_has_activate_layer_collection'] = hasattr(bu, 'activate_layer_collection')
    from mmd_tools.core.model import Model as M
    res['Model_has_clothGroupObject_patched_by_uuunyaa'] = hasattr(M, 'clothGroupObject')
    import mmd_tools.core.model as cm
    import inspect
    res['clothGroupObject_defined_in'] = inspect.getsourcefile(M.clothGroupObject) if hasattr(M, 'clothGroupObject') else None
    res['ui_language'] = bpy.context.preferences.view.language
    res['use_translate_new_dataname'] = bpy.context.preferences.view.use_translate_new_dataname
    res['shared_toon_folder_pref'] = bpy.context.preferences.addons['mmd_tools'].preferences.shared_toon_folder
    res['base_texture_folder_pref'] = bpy.context.preferences.addons['mmd_tools'].preferences.base_texture_folder
    return res

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify_live2_102.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1, default=str)
print('WROTE', out_path)
