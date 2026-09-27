from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
import tkinter as tk
import unittest
from pathlib import Path

import osr_map_maker as app

try:
    import cairosvg
except ImportError:  # Optional renderer; the test explains how to enable it.
    cairosvg = None


def ghostscript_executable() -> str | None:
    return shutil.which("gswin64c") or shutil.which("gs")


def reference_project() -> dict:
    project = app.create_project()
    project["settings"].update({"width": 16, "height": 12, "cellSize": 16})
    room = app.validate_object(app.rect("room", 2, 2, 5, 3), 2)
    room["rotation"] = 18
    corridor = app.validate_object(app.diagonal_corridor(3, 7, 11, 8), 3)
    corridor["width"] = 1.2
    symbol = app.validate_object(app.symbol("torch", 10, 3, 1.3), 4)
    symbol["opacity"] = 0.55
    label = app.validate_object(app.text_obj("R1", 5, 4), 5)
    project["objects"].extend([room, corridor, symbol, label])
    for index, obj in enumerate(project["objects"], start=1):
        obj["id"] = f"visual-reference-{index:03d}"
    return project


def rendered_png(project: dict) -> bytes:
    image, _background = app.render_project_snapshot_image(
        project, 1, {"format": "png", "scope": "map", "include_legend": False}
    )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def rendered_tk_png(project: dict, target: Path) -> None:
    """Render the real Tk Canvas to EPS and rasterize it at one pixel per point."""
    root = tk.Tk()
    root.withdraw()
    try:
        width = project["settings"]["width"] * project["settings"]["cellSize"]
        height = project["settings"]["height"] * project["settings"]["cellSize"]
        canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        canvas.pack()
        app.render_tk(canvas, project, 1, set(), None, None, None)
        root.update_idletasks()
        with tempfile.TemporaryDirectory() as tmp:
            eps = Path(tmp) / "preview.eps"
            eps.write_text(
                canvas.postscript(colormode="color", pagewidth=width, pageheight=height),
                encoding="utf-8",
            )
            subprocess.run(
                [
                    ghostscript_executable() or "gs",
                    "-dSAFER",
                    "-dBATCH",
                    "-dNOPAUSE",
                    "-sDEVICE=pngalpha",
                    "-r72",
                    f"-sOutputFile={target}",
                    "-dEPSCrop",
                    str(eps),
                ],
                check=True,
                capture_output=True,
            )
    finally:
        root.destroy()


def rendered_svg_png(project: dict, target: Path) -> None:
    if cairosvg is None:
        raise RuntimeError("CairoSVG is required to rasterize SVG references.")
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "reference.svg"
        app.save_svg(
            str(source),
            project,
            {"format": "svg", "scope": "map", "scale": 1, "include_legend": False},
        )
        cairosvg.svg2png(url=str(source), write_to=str(target), output_width=256, output_height=192)


@unittest.skipIf(app.Image is None, "Pillow unavailable")
class VisualRegressionTests(unittest.TestCase):
    def test_tk_preview_renderer_records_reference_scene(self) -> None:
        class RecordingCanvas:
            def __init__(self) -> None:
                self.operations: list[str] = []

            def __getattr__(self, name):
                if name == "bbox":
                    return lambda _item: (0, 0, 1, 1)
                if name == "tag_raise":
                    return lambda *_args: None
                if name.startswith("create_"):
                    def create(*_args, **_kwargs):
                        self.operations.append(name)
                        return len(self.operations)

                    return create
                raise AttributeError(name)

        canvas = RecordingCanvas()
        app.render_tk(canvas, reference_project(), 1, set(), None, None, None)
        self.assertIn("create_rectangle", canvas.operations)
        self.assertIn("create_polygon", canvas.operations)
        self.assertIn("create_text", canvas.operations)

    def test_reference_scene_is_pixel_stable(self) -> None:
        actual = rendered_png(reference_project())
        fixture = Path("tests/fixtures/visual/reference.png")
        with app.Image.open(fixture) as reference:
            with app.Image.open(io.BytesIO(actual)) as result:
                report = app.visual_image_difference(
                    reference, result, Path("artifacts/visual"), "pillow-reference"
                )
        self.assertEqual(report["changed_pixels"], 0)

    @unittest.skipUnless(ghostscript_executable(), "Ghostscript is required for Tk preview rasterization")
    def test_real_tk_preview_is_pixel_stable(self) -> None:
        fixture = Path("tests/fixtures/visual/reference-tk.png")
        with tempfile.TemporaryDirectory() as tmp:
            actual_path = Path(tmp) / "actual-tk.png"
            rendered_tk_png(reference_project(), actual_path)
            with app.Image.open(fixture) as reference:
                with app.Image.open(actual_path) as result:
                    report = app.visual_image_difference(
                        reference, result, Path("artifacts/visual"), "tk-reference", tolerance=16
                    )
        self.assertEqual(report["changed_pixels"], 0)

    @unittest.skipUnless(cairosvg is not None, "Install .[svg] to rasterize SVG references")
    def test_rasterized_svg_is_pixel_stable(self) -> None:
        fixture = Path("tests/fixtures/visual/reference-svg.png")
        with tempfile.TemporaryDirectory() as tmp:
            actual_path = Path(tmp) / "actual-svg.png"
            rendered_svg_png(reference_project(), actual_path)
            with app.Image.open(fixture) as reference:
                with app.Image.open(actual_path) as result:
                    report = app.visual_image_difference(
                        reference, result, Path("artifacts/visual"), "svg-raster-reference", tolerance=16
                    )
        self.assertEqual(report["changed_pixels"], 0)

    def test_svg_reference_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "actual.svg"
            app.save_svg(
                str(target),
                reference_project(),
                {"format": "svg", "scope": "map", "scale": 1, "include_legend": False},
            )
            expected = Path("tests/fixtures/visual/reference.svg").read_text(encoding="utf-8")
            actual = target.read_text(encoding="utf-8")
        if actual != expected:
            output = Path("artifacts/visual")
            output.mkdir(parents=True, exist_ok=True)
            (output / "svg-reference.svg").write_text(expected, encoding="utf-8")
            (output / "svg-result.svg").write_text(actual, encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_difference_report_writes_reference_result_and_diff_images(self) -> None:
        reference = app.Image.new("RGB", (3, 3), "white")
        result = reference.copy()
        result.putpixel((1, 1), (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            report = app.visual_image_difference(reference, result, Path(tmp), "probe")
            self.assertGreater(report["changed_pixels"], 0)
            self.assertTrue((Path(tmp) / "probe-reference.png").exists())
            self.assertTrue((Path(tmp) / "probe-result.png").exists())
            self.assertTrue((Path(tmp) / "probe-diff.png").exists())

    def test_shifted_symbol_is_detected_and_leaves_review_images(self) -> None:
        original = app.Image.open(io.BytesIO(rendered_png(reference_project())))
        changed_project = reference_project()
        changed_project["objects"][2]["x"] += 1
        shifted = app.Image.open(io.BytesIO(rendered_png(changed_project)))
        with tempfile.TemporaryDirectory() as tmp:
            report = app.visual_image_difference(original, shifted, Path(tmp), "shifted-symbol")
            self.assertGreater(report["changed_pixels"], 0)
            self.assertTrue((Path(tmp) / "shifted-symbol-reference.png").exists())
            self.assertTrue((Path(tmp) / "shifted-symbol-result.png").exists())
            self.assertTrue((Path(tmp) / "shifted-symbol-diff.png").exists())
