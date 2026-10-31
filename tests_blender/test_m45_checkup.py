"""M4.5 (design doc §15.10): one-click, fix list, fix files, redo from scratch, the checkup.

Regression models: one-click without error-level findings and without pose-test warnings, fix files
written and picked up again, 分步重做 stops at ② and 继续 finishes.  rouffe (optional, skipped when
missing): the knee / elbow helpers merge correctly, duplicate names are reported (with the shrug pose
as evidence) and the split fix clears them, 定位 shows a posed preview and 复位 removes it, 看图 renders
before / after thumbnails, the 下半身 warning is judged by the pose tests, the automatic merge fix works
when the classifier errs, hand-made wrong merges are reported but not overridden, and ignored findings
stay hidden.  Exports and user data go to the test output folder.
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
from xps_to_pmx.blender import posetest as bpt  # noqa: E402
from xps_to_pmx.pipeline import fixlist, runner, stage_checkup, views  # noqa: E402

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
    pose = [f.text for f in job.findings if f.code.startswith("pose.") and f.level != "info"]
    c.check("pose tests: no warnings on a good model", not pose, pose[:3])
    c.check("pose tests ran", job.checkup_run == 1 and bool(bpt._CACHE.get(job.job_id)), job.checkup_run)
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
    c.check("the shrug pose is evidence of a duplicate", any("左肩上耸 25°" in f.detail or "右肩上耸 25°" in f.detail
                                                           for f in dups), [f.detail for f in dups])
    c.check("duplicate findings have a view", all(f.view_json for f in dups))
    lb = next((f for f in job.findings if f.code == "lower_body.high"), None)
    c.check("下半身 warning judged by the pose tests",
            lb is not None and lb.level == "info" and "18 系列成品也是这样" in lb.detail and lb.view_json,
            (lb.level, lb.detail) if lb else None)

    # 定位: posed copies with the vertices selected; the model itself is hidden, not posed
    index = list(job.findings).index(dups[0])
    view = json.loads(dups[0].view_json)
    r = views.locate(bpy.context, job, index)
    coll = job.preview_collection
    c.check("定位 ok", r.ok and coll is not None, [m.text for m in r.messages])
    layer = bpt._layer_collection(bpy.context.view_layer.layer_collection, job.collection)
    c.check("model hidden while previewing", layer is not None and layer.hide_viewport)
    if coll is not None:
        selected = sum(v.select for o in coll.objects for v in o.data.vertices)
        c.check("the view's vertices are selected", selected == len(view["vertices"]), (selected, len(view["vertices"])))
        c.check("edit mode on the preview", bpy.context.mode == 'EDIT_MESH', bpy.context.mode)
    c.check("armature not posed", all(pb.matrix_basis.is_identity for pb in job.armature.pose.bones))
    r = views.reset(bpy.context, job)
    c.check("复位 removes the preview", job.preview_collection is None and bpy.context.mode == 'OBJECT'
            and not any(o.name.startswith(bpt.PREVIEW_PREFIX) for o in bpy.data.objects)
            and not layer.hide_viewport, bpy.context.mode)

    # 看图
    r = views.render_finding(bpy.context, job, index)
    shot = job.findings[index].image_after
    c.check("看图 renders a thumbnail", r.ok and os.path.isfile(shot), [m.text for m in r.messages])
    c.check("render left nothing behind", not any(o.name.startswith(bpt.RENDER_NAME) for o in bpy.data.objects)
            and bpy.data.scenes.get(bpt.RENDER_NAME) is None)
    run = job.checkup_run

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
    right = [b for b in job.armature.data.bones if b.head_local.x < -0.05
             and job.armature.pose.bones[b.name].mmd_bone.name_e.startswith("shawl back right")]
    c.check("the right shawl chain hangs from the right shoulder",
            len(right) == 2 and all(b.parent.head_local.x < 0 for b in right),
            [(b.name, b.parent.name) for b in right])
    c.check("duplicate names gone", not _findings(job, "mapping.duplicate_name"))
    c.check("no side leak left", not [f for f in _findings(job, "checkup.side_leak") if f.level != "info"],
            [f.text for f in _findings(job, "checkup.side_leak")])
    fixed = [f.code for f in job.findings if f.state == "fixed"]
    c.check("report says they are fixed", fixed.count("mapping.duplicate_name") == 2, fixed)
    c.check("pending cleared", not job.fixes_pending)
    c.check("checkup runs counted on", job.checkup_run == run + 1, (run, job.checkup_run))
    gone = [f for f in job.findings if f.state == "fixed" and f.code == "mapping.duplicate_name"]
    c.check("fixed findings keep their views", all(f.view_json for f in gone))
    c.check("before images captured for the ticked fixes", all(os.path.isfile(f.image_before) for f in gone),
            [f.image_before for f in gone])
    if gone:
        index = list(job.findings).index(gone[0])
        r = views.render_finding(bpy.context, job, index)
        c.check("看图 of a fixed finding renders the new model", r.ok and os.path.isfile(job.findings[index].image_after)
                and job.findings[index].image_before != job.findings[index].image_after)
    c.check("no pose warning left after the split", not [f for f in _findings(job) if f.code.startswith("pose.")
                                                         and f.level != "info"],
            [f.text for f in _findings(job) if f.code.startswith("pose.")])

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
    c.check("the knee / elbow poses are evidence", sum("姿势测试" in f.detail for f in warn) >= 2,
            [f.detail for f in warn])
    c.check("wrong merges get the knee / elbow view",
            any(json.loads(f.view_json or "{}").get("test", "").startswith(("knee", "elbow")) for f in warn))

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
