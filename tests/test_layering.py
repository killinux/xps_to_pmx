"""Enforce the layer rules of the design doc (§3.1) by scanning import statements."""
from __future__ import annotations

import ast
import os

PKG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "xps_to_pmx")
BLENDER_ONLY = {"bpy", "bmesh", "mathutils", "bpy_extras", "gpu", "addon_utils"}


def _imports(path):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, 0
        elif isinstance(node, ast.ImportFrom):
            yield (node.module or ""), node.level


def _py_files(subdir):
    root = os.path.join(PKG, subdir)
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


def _resolve(path, module, level):
    """Absolute dotted module name inside the package for a relative import (best effort)."""
    if level == 0:
        return module
    rel = os.path.relpath(os.path.dirname(path), os.path.dirname(PKG)).replace(os.sep, ".")
    parts = rel.split(".")
    base = parts[: len(parts) - (level - 1)] if level > 1 else parts
    return ".".join(base + ([module] if module else []))


def test_core_has_no_blender_dependency():
    offenders = []
    for path in _py_files("core"):
        for module, level in _imports(path):
            top = _resolve(path, module, level).split(".")
            if top[0] in BLENDER_ONLY or (top[0] == "xps_to_pmx" and len(top) > 1
                                          and top[1] not in ("core",)):
                offenders.append((os.path.relpath(path, PKG), module, level))
    assert not offenders, offenders


def test_only_bridge_imports_mmd_tools():
    offenders = []
    for path in _py_files(""):
        if os.path.basename(path) == "mmdtools_bridge.py":
            continue
        for module, level in _imports(path):
            if level == 0 and module.split(".")[0] == "mmd_tools":
                offenders.append(os.path.relpath(path, PKG))
    assert not offenders, offenders


def test_ui_does_not_call_blender_layer():
    offenders = []
    for path in _py_files("ui"):
        for module, level in _imports(path):
            name = _resolve(path, module, level)
            if name.startswith("xps_to_pmx.blender") or name.startswith("xps_to_pmx.pipeline"):
                offenders.append((os.path.relpath(path, PKG), name))
    assert not offenders, offenders


def test_ops_only_use_pipeline_and_props():
    offenders = []
    for path in _py_files("ops"):
        for module, level in _imports(path):
            name = _resolve(path, module, level)
            if name.startswith("xps_to_pmx.blender") or name.startswith("xps_to_pmx.core"):
                offenders.append((os.path.relpath(path, PKG), name))
    assert not offenders, offenders
