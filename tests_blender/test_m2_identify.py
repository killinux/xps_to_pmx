"""M2 acceptance: stage ② in Blender on the regression set.

Import → identify (operator) → required slots, 下半身 case, no error checks;
manual slot edit → marked user, survives re-identify, cleared by reset;
mapping CSV export → re-import restores a cleared slot; owner's 2-column list.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

import bpy  # noqa: E402

harness.register_addon()
from xps_to_pmx import props  # noqa: E402
from xps_to_pmx.pipeline import stage_identify, stage_import  # noqa: E402

EXPECT = {
    "xnalara_inase_arbiter": dict(case="B", slots={"lower_body_bone": "unused trash 17",
                                                   "upper_body2_bone": "spine middle"}),
    "daz_purifier_inase": dict(case="A", slots={"lower_body_bone": "pelvis", "upper_body2_bone": "chestLower",
                                                "left_toe_bone": "lToe"}),
    "biped_stellarblade_eve": dict(case="B", slots={"lower_body_bone": "pelvis alt"}),
    "unreal_gantz_reika": dict(case="A", slots={"lower_body_bone": "pelvis", "upper_body2_bone": "spine_03"}),
}
OWNER_LIST = "E:/mywork/xps2mmd/Purifier_bones.txt"


def check_model(entry, out_dir):
    c = harness.Checker(entry["id"])
    path = entry["path"]
    if not os.path.isfile(path):
        c.check("sample file exists", False, path)
        return c
    harness.reset_scene()
    res, job = stage_import.run(bpy.context, path)
    if not c.check("import ok", res.ok):
        return c
    arm = job.armature
    bpy.context.view_layer.objects.active = arm

    result = bpy.ops.xps2pmx.identify()
    c.check("identify operator finished", result == {'FINISHED'}, result)
    summary = job.summary().get("identify", {})
    c.check("all required slots filled",
            summary.get("required_filled") == summary.get("required_total"), summary)
    want = EXPECT.get(entry["id"], {})
    if want:
        c.check("下半身 case", summary.get("lower_body_case") == want["case"], summary.get("lower_body_case"))
        got = {s: job.slot(s).bone for s in want["slots"]}
        c.check("expected slot bones", got == want["slots"], got)
    errors = [ch.text for ch in job.checks if ch.level == 'error']
    c.check("no error-level checks", not errors, errors[:3])
    c.check("one plan per bone", len(job.bones) == len(arm.data.bones), (len(job.bones), len(arm.data.bones)))
    c.check("slots carry display info", all(s.name_j for s in job.slots))

    # manual edit: wrong bone for the left hand
    hand = job.slot("left_hand_bone")
    original = hand.bone
    finger = job.slot("left_index_1").bone
    hand.bone = finger
    st = props.state(bpy.context)
    c.check("edit marks slot as user", hand.origin == 'user' and st.mapping_dirty)
    bpy.ops.xps2pmx.check_mapping()
    codes = {ch.code for ch in job.checks}
    c.check("recheck flags the wrong hand", "mapping.duplicate" in codes or "mapping.hierarchy" in codes, codes)
    c.check("recheck clears dirty flag", not st.mapping_dirty)
    stage_identify.run(bpy.context, job, keep_user=True)
    c.check("re-identify keeps the user slot", job.slot("left_hand_bone").bone == finger)
    stage_identify.run(bpy.context, job, keep_user=False)
    c.check("reset restores the automatic slot", job.slot("left_hand_bone").bone == original)

    # CSV round trip
    csv_path = os.path.join(out_dir, f"{entry['id']}.mapping.csv")
    res = stage_identify.export_csv(bpy.context, job, csv_path)
    c.check("mapping exported", res.ok and os.path.isfile(csv_path))
    job.slot("left_hand_bone").bone = ""
    res = stage_identify.import_csv(bpy.context, job, csv_path)
    c.check("mapping re-imported", res.ok and job.slot("left_hand_bone").bone == original,
            job.slot("left_hand_bone").bone)
    errors = [ch.text for ch in job.checks if ch.level == 'error']
    c.check("no errors after re-import", not errors, errors[:3])

    if entry["id"] == "daz_purifier_inase" and os.path.isfile(OWNER_LIST):
        res = stage_identify.import_csv(bpy.context, job, OWNER_LIST)
        c.check("owner two-column list imports", res.ok, [m.text for m in res.messages if m.level == 'error'])
        c.check("owner list maps the thigh", job.slot("left_thigh_bone").bone == "lThighBend")
    return c


def main():
    args = harness.parse_args()
    out_dir = os.path.join(args.out, "m2")
    os.makedirs(out_dir, exist_ok=True)
    checkers = [check_model(m, out_dir) for m in harness.regression_models(args.models)]
    report = harness.write_report(args.out, "m2_identify", checkers)
    harness.finish(report)


main()
