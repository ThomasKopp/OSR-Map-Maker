"""Regenerate the checked VTT reference exports from the example map."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from osr_map_maker import (  # noqa: E402
    fantasy_grounds_xml,
    foundry_scene_data,
    read_project_file,
    roll20_page_data,
    validate_project,
)


def main() -> None:
    root = ROOT
    project = validate_project(read_project_file(root / "examples" / "vtt-export.osrmap.json"))
    for index, obj in enumerate(project.get("objects", []), start=1):
        obj["id"] = f"reference-{index:03d}"
    output = root / "examples" / "vtt-reference"
    output.mkdir(exist_ok=True)
    for name, payload in {
        "foundry-scene.json": foundry_scene_data(project),
        "roll20-page.json": roll20_page_data(project),
    }.items():
        (output / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (output / "fantasy-grounds.xml").write_text(
        fantasy_grounds_xml(project), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
