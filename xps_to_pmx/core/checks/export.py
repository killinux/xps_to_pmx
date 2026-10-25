"""Checks on an exported PMX, read back with ``pmx.load`` (design doc §12.1; note 08 Q15-H).

``summary`` is the plain dict produced by ``blender/mmdtools_bridge.read_pmx``;
``expected`` is built from the Blender model before export (bone order, parents,
付与, IK).  Every check compares against those expectations or a fixed PMX/MMD
rule — never against the file itself.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from .mapping import CheckItem

MAX_NAME_BYTES = 15
KNEE_MIN = (-math.pi, 0.0, 0.0)
KNEE_MAX = (math.radians(-0.5), 0.0, 0.0)


def _cp932_problem(name: str) -> Optional[str]:
    try:
        n = len(name.encode("cp932"))
    except UnicodeEncodeError:
        return "含 cp932 无法编码的字符"
    return f"{n} 字节（>15，VMD 会截断）" if n > MAX_NAME_BYTES else None


def check_pmx(summary: Dict, expected: Dict, pmx_path: str = "") -> List[CheckItem]:
    items: List[CheckItem] = []

    def add(level: str, code: str, text: str, bone: str = "") -> None:
        items.append(CheckItem(level, code, text, "", bone))

    bones = summary["bones"]
    names = [b["name"] for b in bones]
    index = {n: i for i, n in enumerate(names)}
    want = expected.get("bones", [])
    want_names = [b["name"] for b in want]
    if names != want_names:
        missing = [n for n in want_names if n not in index]
        extra = [n for n in names if n not in set(want_names)]
        if missing or extra:
            add("error", "export.bone_set", f"PMX 骨与 Blender 不一致：缺 {missing[:5]}，多 {extra[:5]}")
        else:
            first = next(i for i, (a, b) in enumerate(zip(names, want_names)) if a != b)
            add("error", "export.bone_order", f"骨序不一致：第 {first} 根是 {names[first]}，应为 {want_names[first]}")
    for w in want:
        i = index.get(w["name"])
        if i is None:
            continue
        b = bones[i]
        parent = names[b["parent"]] if 0 <= b["parent"] < len(names) else ""
        if parent != w.get("parent", ""):
            add("error", "export.parent", f"{w['name']} 的父骨是 {parent or '无'}，应为 {w.get('parent') or '无'}",
                w["name"])
        if b["parent"] >= i:
            add("error", "export.parent_order", f"{w['name']} 排在父骨 {parent} 之前", w["name"])
        g = w.get("grant")
        if g:
            got = b["grant"]
            if got is None or got[0] < 0:
                add("error", "export.grant_missing", f"{w['name']} 的付与源丢失（索引 -1）", w["name"])
            elif names[got[0]] != g[0] or abs(got[1] - g[1]) > 1e-4:
                add("error", "export.grant", f"{w['name']} 付与 {names[got[0]]}×{got[1]:.2f}，应为 {g[0]}×{g[1]:.2f}",
                    w["name"])
            elif b["transform_order"] < bones[got[0]]["transform_order"] or (
                    b["transform_order"] == bones[got[0]]["transform_order"] and got[0] > i):
                add("error", "export.grant_order", f"{w['name']} 的付与源排在它之后", w["name"])
        elif b["grant"] is not None:
            add("error", "export.grant_unexpected", f"{w['name']} 不应有付与", w["name"])
        if b["transform_order"] != w.get("transform_order", 0):
            add("error", "export.transform_order",
                f"{w['name']} 変形階層 {b['transform_order']}，应为 {w.get('transform_order', 0)}", w["name"])
        for flag in ("visible", "controllable", "movable"):
            if flag in w and bool(b[flag]) != bool(w[flag]):
                add("warning", f"export.flag_{flag}", f"{w['name']} 的 {flag} 为 {b[flag]}，应为 {w[flag]}", w["name"])
        ik = w.get("ik")
        if ik:
            got = b["ik"]
            if not got:
                add("error", "export.ik_missing", f"{w['name']} 不是 IK 骨", w["name"])
                continue
            if names[got["target"]] != ik["target"]:
                add("error", "export.ik_target", f"{w['name']} 的 IK 目标是 {names[got['target']]}，应为 {ik['target']}",
                    w["name"])
            link_names = [names[l["bone"]] for l in got["links"]]
            if link_names != ik["links"]:
                add("error", "export.ik_links", f"{w['name']} 的 IK 链 {link_names}，应为 {ik['links']}", w["name"])
            if got["loop"] != ik["loop"] or abs(got["unit"] - ik["unit"]) > 1e-4:
                add("error", "export.ik_params", f"{w['name']} loop {got['loop']}/单位角 {got['unit']:.4f}，"
                                                 f"应为 {ik['loop']}/{ik['unit']:.4f}", w["name"])
            for l, lim in zip(got["links"], ik.get("limits", [])):
                if lim is None:
                    continue
                if l["min"] is None or any(abs(a - b) > 1e-3 for a, b in zip(l["min"] + l["max"], lim[0] + lim[1])):
                    add("error", "export.ik_limit", f"{w['name']} 链骨 {names[l['bone']]} 的角度限制不对："
                                                    f"{l['min']}～{l['max']}", w["name"])
            for ref in [got["target"]] + [l["bone"] for l in got["links"]]:
                if bones[ref]["transform_order"] > b["transform_order"] or (
                        bones[ref]["transform_order"] == b["transform_order"] and ref > i):
                    add("error", "export.ik_order", f"IK 相关骨 {names[ref]} 排在 {w['name']} 之后", w["name"])
    for b in bones:
        problem = _cp932_problem(b["name"])
        if problem:
            add("warning", "export.bone_name", f"骨名 {b['name']}：{problem}", b["name"])
    if len(set(names)) != len(names):
        add("error", "export.bone_duplicate", "PMX 里有重名骨")

    # weights
    if summary.get("bad_weight_refs"):
        add("error", "export.weight_refs", f"{summary['bad_weight_refs']} 个权重引用了不存在的骨")
    if summary.get("weight_sums_off"):
        add("error", "export.weight_sums", f"{summary['weight_sums_off']} 个顶点权重和不为 1")
    if summary.get("max_influences", 0) > 4:
        add("error", "export.weight_influences", f"有顶点受 {summary['max_influences']} 根骨影响")
    counts = summary.get("weight_counts", [])
    for n in expected.get("no_weight", []):
        i = index.get(n)
        if i is not None and i < len(counts) and counts[i]:
            add("error", "export.weight_on_control", f"{n} 不应有权重（{counts[i]} 个顶点）", n)
    for n in expected.get("need_weight", []):
        i = index.get(n)
        if i is not None and i < len(counts) and not counts[i]:
            add("warning", "export.weight_missing", f"{n} 没有权重", n)
    if expected.get("vertices") is not None and summary.get("unweighted_vertices"):
        add("warning", "export.unweighted", f"{summary['unweighted_vertices']} 个顶点没有权重（绑到第 0 根骨）")

    # geometry: feet on the ground, shoulder height
    if "min_y" in summary and abs(summary["min_y"]) > expected.get("ground_tolerance", 0.5):
        add("warning", "export.ground", f"模型最低点 Y={summary['min_y']:.3f}，没有贴地")
    for n, want_y in expected.get("heights", {}).items():
        i = index.get(n)
        if i is not None and abs(bones[i]["location"][1] - want_y) > 0.15:
            add("warning", "export.height", f"{n} 高 {bones[i]['location'][1]:.2f}，预期 {want_y:.2f}", n)

    # display frames
    frames = summary.get("frames", [])
    if len(frames) < 2 or not (frames[0]["special"] and frames[1]["special"]):
        add("error", "export.frames_special", "表示枠的前两个必须是特殊枠 Root 与 表情")
    in_frames = {}
    for f in frames:
        for t, i in f["items"]:
            if t == 0:
                if not 0 <= i < len(bones):
                    add("error", "export.frame_index", f"表示枠 {f['name']} 引用了无效骨索引 {i}")
                else:
                    in_frames.setdefault(i, []).append(f["name"])
            elif t == 1 and not 0 <= i < summary.get("morphs", 0):
                add("error", "export.frame_index", f"表示枠 {f['name']} 引用了无效表情索引 {i}")
    for i, fs in in_frames.items():
        if len(fs) > 1:
            add("warning", "export.frame_duplicate", f"{names[i]} 出现在多个表示枠：{fs}", names[i])
    loose = [names[i] for i, b in enumerate(bones) if b["visible"] and b["controllable"] and i not in in_frames]
    if loose:
        add("warning", "export.frame_missing", f"{len(loose)} 根可操作骨不在任何表示枠里：{loose[:5]}")

    # textures
    base = os.path.dirname(pmx_path) if pmx_path else ""
    missing_tex = [t for t in summary.get("textures", []) if not os.path.isfile(t)]
    if missing_tex:
        add("warning", "export.texture_missing", f"{len(missing_tex)} 张贴图文件不存在：{missing_tex[:3]}")
    outside = [t for t in summary.get("textures", []) if base and not os.path.normcase(os.path.abspath(t)).startswith(
        os.path.normcase(os.path.abspath(base)))]
    if outside:
        add("warning", "export.texture_outside", f"{len(outside)} 张贴图不在 PMX 目录内（未复制）：{outside[:3]}")
    if not summary.get("materials"):
        add("error", "export.no_materials", "PMX 没有材质")
    return items
