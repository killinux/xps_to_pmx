"""Tests for the pure-Python XPS reader.

Run with ``python -m pytest tests -q`` or, without pytest (e.g. Blender's
bundled Python), ``python tests/test_xps_reader.py``.  Tests using real
sample files are skipped when the files are not on this machine.
"""
from __future__ import annotations

import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from xps_to_pmx.core.xps import (  # noqa: E402
    MAGIC,
    RENDER_GROUPS,
    XpsFormatError,
    XpsHeader,
    describe_render_group,
    has_tangent_layout,
    has_variable_weight_layout,
    load_pose,
    load_xps,
    parse_mesh_name,
    parse_pose_text,
    parse_xps_ascii,
    parse_xps_bytes,
    parse_xps_data,
    validate_model,
)

# --------------------------------------------------------------------------- real samples

#: (path, expected version string, or None for headerless binary, or "ascii")
REAL_SAMPLES = [
    ("E:/day_work/2025money/wish/inase (arbiter)/xps.xps", "3.15"),
    ("E:/day_work/work/riseoferos/alana (archdemon baal)/xps.xps", "3.15"),
    ("E:/day_work/work/gantz/already/DOA-Shimohira Reika/Generic_Item.mesh", None),
    ("E:/day_work/work/model/ffvii_tifa_as_sweater_tights__dl__xps_by_sihsengiu_dj8wr7v/T-Pose.mesh", "2.15"),
    ("E:/day_work/work2/DOAXVV Yukino - Shimmering Elf Dress/Generic_Item.mesh.ascii", "ascii"),
    ("E:/day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/Generic_Item.mesh", None),
]
#: Real files known to contain vertices whose weights sum above 1 (XPS does not enforce normalisation).
UNNORMALISED_SAMPLES = [
    "E:/day_work/2025money/wish/Cooing Suit(EVE)/#Stellar Blade - Eve (Cooling)/xps.xps",
    "E:/4090/blender_file/Valby Ultimate Premium/Premium/Valby Ultimate.xps",
]
POSE_SAMPLE = ("E:/day_work/work/gantz/already/DOA-Shimohira Reika/default.pose",
               "E:/day_work/work/gantz/already/DOA-Shimohira Reika/Generic_Item.mesh")


def _check_invariants(model) -> None:
    assert model.complete, model.warnings
    if model.header is not None:
        assert model.header.magic == MAGIC == 323232
        assert model.header.xna_string == "XNAaraL"
    bone_count = len(model.bones)
    assert bone_count > 0
    for i, bone in enumerate(model.bones):
        assert -1 <= bone.parent_index < bone_count and bone.parent_index != i
    assert model.meshes
    for mesh in model.meshes:
        vertex_count = len(mesh.vertices)
        assert vertex_count > 0, mesh.name
        for face in mesh.faces:
            assert 0 <= face[0] < vertex_count and 0 <= face[1] < vertex_count and 0 <= face[2] < vertex_count
        for v in mesh.vertices:
            assert len(v.uvs) == mesh.uv_layer_count
            assert len(v.bone_indices) == len(v.bone_weights) >= 4
            assert sum(v.bone_weights) <= 1.0 + 1e-2, (mesh.name, v.bone_weights)
            for index, weight in zip(v.bone_indices, v.bone_weights):
                if weight > 0.0:
                    assert 0 <= index < bone_count
    assert validate_model(model) == []


def test_real_samples_invariants():
    found = 0
    for path, expected in REAL_SAMPLES:
        if not Path(path).is_file():
            continue
        found += 1
        model = load_xps(path)
        _check_invariants(model)
        if expected == "ascii":
            assert model.is_ascii and model.header is None and not model.has_tangents
        elif expected is None:
            assert not model.is_ascii and model.header is None
            assert model.has_tangents and not model.has_variable_weights
            assert all(v.tangents is not None and len(v.tangents) == len(v.uvs) for v in model.meshes[0].vertices)
        else:
            assert model.version == expected
            major = int(expected.split(".")[0])
            assert model.has_variable_weights == (major >= 3)
            assert not model.has_tangents
            assert model.header.settings_parsed
    if found < 3:
        raise unittest.SkipTest(f"only {found} of {len(REAL_SAMPLES)} real samples present")


