"""Shared helpers for headless Blender tests.

Run through ``scripts/run_blender_tests.py`` (or directly)::

    blender -b --factory-startup --python-exit-code 1 --python tests_blender/<test>.py -- [--models id ...]

The add-on is imported from the repository (not from the add-ons folder), so
tests always exercise the working tree.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import bpy  # noqa: E402


def script_args(argv=None):
    argv = list(sys.argv if argv is None else argv)
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args(extra=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=None, help="regression model ids (default: all)")
    parser.add_argument("--out", default=os.path.join(REPO, "out", "blender_tests"))
    if extra:
        extra(parser)
    return parser.parse_args(script_args())


def regression_models(ids=None):
    with open(os.path.join(REPO, "tests_blender", "regression_models.json"), encoding="utf-8") as f:
        models = json.load(f)["models"]
    if ids:
        models = [m for m in models if m["id"] in ids]
    return models


def register_addon():
    import xps_to_pmx
    try:
        xps_to_pmx.register()
    except ValueError:  # already registered in this session
        pass
    return xps_to_pmx


def reset_scene():
    bpy.ops.wm.read_homefile(use_empty=True, use_factory_startup=True)


class Checker:
    """Collects pass/fail results per model; a failed check never stops the remaining checks."""

    def __init__(self, name):
        self.name = name
        self.results = []

    def check(self, label, condition, detail=""):
        self.results.append({"check": label, "ok": bool(condition), "detail": str(detail)})
        status = "PASS" if condition else "FAIL"
        print(f"[{status}] {self.name}: {label}" + (f" -- {detail}" if detail else ""))
        return bool(condition)

    def run(self, label, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # report and continue
            self.check(label, False, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
            return None

    @property
    def ok(self):
        return all(r["ok"] for r in self.results)


def write_report(out_dir, test_name, checkers, extra=None):
    os.makedirs(out_dir, exist_ok=True)
    report = {
        "test": test_name,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "blender": bpy.app.version_string,
        "ok": all(c.ok for c in checkers),
        "models": {c.name: c.results for c in checkers},
    }
    if extra:
        report.update(extra)
    path = os.path.join(out_dir, f"{test_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    failed = sum(1 for c in checkers for r in c.results if not r["ok"])
    total = sum(len(c.results) for c in checkers)
    print(f"== {test_name}: {total - failed}/{total} checks passed -> {path}")
    return report


def finish(report):
    sys.stdout.flush()
    if not report["ok"]:
        raise SystemExit(1)
