from __future__ import annotations

import time
import unittest

import constants
import osr_map_maker as app
import project_services
import renderers


class PerformanceSmokeTests(unittest.TestCase):
    def test_modular_facades_import_core_services(self) -> None:
        self.assertEqual(constants.CURRENT_SCHEMA_VERSION, app.CURRENT_SCHEMA_VERSION)
        self.assertIs(renderers.render_pillow, app.render_pillow)
        self.assertIs(project_services.validate_project, app.validate_project)

    def test_large_map_bounds_are_fast(self) -> None:
        project = app.create_project()
        project["settings"]["width"] = 180
        project["settings"]["height"] = 140
        for index in range(250):
            x = 1 + (index * 7) % 170
            y = 1 + (index * 11) % 130
            project["objects"].append(
                app.validate_object(app.rect("room", x, y, 3, 3), index + 2)
            )
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
            project["objects"].append(
                app.validate_object(
                    app.symbol(kind, 1 + index % 70, 1 + (index * 3) % 50, 0.8),
                    index + 2,
                )
            )
        image = app.Image.new(
            "RGBA",
            tuple(int(v) for v in app.canvas_size(project, 1)),
            project["settings"]["backgroundColor"],
        )
        draw = app.ImageDraw.Draw(image)
        started = time.perf_counter()
        app.render_pillow(draw, project, 1, None, None)
        elapsed = time.perf_counter() - started
        self.assertLess(elapsed, 5.0)

    def test_spatial_index_handles_large_project_hit_detection(self) -> None:
        project = app.create_project()
        project["settings"]["width"] = 260
        project["settings"]["height"] = 220
        for index in range(10_000):
            project["objects"].append(
                app.validate_object(
                    app.rect(
                        "room",
                        1 + (index * 7) % 250,
                        1 + (index * 11) % 210,
                        1.5,
                        1.5,
                    ),
                    index + 2,
                )
            )
        target = app.validate_object(app.rect("room", 15, 23, 2, 2), 10_002)
        project["objects"].append(target)

        started = time.perf_counter()
        index = app.build_spatial_index(project["objects"], bucket_size=8)
        hit = app.topmost_hit_object(project, 15, 23, index=index, bucket_size=8)
        elapsed = time.perf_counter() - started

        self.assertEqual(hit["id"], target["id"])
        self.assertLess(elapsed, 1.0)

    def test_static_layer_cache_reuses_rendered_layer(self) -> None:
        if app.Image is None:
            self.skipTest("Pillow is not installed")
        project = app.create_project()
        project["layers"][1]["staticCache"] = True
        project["objects"].append(app.validate_object(app.rect("room", 1, 1, 4, 4), 2))

        first = app.render_static_layer_image(project, "rooms", 1, True)
        before = app.static_layer_cache_stats()["entries"]
        second = app.render_static_layer_image(project, "rooms", 1, True)
        after = app.static_layer_cache_stats()["entries"]

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