def test_real_samples_with_unnormalised_weights_are_reported():
    present = [p for p in UNNORMALISED_SAMPLES if Path(p).is_file()]
    if not present:
        raise unittest.SkipTest("samples with unnormalised weights not present")
    for path in present:
        model = load_xps(path)
        assert model.complete and model.meshes
        issues = validate_model(model)
        assert issues and all("weight sum" in issue for issue in issues), issues


def test_real_pose_file_matches_model_bones():
    pose_path, model_path = POSE_SAMPLE
    if not (Path(pose_path).is_file() and Path(model_path).is_file()):
        raise unittest.SkipTest("pose sample not present")
    pose = load_pose(pose_path)
    bones = {b.name for b in load_xps(model_path).bones}
    assert len(pose) > 100
    matched = sum(1 for name in pose if name in bones)
    assert matched >= 0.9 * len(pose)
    entry = next(iter(pose.values()))
    assert len(entry.rotation_deg) == len(entry.translation) == len(entry.scale) == 3


# --------------------------------------------------------------------------- synthetic writer


def _net_string(text: str) -> bytes:
    raw = text.encode("utf-8")
    length = len(raw)
    prefix = bytearray()
    while True:
        byte = length & 0x7F
        length >>= 7
        if length:
            prefix.append(byte | 0x80)
        else:
            prefix.append(byte)
            break
    return bytes(prefix) + raw


