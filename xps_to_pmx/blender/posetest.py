"""Blender side of the pose tests (design doc §16): the pose rig, the preview for 定位, thumbnails for 看图.

Nothing here poses the converted model.  定位 hides the model's collection and shows posed copies
of its meshes, with the vertices of the finding selected; 看图 renders such copies in a scene of
its own.  The positions come from :mod:`core.checks.posetest` (posed the way MMD poses them), so
the armature, its IK constraints and the export stay untouched.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import bpy
import numpy as np
from mathutils import Matrix, Vector

from ..core.checks import posetest
from . import snapshot

PREVIEW_PREFIX = "XPS2PMX 姿势预览"
RENDER_NAME = "XPS2PMX 看图"
MARK_COLOR = (0.92, 0.16, 0.12, 1.0)
#: job id → (cache key, PoseRig, mesh slices); the snapshot is the slow part of 定位 / 看图
_CACHE: Dict[str, Tuple[tuple, posetest.PoseRig, List[Tuple[str, int, int]]]] = {}
CACHE_SIZE = 3


def pose_rig(arm: bpy.types.Object, rig, body_names: Iterable[str]) -> posetest.PoseRig:
    """Bones with their rotation grants (from mmd_tools' ``mmd_bone``) and the skin of ``rig``."""
    index = {b.name: i for i, b in enumerate(arm.data.bones)}
    bones = []
    for b in arm.data.bones:
        mb = getattr(arm.pose.bones[b.name], "mmd_bone", None)
        grant, rate = -1, 0.0
        if mb is not None and mb.has_additional_rotation and mb.additional_transform_bone in index:
            grant, rate = index[mb.additional_transform_bone], float(mb.additional_transform_influence)
        bones.append(posetest.PoseBone(b.name, index[b.parent.name] if b.parent else -1,
                                       np.array(b.head_local, float), grant, rate))
    return posetest.PoseRig(bones, rig.skin.positions, rig.skin.bones, rig.skin.weights, body_names)


def _cache_key(arm: bpy.types.Object, meshes: Sequence[bpy.types.Object]) -> tuple:
    return (arm.name, tuple((m.name, len(m.data.vertices)) for m in meshes))


def remember(job_id: str, arm: bpy.types.Object, meshes, prig: posetest.PoseRig, slices) -> None:
    _CACHE.pop(job_id, None)
    _CACHE[job_id] = (_cache_key(arm, meshes), prig, list(slices or []))
    while len(_CACHE) > CACHE_SIZE:  # a redo makes a new job; the old one's arrays are not needed
        _CACHE.pop(next(iter(_CACHE)))


def job_rig(job, body_names: Iterable[str]) -> Tuple[posetest.PoseRig, List[Tuple[str, int, int]]]:
    arm = job.armature
    meshes = snapshot.skinned_meshes(arm)
    key = _cache_key(arm, meshes)
    cached = _CACHE.get(job.job_id)
    if cached is not None and cached[0] == key:
        return cached[1], cached[2]
    rig = snapshot.rig_from_blender(arm, meshes=meshes)
    prig = pose_rig(arm, rig, body_names)
    remember(job.job_id, arm, meshes, prig, rig.skin.mesh_slices)
    return prig, list(rig.skin.mesh_slices or [])


# ---------------------------------------------------------------------------
# posed copies

def _copies(arm: bpy.types.Object, slices, positions: np.ndarray, collection: bpy.types.Collection,
            selected: Optional[np.ndarray] = None) -> List[bpy.types.Object]:
    """Copies of the model's meshes at ``positions`` (armature space), without modifiers and shape keys."""
    out = []
    arm_world = np.array(arm.matrix_world)
    for name, start, end in slices:
        src = bpy.data.objects.get(name)
        if src is None or src.type != 'MESH' or len(src.data.vertices) != end - start:
            continue
        me = src.data.copy()
        me.name = f"{PREVIEW_PREFIX} {src.name}"
        obj = bpy.data.objects.new(me.name, me)
        collection.objects.link(obj)
        obj.matrix_world = src.matrix_world.copy()
        if me.shape_keys is not None:
            obj.shape_key_clear()
        local = np.linalg.inv(np.array(src.matrix_world)) @ arm_world
        co = positions[start:end] @ local[:3, :3].T + local[:3, 3]
        me.vertices.foreach_set("co", co.astype(np.float32).ravel())
        if selected is not None:
            me.vertices.foreach_set("select", selected[start:end])
            me.edges.foreach_set("select", np.zeros(len(me.edges), bool))
            me.polygons.foreach_set("select", np.zeros(len(me.polygons), bool))
        me.update()
        out.append(obj)
    return out


def _remove_objects(objects: Iterable[bpy.types.Object]) -> None:
    for obj in list(objects):
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)


