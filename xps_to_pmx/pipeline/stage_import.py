"""Stage ①: read an XPS file and build the Blender scene (headless-callable).

Returns ``(StageResult, job)``.  The stage ends with a self-check comparing the
built Blender data with the file (vertex / face / bone counts, renamed bones,
missing textures).  Nothing here talks to mmd_tools.
"""
from __future__ import annotations

import os
import time
import uuid
from typing import Optional, Tuple

import bpy

from .. import props
from ..blender import importer
from ..core.result import StageResult
from ..core.xps import XpsFormatError, load_xps
from ..core.xps.convert import ImportData, build_import_data

STAGE = "import"


def run(context: bpy.types.Context, filepath: str) -> Tuple[StageResult, Optional[props.XPS2PMX_Job]]:
    res = StageResult(STAGE)
    path = os.path.abspath(bpy.path.abspath(filepath)) if filepath else ""
    if not path or not os.path.isfile(path):
        res.error("import.file_missing", f"找不到 XPS 文件：{path or '（未指定）'}", path)
        return res, None

    t0 = time.perf_counter()
    try:
        model = load_xps(path)
    except (XpsFormatError, OSError) as exc:
        res.error("import.parse_failed", f"XPS 解析失败：{exc}", path)
        return res, None
    t_read = time.perf_counter() - t0
    for warning in model.warnings:
        if "after the last mesh" in warning:  # XPS 11 appends a trailer; the reader skips it on purpose
            res.info("import.trailer", f"读取提示：{warning}")
        else:
            res.warning("import.reader", f"读取提示：{warning}")
    if not model.complete:
        res.error("import.incomplete", "文件不完整或已损坏，读取提前结束", path)
        return res, None

    data = build_import_data(model)
    _report_content(res, data)
    if not data.meshes:
        res.error("import.no_meshes", "文件里没有网格", path)
        return res, None

    job_id = uuid.uuid4().hex[:8]
    built = importer.build_scene(context, data, job_id)
    _self_check(res, data, built)

    st = props.state(context)
    job = st.jobs.add()
    job.job_id = job_id
    job.model_name = data.model_name
    job.source_path = path
    job.collection = built.collection
    job.armature = built.armature
    st.active_job_index = len(st.jobs) - 1

    res.data = {
        "model_name": data.model_name,
        "source": path,
        "version": data.version or "no header",
        "bones": len(data.bones),
        "meshes": len(data.meshes),
        "materials": len(built.materials),
        "vertices": data.vertex_count,
        "faces": data.face_count,
        "normal_swizzle": data.normal_swizzle,
        "has_default_pose": data.has_default_pose,
        "seconds_read": round(t_read, 3),
        "seconds_total": round(time.perf_counter() - t0, 3),
    }
    res.info("import.done",
             f"已导入 {data.model_name}：{len(data.bones)} 骨、{len(data.meshes)} 网格、"
             f"{data.vertex_count} 顶点（{res.data['seconds_total']} 秒）")
    job.record(res)
    return res, job


def _report_content(res: StageResult, data: ImportData) -> None:
    w = data.weight_totals()
    if w.renormalized:
        res.warning("import.weights_renormalized",
                    f"{w.renormalized} 个顶点的权重和不为 1，已归一化")
    if w.truncated:
        res.warning("import.weights_truncated",
                    f"{w.truncated} 个顶点受超过 4 根骨影响（最多 {w.max_influences}），已保留最大的 4 个")
    if w.invalid_refs:
        res.warning("import.weights_invalid", f"{w.invalid_refs} 个权重引用了不存在的骨，已丢弃")
    if w.unweighted and data.bones:
        res.warning("import.weights_missing", f"{w.unweighted} 个顶点没有任何权重")
    dropped = sum(m.dropped_faces for m in data.meshes)
    if dropped:
        res.warning("import.faces_dropped", f"丢弃了 {dropped} 个退化或越界的三角面")
    optional = [m for m in data.meshes if m.optional_visible is not None]
    if optional:
        hidden = sum(1 for m in optional if m.optional_visible is False)
        res.info("import.optional_items",
                 f"{len(optional)} 个可选部件网格（默认隐藏 {hidden} 个），⑤ 阶段可转成材质 morph")
    if not data.bones:
        res.warning("import.no_bones", "文件没有骨骼（可能是道具），后续骨骼阶段不可用")


def _self_check(res: StageResult, data: ImportData, built: importer.BuildResult) -> None:
    for m, obj in zip(data.meshes, built.meshes):
        me = obj.data
        if len(me.vertices) != m.vertex_count or len(me.polygons) != m.face_count:
            res.error("import.count_mismatch",
                      f"网格 {m.raw_name} 顶点/面数与文件不一致："
                      f"{len(me.vertices)}/{len(me.polygons)} vs {m.vertex_count}/{m.face_count}", obj.name)
    if built.armature is not None and len(built.armature.data.bones) != len(data.bones):
        res.error("import.bone_count_mismatch",
                  f"骨骼数不一致：{len(built.armature.data.bones)} vs {len(data.bones)}", built.armature.name)
    for original, renamed in built.renamed_bones:
        res.warning("import.bone_renamed",
                    f"骨名“{original}”过长或重复，Blender 改为“{renamed}”（原名记在骨的属性里）", renamed)
    for mesh_name, role, file in built.missing_textures:
        res.warning("import.texture_missing", f"找不到贴图 {file}（{role}，网格 {mesh_name}）", mesh_name)
