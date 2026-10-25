# -*- coding: utf-8 -*-
"""Live tests for mmd_tools 1.0.2 in Blender 3.6 (headless). Keeps prefs/add-ons intact."""
import json
import os
import sys
import tempfile
import traceback
from math import pi, radians

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
    # do NOT use read_factory_settings (it disables add-ons); purge data blocks instead
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.armatures, bpy.data.materials, bpy.data.images, bpy.data.texts):
        for item in list(coll):
            try:
                coll.remove(item)
            except Exception:
                pass

def cinfo(c):
    d = {'type': c.type, 'name': c.name, 'target': getattr(getattr(c, 'target', None), 'name', None),
         'subtarget': getattr(c, 'subtarget', None), 'influence': round(c.influence, 4), 'mute': c.mute}
    if c.type == 'TRANSFORM':
        d.update({'map_from': c.map_from, 'map_to': c.map_to, 'owner_space': c.owner_space, 'target_space': c.target_space,
                  'use_motion_extrapolate': c.use_motion_extrapolate, 'from_rotation_mode': c.from_rotation_mode,
                  'to_euler_order': c.to_euler_order, 'mix_mode_rot': c.mix_mode_rot, 'mix_mode': c.mix_mode,
                  'from_min_x_rot': round(c.from_min_x_rot, 4), 'from_max_x_rot': round(c.from_max_x_rot, 4),
                  'to_min_x_rot': round(c.to_min_x_rot, 4), 'to_max_x_rot': round(c.to_max_x_rot, 4),
                  'from_min_x': c.from_min_x, 'from_max_x': c.from_max_x, 'to_min_x': c.to_min_x, 'to_max_x': c.to_max_x})
    if c.type == 'COPY_TRANSFORMS':
        d.update({'owner_space': c.owner_space, 'target_space': c.target_space})
    if c.type == 'IK':
        d.update({'chain_count': c.chain_count, 'iterations': c.iterations, 'use_tail': c.use_tail,
                  'pole_target': getattr(c.pole_target, 'name', None), 'is_valid': c.is_valid})
    if c.type == 'LIMIT_ROTATION':
        d.update({'owner_space': c.owner_space, 'use_limit_x': c.use_limit_x, 'use_limit_y': c.use_limit_y, 'use_limit_z': c.use_limit_z,
                  'min_x': round(c.min_x, 4), 'max_x': round(c.max_x, 4), 'min_y': round(c.min_y, 4), 'max_y': round(c.max_y, 4),
                  'min_z': round(c.min_z, 4), 'max_z': round(c.max_z, 4)})
    if c.type == 'DAMPED_TRACK':
        d.update({'track_axis': c.track_axis})
    return d

def bone_dump(pb):
    return {
        'is_mmd_shadow_bone': pb.is_mmd_shadow_bone, 'mmd_shadow_bone_type': pb.mmd_shadow_bone_type,
        'parent': getattr(pb.parent, 'name', None), 'use_deform': pb.bone.use_deform, 'use_connect': pb.bone.use_connect,
        'layers_on': [i for i, v in enumerate(pb.bone.layers) if v], 'bone_group': getattr(pb.bone_group, 'name', None),
        'hide': pb.bone.hide, 'name_j': pb.mmd_bone.name_j, 'name_e': pb.mmd_bone.name_e, 'bone_id': pb.mmd_bone.bone_id,
        'transform_order': pb.mmd_bone.transform_order, 'is_tip': pb.mmd_bone.is_tip,
        'ik_rotation_constraint': round(pb.mmd_bone.ik_rotation_constraint, 4),
        'has_add_rot': pb.mmd_bone.has_additional_rotation, 'has_add_loc': pb.mmd_bone.has_additional_location,
        'add_bone': pb.mmd_bone.additional_transform_bone, 'add_bone_id': pb.mmd_bone.additional_transform_bone_id,
        'add_influence': pb.mmd_bone.additional_transform_influence, 'dirty': pb.mmd_bone.is_additional_transform_dirty,
        'use_ik_limit': (pb.use_ik_limit_x, pb.use_ik_limit_y, pb.use_ik_limit_z),
        'ik_min_max_x': (round(pb.ik_min_x, 4), round(pb.ik_max_x, 4)),
        'lock_location': tuple(pb.lock_location), 'lock_rotation': tuple(pb.lock_rotation),
        'constraints': [cinfo(c) for c in pb.constraints],
    }

