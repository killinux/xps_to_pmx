# -*- coding: utf-8 -*-
"""Headless verification of mmd_tools 1.0.2 facts in Blender 3.6.
Run: blender.exe --background --python verify_mmd_tools_102.py
"""
import inspect
import json
import sys
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

# ---------------------------------------------------------------- enable addon
@section('addon_enable')
def _():
    import addon_utils
    enabled = {m.__name__ for m in addon_utils.modules() if addon_utils.check(m.__name__)[1]}
    res = {'blender_version': bpy.app.version_string, 'python': sys.version}
    for name in ('mmd_tools', 'mmd_uuunyaa_tools'):
        if name not in enabled:
            try:
                bpy.ops.preferences.addon_enable(module=name)
                res[name] = 'enabled now'
            except Exception as e:
                res[name] = 'enable failed: %r' % e
        else:
            res[name] = 'already enabled'
    return res

@section('version_identity')
def _():
    import mmd_tools
    res = {
        'bl_info_version': mmd_tools.bl_info['version'],
        'bl_info_blender': mmd_tools.bl_info['blender'],
        'bl_info_author': mmd_tools.bl_info['author'],
        'bl_info_description': mmd_tools.bl_info['description'],
        'module_file': mmd_tools.__file__,
        'package_name': mmd_tools.__package__,
        'has_MMD_TOOLS_VERSION': hasattr(mmd_tools, 'MMD_TOOLS_VERSION'),
        'in_preferences_addons': 'mmd_tools' in bpy.context.preferences.addons,
    }
    try:
        import mmd_uuunyaa_tools
        res['uuunyaa_version'] = mmd_uuunyaa_tools.bl_info['version']
        res['uuunyaa_blender'] = mmd_uuunyaa_tools.bl_info['blender']
    except Exception as e:
        res['uuunyaa_import_error'] = repr(e)
    return res

@section('operator_ids')
def _():
    ops = sorted(dir(bpy.ops.mmd_tools))
    res = {'count': len(ops), 'ids': ops}
    try:
        res['uuunyaa_ops'] = sorted(dir(bpy.ops.mmd_uuunyaa_tools))
    except Exception as e:
        res['uuunyaa_ops_error'] = repr(e)
    for missing in ('fix_bone_order', 'bone_id_move_up', 'validate_bones', 'convert_bone_morph_to_vertex_morph',
                    'translate_mmd_model', 'display_item_quick_setup', 'convert_to_mmd_model', 'apply_additional_transform',
                    'global_translation_popup', 'show_global_translation_popup', 'attach_meshes', 'model_validation'):
        res['has_' + missing] = missing in ops
    return res

@section('signatures')
def _():
    from mmd_tools.core.model import Model, FnModel
    from mmd_tools.core.bone import FnBone
    from mmd_tools.core.material import FnMaterial
    from mmd_tools.core.pmx import exporter, importer
    res = {
        'Model.create': str(inspect.signature(Model.create)),
        'Model.createRigidBody': str(inspect.signature(Model.createRigidBody)),
        'Model.createJoint': str(inspect.signature(Model.createJoint)),
        'Model.initialDisplayFrames': str(inspect.signature(Model.initialDisplayFrames)),
        'Model.create_ik_constraint': str(inspect.signature(Model.create_ik_constraint)),
        'FnBone.apply_additional_transformation': str(inspect.signature(FnBone.apply_additional_transformation)),
        'FnBone.clean_additional_transformation': str(inspect.signature(FnBone.clean_additional_transformation)),
        'FnBone.apply_auto_bone_roll': str(inspect.signature(FnBone.apply_auto_bone_roll)),
        'FnBone.update_bone_roll': str(inspect.signature(FnBone.update_bone_roll)),
        'FnMaterial.create_texture': str(inspect.signature(FnMaterial.create_texture)),
        'FnMaterial.convert_to_mmd_material': str(inspect.signature(FnMaterial.convert_to_mmd_material)),
        'exporter.export': str(inspect.signature(exporter.export)),
        'importer.PMXImporter.execute': str(inspect.signature(importer.PMXImporter.execute)),
        'FnModel_methods': sorted(k for k in vars(FnModel) if not k.startswith('_')),
        'Model_methods': sorted(k for k in vars(Model) if not k.startswith('_')),
        'FnBone_methods': sorted(k for k in vars(FnBone) if not k.startswith('_')),
    }
    return res

