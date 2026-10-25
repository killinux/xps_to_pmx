"""Offline tests for xps_to_pmx.core.xps.convert (no Blender needed)."""
from __future__ import annotations

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xps_to_pmx.core.xps import XpsMesh, XpsModel, XpsVertex, load_xps  # noqa: E402
from xps_to_pmx.core.xps.convert import (  # noqa: E402
    MIN_BONE_LENGTH, build_import_data, compute_tails, convert_faces, convert_weights, model_display_name,
    normal_green_inverted, xna_to_blender)
from xps_to_pmx.core.xps.reader import parse_mesh_name  # noqa: E402

SAMPLES = [
    r"E:/day_work/2025money/wish/inase (arbiter)/xps.xps",
    r"E:/mywork/add_on/Purifier (Inase)/xps.xps",
]


def _vertex(pos=(0, 0, 0), bones=(0,), weights=(1.0,), uvs=((0.25, 0.75),)):
    return XpsVertex(position=pos, normal=(0, 1, 0), color_rgba=(255, 255, 255, 255), uvs=list(uvs),
                     tangents=None, bone_indices=list(bones), bone_weights=list(weights))


def _mesh(vertices, faces, name="1_body_0.5_0_0"):
    info = parse_mesh_name(name)
    return XpsMesh(name=name, uv_layer_count=1, textures=[], vertices=vertices, faces=faces,
                   render_group=info.render_group, mesh_base_name=info.base_name, specular=info.specular,
                   bump_repeat1=info.bump_repeat1, bump_repeat2=info.bump_repeat2,
                   optional_visible=info.optional_visible, optional_group=info.optional_group,
                   join_name=info.join_name)


def test_xna_to_blender_is_rotation_about_x():
    pts = np.array([[1.0, 2.0, 3.0]])
    assert xna_to_blender(pts).tolist() == [[1.0, -3.0, 2.0]]
    # a pure rotation keeps handedness: det = +1
    m = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)
    assert np.isclose(np.linalg.det(m), 1.0)


def test_faces_rewound_and_degenerates_dropped():
    verts = [_vertex() for _ in range(4)]
    mesh = _mesh(verts, [(0, 1, 2), (1, 1, 2), (0, 2, 9), (1, 2, 3)])
    faces, dropped = convert_faces(mesh)
    assert faces.tolist() == [[0, 2, 1], [1, 3, 2]]
    assert dropped == 2


def test_weights_cleaned_normalised_and_limited():
    verts = [
        _vertex(bones=(0, 1), weights=(0.5, 0.5)),                       # already fine
        _vertex(bones=(0, 1, 2), weights=(0.6, 0.6, 0.2)),               # sums to 1.4
        _vertex(bones=(0, 1, 2, 3, 4, 5), weights=(.3, .25, .2, .1, .1, .05)),  # 6 influences
        _vertex(bones=(0, 0), weights=(0.4, 0.6)),                       # duplicate bone
        _vertex(bones=(7, 1), weights=(0.5, 0.5)),                       # bone 7 does not exist
        _vertex(bones=(0,), weights=(0.0,)),                             # unweighted
    ]
    bones, values, stats = convert_weights(_mesh(verts, []), bone_count=6)
    assert np.allclose(values[:5].sum(axis=1), 1.0, atol=1e-6)
    assert values[5].sum() == 0 and bones[5].tolist() == [-1, -1, -1, -1]
    assert bones[2].tolist() == [0, 1, 2, 3]  # 4 largest kept, ordered by weight
    assert bones[3, 0] == 0 and np.isclose(values[3, 0], 1.0)  # duplicates merged
    assert bones[4, 0] == 1 and np.isclose(values[4, 0], 1.0)  # invalid reference dropped
    assert stats.truncated == 1 and stats.unweighted == 1 and stats.invalid_refs == 1
    # vertex 1 (sum 1.4), vertex 2 (0.85 after truncation), vertex 4 (0.5 after dropping bone 7)
    assert stats.renormalized == 3
    assert stats.max_influences == 6


