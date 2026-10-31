"""Thumbnails for 看图 (design doc §16.5), loaded with ``bpy.utils.previews`` and reloaded when the file changes."""
from __future__ import annotations

import os

import bpy.utils.previews

_COLLECTION = None


def icon_id(path: str) -> int:
    """Icon id of the image at ``path`` (0 when there is none)."""
    global _COLLECTION
    if not path or not os.path.isfile(path):
        return 0
    if _COLLECTION is None:
        _COLLECTION = bpy.utils.previews.new()
    key = f"{path}|{os.path.getmtime(path)}"
    item = _COLLECTION.get(key)
    if item is None:
        item = _COLLECTION.load(key, path, 'IMAGE')
        item.image_size[:]  # noqa: B018 - touching the size loads the image now instead of on a later redraw
    return item.icon_id


def register() -> None:
    pass


def unregister() -> None:
    global _COLLECTION
    if _COLLECTION is not None:
        bpy.utils.previews.remove(_COLLECTION)
        _COLLECTION = None
