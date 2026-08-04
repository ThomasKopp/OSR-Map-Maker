from __future__ import annotations

from pathlib import Path
from typing import Any

from osr_map_maker import (
    now_iso,
    read_project_file,
    validate_project,
    write_project_data,
)


def load_project(path: str | Path) -> dict[str, Any]:
    return validate_project(read_project_file(Path(path)))


def save_project(path: str | Path, project: dict[str, Any]) -> None:
    project["meta"]["updatedAt"] = now_iso()
    write_project_data(Path(path), project)


def autosave_project(path: str | Path, project: dict[str, Any]) -> None:
    save_project(path, project)