# ------------------------------------------------------------------ 1. Model.create + apply_additional_transformation directly
@section('A_create_and_additional_transform')
def _():
    from mmd_tools.core.model import Model
    from mmd_tools.core.bone import FnBone
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    reset_scene()
    rig = Model.create('TestModel', 'TestModel_e', scale=1.0, obj_name='Test', add_root_bone=True)
    root, arm = rig.rootObject(), rig.armature()
    res = {'root_name': root.name, 'root_mmd_type': root.mmd_type, 'mmd_root_name': root.mmd_root.name,
           'armature_name': arm.name, 'armature_parent': arm.parent.name, 'armature_data_name': arm.data.name,
           'bones_after_create': [b.name for b in arm.data.bones],
           'root_bone_name_j_e': (arm.pose.bones[0].mmd_bone.name_j, arm.pose.bones[0].mmd_bone.name_e) if arm.pose.bones else None,
           'bone_groups_after_create': [g.name for g in arm.pose.bone_groups],
           'root_empty_display_size': root.empty_display_size, 'arm_display_type': arm.display_type, 'arm_show_in_front': arm.show_in_front,
           'display_frames_after_create': [f.name for f in root.mmd_root.display_item_frames],
           'active_object_after_create': getattr(bpy.context.view_layer.objects.active, 'name', None),
           'children_of_root': [o.name for o in root.children]}
    rig.initialDisplayFrames()
    res['display_frames_after_initial'] = [(f.name, f.name_e, f.is_special, [(d.type, d.name) for d in f.data]) for f in root.mmd_root.display_item_frames]

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    def nb(name, head, tail, parent=None):
        b = eb.new(name); b.head = head; b.tail = tail
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
    def set_at(name, target, influence, rot=True, loc=False):
        mb = pb[name].mmd_bone
        mb.has_additional_rotation = rot
        mb.has_additional_location = loc
        mb.additional_transform_influence = influence
        mb.additional_transform_bone = target    # setter stores bone_id, marks dirty
    set_at('左目', '両目', 1.0)
    set_at('左肩C', '左肩P', -1.0)
    set_at('左足D', '左足', 1.0)
    res['before_apply'] = {n: {'dirty': pb[n].mmd_bone.is_additional_transform_dirty, 'add_bone': pb[n].mmd_bone.additional_transform_bone,
                               'add_bone_id': pb[n].mmd_bone.additional_transform_bone_id, 'constraints': [c.name for c in pb[n].constraints]}
                           for n in ('左目', '左肩C', '左足D')}
    res['bone_ids_after_setting_targets'] = {b.name: b.mmd_bone.bone_id for b in pb}

    FnBone.apply_additional_transformation(arm)
    res['after_apply'] = {b.name: bone_dump(b) for b in pb if b.constraints or b.is_mmd_shadow_bone}
    res['all_bones_after_apply'] = [b.name for b in arm.data.bones]
    res['armature_layers_visible'] = [i for i, v in enumerate(arm.data.layers) if v]

    FnBone.clean_additional_transformation(arm)
    res['bones_after_clean'] = [b.name for b in arm.data.bones]
    res['constraints_after_clean'] = {b.name: [c.name for c in b.constraints] for b in pb if b.constraints}
    res['dirty_after_clean'] = {n: pb[n].mmd_bone.is_additional_transform_dirty for n in ('左目', '左肩C', '左足D', 'センター')}
    FnBone.apply_additional_transformation(arm)
    res['bones_after_reapply'] = [b.name for b in arm.data.bones]

    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_verify_A.pmx')
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=[], rigid_bodies=[], joints=[], copy_textures=False)
    m = pmx.load(out)
    res['exported_bones'] = [(i, b.name, b.name_e, b.parent, b.hasAdditionalRotate, b.hasAdditionalLocation, b.additionalTransform, b.transform_order, b.visible, b.displayConnection) for i, b in enumerate(m.bones)]
    res['exported_display'] = [(d.name, d.name_e, d.isSpecial, d.data) for d in m.display]
    return res

