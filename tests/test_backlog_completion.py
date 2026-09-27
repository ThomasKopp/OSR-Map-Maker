from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import osr_map_maker as app
import storage
from tests.test_storage_recovery import headless_maker


@unittest.skipIf(app.Image is None, "Pillow unavailable")
class BackgroundExportTests(unittest.TestCase):
    def test_late_autosave_result_never_marks_newer_revision_saved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp) / "autosaves")
            callbacks = []
            maker.__dict__["tk"] = object()  # Enables the live-Tk worker path.
            maker.after = lambda _delay, callback: callbacks.append(callback) or "after"
            maker._background_jobs = {}
            maker.run_autosave()
            job = maker._background_jobs["autosave"]
            job.thread.join(timeout=5)
            self.assertFalse(job.thread.is_alive())
            maker._project_revision = 2  # Edit made while the worker was writing.
            callbacks.pop(0)()
            self.assertEqual(maker._autosave_revision, -1)
            self.assertTrue(maker.autosave_file.exists())

    def test_cancel_stops_between_atomic_export_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = app.plan_batch_export(
                [
                    (None, "map", {"format": "png", "scale": 1}, root / f"{i}.png")
                    for i in range(3)
                ]
            )
            checks = 0

            def cancelled() -> bool:
                nonlocal checks
                checks += 1
                return checks > 1

            results = app.execute_batch_export(
                plan,
                lambda _item: (app.Image.new("RGB", (2, 2), "white"), "#fff"),
                should_cancel=cancelled,
            )
            self.assertEqual([item.status for item in results], ["Saved", "Cancelled", "Cancelled"])
            self.assertTrue(plan[0].path.exists())
            self.assertFalse(plan[1].path.exists())
            self.assertFalse(plan[2].path.exists())


class PlayerExportTests(unittest.TestCase):
    def test_player_vtt_and_handout_do_not_contain_gm_only_text_or_state(self) -> None:
        project = app.create_project()
        project["settings"]["exportAudience"] = "Player"
        hidden = app.validate_object(app.rect("room", 2, 2, 3, 3), 2)
        hidden.update({"playerVisible": False, "gmNotes": "GM-SECRET", "roomName": "GM-SECRET"})
        visible = app.validate_object(app.rect("room", 7, 2, 3, 3), 3)
        visible.update({"readAloud": "Public inscription", "gmNotes": "GM-SECRET"})
        secret = app.validate_object(app.symbol("secret_door", 4, 4, 1), 4)
        project["objects"].extend([hidden, visible, secret])
        project["sessionState"] = {"gmSecret": "GM-SECRET"}

        payloads = [
            app.foundry_scene_data(project),
            app.roll20_page_data(project),
            app.fantasy_grounds_xml(project),
            {"handout": app.handout_export_markdown(project)},
        ]
        for payload in payloads:
            text = json.dumps(payload)
            self.assertNotIn("GM-SECRET", text)
        self.assertEqual(app.foundry_scene_data(project)["session"], {})
        self.assertEqual(app.roll20_page_data(project)["encounter_starts"], [])

    @unittest.skipIf(app.Image is None, "Pillow unavailable")
    def test_player_raster_svg_and_preview_share_the_export_filter(self) -> None:
        project = app.create_project()
        project["settings"]["exportAudience"] = "Player"
        hidden = app.validate_object(app.text_obj("GM-SECRET", 3, 3), 2)
        hidden["playerVisible"] = False
        public = app.validate_object(app.text_obj("PUBLIC", 4, 4), 3)
        project["objects"].extend([hidden, public])
        options = {"format": "png", "scope": "map", "audience": "Player", "include_legend": False}
        image, _background = app.render_project_snapshot_image(project, 1, options)
        expected_project = app.json_clone(project)
        expected_project["objects"] = [public]
        expected, _background = app.render_project_snapshot_image(expected_project, 1, options)
        self.assertEqual(image.tobytes(), expected.tobytes())
        self.assertFalse(any("GM-SECRET" in str(value) for value in image.info.values()))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "player.svg"
            app.save_svg(str(path), project, {**options, "format": "svg"})
            self.assertNotIn("GM-SECRET", path.read_text(encoding="utf-8"))
            self.assertIn("PUBLIC", path.read_text(encoding="utf-8"))

    def test_checked_reference_exports_match_the_reference_project(self) -> None:
        project = app.validate_project(
            app.read_project_file(Path("examples/vtt-export.osrmap.json"))
        )
        for index, obj in enumerate(project.get("objects", []), start=1):
            obj["id"] = f"reference-{index:03d}"
        expected = {
            "foundry-scene.json": app.foundry_scene_data(project),
            "roll20-page.json": app.roll20_page_data(project),
            "fantasy-grounds.xml": app.fantasy_grounds_xml(project),
        }
        for name, data in expected.items():
            path = Path("examples/vtt-reference") / name
            if path.suffix == ".json":
                self.assertEqual(
                    json.loads(path.read_text(encoding="utf-8")),
                    json.loads(json.dumps(data)),
                )
            else:
                self.assertEqual(path.read_text(encoding="utf-8"), data)


class ResourceGuardTests(unittest.TestCase):
    def test_oversized_compressed_project_is_rejected_before_json_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large.osrmapz"
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("project.json", "x" * 100)
            limits = storage.ProjectResourceLimits(max_file_bytes=1024, max_uncompressed_bytes=32)
            with self.assertRaisesRegex(ValueError, "expands"):
                storage.read_project_file(path, limits)

    def test_extreme_raster_area_explains_the_safe_alternatives(self) -> None:
        limits = storage.ProjectResourceLimits(max_export_pixels=100)
        with self.assertRaisesRegex(app.ExportResourceLimitError, "smaller scale or a tiled/atlas"):
            app.ensure_export_resources(11, 10, limits)

    @unittest.skipIf(app.Image is None, "Pillow unavailable")
    def test_tiled_export_keeps_each_tile_under_the_pixel_limit(self) -> None:
        project = app.create_project()
        project["settings"].update({"width": 40, "height": 20, "cellSize": 10})
        limits = storage.ProjectResourceLimits(max_export_pixels=10_000)
        tiles = app.render_project_snapshot_tiles(
            project, 1, {"format": "png", "scope": "map"}, limits
        )
        self.assertGreater(len(tiles), 1)
        self.assertTrue(all(tile.width * tile.height <= limits.max_export_pixels for *_meta, tile, _bg in tiles))
        paths = app.tiled_export_paths(Path("map.png"), 2, 2)
        self.assertEqual(paths[0].name, "map-r01-c01.png")
        self.assertEqual(paths[-1].name, "map-r02-c02.png")


class ModuleBoundaryTests(unittest.TestCase):
    def test_storage_and_structural_validation_import_without_tk_application(self) -> None:
        import geometry
        import rendering
        import validation

        self.assertEqual(validation.validate_project_document({"objects": []})["objects"], [])
        with self.assertRaisesRegex(ValueError, "objects"):
            validation.validate_project_document({"objects": {}})
        self.assertTrue(geometry.rects_overlap((0, 0, 2, 2), (1, 1, 2, 2)))
        self.assertEqual(geometry.rotate_xy(2, 1, 1, 1, 90), (1.0, 2.0))
        self.assertTrue(callable(rendering.visual_image_difference))