def _layer_collection(layer: bpy.types.LayerCollection, coll: bpy.types.Collection):
    if layer.collection == coll:
        return layer
    for child in layer.children:
        found = _layer_collection(child, coll)
        if found is not None:
            return found
    return None


# ---------------------------------------------------------------------------
# 定位: the preview in the viewport

def preview_active(job) -> bool:
    return job.preview_collection is not None


def show_preview(context: bpy.types.Context, job, view: Dict, prig: posetest.PoseRig, slices,
                 label: str) -> int:
    """Hide the model, show it posed for ``view`` with the view's vertices selected, frame them.

    Returns the number of selected vertices.
    """
    clear_preview(context, job)
    positions = posetest.view_positions(prig, view)
    selected = np.zeros(len(positions), bool)
    verts = np.asarray(view.get("vertices", []), np.int64)
    verts = verts[(verts >= 0) & (verts < len(positions))]
    selected[verts] = True
    coll = bpy.data.collections.new(f"{PREVIEW_PREFIX} {job.model_name}")
    context.scene.collection.children.link(coll)
    objs = _copies(job.armature, slices, positions, coll, selected)
    job.preview_collection = coll
    job.pose_preview = label
    if job.collection is not None:
        layer = _layer_collection(context.view_layer.layer_collection, job.collection)
        if layer is not None:
            layer.hide_viewport = True
    if context.view_layer.objects.active is not None and context.view_layer.objects.active.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in context.view_layer.objects:
        obj.select_set(False)
    chosen = [o for o in objs if any(v.select for v in o.data.vertices)] if len(verts) else []
    if chosen:
        for obj in chosen:
            obj.select_set(True)
        context.view_layer.objects.active = max(chosen, key=lambda o: sum(v.select for v in o.data.vertices))
        bpy.ops.object.mode_set(mode='EDIT')
        context.tool_settings.mesh_select_mode = (True, False, False)
    elif objs:
        context.view_layer.objects.active = objs[0]
    frame(context, job.armature, view)
    return int(len(verts))


def frame(context: bpy.types.Context, arm: bpy.types.Object, view: Dict) -> bool:
    """Point the first 3D view at the view's focus, from its direction."""
    screen = context.screen
    area = next((a for a in screen.areas if a.type == 'VIEW_3D'), None) if screen is not None else None
    if area is None:
        return False
    r3d = area.spaces.active.region_3d
    scale = arm.matrix_world.to_scale()[0] or 1.0
    r3d.view_location = arm.matrix_world @ Vector(view.get("focus", (0.0, 0.0, 1.0)))
    r3d.view_distance = float(view.get("size", 1.0)) * scale * 1.4
    direction = Vector(view.get("dir", (0.0, -1.0, 0.0)))
    if direction.length > 1e-9:
        r3d.view_rotation = direction.normalized().to_track_quat('Z', 'Y')
    return True


def clear_preview(context: bpy.types.Context, job) -> bool:
    """Remove the preview and show the model again; False when there was none."""
    coll = job.preview_collection
    if coll is None:
        return False
    active = context.view_layer.objects.active
    if active is not None and active.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    _remove_objects(coll.objects)
    bpy.data.collections.remove(coll)
    job.preview_collection = None
    job.pose_preview = ""
    if job.collection is not None:
        layer = _layer_collection(context.view_layer.layer_collection, job.collection)
        if layer is not None:
            layer.hide_viewport = False
    if job.armature is not None and job.armature.name in context.view_layer.objects:
        for obj in context.view_layer.objects:
            obj.select_set(False)
        job.armature.select_set(True)
        context.view_layer.objects.active = job.armature
    return True