# ------------------------------------------------------------------ 2. Importer round-trip: 付与 + IK + display frames
@section('B_importer_roundtrip')
def _():
    from mmd_tools.core import pmx
    from mmd_tools.core.pmx.importer import PMXImporter
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core.model import Model
    reset_scene()

    m = pmx.Model()
    m.name, m.name_e, m.comment, m.comment_e = 'RT', 'RT_e', 'c', 'c_e'
    names = ['全ての親', 'センター', '上半身', '首', '頭', '両目', '左目', '左肩P', '左肩', '左肩C', '左腕', '下半身',
             '左足', '左ひざ', '左足首', '左つま先', '左足ＩＫ', '左つま先ＩＫ', '左足D', '左ひざD', '左足首D']
    idx = {n: i for i, n in enumerate(names)}
    loc = {'全ての親': (0,0,0), 'センター': (0,8,0), '上半身': (0,12,0), '首': (0,16,0), '頭': (0,17,0),
           '両目': (0,22,0), '左目': (0.5,18,-1), '左肩P': (1,15.5,0), '左肩': (1,15.5,0), '左肩C': (2.5,15.5,0), '左腕': (2.5,15.5,0),
           '下半身': (0,12,0), '左足': (1,10,0), '左ひざ': (1,5,0), '左足首': (1,1,0), '左つま先': (1,0,-1.5),
           '左足ＩＫ': (1,1,0), '左つま先ＩＫ': (1,0,-1.5), '左足D': (1,10,0), '左ひざD': (1,5,0), '左足首D': (1,1,0)}
    parent = {'全ての親': None, 'センター': '全ての親', '上半身': 'センター', '首': '上半身', '頭': '首', '両目': '頭', '左目': '頭',
              '左肩P': '上半身', '左肩': '左肩P', '左肩C': '左肩', '左腕': '左肩C', '下半身': 'センター',
              '左足': '下半身', '左ひざ': '左足', '左足首': '左ひざ', '左つま先': '左足首', '左足Ｉ＋': None,
              '左足ＩＫ': '全ての親', '左つま先ＩＫ': '左足ＩＫ', '左足D': '下半身', '左ひざD': '左足D', '左足首D': '左ひざD'}
    child_conn = {'センター': None, '上半身': '首', '首': '頭', '左肩': '左肩C', '左腕': None, '左足': '左ひざ', '左ひざ': '左足首', '左足首': '左つま先',
                  '左足D': '左ひざD', '左ひざD': '左足首D'}
    for n in names:
        b = pmx.Bone(); b.name = n; b.name_e = n + '_e'; b.location = list(loc[n])
        b.parent = idx[parent[n]] if parent.get(n) else -1
        c = child_conn.get(n)
        b.displayConnection = idx[c] if c else [0.0, 1.0, 0.0]
        b.transform_order = 0
        m.bones.append(b)
    def add(name, target, inf, rot=True, mov=False):
        b = m.bones[idx[name]]; b.hasAdditionalRotate = rot; b.hasAdditionalLocation = mov; b.additionalTransform = (idx[target], inf)
    add('左目', '両目', 1.0)
    add('左肩C', '左肩P', -1.0)
    add('左足D', '左足', 1.0); add('左ひざD', '左ひざ', 1.0); add('左足首D', '左足首', 1.0)
    for n in ('左足D', '左ひざD', '左足首D'):
        m.bones[idx[n]].transform_order = 1
    m.bones[idx['左つま先']].displayConnection = -1   # tip bone
    m.bones[idx['左足首D']].displayConnection = [0.0, -1.0, 0.0]
    # IK
    ik = m.bones[idx['左足ＩＫ']]; ik.isIK = True; ik.target = idx['左足首']; ik.loopCount = 40; ik.rotationConstraint = 1.0
    l0 = pmx.IKLink(); l0.target = idx['左ひざ']; l0.minimumAngle = [radians(-180), 0, 0]; l0.maximumAngle = [radians(-0.5), 0, 0]
    l1 = pmx.IKLink(); l1.target = idx['左足']; l1.minimumAngle = None; l1.maximumAngle = None
    ik.ik_links = [l0, l1]
    ik.displayConnection = [0.0, 0.0, 1.0]
    ik2 = m.bones[idx['左つま先ＩＫ']]; ik2.isIK = True; ik2.target = idx['左つま先']; ik2.loopCount = 3; ik2.rotationConstraint = 4.0
    l2 = pmx.IKLink(); l2.target = idx['左足首']; l2.minimumAngle = None; l2.maximumAngle = None
    ik2.ik_links = [l2]
    ik2.displayConnection = [0.0, 0.0, 1.0]
    # display frames: Root/表情 default + custom
    d = pmx.Display(); d.name = '体'; d.name_e = 'Body'; d.data = [(0, idx['センター']), (0, idx['上半身']), (0, idx['下半身'])]
    m.display.append(d)
    d = pmx.Display(); d.name = '足'; d.name_e = 'Legs'; d.data = [(0, idx['左足']), (0, idx['左ひざ']), (0, idx['左足ＩＫ']), (0, idx['左つま先ＩＫ'])]
    m.display.append(d)
    if m.display and m.display[0].name == 'Root':
        m.display[0].data = [(0, idx['全ての親'])]
    path = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_rt_in.pmx')
    pmx.save(path, m)

    res = {'default_display_frames_in_pmx_Model': [(d.name, d.name_e, d.isSpecial) for d in pmx.Model().display]}
    PMXImporter().execute(filepath=path, types={'ARMATURE', 'DISPLAY'}, scale=1.0, rename_LR_bones=False, clean_model=False)
    root = next(o for o in bpy.data.objects if o.mmd_type == 'ROOT')
    rig = Model(root); arm = rig.armature()
    pb = arm.pose.bones
    res['root_name'] = root.name; res['armature_name'] = arm.name
    res['import_folder'] = root.get('import_folder')
    res['mmd_ik_loop_factor_custom_prop'] = arm.get('mmd_ik_loop_factor')
    res['comment_text_blocks'] = (root.mmd_root.comment_text, root.mmd_root.comment_e_text)
    res['mesh_objects'] = [(o.name, [md.name + ':' + md.type for md in o.modifiers], [g.name for g in o.vertex_groups][:6], len(o.data.vertices)) for o in rig.meshes()]
    res['all_bones'] = [b.name for b in arm.data.bones]
    res['bone_groups'] = [(g.name, [b.name for b in pb if b.bone_group == g]) for g in arm.pose.bone_groups]
    res['display_frames'] = [(f.name, f.name_e, f.is_special, [(d.type, d.name) for d in f.data]) for f in root.mmd_root.display_item_frames]
    res['bones'] = {n: bone_dump(pb[n]) for n in ('左目', '両目', '左肩C', '左肩P', '左足D', '左ひざD', '左足首D', '左足', '左ひざ', '左足首', '左つま先', '左足ＩＫ', '左つま先ＩＫ')}
    res['shadow_bones'] = {b.name: bone_dump(b) for b in pb if b.is_mmd_shadow_bone}
    res['armature_layers_visible'] = [i for i, v in enumerate(arm.data.layers) if v]

    # export back and compare
    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_rt_out.pmx')
    arm.data.pose_position = 'REST'
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    m2 = pmx.load(out)
    def bd(b):
        return {'name': b.name, 'parent': b.parent, 'order': b.transform_order, 'addRot': b.hasAdditionalRotate, 'addLoc': b.hasAdditionalLocation,
                'addT': b.additionalTransform, 'isIK': b.isIK, 'target': b.target if b.isIK else None, 'loop': b.loopCount if b.isIK else None,
                'angle': round(b.rotationConstraint, 4) if b.isIK else None,
                'links': [(l.target, [round(x, 3) for x in l.minimumAngle] if l.minimumAngle else None, [round(x, 3) for x in l.maximumAngle] if l.maximumAngle else None) for l in b.ik_links] if b.isIK else None,
                'disp': b.displayConnection, 'visible': b.visible, 'movable': b.isMovable, 'rotatable': b.isRotatable}
    res['exported_bones'] = [bd(b) for b in m2.bones]
    res['exported_display'] = [(d.name, d.name_e, d.isSpecial, d.data) for d in m2.display]
    res['exported_bone_count_vs_input'] = (len(m2.bones), len(m.bones))
    return res

