"""Fix list and its file format (design doc §15.3–§15.4): round trip, strict parsing, queries."""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xps_to_pmx.core import fixes as fx  # noqa: E402
from xps_to_pmx.core.weights.split import side_fraction, split_by_side  # noqa: E402


def _sample():
    return fx.FixFile(
        model="rouffe", source="E:/m/rouffe/xps.xps", source_sha1="ab" * 20,
        options={"scale_mode": "SHOULDER", "shoulder_target": 17.0, "level_shoulders": True},
        fixes=[
            fx.Fix("bone", bone="unused bip001 lcalftwist", src="unused bip001 lcalftwist", action="merge",
                   slot_id="left_knee_bone", origin="checkup", auto=True, note="95%"),
            fx.Fix("slot", slot_id="left_toe_bone", bone=""),
            fx.Fix("split_side", bone="shawl back right 1", src="shawl back right 1", twin="shawl back right 1.001",
                   origin="checkup"),
            fx.Fix("ignore", finding="checkup.side_leak:骨L1_2", enabled=False),
        ])


def test_round_trip():
    ff = _sample()
    back = fx.parse_fixes(fx.write_fixes(ff))
    assert back == ff
    data = json.loads(fx.write_fixes(ff))
    assert data["schema"] == fx.SCHEMA and data["version"] == fx.VERSION
    assert set(data["fixes"][1]) == set(fx.COMMON_KEYS + fx.KIND_KEYS["slot"])


@pytest.mark.parametrize("mutate, message", [
    (lambda d: d.update(extra=1), "未知的键 extra"),
    (lambda d: d.pop("options"), "缺少 options"),
    (lambda d: d.update(version=2), "version"),
    (lambda d: d.update(schema="other"), "schema"),
    (lambda d: d["options"].update(colour="red"), "未知的选项 colour"),
    (lambda d: d["options"].update(shoulder_target="17"), "必须是数字"),
    (lambda d: d["fixes"][0].update(color=1), "未知的键 color"),
    (lambda d: d["fixes"][0].pop("slot_id"), "缺少 slot_id"),
    (lambda d: d["fixes"][0].update(action="steal"), "未知的处置"),
    (lambda d: d["fixes"][0].update(kind="teleport"), "未知的 kind"),
    (lambda d: d["fixes"][1].update(enabled="yes"), "类型错误"),
    (lambda d: d["fixes"][2].update(twin=""), "twin"),
    (lambda d: d["fixes"][3].update(finding=""), "finding"),
])
def test_strict_parsing(mutate, message):
    data = json.loads(fx.write_fixes(_sample()))
    mutate(data)
    with pytest.raises(fx.FixFileError) as exc:
        fx.parse_fixes(json.dumps(data))
    assert any(message in p for p in exc.value.problems), exc.value.problems


def test_writer_refuses_invalid_fixes():
    with pytest.raises(fx.FixFileError):
        fx.write_fixes(fx.FixFile(fixes=[fx.Fix("bone", bone="x", action="merge")]))  # merge without a slot


def test_queries_only_see_enabled_fixes():
    fixes = _sample().fixes
    assert fx.fixed_slots(fixes) == {"left_toe_bone": ""}
    assert list(fx.bone_fixes(fixes)) == ["unused bip001 lcalftwist"]
    assert [f.bone for f in fx.split_fixes(fixes)] == ["shawl back right 1"]
    assert fx.ignored(fixes) == set()           # the ignore fix is disabled
    assert fx.user_decided(fixes) == {"slot:left_toe_bone", "ignore:checkup.side_leak:骨L1_2"}


def test_upsert_replaces_by_key():
    fixes = _sample().fixes
    n = len(fixes)
    fx.upsert(fixes, fx.Fix("bone", bone="unused bip001 lcalftwist", action="keep", origin="user"))
    assert len(fixes) == n and fixes[0].action == "keep" and fixes[0].origin == "user"
    fx.upsert(fixes, fx.Fix("slot", slot_id="head_bone", bone="head"))
    assert len(fixes) == n + 1


def test_describe_lines():
    fixes = _sample().fixes
    names = {"left_knee_bone": "左ひざ", "left_toe_bone": "左つま先"}.get
    assert fixes[0].describe(lambda s: names(s, s)) == "unused bip001 lcalftwist：并入 左ひざ"
    assert fixes[1].describe(lambda s: names(s, s)) == "左つま先 留空（生成）"


def test_split_by_side_conserves_weight_and_blends_at_the_seam():
    x = np.array([-0.2, -0.01, 0.0, 0.01, 0.2])
    w = np.array([1.0, 0.8, 0.6, 0.4, 0.2])
    keep, move = split_by_side(x, w, twin_side=-1.0, margin=0.02)   # twin on the right (x < 0)
    assert np.allclose(keep + move, w)
    assert move[0] == pytest.approx(1.0) and keep[-1] == pytest.approx(0.2)
    assert move[2] == pytest.approx(0.3)                              # half of 0.6 on the centre line
    assert side_fraction(np.array([0.5]), 1.0, 0.0)[0] == 1.0