@section('property_lists')
def _():
    from mmd_tools.properties.bone import MMDBone
    from mmd_tools.properties.root import MMDRoot, MMDDisplayItem, MMDDisplayItemFrame
    from mmd_tools.properties.material import MMDMaterial
    from mmd_tools.properties.rigid_body import MMDRigidBody, MMDJoint
    def props(cls):
        return sorted(p.identifier for p in cls.bl_rna.properties if p.identifier not in ('rna_type', 'name'))
    res = {
        'MMDBone': props(MMDBone),
        'MMDRoot': props(MMDRoot),
        'MMDDisplayItem': props(MMDDisplayItem),
        'MMDDisplayItemFrame': props(MMDDisplayItemFrame),
        'MMDMaterial': props(MMDMaterial),
        'MMDRigidBody': props(MMDRigidBody),
        'MMDJoint': props(MMDJoint),
        'PoseBone_extra': [p for p in ('mmd_bone', 'is_mmd_shadow_bone', 'mmd_shadow_bone_type', 'mmd_ik_toggle') if hasattr(bpy.types.PoseBone, p)],
        'Object_extra': [p for p in ('mmd_type', 'mmd_root', 'mmd_rigid', 'mmd_joint', 'mmd_camera', 'mmd_data_query') if hasattr(bpy.types.Object, p)],
        'mmd_type_enum': [i.identifier for i in bpy.types.Object.bl_rna.properties['mmd_type'].enum_items],
        'MMDBone_bone_id_default': MMDBone.bl_rna.properties['bone_id'].default,
        'MMDBone_ik_rotation_constraint_default': MMDBone.bl_rna.properties['ik_rotation_constraint'].default,
        'MMDBone_additional_transform_influence_default': MMDBone.bl_rna.properties['additional_transform_influence'].default,
        'MMDRoot_has_ik_loop_factor': 'ik_loop_factor' in props(MMDRoot),
        'MMDBone_has_display_connection_type': 'display_connection_type' in props(MMDBone),
    }
    return res

@section('import_export_operator_props')
def _():
    def op_props(op):
        rna = op.get_rna_type()
        out = {}
        for p in rna.properties:
            if p.identifier in ('rna_type',):
                continue
            d = {'type': p.type}
            if p.type == 'ENUM':
                d['items'] = [i.identifier for i in p.enum_items]
                try:
                    d['default'] = p.default if not p.is_enum_flag else sorted(p.default_flag)
                except Exception:
                    pass
            elif p.type in ('BOOLEAN', 'INT', 'FLOAT', 'STRING'):
                try:
                    d['default'] = p.default
                except Exception:
                    pass
            out[p.identifier] = d
        return out
    return {
        'import_model': op_props(bpy.ops.mmd_tools.import_model),
        'export_pmx': op_props(bpy.ops.mmd_tools.export_pmx),
        'display_item_quick_setup': op_props(bpy.ops.mmd_tools.display_item_quick_setup),
        'translate_mmd_model': op_props(bpy.ops.mmd_tools.translate_mmd_model),
        'rigid_body_add': op_props(bpy.ops.mmd_tools.rigid_body_add),
        'joint_add': op_props(bpy.ops.mmd_tools.joint_add),
    }