# ------------------------------------------------------------------ 3. rename_LR_bones=True naming
@section('C_import_with_rename_LR')
def _():
    from mmd_tools.core.pmx.importer import PMXImporter
    from mmd_tools.core.model import Model
    reset_scene()
    path = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_rt_in.pmx')
    PMXImporter().execute(filepath=path, types={'ARMATURE', 'DISPLAY'}, scale=0.08, rename_LR_bones=True, use_underscore=False, clean_model=False)
    root = next(o for o in bpy.data.objects if o.mmd_type == 'ROOT')
    rig = Model(root); arm = rig.armature()
    mesh = rig.firstMesh()
    return {'bone_names': [(b.name, b.mmd_bone.name_j) for b in arm.pose.bones if not b.is_mmd_shadow_bone],
            'shadow_bone_names': [b.name for b in arm.pose.bones if b.is_mmd_shadow_bone],
            'vertex_groups': [g.name for g in mesh.vertex_groups],
            'display_items_renamed': [(f.name, [d.name for d in f.data]) for f in root.mmd_root.display_item_frames],
            'ik_subtargets': [(b.name, c.subtarget) for b in arm.pose.bones for c in b.constraints if c.type == 'IK'],
            'root_scale_display_size': root.empty_display_size}

# ------------------------------------------------------------------ 4. Bone order override with a mesh
@section('D_bone_order_override')
def _():
    from mmd_tools.core.model import Model
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    reset_scene()
    rig = Model.create('Order', 'Order', scale=1.0, obj_name='Order', add_root_bone=False)
    root, arm = rig.rootObject(), rig.armature()
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    for i, n in enumerate(['C', 'A', 'B', 'D_shadowless']):
        b = eb.new(n); b.head = (i, 0, 0); b.tail = (i, 0, 1)
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = bpy.data.meshes.new('m')
    mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)], [], [(0,1,2)])
    obj = bpy.data.objects.new('mesh', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = arm
    for n in ['A', 'B', 'C']:   # D intentionally has no vertex group
        obj.vertex_groups.new(name=n)
    obj.vertex_groups['A'].add([0, 1, 2], 1.0, 'REPLACE')
    obj.vertex_groups['B'].add([0], 0.5, 'REPLACE')
    mod = obj.modifiers.new(name='mmd_bone_order_override', type='ARMATURE')
    mod.object = arm
    res = {'armature_bone_order': [b.name for b in arm.data.bones], 'vg_order': [g.name for g in obj.vertex_groups]}
    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_order.pmx')
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    m = pmx.load(out)
    res['exported_bone_order_with_override'] = [b.name for b in m.bones]
    res['vertex_weights'] = [(v.weight.type, v.weight.bones, v.weight.weights) for v in m.vertices]
    # reorder vertex groups programmatically: move 'C' to top via active_index + vertex_group_move
    bpy.context.view_layer.objects.active = obj
    obj.vertex_groups.active_index = obj.vertex_groups['C'].index
    bpy.ops.object.vertex_group_move(direction='UP'); bpy.ops.object.vertex_group_move(direction='UP')
    res['vg_order_after_move'] = [g.name for g in obj.vertex_groups]
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    res['exported_bone_order_after_move'] = [b.name for b in pmx.load(out).bones]
    mod.name = 'Armature'
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    res['exported_bone_order_without_override_modifier'] = [b.name for b in pmx.load(out).bones]
    return res

# ------------------------------------------------------------------ 5. material + texture node creation + export
@section('E_material_texture')
def _():
    from mmd_tools.core.model import Model
    from mmd_tools.core.material import FnMaterial
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    reset_scene()
    rig = Model.create('Mat', 'Mat', scale=1.0, obj_name='Mat', add_root_bone=True)
    root, arm = rig.rootObject(), rig.armature()
    mesh = bpy.data.meshes.new('m')
    mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)], [], [(0,1,2)])
    obj = bpy.data.objects.new('mesh', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = arm
    mat = bpy.data.materials.new('体')
    mesh.materials.append(mat)
    mat.mmd_material.name_j = '体'
    mat.mmd_material.name_e = 'body'
    tex_path = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_tex.png')
    img = bpy.data.images.new('tmp_tex', 4, 4); img.filepath_raw = tex_path; img.file_format = 'PNG'; img.save()
    bpy.data.images.remove(img)
    slot = FnMaterial(mat).create_texture(tex_path)
    res = {'use_nodes': mat.use_nodes, 'node_names': sorted(n.name for n in mat.node_tree.nodes),
           'node_groups': sorted(ng.name for ng in bpy.data.node_groups),
           'returned_slot_type': type(slot).__name__, 'returned_image': getattr(slot.texture.image, 'filepath', None),
           'blend_method': mat.blend_method, 'shader_inputs': [s.name for s in mat.node_tree.nodes['mmd_shader'].inputs]}
    mat.mmd_material.is_shared_toon_texture = True; mat.mmd_material.shared_toon_texture = 2
    res['node_names_after_toon'] = sorted(n.name for n in mat.node_tree.nodes)
    out_dir = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_matexport'); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, 'mat.pmx')
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=True)
    m = pmx.load(out)
    res['exported_textures'] = [t.path for t in m.textures]
    res['exported_material'] = [(mt.name, mt.name_e, mt.texture, mt.toon_texture, mt.is_shared_toon_texture, mt.sphere_texture_mode, mt.vertex_count) for mt in m.materials]
    res['files_in_out_dir'] = sorted(os.path.relpath(os.path.join(dp, f), out_dir) for dp, dn, fn in os.walk(out_dir) for f in fn)
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=[], joints=[], copy_textures=False)
    res['exported_textures_no_copy'] = [t.path for t in pmx.load(out).textures]
    return res