def _header(major: int, minor: int, pose_text: str = "",
            flags=((2, 1), (3, 0), (4, 3), (5, 4))) -> bytes:
    """Header in the layout XPS 11 / XNALaraMesh write: hash, 3 items (pose, flags, padding)."""
    pose = pose_text.encode("utf-8")
    body = struct.pack("<II", 180, 3)
    body += struct.pack("<3I", 1, len(pose), sum(1 for line in pose_text.splitlines() if line.strip()))
    body += pose + b"\0" * ((-len(pose)) % 4)
    body += struct.pack("<3I", 2, len(flags), len(flags))
    for flag_id, value in flags:
        body += struct.pack("<2I", flag_id, value)
    used_words = len(body) // 4 + 3
    pad_words = max(0, 275 - used_words)
    body += struct.pack("<3I", 0, pad_words, 0) + b"\0" * (pad_words * 4)
    return (struct.pack("<IHH", MAGIC, major, minor) + _net_string("XNAaraL")
            + struct.pack("<I", len(body) // 4) + _net_string("enihcam") + _net_string("resu")
            + _net_string("resu@C:\\models\\test.blend") + body)


LONG_NAME = ("very long bone name " * 8).strip()  # 159 bytes -> two-byte length prefix

BONES = [
    ("root ground", -1, (0.0, 0.0, 0.0)),
    ("root hips", 0, (0.0, 1.0, 0.01)),
    ("骨头 bone", 1, (0.1, 1.5, -0.02)),
    (LONG_NAME, 2, (0.2, 1.6, 0.0)),
]


def _mesh_a(weights_per_vertex=(4, 4, 4)):
    vertices = []
    for i, count in enumerate(weights_per_vertex):
        indices = [(i + k) % len(BONES) for k in range(count)]
        weights = [1.0 / count] * count
        vertices.append({
            "pos": (0.1 * i, 0.5 + 0.25 * i, -0.05 * i), "normal": (0.0, 0.0, 1.0),
            "color": (255, 128, 64, 255), "uvs": [(0.1 * i, 0.9), (0.5, 0.25 * i)],
            "bones": indices, "weights": weights})
    return {"name": "24_body_0.5_16_16", "uv_layers": 2,
            "textures": [("C:\\textures\\body_d.png", 0), ("maps/body_n.dds", 1)],
            "vertices": vertices, "faces": [(0, 1, 2)]}


def _mesh_b():
    vertices = []
    for i in range(4):
        vertices.append({
            "pos": (0.3 * (i % 2), 1.2 + 0.3 * (i // 2), 0.05), "normal": (0.0, 1.0, 0.0),
            "color": (10, 20, 30, 40), "uvs": [((i % 2) * 1.0, (i // 2) * 1.0)],
            "bones": [1, 0, 0, 0], "weights": [1.0, 0.0, 0.0, 0.0]})
    return {"name": "-FAU|neutral", "uv_layers": 1, "textures": [("face.png", 0)],
            "vertices": vertices, "faces": [(0, 1, 2), (2, 1, 3)]}


def _write_binary(bones, meshes, header: bytes = b"", *, tangents: bool, variable: bool) -> bytes:
    out = bytearray(header)
    out += struct.pack("<I", len(bones))
    for name, parent, pos in bones:
        out += _net_string(name) + struct.pack("<h3f", parent, *pos)
    out += struct.pack("<I", len(meshes))
    for mesh in meshes:
        out += _net_string(mesh["name"]) + struct.pack("<II", mesh["uv_layers"], len(mesh["textures"]))
        for file_name, uv_layer in mesh["textures"]:
            out += _net_string(file_name) + struct.pack("<I", uv_layer)
        out += struct.pack("<I", len(mesh["vertices"]))
        for v in mesh["vertices"]:
            out += struct.pack("<3f3f4B", *v["pos"], *v["normal"], *v["color"])
            for k, uv in enumerate(v["uvs"]):
                out += struct.pack("<2f", *uv)
                if tangents:
                    out += struct.pack("<4f", 1.0, 0.0, 0.0, float(k))
            if bones:
                indices, weights = v["bones"], v["weights"]
                if variable:
                    out += struct.pack("<H", len(indices))
                else:
                    assert len(indices) == 4
                out += struct.pack(f"<{len(indices)}h", *indices) + struct.pack(f"<{len(weights)}f", *weights)
        out += struct.pack("<I", len(mesh["faces"]))
        for face in mesh["faces"]:
            out += struct.pack("<3I", *face)
    return bytes(out)


def _write_ascii(bones, meshes) -> str:
    lines = [f"{len(bones)} # bones"]
    for name, parent, pos in bones:
        lines += [name, f"{parent} # parent index", " ".join(repr(c) for c in pos)]
    lines.append(f"{len(meshes)} # meshes")
    for mesh in meshes:
        lines += [mesh["name"], f"{mesh['uv_layers']} # uv layers", f"{len(mesh['textures'])} # textures"]
        for file_name, uv_layer in mesh["textures"]:
            lines += [file_name, f"{uv_layer} # uv layer index"]
        lines.append(f"{len(mesh['vertices'])} # vertices")
        for v in mesh["vertices"]:
            lines.append(" ".join(repr(c) for c in v["pos"]))
            lines.append(" ".join(repr(c) for c in v["normal"]))
            lines.append(" ".join(str(c) for c in v["color"]))
            for uv in v["uvs"]:
                lines.append(" ".join(repr(c) for c in uv))
            if bones:
                lines.append(" ".join(str(i) for i in v["bones"]))
                lines.append(" ".join(repr(w) for w in v["weights"]))
        lines.append(f"{len(mesh['faces'])} # faces")
        for face in mesh["faces"]:
            lines.append(" ".join(str(i) for i in face))
    return "\r\n".join(lines) + "\r\n"


def _assert_matches_source(model, meshes, *, expect_tangents: bool) -> None:
    assert [b.name for b in model.bones] == [b[0] for b in BONES]
    assert [b.parent_index for b in model.bones] == [b[1] for b in BONES]
    for bone, source in zip(model.bones, BONES):
        assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(bone.position, source[2]))
    assert len(model.meshes) == len(meshes)
    for mesh, source in zip(model.meshes, meshes):
        assert mesh.name == source["name"]
        assert mesh.uv_layer_count == source["uv_layers"]
        assert [(t.file, t.uv_layer) for t in mesh.textures] == [
            (f.replace("\\", "/").split("/")[-1], uv) for f, uv in source["textures"]]
        assert mesh.faces == [tuple(f) for f in source["faces"]]
        assert len(mesh.vertices) == len(source["vertices"])
        for v, sv in zip(mesh.vertices, source["vertices"]):
            assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(v.position, sv["pos"]))
            assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(v.normal, sv["normal"]))
            assert tuple(v.color_rgba) == tuple(sv["color"])
            assert len(v.uvs) == len(sv["uvs"])
            for uv, suv in zip(v.uvs, sv["uvs"]):
                assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(uv, suv))
            if expect_tangents:
                assert v.tangents is not None and len(v.tangents) == len(v.uvs)
                assert v.tangents[-1][3] == float(len(v.uvs) - 1)
            else:
                assert v.tangents is None
            stored = len(sv["bones"])
            assert v.bone_indices[:stored] == list(sv["bones"])
            assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(v.bone_weights, sv["weights"]))
    assert validate_model(model) == []


def test_roundtrip_headerless_mesh_with_tangents():
    meshes = [_mesh_a(), _mesh_b()]
    data = _write_binary(BONES, meshes, tangents=True, variable=False)
    model = parse_xps_bytes(data, "synthetic.mesh", strict=True)
    assert model.header is None and model.has_tangents and not model.has_variable_weights
    assert model.warnings == [] and model.trailing_bytes == 0
    _assert_matches_source(model, meshes, expect_tangents=True)


def test_roundtrip_version_2_12_keeps_tangents_and_skips_settings():
    meshes = [_mesh_a(), _mesh_b()]
    data = _write_binary(BONES, meshes, _header(2, 12), tangents=True, variable=False)
    model = parse_xps_bytes(data, strict=True)
    assert model.version == "2.12" and model.has_tangents
    assert not model.header.settings_parsed and model.header.flags == {}
    assert len(model.header.settings_raw) == model.header.settings_len * 4
    _assert_matches_source(model, meshes, expect_tangents=True)


def test_roundtrip_version_2_15_fixed_weights_no_tangents():
    meshes = [_mesh_a(), _mesh_b()]
    data = _write_binary(BONES, meshes, _header(2, 15), tangents=False, variable=False)
    model = parse_xps_bytes(data, strict=True)
    assert model.version == "2.15" and not model.has_tangents and not model.has_variable_weights
    _assert_matches_source(model, meshes, expect_tangents=False)


def test_roundtrip_version_3_15_variable_weights_pose_and_flags():
    meshes = [_mesh_a(weights_per_vertex=(1, 4, 6)), _mesh_b()]
    pose_text = "root ground: 0 0 0 0 0 0 1 1 1\nroot hips: 10.5 -20 30 0.1 0.2 0.3 1 1 1\n"
    data = _write_binary(BONES, meshes, _header(3, 15, pose_text, flags=((2, 1), (3, 0), (4, 2), (5, 4), (7, 1))),
                         tangents=False, variable=True)
    model = parse_xps_bytes(data, strict=True)
    header = model.header
    assert model.version == "3.15" and model.has_variable_weights and not model.has_tangents
    assert header.settings_parsed and header.settings_hash == 180 and header.settings_item_count == 3
    assert [item[0] for item in header.settings_items] == [1, 2, 0]
    assert header.default_pose_text == pose_text
    assert header.default_pose["root hips"].rotation_deg == (10.5, -20.0, 30.0)
    assert header.default_pose["root hips"].translation == (0.1, 0.2, 0.3)
    assert header.flags_raw == {2: 1, 3: 0, 4: 2, 5: 4, 7: 1}
    assert header.flags["modelCastShadows"] is True and header.flags["hasBoneDirections"] is True
    assert header.flags["tangentSpaceGreen"] == 0 and header.normal_map_swizzle == "X+ Y+ Z+"
    assert header.flag("backFaceCulling") is False  # absent -> XPS default
    assert [len(v.bone_indices) for v in model.meshes[0].vertices] == [1, 4, 6]
    assert model.warnings == []
    _assert_matches_source(model, meshes, expect_tangents=False)


def test_model_without_bones_has_no_weights():
    meshes = [_mesh_b()]
    data = _write_binary([], meshes, _header(2, 15), tangents=False, variable=False)
    model = parse_xps_bytes(data, strict=True)
    assert model.bones == []
    assert all(v.bone_indices == [] and v.bone_weights == [] for v in model.meshes[0].vertices)


def test_trailing_data_is_reported_not_fatal():
    meshes = [_mesh_a(), _mesh_b()]
    footer = b"\x01B\x01 " + b"\x7f\x00\x00\x00" * 4 + b"\x02MM"
    data = _write_binary(BONES, meshes, _header(3, 15), tangents=False, variable=True) + footer
    model = parse_xps_bytes(data, strict=True)
    assert model.complete and model.trailing_bytes == len(footer)
    assert any("after the last mesh" in w for w in model.warnings)
    assert len(model.meshes) == 2


def test_truncated_file_strict_and_tolerant():
    meshes = [_mesh_a(), _mesh_b()]
    data = _write_binary(BONES, meshes, _header(2, 15), tangents=False, variable=False)
    cut = data[:-20]
    try:
        parse_xps_bytes(cut, strict=True)
    except XpsFormatError:
        pass
    else:
        raise AssertionError("strict parse of a truncated file must raise")
    model = parse_xps_bytes(cut, strict=False)
    assert not model.complete and model.declared_mesh_count == 2
    assert len(model.meshes) == 1 and model.meshes[0].name == "24_body_0.5_16_16"
    assert any("truncated" in w for w in model.warnings)


def test_layout_fallback_when_version_lies():
    meshes = [_mesh_a(), _mesh_b()]
    # Header claims 2.12 (tangents) but the vertices were written without tangents.
    data = _write_binary(BONES, meshes, _header(2, 12), tangents=False, variable=False)
    model = parse_xps_bytes(data, strict=True)
    assert not model.has_tangents and model.complete
    assert any("vertex layout implied" in w for w in model.warnings)
    _assert_matches_source(model, meshes, expect_tangents=False)


def test_ascii_roundtrip_and_dispatch():
    meshes = [_mesh_a(weights_per_vertex=(4, 4, 6)), _mesh_b()]
    text = _write_ascii(BONES, meshes)
    model = parse_xps_ascii(text, strict=True)
    assert model.is_ascii and model.header is None and model.has_variable_weights
    _assert_matches_source(model, meshes, expect_tangents=False)
    with tempfile.TemporaryDirectory() as tmp:
        ascii_path = Path(tmp) / "Generic_Item.mesh.ascii"
        ascii_path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
        from_file = load_xps(ascii_path)
        assert from_file.is_ascii and [m.name for m in from_file.meshes] == [m["name"] for m in meshes]
        mislabeled = Path(tmp) / "text_inside.mesh"
        mislabeled.write_text(text, encoding="utf-8")
        model2 = load_xps(mislabeled)
        assert model2.is_ascii and any("text content" in w for w in model2.warnings)
        binary_path = Path(tmp) / "xps.xps"
        binary_path.write_bytes(_write_binary(BONES, meshes[1:], _header(2, 15), tangents=False, variable=False))
        assert not load_xps(binary_path).is_ascii
    data_model = parse_xps_data(text.encode("utf-8"), "x.ascii")
    assert data_model.is_ascii


def test_layout_rules():
    def header(major, minor):
        return XpsHeader(MAGIC, major, minor, "XNAaraL", 0, "", "", "", b"")
    assert has_tangent_layout(None) and not has_variable_weight_layout(None)
    assert has_tangent_layout(header(2, 12)) and has_tangent_layout(header(1, 0))
    assert not has_tangent_layout(header(2, 15)) and not has_tangent_layout(header(3, 15))
    assert not has_variable_weight_layout(header(2, 15)) and has_variable_weight_layout(header(3, 0))


# --------------------------------------------------------------------------- mesh names


def test_mesh_name_render_group_and_parameters():
    info = parse_mesh_name("3_body_0.1")
    assert (info.render_group, info.base_name, info.specular, info.bump_repeat1, info.bump_repeat2) == \
        (3, "body", 0.1, 0.0, 0.0)
    assert info.optional_visible is None and not info.is_optional

    info = parse_mesh_name("body")
    assert info.render_group is None and info.effective_render_group == 5
    assert info.base_name == "body" and info.specular == 1.0 and info.bump_repeat1 == 0.0

    info = parse_mesh_name("1_PC_10.0_0_0_BODY")
    assert (info.render_group, info.base_name, info.specular, info.extra_params) == (1, "PC", 10.0, ["BODY"])

    info = parse_mesh_name("1_Body_Upper_0.1_0_0")  # name part containing "_"
    assert info.base_name == "Body_Upper" and info.specular == 0.1


def test_mesh_name_optional_items():
    info = parse_mesh_name("6_+hair_0.5_0_0")
    assert info.render_group == 6 and info.optional_visible is True
    assert (info.base_name, info.optional_item, info.optional_group) == ("hair", "hair", None)
    assert (info.specular, info.bump_repeat1, info.bump_repeat2) == (0.5, 0.0, 0.0)

    info = parse_mesh_name("-FAU|neutral")
    assert info.render_group is None and info.optional_visible is False
    assert (info.optional_group, info.optional_item, info.optional_part) == ("FAU", "neutral", None)
    assert info.base_name == "FAU|neutral"

    info = parse_mesh_name("-glasses.frame")
    assert info.optional_visible is False
    assert (info.optional_item, info.optional_part) == ("glasses", "frame")

    info = parse_mesh_name("23_+shoes|Ashley strap.black_1.0_10.0_1.0")  # from a real model
    assert info.render_group == 23 and info.optional_visible is True
    assert (info.optional_group, info.optional_item, info.optional_part) == ("shoes", "Ashley strap", "black")
    assert (info.specular, info.bump_repeat1, info.bump_repeat2) == (1.0, 10.0, 1.0)

    info = parse_mesh_name("+40_hat_0.5_0_0")  # sign written in front of the render group
    assert info.render_group == 40 and info.optional_visible is True and info.base_name == "hat"

    info = parse_mesh_name("5_body.material01_0.5_0_0")  # "." is only special for optional items
    assert info.optional_visible is None and info.base_name == "body.material01" and info.optional_part is None


def test_mesh_name_npart_markers():
    info = parse_mesh_name("24_body1nPart!_0_16_16")  # real split part
    assert info.join_name == "24_body_0_16_16" and info.part_index == 1 and info.is_split_part
    assert (info.render_group, info.base_name, info.specular, info.bump_repeat1, info.bump_repeat2) == \
        (24, "body", 0.0, 16.0, 16.0)

    assert parse_mesh_name("24_body1nPart!!wrong!_0_16_16").join_name == "24_body_0_16_16"

    info = parse_mesh_name("2nPart!3_hair_0.5_0_0")  # marker in front of the render group
    assert info.join_name == "3_hair_0.5_0_0" and info.part_index == 2 and info.render_group == 3

    info = parse_mesh_name("24_body1nPart!_0_")  # empty trailing parameter keeps the default
    assert info.join_name == "24_body_0_" and info.specular == 0.0 and info.bump_repeat1 == 0.0

    # Without digits "nPart!" is not a split marker; the importer's regex only drops the "!".
    info = parse_mesh_name("nPart!2_hair_0.5")
    assert info.join_name == "nPart2_hair_0.5" and info.part_index is None and info.render_group is None

    plain = parse_mesh_name("24_body_0_16_16")
    assert not plain.is_split_part and plain.part_index is None


def test_render_group_table():
    assert sorted(RENDER_GROUPS) == list(range(1, 44))
    assert describe_render_group(None).number == 5
    assert describe_render_group(7).alpha and not describe_render_group(24).alpha
    assert describe_render_group(25).texture_slots == ("diffuse", "lightmap", "bump", "specular")
    assert describe_render_group(10).shadeless
    unknown = describe_render_group(99)
    assert not unknown.known and unknown.slot_kind(0) == "diffuse"


def test_pose_text_parsing():
    pose = parse_pose_text("root ground: 0 0 0 0 0 0 1 1 1\r\nmixamorig:Hips: 10 20 30 0.1 0.2 0.3\r\n\r\n")
    assert set(pose) == {"root ground", "mixamorig:Hips"}
    hips = pose["mixamorig:Hips"]
    assert hips.rotation_deg == (10.0, 20.0, 30.0) and hips.translation == (0.1, 0.2, 0.3)
    assert hips.scale == (1.0, 1.0, 1.0)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "a.pose"
        path.write_bytes("\ufeffhead: 1 2 3 4 5 6 7 8 9\n".encode("utf-8"))
        assert load_pose(path)["head"].scale == (7.0, 8.0, 9.0)


# --------------------------------------------------------------------------- plain-script runner


def _run_without_pytest() -> int:
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failed = skipped = 0
    for name, fn in tests:
        try:
            fn()
        except unittest.SkipTest as skip:
            skipped += 1
            print(f"SKIP {name}: {skip}")
        except Exception as err:  # noqa: BLE001 - report every failure
            failed += 1
            import traceback
            print(f"FAIL {name}: {err!r}")
            traceback.print_exc()
        else:
            print(f"ok   {name}")
    print(f"{len(tests) - failed - skipped} passed, {failed} failed, {skipped} skipped "
          f"(Python {sys.version.split()[0]})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_without_pytest())
