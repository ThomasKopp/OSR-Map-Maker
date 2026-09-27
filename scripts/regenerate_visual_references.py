"""Regenerate renderer baselines after a deliberate visual review."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from osr_map_maker import save_svg  # noqa: E402
from tests.test_visual_regression import (  # noqa: E402
    cairosvg,
    ghostscript_executable,
    reference_project,
    rendered_png,
    rendered_svg_png,
    rendered_tk_png,
)


def main() -> None:
    output = ROOT / "tests" / "fixtures" / "visual"
    output.mkdir(parents=True, exist_ok=True)
    project = reference_project()
    (output / "reference.png").write_bytes(rendered_png(project))
    save_svg(
        str(output / "reference.svg"),
        project,
        {"format": "svg", "scope": "map", "scale": 1, "include_legend": False},
    )
    if ghostscript_executable():
        rendered_tk_png(project, output / "reference-tk.png")
    if cairosvg is not None:
        rendered_svg_png(project, output / "reference-svg.png")


if __name__ == "__main__":
    main()