# ---------------------------------------------------------------- live test: additional transform
@section('additional_transform_live_test')
def _():
    from math import pi
    from mmd_tools.core.model import Model
    from mmd_tools.core.bone import FnBone
    import mathutils

    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = Model.create('TestModel', 'TestModel_e', scale=1.0, obj_name='Test', add_root_bone=True)
    root = rig.rootObject()
    arm = rig.armature()
    res = {
        'root_name': root.name, 'root_mmd_type': root.mmd_type, 'root_mmd_root_name': root.mmd_root.name,
        'armature_name': arm.name, 'armature_parent': arm.parent.name,
        'bones_after_create': [b.name for b in arm.data.bones],
        'bone_groups_after_create': [g.name for g in arm.pose.bone_groups],
        'root_empty_display_size': root.empty_display_size,
        'display_frames_after_create': [f.name for f in root.mmd_root.display_item_frames],
    }
    rig.initialDisplayFrames()
    res['display_frames_after_initial'] = [(f.name, f.name_e, f.is_special, [(d.type, d.name) for d in f.data]) for f in root.mmd_root.display_item_frames]

    # build a small chain: 全ての親 -> センター -> 上半身 -> 両目, 左目 (左目 gets Rotate+ from 両目, inf 1.0)
    # plus 左肩P -> 左肩 -> 左肩C (左肩C gets Rotate+ from 左肩P, inf -1.0)  (a test of negative influence)
    # plus 左足 -> 左足D (左足D Rotate+ from 左足, inf 1.0, aligned)  (a test of well-aligned skip)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    def nb(name, head, tail, parent=None):
        b = eb.new(name)
        b.head = head; b.tail = tail
        if parent: b.parent = eb[parent]
        return b
    nb('センター', (0,0,0.8), (0,0,1.0), '全ての親')
    nb('上半身', (0,0,1.2), (0,0,1.5), 'センター')
    nb('頭', (0,0,1.6), (0,0,1.8), '上半身')
    nb('両目', (0,0,2.2), (0,-0.1,2.2), '頭')
    nb('左目', (0.05,-0.1,1.7), (0.05,-0.15,1.7), '頭')
    nb('左肩P', (0.1,0,1.5), (0.1,0,1.6), '上半身')
    nb('左肩', (0.1,0,1.5), (0.25,0,1.5), '左肩P')
    nb('左肩C', (0.25,0,1.5), (0.25,0,1.6), '左肩')
    nb('左腕', (0.25,0,1.5), (0.5,0,1.3), '左肩C')
    nb('左足', (0.1,0,0.8), (0.1,0,0.4), 'センター')
    nb('左足D', (0.1,0,0.8), (0.1,0,0.4), 'センター')
    bpy.ops.object.mode_set(mode='OBJECT')

    pb = arm.pose.bones
    for b in pb:
        b.mmd_bone.name_j = b.name
    # set 付与 like the PMX importer does (importer.py __importBones)
    def set_at(name, target, influence, rot=True, loc=False):
        mb = pb[name].mmd_bone
        mb.has_additional_rotation = rot
        mb.has_additional_location = loc
        mb.additional_transform_influence = influence
        mb.additional_transform_bone = target
    set_at('左目', '両目', 1.0)
    set_at('左肩C', '左肩P', -1.0)
    set_at('左足D', '左足', 1.0)
    res['before_apply'] = {
        n: {'dirty': pb[n].mmd_bone.is_additional_transform_dirty,
            'at_bone': pb[n].mmd_bone.additional_transform_bone,
            'at_bone_id': pb[n].mmd_bone.additional_transform_bone_id,
            'constraints': [c.name for c in pb[n].constraints]}
        for n in ('左目', '左肩C', '左足D')}
    res['bone_ids_assigned'] = {b.name: b.mmd_bone.bone_id for b in pb}

    FnBone.apply_additional_transformation(arm)

    def cinfo(c):
        d = {'type': c.type, 'name': c.name, 'target': getattr(c.target, 'name', None), 'subtarget': getattr(c, 'subtarget', None),
             'influence': c.influence, 'mute': c.mute}
        if c.type == 'TRANSFORM':
            d.update({'map_from': c.map_from, 'map_to': c.map_to, 'owner_space': c.owner_space, 'target_space': c.target_space,
                      'use_motion_extrapolate': c.use_motion_extrapolate,
                      'from_rotation_mode': c.from_rotation_mode, 'to_euler_order': c.to_euler_order, 'mix_mode_rot': c.mix_mode_rot,
                      'from_min_x_rot': c.from_min_x_rot, 'from_max_x_rot': c.from_max_x_rot,
                      'to_min_x_rot': c.to_min_x_rot, 'to_max_x_rot': c.to_max_x_rot,
                      'from_min_x': c.from_min_x, 'from_max_x': c.from_max_x, 'to_min_x': c.to_min_x, 'to_max_x': c.to_max_x})
        if c.type == 'COPY_TRANSFORMS':
            d.update({'owner_space': c.owner_space, 'target_space': c.target_space})
        return d
    res['after_apply'] = {}
    for b in pb:
        if b.constraints or b.is_mmd_shadow_bone:
            res['after_apply'][b.name] = {
                'is_mmd_shadow_bone': b.is_mmd_shadow_bone,
                'mmd_shadow_bone_type': b.mmd_shadow_bone_type,
                'parent': getattr(b.parent, 'name', None),
                'use_deform': b.bone.use_deform,
                'layers_on': [i for i, v in enumerate(b.bone.layers) if v],
                'bone_group': getattr(b.bone_group, 'name', None),
                'dirty': b.mmd_bone.is_additional_transform_dirty,
                'constraints': [cinfo(c) for c in b.constraints],
            }
    res['all_bones_after_apply'] = [b.name for b in arm.data.bones]
    res['armature_layers_visible'] = [i for i, v in enumerate(arm.data.layers) if v]

    # now test clean
    FnBone.clean_additional_transformation(arm)
    res['bones_after_clean'] = [b.name for b in arm.data.bones]
    res['dirty_after_clean'] = {b.name: b.mmd_bone.is_additional_transform_dirty for b in pb if b.name in ('左目','左肩C','左足D')}
    FnBone.apply_additional_transformation(arm)
    res['bones_after_reapply'] = [b.name for b in arm.data.bones]

    # export test (no meshes) to check 付与 roundtrip in pmx data
    import os, tempfile
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_verify.pmx')
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=[], rigid_bodies=[], joints=[], copy_textures=False)
    m = pmx.load(out)
    res['exported_bones'] = [(i, b.name, b.parent, b.hasAdditionalRotate, b.hasAdditionalLocation, b.additionalTransform, b.transform_order) for i, b in enumerate(m.bones)]
    res['exported_bone_count'] = len(m.bones)
    return res

