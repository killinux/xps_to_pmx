"""XNALara / XPS render groups 1-43.

Transcribed from section 3 of
``docs/research_notes/XPS 转 PMX 方案调研/01_xps格式与导入.md`` (which in turn
documents the behaviour of XNALara and the XNALaraMesh importer).  A render
group is the number that prefixes a mesh name (``22_body_0.1_4_4``) and
decides the texture slot order, alpha blending, shading mode and which of the
numeric name parameters are used.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# Texture slot kinds, in the order XNALara numbers them (1..9).
DIFFUSE = "diffuse"
LIGHTMAP = "lightmap"
BUMP = "bump"
MASK = "mask"
BUMP1 = "bump1"
BUMP2 = "bump2"
SPECULAR = "specular"
ENVIRONMENT = "environment"
EMISSION = "emission"

# Shading modes.
SHADING_LIT = "lit"              # normal lighting
SHADING_SHADELESS = "shadeless"  # unlit / fullbright
SHADING_VERTEX = "vertex"        # vertex lighting
SHADING_SWITCHABLE = "lit/unlit"  # lighting can be toggled in XPS ("Yes/No")

# Specular behaviour.
SPECULAR_YES = "yes"
SPECULAR_NO = "no"
SPECULAR_INTENSITY = "intensity"  # specular strength driven by the name parameter

#: Render group XPS assumes when the mesh name has no numeric prefix.
DEFAULT_RENDER_GROUP = 5

#: Slot order the XNALaraMesh importer falls back to for unknown numbers.
UNKNOWN_SLOTS: Tuple[str, ...] = (DIFFUSE, MASK, MASK, MASK, MASK, MASK)


@dataclass(frozen=True)
class RenderGroupInfo:
    """Static description of one render group."""

    number: Optional[int]
    alpha: bool
    texture_slots: Tuple[str, ...]
    shading: str = SHADING_LIT
    posable: bool = True
    specular: str = SPECULAR_YES
    bump1_repeat: bool = False   # name parameter 2 is used as micro-bump 1 tiling
    bump2_repeat: bool = False   # name parameter 3 is used as micro-bump 2 tiling
    spec1_repeat: bool = False   # specular map is tiled (42/43)
    known: bool = True
    note: str = ""

    @property
    def texture_count(self) -> int:
        return len(self.texture_slots)

    @property
    def shadeless(self) -> bool:
        return self.shading == SHADING_SHADELESS

    def slot_kind(self, texture_index: int) -> Optional[str]:
        """Kind of the texture at ``texture_index`` in the mesh's texture list, or ``None`` if surplus."""
        if 0 <= texture_index < len(self.texture_slots):
            return self.texture_slots[texture_index]
        return None

    def slot_index(self, kind: str) -> Optional[int]:
        """Position of the first slot of ``kind`` (e.g. ``DIFFUSE``), or ``None``."""
        try:
            return self.texture_slots.index(kind)
        except ValueError:
            return None


def _rg(number: int, alpha: bool, slots: Tuple[str, ...], shading: str = SHADING_LIT,
        posable: bool = True, specular: str = SPECULAR_YES, bump1: bool = False,
        bump2: bool = False, spec1: bool = False, note: str = "") -> RenderGroupInfo:
    return RenderGroupInfo(number, alpha, slots, shading, posable, specular, bump1, bump2, spec1, True, note)


_SIX = (DIFFUSE, LIGHTMAP, BUMP, MASK, BUMP1, BUMP2)
_SEVEN = _SIX + (SPECULAR,)