# ------------------------------------------------------------------ 6. Rigid body / joint creation API
@section('F_rigid_joint')
def _():
    from mmd_tools.core.model import Model
    from mmd_tools.core.pmx import exporter as pmx_exporter
    from mmd_tools.core import pmx
    reset_scene()
    rig = Model.create('RB', 'RB', scale=1.0, obj_name='RB', add_root_bone=True)
    root, arm = rig.rootObject(), rig.armature()
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    b = arm.data.edit_bones.new('髪1'); b.head = (0, 0, 1.5); b.tail = (0, 0, 1.2); b.parent = arm.data.edit_bones['全ての親']
    bpy.ops.object.mode_set(mode='OBJECT')
    arm.pose.bones['髪1'].mmd_bone.name_j = '髪1'
    res = {'rigidbody_world_before': bpy.context.scene.rigidbody_world is not None}
    r1 = rig.createRigidBody(name='髪1', name_e='hair1', shape_type=2, dynamics_type=1, location=(0, 0, 1.35), rotation=(0, 0, 0), size=(0.05, 0.3, 0),
                             collision_group_number=3, collision_group_mask=[i == 3 for i in range(16)], bone='髪1', mass=0.5, friction=0.5,
                             angular_damping=0.5, linear_damping=0.5, bounce=0.0)
    r0 = rig.createRigidBody(name='頭', name_e='head', shape_type=0, dynamics_type=0, location=(0, 0, 1.6), rotation=(0, 0, 0), size=(0.1, 0, 0),
                             collision_group_number=0, collision_group_mask=[False]*16, bone='全ての親')
    j = rig.createJoint(name='髪1', name_e='hair1', location=(0, 0, 1.5), rotation=(0, 0, 0), rigid_a=r0, rigid_b=r1,
                        maximum_location=(0, 0, 0), minimum_location=(0, 0, 0), maximum_rotation=(0.5, 0.5, 0.5), minimum_rotation=(-0.5, -0.5, -0.5),
                        spring_linear=(0, 0, 0), spring_angular=(10, 10, 10))
    res.update({'rigid_names': [(o.name, o.mmd_type, o.mmd_rigid.name_j, o.mmd_rigid.type, o.mmd_rigid.shape, tuple(round(x, 3) for x in o.mmd_rigid.size), o.mmd_rigid.bone,
                                 o.rigid_body.mass if o.rigid_body else None, o.rigid_body.kinematic if o.rigid_body else None, o.parent.name,
                                 [c.name + ':' + c.type for c in o.constraints]) for o in rig.rigidBodies()],
                'joint': (j.name, j.mmd_type, j.mmd_joint.name_j, j.parent.name, j.rigid_body_constraint.type, j.rigid_body_constraint.object1.name, j.rigid_body_constraint.object2.name,
                          j.rigid_body_constraint.spring_stiffness_ang_x),
                'group_objects': [(o.name, o.mmd_type) for o in root.children],
                'rigidbody_world_after': bpy.context.scene.rigidbody_world is not None,
                'is_built': root.mmd_root.is_built})
    out = os.path.join(tempfile.gettempdir(), 'mmd_tools_102_rb.pmx')
    pmx_exporter.export(filepath=out, scale=1.0, root=root, armature=arm, meshes=[], rigid_bodies=list(rig.rigidBodies()), joints=list(rig.joints()), copy_textures=False)
    m = pmx.load(out)
    res['exported_rigids'] = [(r.name, r.bone, r.type, r.mode, [round(x, 3) for x in r.size], [round(x, 3) for x in r.location], r.collision_group_number, r.collision_group_mask, r.mass) for r in m.rigids]
    res['exported_joints'] = [(jj.name, jj.src_rigid, jj.dest_rigid, [round(x, 3) for x in jj.maximum_rotation], [round(x, 3) for x in jj.spring_rotation_constant]) for jj in m.joints]
    return res

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify_live_102.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1, default=str)
print('WROTE', out_path)
