"""XPS / XNALara file support: data types, render-group table and a pure-Python reader."""
from .types import (
    DEFAULT_FLAGS,
    FLAG_NAMES,
    MAGIC,
    XNA_ARAL,
    MeshNameInfo,
    XpsBone,
    XpsHeader,
    XpsMesh,
    XpsModel,
    XpsPoseEntry,
    XpsTexture,
    XpsVertex,
)
from .render_groups import (
    DEFAULT_RENDER_GROUP,
    RENDER_GROUPS,
    RenderGroupInfo,
    describe_render_group,
    is_alpha_render_group,
)
from .reader import (
    XpsFormatError,
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

__all__ = [
    "DEFAULT_FLAGS", "FLAG_NAMES", "MAGIC", "XNA_ARAL",
    "MeshNameInfo", "XpsBone", "XpsHeader", "XpsMesh", "XpsModel", "XpsPoseEntry", "XpsTexture", "XpsVertex",
    "DEFAULT_RENDER_GROUP", "RENDER_GROUPS", "RenderGroupInfo", "describe_render_group", "is_alpha_render_group",
    "XpsFormatError", "has_tangent_layout", "has_variable_weight_layout", "load_pose", "load_xps",
    "parse_mesh_name", "parse_pose_text", "parse_xps_ascii", "parse_xps_bytes", "parse_xps_data",
    "validate_model",
]