# ---------------------------------------------------------------------------
# 看图: a thumbnail of the posed copies

def render(job, view: Dict, prig: posetest.PoseRig, slices, path: str, resolution: int = 360) -> bool:
    """Render the posed model around the view's focus into ``path`` (PNG) and mark the view's vertices."""
    positions = posetest.view_positions(prig, view)
    arm = job.armature
    scene = bpy.data.scenes.new(RENDER_NAME)
    coll = bpy.data.collections.new(RENDER_NAME)
    scene.collection.children.link(coll)
    world = bpy.data.worlds.new(RENDER_NAME)
    objs: List[bpy.types.Object] = []
    try:
        objs = _copies(arm, slices, positions, coll)
        cam_data = bpy.data.cameras.new(RENDER_NAME)
        cam = bpy.data.objects.new(RENDER_NAME, cam_data)
        coll.objects.link(cam)
        objs.append(cam)
        scale = arm.matrix_world.to_scale()[0] or 1.0
        size = float(view.get("size", 1.0)) * scale
        focus = arm.matrix_world @ Vector(view.get("focus", (0.0, 0.0, 1.0)))
        direction = Vector(view.get("dir", (0.0, -1.0, 0.0)))
        direction = direction.normalized() if direction.length > 1e-9 else Vector((0.0, -1.0, 0.0))
        reach = prig.height * scale * 2.0 + size
        cam.matrix_world = Matrix.Translation(focus + direction * reach) @ \
            direction.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = size
        cam_data.clip_start = 0.001
        cam_data.clip_end = reach * 2.0 + size
        scene.camera = cam
        scene.world = world
        world.color = (0.86, 0.86, 0.86)
        r = scene.render
        r.engine = 'BLENDER_WORKBENCH'
        r.resolution_x = r.resolution_y = resolution
        r.resolution_percentage = 100
        r.film_transparent = False
        r.image_settings.file_format = 'PNG'
        r.image_settings.color_mode = 'RGB'
        r.filepath = path
        shading = scene.display.shading
        shading.light = 'STUDIO'
        shading.color_type = 'SINGLE'
        shading.single_color = (0.80, 0.76, 0.72)
        shading.show_cavity = True
        bpy.ops.render.render(write_still=True, scene=scene.name)
        verts = np.asarray(view.get("vertices", []), np.int64)
        verts = verts[(verts >= 0) & (verts < len(positions))]
        if len(verts):
            world_pts = positions[verts] @ np.array(arm.matrix_world)[:3, :3].T + np.array(arm.matrix_world)[:3, 3]
            _mark(path, world_pts, cam, size, resolution)
        return True
    finally:
        _remove_objects(objs)
        bpy.data.collections.remove(coll)
        bpy.data.worlds.remove(world)
        bpy.data.scenes.remove(scene)


def _mark(path: str, points: np.ndarray, cam: bpy.types.Object, size: float, resolution: int) -> None:
    """Draw the points as small red dots onto the rendered image."""
    img = bpy.data.images.load(path, check_existing=False)
    try:
        w, h = img.size
        px = np.empty(w * h * 4, np.float32)
        img.pixels.foreach_get(px)
        px = px.reshape(h, w, 4)
        inv = np.array(cam.matrix_world.inverted())
        c = points @ inv[:3, :3].T + inv[:3, 3]
        front = c[:, 2] < 0
        u = ((c[:, 0] / size) + 0.5) * w
        v = ((c[:, 1] / size) + 0.5) * h
        keep = front & (u >= 0) & (u < w) & (v >= 0) & (v < h)
        ui, vi = u[keep].astype(np.int64), v[keep].astype(np.int64)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                px[np.clip(vi + dy, 0, h - 1), np.clip(ui + dx, 0, w - 1)] = MARK_COLOR
        img.pixels.foreach_set(px.ravel())
        img.filepath_raw = path
        img.file_format = 'PNG'
        img.save()
    finally:
        bpy.data.images.remove(img)
