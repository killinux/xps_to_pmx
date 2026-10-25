"""Specification tables (CSV) loaded and validated in one place (hard constraints 2 and 5)."""
from .bone_slots import (DEFAULT_PATH, Alias, BoneSpec, IkLink, SlotSpec, SpecError, load_bone_spec,
                         merge_specs, mmd_name_problems, norm_name, parse_bone_spec)

__all__ = ["DEFAULT_PATH", "Alias", "BoneSpec", "IkLink", "SlotSpec", "SpecError", "load_bone_spec",
           "merge_specs", "mmd_name_problems", "norm_name", "parse_bone_spec"]
