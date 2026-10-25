"""Build Blender objects from :class:`ImportData` (bpy adapter for stage ①).

Creates one collection per import containing the armature and one mesh object
per XPS mesh.  Every bone remembers its original XPS name in
``bone["xps2pmx_src"]`` (names longer than Blender's 63-byte limit or
duplicates get renamed by Blender), every material stores the complete texture
manifest in ``material["xps2pmx"]`` (the data source for re-attaching HD
materials after a PMX round trip), and every object carries the job id.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional

import bmesh
import bpy
import numpy as np

from ..core.xps.convert import ImportData, ImportMesh, normal_green_inverted
from ..core.xps.render_groups import BUMP, DIFFUSE

PROP_SRC = "xps2pmx_src"
PROP_INDEX = "xps2pmx_index"
PROP_JOB = "xps2pmx_job"
PROP_MANIFEST = "xps2pmx"
PROP_MESH_INDEX = "xps2pmx_mesh_index"
UNUSED_GROUP = "xps_unused"
MANIFEST_SCHEMA = 1


class BuildResult:
    def __init__(self) -> None:
        self.collection: Optional[bpy.types.Collection] = None
        self.armature: Optional[bpy.types.Object] = None
        self.meshes: List[bpy.types.Object] = []
        self.bone_names: List[str] = []
        self.renamed_bones: List[tuple] = []
        self.materials: Dict[str, bpy.types.Material] = {}
        self.missing_textures: List[tuple] = []


def build_scene(context: bpy.types.Context, data: ImportData, job_id: str) -> BuildResult:
    result = BuildResult()
    _ensure_object_mode(context)
    coll = bpy.data.collections.new(f"XPS {data.model_name}")
    context.scene.collection.children.link(coll)
    result.collection = coll
    if data.bones:
        result.armature = _build_armature(context, coll, data, job_id, result)
    for m in data.meshes:
        mat = result.materials.get(m.material_key)
        if mat is None:
            mat = _build_material(m, data)
            result.materials[m.material_key] = mat
            for tex in m.textures:
                if not tex.found:
                    result.missing_textures.append((m.raw_name, tex.role, tex.file))
        result.meshes.append(_build_mesh_object(coll, data, m, mat, result, job_id))
    if result.armature is not None:
        for obj in context.view_layer.objects:
            obj.select_set(False)
        context.view_layer.objects.active = result.armature
        result.armature.select_set(True)
    return result


# ---------------------------------------------------------------------------
# armature

def _ensure_object_mode(context: bpy.types.Context) -> None:
    obj = context.view_layer.objects.active
    if obj is not None and obj.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')


def _build_armature(context, coll, data: ImportData, job_id: str, result: BuildResult) -> bpy.types.Object:
    arm = bpy.data.armatures.new(f"{data.model_name}_arm")
    arm.display_type = 'STICK'
    obj = bpy.data.objects.new(f"{data.model_name}_arm", arm)
    obj.show_in_front = True
    coll.objects.link(obj)
    obj[PROP_JOB] = job_id
    obj["xps2pmx_source"] = data.source_path

    for other in context.view_layer.objects:
        other.select_set(False)
    context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    try:
        edit_bones = arm.edit_bones
        created = []
        for b in data.bones:
            eb = edit_bones.new(b.name)
            eb.head = b.head
            eb.tail = b.tail
            eb.use_connect = False
            created.append(eb)
        names = [eb.name for eb in created]
        for b, eb in zip(data.bones, created):
            if b.parent >= 0:
                eb.parent = created[b.parent]
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')

    result.bone_names = names
    for b, name in zip(data.bones, names):
        bone = arm.bones[name]
        bone[PROP_SRC] = b.name
        bone[PROP_INDEX] = b.index
        if name != b.name:
            result.renamed_bones.append((b.name, name))

    unused = [name for b, name in zip(data.bones, names) if b.name.lower().startswith("unused")]
    if unused:
        group = obj.pose.bone_groups.new(name=UNUSED_GROUP)
        group.color_set = 'THEME10'
        for name in unused:
            obj.pose.bones[name].bone_group = group
    return obj


# ---------------------------------------------------------------------------
# meshes

def _build_mesh_object(coll, data: ImportData, m: ImportMesh, mat, result: BuildResult,
                       job_id: str) -> bpy.types.Object:
    name = f"{data.model_name}_{m.index:02d}_{m.base_name}"[:63]
    me = bpy.data.meshes.new(name)
    me.from_pydata(m.positions.tolist(), [], m.faces.tolist())
    me.update(calc_edges=True)

    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    obj[PROP_JOB] = job_id
    obj[PROP_MESH_INDEX] = m.index
    obj["xps2pmx_raw_name"] = m.raw_name
    me.materials.append(mat)

    if result.armature is not None:
        _assign_weights(obj, me, m, result.bone_names)
        obj.parent = result.armature
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = result.armature

    loop_vertex = m.faces.reshape(-1)
    for layer, uv in enumerate(m.uvs):
        uv_layer = me.uv_layers.new(name="UVMap" if layer == 0 else f"UVMap.{layer:03d}")
        if loop_vertex.size:
            uv_layer.data.foreach_set("uv", uv[loop_vertex].reshape(-1))
    if not m.colors_are_uniform:
        attr = me.color_attributes.new(name="Col", type='BYTE_COLOR', domain='POINT')
        try:  # XPS stores sRGB bytes; ``color_srgb`` avoids a double conversion where available
            attr.data.foreach_set("color_srgb", m.colors.reshape(-1))
        except (AttributeError, TypeError):
            attr.data.foreach_set("color", m.colors.reshape(-1))

    if m.face_count:
        me.polygons.foreach_set("use_smooth", np.ones(m.face_count, dtype=bool))
        me.use_auto_smooth = True
        me.normals_split_custom_set_from_vertices(m.normals.tolist())
    me.update()
    return obj


def _assign_weights(obj, me, m: ImportMesh, bone_names: List[str]) -> None:
    used = sorted({int(b) for b in np.unique(m.weight_bones) if b >= 0})
    if not used:
        return
    group_index = {}
    for b in used:
        group_index[b] = obj.vertex_groups.new(name=bone_names[b]).index
    bm = bmesh.new()
    try:
        bm.from_mesh(me)
        layer = bm.verts.layers.deform.verify()
        bm.verts.ensure_lookup_table()
        bones = m.weight_bones.tolist()
        values = m.weight_values.tolist()
        for vert, vb, vw in zip(bm.verts, bones, values):
            dv = vert[layer]
            for b, w in zip(vb, vw):
                if b < 0:
                    break
                dv[group_index[b]] = w
        bm.to_mesh(me)
    finally:
        bm.free()


# ---------------------------------------------------------------------------
# materials

def _load_image(path: str, color: bool) -> Optional[bpy.types.Image]:
    try:
        img = bpy.data.images.load(path, check_existing=True)
    except RuntimeError:
        return None
    if not color:
        try:
            img.colorspace_settings.name = 'Non-Color'
        except TypeError:
            pass
    return img


def manifest_for(m: ImportMesh, data: ImportData) -> dict:
    """Everything needed later to rebuild an HD material for this mesh (stored as an ID property)."""
    sign = "" if m.optional_visible is None else ("+" if m.optional_visible else "-")
    return {
        "schema": MANIFEST_SCHEMA,
        "key": m.material_key,
        "mesh_index": m.index,
        "raw_name": m.raw_name,
        "base_name": m.base_name,
        "join_name": m.join_name,
        "render_group": -1 if m.render_group is None else int(m.render_group),
        "effective_render_group": int(m.rg_info.number if m.rg_info.number is not None else 5),
        "rg_alpha": bool(m.rg_info.alpha),
        "rg_shading": m.rg_info.shading,
        "specular": float(m.specular),
        "bump_repeat1": float(m.bump_repeat1),
        "bump_repeat2": float(m.bump_repeat2),
        "optional": {"sign": sign, "group": m.optional_group or "", "item": m.optional_item or "",
                     "part": m.optional_part or ""},
        "normal_swizzle": data.normal_swizzle,
        "source": data.source_path,
        "textures": [{"slot": t.slot, "role": t.role, "file": t.file, "raw_path": t.raw_path,
                      "uv_layer": int(t.uv_layer), "path": t.path or ""} for t in m.textures],
    }


def _build_material(m: ImportMesh, data: ImportData) -> bpy.types.Material:
    mat = bpy.data.materials.new(m.base_name or m.material_key)
    mat.use_nodes = True
    mat.use_backface_culling = False
    mat[PROP_MANIFEST] = manifest_for(m, data)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        return mat
    bsdf.inputs["Roughness"].default_value = 0.6

    diffuse = m.texture(DIFFUSE)
    if diffuse is not None and diffuse.found:
        img = _load_image(diffuse.path, color=True)
        if img is not None:
            tex = nodes.new("ShaderNodeTexImage")
            tex.name = tex.label = "xps_diffuse"
            tex.image = img
            tex.location = (-600, 300)
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            if m.rg_info.alpha:
                links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
                mat.blend_method = 'HASHED'
                mat.shadow_method = 'HASHED'

    bump = m.texture(BUMP)
    if bump is not None and bump.found:
        img = _load_image(bump.path, color=False)
        if img is not None:
            tex = nodes.new("ShaderNodeTexImage")
            tex.name = tex.label = "xps_bump"
            tex.image = img
            tex.location = (-900, -200)
            nmap = nodes.new("ShaderNodeNormalMap")
            nmap.location = (-300, -200)
            color_out = tex.outputs["Color"]
            if normal_green_inverted(data.normal_swizzle):
                color_out = _invert_green(nodes, links, color_out)
            links.new(color_out, nmap.inputs["Color"])
            links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def _invert_green(nodes, links, color_socket):
    sep = nodes.new("ShaderNodeSeparateColor")
    sep.location = (-650, -350)
    inv = nodes.new("ShaderNodeMath")
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    inv.location = (-500, -350)
    comb = nodes.new("ShaderNodeCombineColor")
    comb.location = (-400, -250)
    links.new(color_socket, sep.inputs["Color"])
    links.new(sep.outputs["Red"], comb.inputs["Red"])
    links.new(sep.outputs["Green"], inv.inputs[1])
    links.new(inv.outputs["Value"], comb.inputs["Green"])
    links.new(sep.outputs["Blue"], comb.inputs["Blue"])
    return comb.outputs["Color"]


def remove_collection_objects(coll: bpy.types.Collection) -> None:
    """Delete a job's collection with its objects and the data they own (used by "重来")."""
    meshes, arms = set(), set()
    for obj in list(coll.all_objects):
        if obj.type == 'MESH':
            meshes.add(obj.data)
        elif obj.type == 'ARMATURE':
            arms.add(obj.data)
        bpy.data.objects.remove(obj, do_unlink=True)
    for me in meshes:
        if me.users == 0:
            bpy.data.meshes.remove(me)
    for arm in arms:
        if arm.users == 0:
            bpy.data.armatures.remove(arm)
    for child in list(coll.children):
        remove_collection_objects(child)
    bpy.data.collections.remove(coll)


def source_dir(data: ImportData) -> str:
    return os.path.dirname(os.path.abspath(data.source_path)) if data.source_path else ""
