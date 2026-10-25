"""MMD material naming, memo and draw order from the XPS material manifest (design doc §9; no bpy)."""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

MEMO_PREFIX = "xps2pmx:"


def material_name(manifest: Dict, fallback: str = "") -> str:
    """XPS mesh name without render-group prefix and parameter suffix (``4_Body_0.1_0_0`` → ``Body``), keeping +/-."""
    base = manifest.get("base_name") or fallback or manifest.get("key", "")
    opt = manifest.get("optional") or {}
    sign = opt.get("sign", "")
    if sign and not base.startswith(("+", "-")):
        base = sign + base
    return base


def material_memo(manifest: Dict) -> str:
    """Memo written to the PMX material comment; lets the HD re-attach find the manifest entry again."""
    rg = manifest.get("render_group", -1)
    params = ",".join(f"{float(manifest.get(k, 0.0)):g}" for k in ("specular", "bump_repeat1", "bump_repeat2"))
    return f"{MEMO_PREFIX} key={manifest.get('key', '')}; RenderGroup={rg}; Params={params}"


def parse_memo(text: str) -> Dict[str, str]:
    if not text or not text.startswith(MEMO_PREFIX):
        return {}
    out = {}
    for part in text[len(MEMO_PREFIX):].split(";"):
        key, sep, val = part.strip().partition("=")
        if sep:
            out[key.strip()] = val.strip()
    return out


def draw_order(items: Sequence[Tuple[str, Dict]]) -> List[str]:
    """Object names in PMX draw order: opaque render groups first, ``rgAlpha`` ones after, original order inside."""
    def key(entry):
        name, manifest = entry
        return (1 if manifest.get("rg_alpha") else 0, int(manifest.get("mesh_index", 0)), name)
    return [name for name, _ in sorted(items, key=key)]
