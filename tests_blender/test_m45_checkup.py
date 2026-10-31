"""M4.5 (design doc §15.10): one-click, fix list, fix files, redo from scratch, the checkup.

Regression models: one-click without error-level findings, fix files written and picked up again,
分步重做 stops at ② and 继续 finishes.  rouffe (optional, skipped when missing): the knee / elbow
helpers merge correctly, duplicate names are reported and the split fix clears them, the automatic
merge fix works when the classifier errs, hand-made wrong merges are reported but not overridden,
and ignored findings stay hidden.  Exports and user data go to the test output folder.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

import bpy  # noqa: E402

ARGS = harness.parse_args()
OUT = os.path.join(ARGS.out, "m45")
os.environ["XPS2PMX_EXPORT_ROOT"] = os.path.join(OUT, "exports")
os.environ["XPS2PMX_USER_DATA"] = os.path.join(OUT, "user_data")

harness.register_addon()
from xps_to_pmx.core.rig import classify  # noqa: E402
from xps_to_pmx.pipeline import fixlist, runner, stage_checkup  # noqa: E402

ROUFFE = "E:/Downloads/rouffe (grand magician)/rouffe/xps.xps"
HELPERS = {"unused bip001 lcalftwist": ("left_knee_bone", "left_thigh_bone"),
           "unused bip001 rcalftwist": ("right_knee_bone", "right_thigh_bone"),
           "unused trash 18": ("left_lower_arm_bone", "left_upper_arm_bone"),
           "unused trash 19": ("right_lower_arm_bone", "right_upper_arm_bone")}


def _errors(res):
    return [m.text for m in res.messages if m.level == "error"]


def _findings(job, code=None, level=None):
    return [f for f in job.findings if (code is None or f.code == code) and (level is None or f.level == level)
            and f.state != "fixed"]


def _merge_slots(job):
    return {r["bone"]: r["slot"] for r in json.loads(job.merge_analysis_json or "[]")}


def _clean_user_data():
    folder = os.path.join(os.environ["XPS2PMX_USER_DATA"], "fixes")
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            os.remove(os.path.join(folder, name))


def check_model(entry, first: bool):
    c = harness.Checker(entry["id"] + " (one-click)")
    if not os.path.isfile(entry["path"]):
        c.check("model file present (skipped)", True, entry["path"])
        return c
    harness.reset_scene()
    res, job = runner.one_click(bpy.context, entry["path"], remember=False)
    c.check("one-click ok", res.ok and job is not None and job.stage == "checkup", _errors(res)[:3])
    if job is None:
        return c
    errors = [f.text for f in _findings(job, level="error")]
    c.check("no error-level findings", not errors, errors[:3])
    new_checks = [f.text for f in job.findings if f.code in ("checkup.joint_leak", "checkup.side_leak")
                  and f.level != "info"]
    c.check("new symptom checks: no warnings on a good model", not new_checks, new_checks[:3])
    pmx = job.last_export
    c.check("fix file next to the PMX", os.path.isfile(fixlist.pmx_fixes_path(pmx)), pmx)
    c.check("fix file in the user data folder",
            os.path.isfile(fixlist.user_fixes_path(bpy.context, job.source_sha1)), job.source_sha1)
    with open(os.path.splitext(pmx)[0] + ".report.json", encoding="utf-8") as f:
        report = json.load(f)
    c.check("report has the checkup", "checkup" in report and report["checkup"]["counts"] is not None)
    if not first:
        return c

    # remembered fixes and options: change both, export, convert again in a fresh scene
    sha1 = job.source_sha1
    job.shoulder_target = 17.5
    target = next(f for f in job.findings if f.state != "fixed")
    target_key = target.key                      # the item reference dies with the removal below
    fixlist.ignore_finding(bpy.context, job, list(job.findings).index(target))
    ignored_key = f"ignore:{target_key}"
    saved = fixlist.save(bpy.context, job, pmx)
    c.check("fix files saved", len(saved.data.get("paths", [])) == 2, saved.data)
    harness.reset_scene()
    res, job = runner.one_click(bpy.context, entry["path"])
    c.check("second one-click ok", res.ok and job is not None, _errors(res)[:3])
    if job is None:
        return c
    c.check("remembered fix list applied", job.fix_item(ignored_key) is not None and job.source_sha1 == sha1,
            [f.key for f in job.fixes])
    c.check("remembered option applied", abs(job.shoulder_target - 17.5) < 1e-6, job.shoulder_target)
    c.check("ignored finding hidden", all(f.key != target_key for f in job.findings), target_key)
    c.check("loaded message", any(m.code == "fixes.loaded" for m in res.messages))

    # 分步重做 stops at ②, 继续 finishes, the checkup compares with the previous one
    before = {f.key for f in job.findings if f.state != "fixed"}
    res, job = runner.redo(bpy.context, job, stop_after="identify")
    c.check("分步重做 stops at ②", res.ok and job is not None and job.stage == "identify",
            (job.stage if job else None, _errors(res)[:3]))
    if job is None:
        return c
    res = runner.continue_job(bpy.context, job)
    c.check("继续 runs to ⑨", res.ok and job.stage == "checkup", _errors(res)[:3])
    after = {f.key for f in job.findings if f.state != "fixed"}
    c.check("same findings after redo (remaining)", after == before and all(
        f.state in ("remaining", "auto_fixed") for f in job.findings), sorted(after ^ before)[:5])
    c.check("one job left", len(bpy.context.scene.xps2pmx.jobs) == 1, len(bpy.context.scene.xps2pmx.jobs))
    return c


def check_rouffe():
    c = harness.Checker("rouffe (checkup)")
    if not os.path.isfile(ROUFFE):
        c.check("rouffe present (skipped)", True)
        return c
    _clean_user_data()
    harness.reset_scene()
    res, job = runner.one_click(bpy.context, ROUFFE, remember=False)
    c.check("one-click ok", res.ok and job is not None, _errors(res)[:3])
    if job is None:
        return c
    slots = _merge_slots(job)
    c.check("helpers merge into ひざ/ひじ by weight",
            all(slots.get(b) == right for b, (right, _) in HELPERS.items()), {b: slots.get(b) for b in HELPERS})
    c.check("no joint leak", not _findings(job, "checkup.joint_leak"), [f.text for f in _findings(job, "checkup.joint_leak")])
    dups = _findings(job, "mapping.duplicate_name")
    c.check("two duplicate names reported", len(dups) == 2, [f.text for f in dups])
    c.check("duplicate findings carry the side-leak evidence", all("体检" in f.detail for f in dups),
            [f.detail for f in dups])
    c.check("split fixes are not automatic", not any(f.kind == "split_side" for f in job.fixes))

    # tick both split fixes and redo
    for f in list(job.findings):
        if f.code == "mapping.duplicate_name":
            fixlist.toggle_finding_fix(bpy.context, job, list(job.findings).index(f))
    c.check("fix list pending", job.fixes_pending and sum(1 for f in job.fixes if f.kind == "split_side") == 2)
    res, job = runner.redo(bpy.context, job)
    c.check("redo ok", res.ok and job is not None, _errors(res)[:3])
    if job is None:
        return c
    c.check("splits applied once", len(json.loads(job.splits_done_json)) == 2, job.splits_done_json)
    c.check("duplicate names gone", not _findings(job, "mapping.duplicate_name"))
    c.check("no side leak left", not [f for f in _findings(job, "checkup.side_leak") if f.level != "info"],
            [f.text for f in _findings(job, "checkup.side_leak")])
    fixed = [f.code for f in job.findings if f.state == "fixed"]
    c.check("report says they are fixed", fixed.count("mapping.duplicate_name") == 2, fixed)
    c.check("pending cleared", not job.fixes_pending)

    # the automatic merge fix when the classifier errs (simulated: head rule only)
    original = classify.segment_mass
    classify.segment_mass = lambda *a, **k: None
    try:
        harness.reset_scene()
        res, job = runner.one_click(bpy.context, ROUFFE, remember=False)
    finally:
        classify.segment_mass = original
    c.check("one-click ok (old classifier)", res.ok and job is not None, _errors(res)[:3])
    if job is None:
        return c
    auto = {f.bone: f.slot_id for f in job.fixes if f.auto and f.enabled}
    c.check("four automatic fixes", auto == {b: right for b, (right, _) in HELPERS.items()}, auto)
    c.check("report lists them as auto-fixed", len([f for f in job.findings if f.state == "auto_fixed"]) == 4)
    slots = _merge_slots(job)
    c.check("final merges correct", all(slots.get(b) == right for b, (right, _) in HELPERS.items()), slots)
    c.check("no joint leak", not _findings(job, "checkup.joint_leak"))

    # hand-made wrong merges are reported, not overridden
    from xps_to_pmx.core.fixes import Fix
    for bone, (_, wrong) in HELPERS.items():
        job.upsert_fix(Fix("bone", bone=bone, src=bone, action="merge", slot_id=wrong, origin="user"))
    res, job = runner.redo(bpy.context, job)
    c.check("redo ok (hand-made merges)", res.ok and job is not None, _errors(res)[:3])
    if job is None:
        return c
    slots = _merge_slots(job)
    c.check("hand-made merges kept", all(slots.get(b) == wrong for b, (_, wrong) in HELPERS.items()), slots)
    warn = _findings(job, "mapping.merge_segment")
    c.check("four merge-segment warnings", len(warn) == 4 and all(not json.loads(f.fix_json)["auto"] for f in warn),
            [f.text for f in warn])
    c.check("knee / elbow symptoms found and joined to them", sum("体检" in f.detail for f in warn) >= 2,
            [f.detail for f in warn])

    # ignore a finding
    lb = next((f for f in job.findings if f.code == "lower_body.high"), None)
    if lb is not None:
        fixlist.ignore_finding(bpy.context, job, list(job.findings).index(lb))
        res, job = runner.redo(bpy.context, job)
        c.check("ignored finding stays hidden", job is not None and not _findings(job, "lower_body.high"))
        c.check("ignored count reported", job is not None and job.summary().get("checkup", {}).get("ignored") == 1,
                job.summary().get("checkup") if job else None)
    c.check("previous findings snapshot works", isinstance(stage_checkup.snapshot_findings(job), dict))
    return c


def main():
    models = harness.regression_models(ARGS.models)
    _clean_user_data()
    checkers = [check_model(m, first=(i == 0)) for i, m in enumerate(models)]
    if not ARGS.models:
        checkers.append(check_rouffe())
    report = harness.write_report(ARGS.out, "m45_checkup", checkers)
    harness.finish(report)


main()