RENDER_GROUPS: Dict[int, RenderGroupInfo] = {
    1: _rg(1, False, _SIX, bump1=True, bump2=True, note="6 textures"),
    2: _rg(2, False, (DIFFUSE, LIGHTMAP, BUMP)),
    3: _rg(3, False, (DIFFUSE, LIGHTMAP), specular=SPECULAR_NO),
    4: _rg(4, False, (DIFFUSE, BUMP)),
    5: _rg(5, False, (DIFFUSE,), specular=SPECULAR_NO, note="default when the name has no numeric prefix"),
    6: _rg(6, True, (DIFFUSE, BUMP)),
    7: _rg(7, True, (DIFFUSE,), specular=SPECULAR_NO),
    8: _rg(8, True, (DIFFUSE, LIGHTMAP, BUMP)),
    9: _rg(9, True, (DIFFUSE, LIGHTMAP), specular=SPECULAR_NO),
    10: _rg(10, False, (DIFFUSE,), SHADING_SHADELESS, specular=SPECULAR_NO),
    11: _rg(11, False, (DIFFUSE, BUMP), SHADING_VERTEX, posable=False),
    12: _rg(12, True, (DIFFUSE, BUMP), SHADING_VERTEX, posable=False),
    13: _rg(13, False, (DIFFUSE,), SHADING_SHADELESS, posable=False, specular=SPECULAR_NO),
    14: _rg(14, False, (DIFFUSE, BUMP), SHADING_SHADELESS, posable=False),
    15: _rg(15, True, (DIFFUSE, BUMP), SHADING_SHADELESS, posable=False),
    16: _rg(16, False, (DIFFUSE,), posable=False, specular=SPECULAR_NO),
    17: _rg(17, False, (DIFFUSE, LIGHTMAP), posable=False, specular=SPECULAR_NO),
    18: _rg(18, True, (DIFFUSE,), posable=False, specular=SPECULAR_NO),
    19: _rg(19, True, (DIFFUSE, LIGHTMAP), posable=False, specular=SPECULAR_NO),
    20: _rg(20, True, _SIX, bump1=True, bump2=True, note="alpha variant of 1"),
    21: _rg(21, True, (DIFFUSE,), SHADING_SHADELESS, specular=SPECULAR_NO),
    22: _rg(22, False, _SEVEN, bump1=True, bump2=True, note="7 textures"),
    23: _rg(23, True, _SEVEN, bump1=True, bump2=True, note="7 textures"),
    24: _rg(24, False, (DIFFUSE, LIGHTMAP, BUMP, SPECULAR), note="community: deprecated, use 22"),
    25: _rg(25, True, (DIFFUSE, LIGHTMAP, BUMP, SPECULAR), note="community: deprecated, use 23"),
    26: _rg(26, False, (DIFFUSE, BUMP, ENVIRONMENT, MASK), SHADING_SWITCHABLE,
            specular=SPECULAR_INTENSITY, note="environment reflection; community: deprecated, use 28"),
    27: _rg(27, True, (DIFFUSE, BUMP, ENVIRONMENT, MASK), SHADING_SWITCHABLE, specular=SPECULAR_INTENSITY),
    28: _rg(28, False, (DIFFUSE, BUMP, MASK, BUMP1, BUMP2, ENVIRONMENT), SHADING_SWITCHABLE,
            specular=SPECULAR_INTENSITY, bump1=True, bump2=True, note="bump1 tiling uses parameter 3"),
    29: _rg(29, True, (DIFFUSE, BUMP, MASK, BUMP1, BUMP2, ENVIRONMENT), SHADING_SWITCHABLE,
            specular=SPECULAR_INTENSITY, bump1=True, bump2=True, note="bump1 tiling uses parameter 3"),
    30: _rg(30, False, (DIFFUSE, BUMP, EMISSION), SHADING_SWITCHABLE, specular=SPECULAR_INTENSITY),
    31: _rg(31, True, (DIFFUSE, BUMP, EMISSION), SHADING_SWITCHABLE, specular=SPECULAR_INTENSITY),
    32: _rg(32, False, (DIFFUSE,)),
    33: _rg(33, True, (DIFFUSE,)),
    # 34/35: the importer only defines the slot order; every other attribute is its class default.
    34: _rg(34, False, (DIFFUSE, BUMP, MASK, SPECULAR), bump1=True, bump2=True,
            note="only texture slots documented; other attributes are importer defaults"),
    35: _rg(35, False, (DIFFUSE, BUMP, MASK, SPECULAR), bump1=True, bump2=True,
            note="only texture slots documented; not flagged alpha upstream although the odd number "
                 "suggests the alpha variant of 34 (unverified)"),
    36: _rg(36, False, (DIFFUSE, BUMP, EMISSION), SHADING_SWITCHABLE, specular=SPECULAR_INTENSITY,
            bump1=True, note="emission scaled by parameter 1"),
    37: _rg(37, True, (DIFFUSE, BUMP, EMISSION), SHADING_SWITCHABLE, specular=SPECULAR_INTENSITY,
            bump1=True, note="emission scaled by parameter 1"),
    38: _rg(38, False, (DIFFUSE, BUMP, SPECULAR, EMISSION), SHADING_SWITCHABLE,
            specular=SPECULAR_INTENSITY, bump1=True),
    39: _rg(39, True, (DIFFUSE, BUMP, SPECULAR, EMISSION), SHADING_SWITCHABLE,
            specular=SPECULAR_INTENSITY, bump1=True),
    40: _rg(40, False, (DIFFUSE, BUMP, SPECULAR)),
    41: _rg(41, True, (DIFFUSE, BUMP, SPECULAR)),
    42: _rg(42, False, (DIFFUSE, BUMP, SPECULAR), spec1=True, note="tiled specular map"),
    43: _rg(43, True, (DIFFUSE, BUMP, SPECULAR), spec1=True, note="tiled specular map"),
}


def describe_render_group(number: Optional[int]) -> RenderGroupInfo:
    """Return the description of render group ``number``.

    ``None`` (no numeric prefix in the mesh name) maps to render group 5 like XPS
    does.  Numbers outside the table come back with ``known=False`` and the
    importer's fallback slot order, so callers can still find the diffuse slot.
    """
    if number is None:
        return RENDER_GROUPS[DEFAULT_RENDER_GROUP]
    info = RENDER_GROUPS.get(number)
    if info is not None:
        return info
    return RenderGroupInfo(number, False, UNKNOWN_SLOTS, known=False,
                           note="unknown render group; slot order is the importer fallback")


def is_alpha_render_group(number: Optional[int]) -> bool:
    """Whether meshes of this render group are alpha blended in XPS."""
    return describe_render_group(number).alpha
