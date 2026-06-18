from __future__ import annotations

import base64
import io
import time
import unittest

import constants
import osr_map_maker as app
import project_services
import renderers


class PerformanceSmokeTests(unittest.TestCase):
    def tearDown(self) -> None:
        app.clear_performance_caches()

    def test_modular_facades_import_core_services(self) -> None:
        self.assertEqual(constants.CURRENT_SCHEMA_VERSION, app.CURRENT_SCHEMA_VERSION)
        self.assertIs(renderers.render_pillow, app.render_pillow)
        self.assertIs(project_services.validate_project, app.validate_project)

    def test_performance_profiler_records_and_summarizes_samples(self) -> None:
        profiler = app.PerformanceProfiler(enabled=True)

        profiler.record("redraw", 4.0)
        profiler.record("redraw", 8.0)

        self.assertEqual(profiler.samples["redraw"].count, 2)
        self.assertEqual(profiler.samples["redraw"].average_ms, 6.0)
        self.assertIn("redraw 6.0/8.0ms", profiler.summary(("redraw",)))

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

    def test_canvas_size_cache_reuses_bounds_until_project_changes(self) -> None:
        project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        project["objects"].append(room)
        original_bounds = app.bounds
        calls = 0

        def counting_bounds(obj):
            nonlocal calls
            calls += 1
            return original_bounds(obj)

        app.bounds = counting_bounds
        try:
            first = app.canvas_size(project, 1.0)
            second = app.canvas_size(project, 1.0)
            room["x"] = 80
            third = app.canvas_size(project, 1.0)
        finally:
            app.bounds = original_bounds

        self.assertEqual(first, second)
        self.assertNotEqual(second, third)
        self.assertEqual(calls, 2)

    def test_floor_geometry_cache_reuses_polygon_points(self) -> None:
        cave = app.validate_object(app.rect("cave", 1, 1, 4, 4), 2)
        original_compute = app.compute_floor_polygon_points
        calls = 0

        def counting_compute(obj, cell):
            nonlocal calls
            calls += 1
            return original_compute(obj, cell)

        app.compute_floor_polygon_points = counting_compute
        try:
            first = app.floor_polygon_points(cave, 18)
            second = app.floor_polygon_points(cave, 18)
            cave["width"] = 5
            third = app.floor_polygon_points(cave, 18)
        finally:
            app.compute_floor_polygon_points = original_compute

        self.assertEqual(first, second)
        self.assertNotEqual(second, third)
        self.assertEqual(calls, 2)

    def test_underlay_transform_cache_reuses_loaded_image(self) -> None:
        if app.Image is None:
            self.skipTest("Pillow is not installed")
        image = app.Image.new("RGBA", (4, 4), (255, 0, 0, 255))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        underlay = {
            "id": "underlay_1",
            "embeddedData": base64.b64encode(buffer.getvalue()).decode("ascii"),
            "rotation": 15,
        }

        first = app.transformed_underlay_image(underlay, 12, 10, 0.5)
        stats_after_first = app.performance_cache_stats()
        second = app.transformed_underlay_image(underlay, 12, 10, 0.5)
        stats_after_second = app.performance_cache_stats()

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertIsNot(first, second)
        self.assertEqual(stats_after_first["underlay_sources"], 1)
        self.assertEqual(stats_after_first["underlay_transforms"], 1)
        self.assertEqual(stats_after_second["underlay_sources"], 1)
        self.assertEqual(stats_after_second["underlay_transforms"], 1)

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

    def test_scheduled_redraws_coalesce_and_preserve_full_canvas_priority(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.redraw_after_id = None
        maker._pending_redraw_full_canvas = False
        maker._pending_redraw_refresh_panels = False
        maker._pending_redraw_refresh_minimap = False
        scheduled: list[tuple[int, object]] = []
        flushed: list[tuple[bool, bool]] = []
        maker.after = (
            lambda delay, callback: scheduled.append((delay, callback)) or "after_1"
        )
        maker.redraw = (
            lambda refresh_panels=True, refresh_minimap=True, cancel_pending=True:
            flushed.append((refresh_panels, refresh_minimap))
        )
        maker.redraw_interaction_overlays = lambda: flushed.append((False, False))
        maker.update_status = lambda: None

        app.OSRMapMaker.schedule_redraw(maker, full_canvas=False)
        app.OSRMapMaker.schedule_redraw(maker, refresh_panels=True)

        self.assertEqual(len(scheduled), 1)
        app.OSRMapMaker.flush_scheduled_redraw(maker)
        self.assertEqual(flushed, [(True, True)])

    def test_minimap_redraws_are_throttled_and_full_priority_wins(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.minimap_after_id = None
        maker._pending_minimap_full = False
        maker.minimap_visible_var = type("Var", (), {"get": lambda self: True})()
        scheduled: list[tuple[int, object]] = []
        flushed: list[bool] = []
        maker.after = (
            lambda delay, callback: scheduled.append((delay, callback)) or "mini_1"
        )
        maker.after_cancel = lambda _after_id: None
        maker.redraw_minimap = lambda full=True: flushed.append(full)

        app.OSRMapMaker.schedule_minimap_redraw(maker, full=False)
        app.OSRMapMaker.schedule_minimap_redraw(maker, full=True)

        self.assertEqual(len(scheduled), 1)
        app.OSRMapMaker.flush_scheduled_minimap_redraw(maker)
        self.assertEqual(flushed, [True])

    def test_canvas_item_tagging_only_marks_new_items(self) -> None:
        class FakeCanvas:
            def __init__(self) -> None:
                self.items = [1]
                self.tags: dict[int, set[str]] = {}

            def find_all(self):
                return tuple(self.items)

            def addtag_withtag(self, tag: str, item_id: int) -> None:
                self.tags.setdefault(item_id, set()).add(tag)

            def create_fake_item(self) -> None:
                self.items.append(max(self.items) + 1)

        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        canvas = FakeCanvas()
        maker.canvas = canvas

        app.OSRMapMaker.tag_canvas_items_created_by(
            maker,
            app.CANVAS_INTERACTION_TAG,
            lambda: (canvas.create_fake_item(), canvas.create_fake_item()),
        )

        self.assertNotIn(1, canvas.tags)
        self.assertEqual(canvas.tags[2], {app.CANVAS_INTERACTION_TAG})
        self.assertEqual(canvas.tags[3], {app.CANVAS_INTERACTION_TAG})

    def test_render_context_precomputes_layer_and_player_visibility(self) -> None:
        project = app.create_project()
        project["settings"]["exportAudience"] = "Player"
        project["layers"][1]["visible"] = False
        hidden_room = app.validate_object(
            {**app.rect("room", 2, 2, 3, 3), "playerVisible": False}, 2
        )
        note = app.validate_object(
            {**app.text_obj("GM only", 3, 3), "roomId": hidden_room["id"]}, 3
        )
        project["objects"].extend([hidden_room, note])

        context = app.render_context(project)

        self.assertFalse(app.project_layer_visible(project, "rooms", context))
        self.assertIn(hidden_room["id"], context.hidden_player_room_ids)
        self.assertFalse(
            app.should_render_object(project, note, for_export=True, context=context)
        )

    def test_layer_index_reuses_project_layer_maps(self) -> None:
        project = app.create_project()
        project["layers"][1]["visible"] = False
        project["layers"][2]["locked"] = True
        project["layers"][2]["opacity"] = 0.35

        index = app.project_layer_index(project)
        second = app.project_layer_index(project)

        self.assertIs(index, second)
        self.assertEqual(index.id_by_name[project["layers"][2]["name"]], "corridors")
        self.assertFalse(app.project_layer_visible(project, "rooms"))
        self.assertEqual(app.project_layer_opacity(project, "corridors"), 0.35)

    def test_tk_static_layer_signature_tracks_layer_objects(self) -> None:
        project = app.create_project()
        project["layers"][1]["staticCache"] = True
        room = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        project["objects"].append(room)
        context = app.render_context(project)

        first = app.tk_static_layer_signature(project, "rooms", 1.0, context)
        room["x"] = 3
        second = app.tk_static_layer_signature(project, "rooms", 1.0, app.render_context(project))

        self.assertNotEqual(first, second)

    def test_spatial_index_reuses_revision_until_project_changes(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        maker.project["objects"].append(
            app.validate_object(app.rect("room", 1, 1, 2, 2), 2)
        )
        maker._spatial_index = None
        maker._spatial_index_revision = -1
        maker._spatial_index_bucket_size = 8.0
        maker._project_revision = 0
        maker._static_canvas_signature = ""

        first = app.OSRMapMaker.current_spatial_index(maker)
        second = app.OSRMapMaker.current_spatial_index(maker)
        app.OSRMapMaker.bump_project_revision(maker)
        third = app.OSRMapMaker.current_spatial_index(maker)

        self.assertIs(first, second)
        self.assertIsNot(second, third)

    def test_object_index_reuses_revision_and_refreshes_bounds(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 2, 2), 2)
        room["group"] = "grp_a"
        maker.project["objects"].append(room)
        maker._object_index = None
        maker._object_index_revision = -1
        maker._project_revision = 0
        maker._static_canvas_signature = ""
        maker.selected_ids = {room["id"]}

        first = app.OSRMapMaker.current_object_index(maker)
        room["x"] = 8
        second = app.OSRMapMaker.current_object_index(maker)
        app.OSRMapMaker.bump_project_revision(maker)
        third = app.OSRMapMaker.current_object_index(maker)

        self.assertIs(first, second)
        self.assertIsNot(second, third)
        self.assertEqual(first.object_by_id[room["id"]], room)
        self.assertIn(room, first.objects_by_group["grp_a"])
        self.assertEqual(first.bounds_by_id[room["id"]][0], 1)
        self.assertEqual(third.bounds_by_id[room["id"]][0], 8)
        self.assertEqual(app.OSRMapMaker.selected_objects(maker), [room])

    def test_object_list_refresh_skips_rebuild_when_only_selection_changes(self) -> None:
        class Var:
            def __init__(self, value):
                self.value = value

            def get(self):
                return self.value

            def set(self, value):
                self.value = value

        class Combo:
            def __init__(self):
                self.values = ()

            def configure(self, **kwargs):
                self.values = kwargs.get("values", self.values)

        class ListBox:
            def __init__(self):
                self.items: list[str] = []
                self.selected: set[int] = set()
                self.deletes = 0
                self.seen: list[int] = []

            def delete(self, _start, _end):
                self.deletes += 1
                self.items = []
                self.selected = set()

            def insert(self, _where, value):
                self.items.append(value)

            def selection_clear(self, _start, _end):
                self.selected = set()

            def selection_set(self, index):
                self.selected.add(index)

            def see(self, index):
                self.seen.append(index)

        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 2, 2), 2)
        maker.project["objects"].append(room)
        maker._project_revision = 0
        maker._object_index = None
        maker._object_index_revision = -1
        maker._layer_index = None
        maker._layer_index_revision = -1
        maker._object_list_signature = ""
        maker._object_list_selection_signature = ""
        maker.object_listbox = ListBox()
        maker.object_layer_combo = Combo()
        maker.object_search_var = Var("")
        maker.object_type_filter_var = Var("All")
        maker.object_layer_filter_var = Var("All")
        maker.selected_ids = set()

        app.OSRMapMaker.refresh_object_list(maker)
        maker.selected_ids = {room["id"]}
        app.OSRMapMaker.refresh_object_list(maker)

        self.assertEqual(maker.object_listbox.deletes, 1)
        self.assertIn(maker.object_list_ids.index(room["id"]), maker.object_listbox.selected)

    def test_object_list_refresh_shows_empty_state(self) -> None:
        class Var:
            def __init__(self, value):
                self.value = value

            def get(self):
                return self.value

            def set(self, value):
                self.value = value

        class Combo:
            def configure(self, **_kwargs):
                return None

        class ListBox:
            def __init__(self):
                self.items: list[str] = []
                self.selected: set[int] = set()

            def delete(self, _start, _end):
                self.items = []
                self.selected = set()

            def insert(self, _where, value):
                self.items.append(value)

            def selection_clear(self, _start, _end):
                self.selected = set()

            def selection_set(self, index):
                self.selected.add(index)

            def see(self, _index):
                return None

        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        maker.project["objects"] = []
        maker._project_revision = 0
        maker._object_list_signature = ""
        maker._object_list_selection_signature = ""
        maker.object_listbox = ListBox()
        maker.object_layer_combo = Combo()
        maker.object_search_var = Var("")
        maker.object_type_filter_var = Var("All")
        maker.object_layer_filter_var = Var("All")
        maker.selected_ids = set()

        app.OSRMapMaker.refresh_object_list(maker)
        self.assertEqual(maker.object_list_ids, [""])
        self.assertEqual(maker.object_listbox.items, ["No objects on this map yet."])

        maker.object_search_var.set("missing")
        app.OSRMapMaker.refresh_object_list(maker)
        self.assertEqual(
            maker.object_listbox.items,
            ["No objects match the current filter."],
        )

    def test_spatial_index_uses_cached_object_bounds(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        for index in range(30):
            maker.project["objects"].append(
                app.validate_object(app.rect("room", index, 0, 1, 1), index + 2)
            )
        maker._object_index = None
        maker._object_index_revision = -1
        maker._spatial_index = None
        maker._spatial_index_revision = -1
        maker._spatial_index_bucket_size = 8.0
        maker._project_revision = 0
        maker._static_canvas_signature = ""

        original_bounds = app.bounds
        calls = 0

        def counting_bounds(obj):
            nonlocal calls
            calls += 1
            return original_bounds(obj)

        app.bounds = counting_bounds
        try:
            app.OSRMapMaker.current_object_index(maker)
            calls_after_object_index = calls
            app.OSRMapMaker.current_spatial_index(maker)
        finally:
            app.bounds = original_bounds

        self.assertGreater(calls_after_object_index, 0)
        self.assertEqual(calls, calls_after_object_index)

    def test_drag_object_snap_guides_are_prepared_and_reused(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        maker.project["settings"]["snapToGrid"] = False
        maker.project["settings"]["snapToObjects"] = True
        moving = app.validate_object(app.rect("room", 0, 0, 2, 2), 2)
        anchor = app.validate_object(app.rect("room", 5, 0, 2, 2), 3)
        maker.project["objects"].extend([moving, anchor])
        maker._object_index = None
        maker._object_index_revision = -1
        maker._project_revision = 0
        maker._static_canvas_signature = ""
        maker.drag_originals = {moving["id"]: app.json_clone(moving)}
        maker.smart_guides = []

        app.OSRMapMaker.prepare_drag_snap_guides(maker, {moving["id"]})

        original_alignment = app.object_alignment_guides

        def fail_alignment(*_args, **_kwargs):
            raise AssertionError("drag snap guides should be reused")

        app.object_alignment_guides = fail_alignment
        try:
            dx, dy = app.OSRMapMaker.snap_move_delta_to_objects(maker, 2.9, 0.0)
        finally:
            app.object_alignment_guides = original_alignment

        self.assertAlmostEqual(dx, 3.0)
        self.assertAlmostEqual(dy, 0.0)
        self.assertIn(("x", 5), maker.smart_guides)

    def test_static_canvas_signature_tracks_grid_relevant_settings(self) -> None:
        project = app.create_project()
        context = app.render_context(project)

        first = app.tk_static_canvas_signature(project, 1.0, context)
        project["settings"]["showSubGrid"] = not project["settings"]["showSubGrid"]
        second = app.tk_static_canvas_signature(
            project, 1.0, app.render_context(project)
        )

        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