# ---------------------------------------------------------------- live test: bone order override with a mesh
@section('bone_order_live_test')
def _():
    from mmd_tools.core.model import Model
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    import os, tempfile
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = Model.create('Order', 'Order', scale=1.0, obj_name='Order', add_root_bone=False)
    root, arm = rig.rootObject(), rig.armature()
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    names = ['C', 'A', 'B']  # creation order deliberately not desired order
    for i, n in enumerate(names):
        b = eb.new(n); b.head = (i, 0, 0); b.tail = (i, 0, 1)
    bpy.ops.object.mode_set(mode='OBJECT')
    # mesh with vertex groups in desired order A, B, C and the special modifier
    mesh = bpy.data.meshes.new('m')
    mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)], [], [(0,1,2)])
    obj = bpy.data.objects.new('mesh', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = arm
    for n in ['A', 'B', 'C']:
        obj.vertex_groups.new(name=n)
    obj.vertex_groups['A'].add([0,1,2], 1.0, 'REPLACE')
    mod = obj.modifiers.new(name='mmd_bone_order_override', type='ARMATURE')
    mod.object = arm
    res = {'armature_bone_order': [b.name for b in arm.data.bones], 'vg_order': [g.name for g in obj.vertex_groups]}
    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_order.pmx')
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    m = pmx.load(out)
    res['exported_bone_order_with_override'] = [b.name for b in m.bones]
    # rename modifier -> order falls back to armature order
    mod.name = 'Armature'
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    m = pmx.load(out)
    res['exported_bone_order_without_override'] = [b.name for b in m.bones]
    res['vertex_weights'] = [(v.weight.type, v.weight.bones) for v in m.vertices]
    res['vertex_count'] = len(m.vertices)
    return res

# ---------------------------------------------------------------- dump
import os
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd(), 'verify_mmd_tools_102.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1, default=str)
print('WROTE', out_path)
