"""UI-independent structural validation for on-disk project documents."""
from __future__ import annotations

from typing import Any


def validate_project_document(value: Any) -> dict[str, Any]:
    """Reject malformed root documents before the UI migration layer runs.

    Detailed migration/defaulting remains in ``osr_map_maker.validate_project``;
    this narrow check is intentionally dependency-free so storage callers can
    validate untrusted files without importing Tkinter.
    """
    if not isinstance(value, dict):
        raise ValueError("This project format is not supported.")
    for key in ("objects", "maps"):
        item = value.get(key)
        if item is not None and not isinstance(item, list):
            raise ValueError(f"Project field '{key}' must be a list.")
    for key in ("meta", "settings"):
        item = value.get(key)
        if item is not None and not isinstance(item, dict):
            raise ValueError(f"Project field '{key}' must be an object.")
    return value
