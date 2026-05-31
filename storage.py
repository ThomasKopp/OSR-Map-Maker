from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from osr_map_maker import now_iso, validate_project


def load_project(path: str | Path) -> dict[str, Any]:
    return validate_project(json.loads(Path(path).read_text(encoding="utf-8")))


def save_project(path: str | Path, project: dict[str, Any]) -> None:
    project["meta"]["updatedAt"] = now_iso()
    Path(path).write_text(json.dumps(project, indent=2), encoding="utf-8")


def autosave_project(path: str | Path, project: dict[str, Any]) -> None:
    save_project(path, project)
