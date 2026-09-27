"""Renderer-independent image comparison helpers.

Kept free of Tk and the application model so visual-reference tests can use it
without importing the UI.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:  # pragma: no cover - callers receive a useful runtime error.
    Image = None


def visual_image_difference(
    reference: Any, result: Any, output_dir: Path, name: str, tolerance: int = 8
) -> dict[str, int]:
    """Compare images and emit reference/result/diff PNGs only on a mismatch."""
    if Image is None:
        raise RuntimeError("Pillow is required for visual regression checks.")
    output_dir.mkdir(parents=True, exist_ok=True)
    reference = reference.convert("RGBA")
    result = result.convert("RGBA")
    if reference.size != result.size:
        reference.save(output_dir / f"{name}-reference.png")
        result.save(output_dir / f"{name}-result.png")
        raise AssertionError(f"Image dimensions differ: {reference.size} != {result.size}")
    diff = Image.new("RGBA", reference.size, (0, 0, 0, 0))
    changed = 0
    for y in range(reference.height):
        for x in range(reference.width):
            left = reference.getpixel((x, y))
            right = result.getpixel((x, y))
            distance = max(abs(a - b) for a, b in zip(left, right, strict=True))
            if distance > tolerance:
                changed += 1
                diff.putpixel((x, y), (255, 0, 180, 255))
    if changed:
        reference.save(output_dir / f"{name}-reference.png")
        result.save(output_dir / f"{name}-result.png")
        diff.save(output_dir / f"{name}-diff.png")
    return {"changed_pixels": changed, "total_pixels": reference.width * reference.height}