def test_tails_prefer_centred_child_and_middle_finger():
    names = ["spine", "neck", "shoulder L", "hand L", "thumb", "index", "middle", "ring", "pinky", "eye"]
    parents = [-1, 0, 0, -1, 3, 3, 3, 3, 3, 1]
    heads = np.array([
        [0, 0, 1.3], [0, 0, 1.5], [0.15, 0, 1.45],
        [0.7, 0, 1.4], [0.72, -0.03, 1.39], [0.78, -0.01, 1.4], [0.79, 0, 1.4], [0.78, 0.01, 1.4],
        [0.76, 0.02, 1.4], [0, -0.05, 1.6]], dtype=float)
    tails = compute_tails(names, parents, heads)
    assert np.allclose(tails[0], heads[1])            # spine -> neck, not the shoulder
    assert np.allclose(tails[3], heads[6])            # hand -> middle finger
    lengths = np.linalg.norm(tails - heads, axis=1)
    assert np.all(lengths >= MIN_BONE_LENGTH - 1e-9)
    # leaf continues the parent direction
    leaf_dir = (tails[9] - heads[9]) / np.linalg.norm(tails[9] - heads[9])
    parent_dir = (heads[9] - heads[1]) / np.linalg.norm(heads[9] - heads[1])
    assert np.allclose(leaf_dir, parent_dir)


def test_tails_root_without_children_points_up():
    tails = compute_tails(["lonely"], [-1], np.array([[0.0, 0.0, 0.0]]))
    assert np.allclose(tails[0], [0.0, 0.0, 0.1])


def test_model_display_name_uses_folder_for_generic_stems():
    assert model_display_name(r"E:/models/inase (arbiter)/xps.xps") == "inase (arbiter)"
    assert model_display_name(r"E:/models/x/Generic_Item.mesh.ascii") == "x"
    assert model_display_name(r"E:/models/x/Valby Ultimate.xps") == "Valby Ultimate"


def test_normal_swizzle_green():
    assert normal_green_inverted("X+ Y- Z+")
    assert not normal_green_inverted("X+ Y+ Z+")


def test_split_parts_share_one_material_key():
    verts = [_vertex() for _ in range(3)]
    model = XpsModel(header=None, bones=[], source_path="", is_ascii=False, meshes=[
        _mesh(verts, [(0, 1, 2)], name="24_body1nPart!_0_16_16"),
        _mesh(verts, [(0, 1, 2)], name="24_body2nPart!_0_16_16"),
        _mesh(verts, [(0, 1, 2)], name="24_hair_0_16_16"),
    ])
    data = build_import_data(model)
    keys = [m.material_key for m in data.meshes]
    assert keys[0] == keys[1] != keys[2]


@pytest.mark.parametrize("path", [p for p in SAMPLES if os.path.isfile(p)] or
                         [pytest.param("missing", marks=pytest.mark.skip("no sample files"))])
def test_real_sample_conversion(path):
    model = load_xps(path)
    data = build_import_data(model)
    assert len(data.meshes) == len(model.meshes)
    assert len(data.bones) == len(model.bones)
    for xm, im in zip(model.meshes, data.meshes):
        assert im.vertex_count == len(xm.vertices)
        assert im.face_count + im.dropped_faces == len(xm.faces)
        if im.vertex_count:
            x, y, z = xm.vertices[0].position
            assert np.allclose(im.positions[0], [x, -z, y], atol=1e-6)
            if im.uvs:
                assert np.isclose(im.uvs[0][0, 1], 1.0 - xm.vertices[0].uvs[0][1], atol=1e-6)
            weighted = im.weight_bones[:, 0] >= 0
            assert np.allclose(im.weight_values[weighted].sum(axis=1), 1.0, atol=1e-5)
            assert im.weight_bones.max() < len(model.bones)
    heads = np.array([b.head for b in data.bones])
    tails = np.array([b.tail for b in data.bones])
    assert np.all(np.linalg.norm(tails - heads, axis=1) >= MIN_BONE_LENGTH - 1e-9)
    # the model stands on +Z and faces -Y after conversion
    zs = np.concatenate([m.positions[:, 2] for m in data.meshes if m.vertex_count])
    assert zs.max() - zs.min() > 1.0
