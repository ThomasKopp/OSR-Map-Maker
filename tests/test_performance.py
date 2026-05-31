from __future__ import annotations

import time
import unittest

import osr_map_maker as app


class PerformanceSmokeTests(unittest.TestCase):
    def test_large_map_bounds_are_fast(self) -> None:
        project = app.create_project()
        project["settings"]["width"] = 180
        project["settings"]["height"] = 140
        for index in range(250):
            x = 1 + (index * 7) % 170
            y = 1 + (index * 11) % 130
            project["objects"].append(app.validate_object(app.rect("room", x, y, 3, 3), index + 2))
        started = time.perf_counter()
        size = app.canvas_size(project, 0.5)
        elapsed = time.perf_counter() - started
        self.assertGreater(size[0], 0)
        self.assertLess(elapsed, 1.0)

    def test_many_symbol_pillow_render_smoke(self) -> None:
        if app.Image is None:
            self.skipTest("Pillow is not installed")
        project = app.create_project()
        project["settings"]["width"] = 80
        project["settings"]["height"] = 60
        kinds = list(app.SYMBOL_LABELS)[:20]
        for index in range(300):
            kind = kinds[index % len(kinds)]
            project["objects"].append(app.validate_object(app.symbol(kind, 1 + index % 70, 1 + (index * 3) % 50, 0.8), index + 2))
        image = app.Image.new("RGBA", tuple(int(v) for v in app.canvas_size(project, 1)), project["settings"]["backgroundColor"])
        draw = app.ImageDraw.Draw(image)
        started = time.perf_counter()
        app.render_pillow(draw, project, 1, None, None)
        elapsed = time.perf_counter() - started
        self.assertLess(elapsed, 5.0)


if __name__ == "__main__":
    unittest.main()
