from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import osr_map_maker as app


class ProjectModelTests(unittest.TestCase):
    def test_validate_project_adds_missing_fields(self) -> None:
        project = {"objects": [{"type": "room", "x": 1, "y": 2, "width": 3, "height": 4}]}
        validated = app.validate_project(project)
        self.assertEqual(validated["schemaVersion"], app.CURRENT_SCHEMA_VERSION)
        self.assertIn("layers", validated)
        self.assertIn("exportProfiles", validated)
        self.assertIn("exportFrames", validated)
        self.assertIn("colorPalettes", validated)
        self.assertIn("shortcuts", validated["settings"])
        self.assertEqual(validated["settings"]["cellScale"], 10.0)
        self.assertTrue(validated["objects"][0]["playerVisible"])
        self.assertEqual(validated["objects"][0]["roomStatus"], "undiscovered")
        self.assertIn("encounterTable", validated["campaign"])

    def test_validate_project_collects_warnings_and_keeps_valid_objects(self) -> None:
        project = {
            "objects": [
                {"type": "room", "x": 1, "y": 1, "width": 2, "height": 2},
                {"type": "unknown", "x": 0, "y": 0},
            ]
        }
        validated = app.validate_project(project)

        self.assertTrue(any("unknown" in warning for warning in validated["validationWarnings"]))
        self.assertTrue(any(obj["type"] == "room" for obj in validated["objects"]))

    def test_export_profiles_frames_palettes_and_layer_opacity_validate(self) -> None:
        project = app.create_project()
        project["layers"][1]["opacity"] = 0.35
        project["exportProfiles"] = [{"name": "My Player", "format": "jpg", "scope": "frame", "audience": "Player"}]
        project["exportFrames"] = [{"name": "Boss Room", "x": 2, "y": 3, "width": 8, "height": 6}]
        project["colorPalettes"] = [{"name": "Night", "colors": {"backgroundColor": "#101010", "gridColor": "#eeeeee"}}]

        validated = app.validate_project(project)

        self.assertAlmostEqual(validated["layers"][1]["opacity"], 0.35)
        self.assertEqual(next(item for item in validated["exportProfiles"] if item["name"] == "My Player")["format"], "jpeg")
        self.assertEqual(validated["exportFrames"][0]["name"], "Boss Room")
        self.assertEqual(validated["colorPalettes"][0]["colors"]["backgroundColor"], "#101010")

    def test_validate_project_migrates_legacy_symbols(self) -> None:
        project = {
            "schemaVersion": 1,
            "settings": {},
            "objects": [{"type": "symbol", "kind": "secret", "x": 2, "y": 3, "size": 1}],
        }
        validated = app.validate_project(project)
        self.assertEqual(validated["objects"][0]["kind"], "secret_door")

    def test_validate_project_preserves_custom_symbol_keys(self) -> None:
        project = app.create_project()
        project["customSymbols"] = {"custom_skull": {"label": "Skull", "sourceType": "png", "path": "missing.png"}}
        project["customSymbolGroups"] = [{"name": "Custom", "entries": [{"kind": "custom_skull", "label": "Skull"}]}]
        project["objects"].append(app.symbol("custom_skull", 2, 3, 1))

        validated = app.validate_project(project)

        self.assertIn("custom_skull", validated["customSymbols"])
        self.assertEqual(validated["customSymbolGroups"][0]["entries"][0]["kind"], "custom_skull")
        self.assertEqual(validated["objects"][-1]["kind"], "custom_skull")
        self.assertTrue(app.is_custom_symbol(validated, "custom_skull"))

    def test_symbol_metadata_search_variants_and_style_validation(self) -> None:
        project = app.create_project()
        self.assertIn("door", app.symbol_tags(project, "door"))
        self.assertIn("open_door", [item["id"] for item in app.symbol_variant_options(project, "door")])
        self.assertIn("barred", app.symbol_search_blob(project, "door", "Door"))

        styled = app.validate_object(
            {
                **app.symbol("door", 2, 3, 1),
                "variant": "open_door",
                "sizePreset": "Large",
                "color": "#cc0000",
                "opacity": 0.42,
                "shadow": True,
                "outline": True,
                "legendLabel": "Red Door",
            },
            1,
        )

        self.assertEqual(styled["variant"], "open_door")
        self.assertEqual(styled["sizePreset"], "Large")
        self.assertEqual(styled["color"], "#cc0000")
        self.assertAlmostEqual(styled["opacity"], 0.42)
        self.assertTrue(styled["shadow"])
        self.assertTrue(styled["outline"])

    def test_symbol_set_import_export_merges_custom_symbols(self) -> None:
        source = app.create_project()
        source["customSymbols"] = {
            "custom_skull": {
                "label": "Skull",
                "sourceType": "png",
                "path": "missing.png",
                "tags": ["undead"],
                "variants": [{"id": "custom_skull_red", "label": "Red Skull", "sourceType": "png", "path": "missing-red.png"}],
            }
        }
        source["customSymbolGroups"] = [{"name": "Bones", "entries": [{"kind": "custom_skull", "label": "Skull"}]}]

        target = app.create_project()
        count = app.import_symbol_set_data(target, app.export_symbol_set_data(source))

        self.assertEqual(count, 1)
        self.assertIn("custom_skull", target["customSymbols"])
        self.assertEqual(target["customSymbols"]["custom_skull"]["variants"][0]["id"], "custom_skull_red")
        self.assertEqual(target["customSymbolGroups"][-1]["name"], "Bones")

    def test_validate_project_keeps_active_map_and_extra_maps(self) -> None:
        project = app.create_project()
        active_symbol = app.validate_object(app.symbol("stairs", 2, 3, 1), 2)
        project["objects"].append(active_symbol)
        second_settings = app.validate_settings({**project["settings"], "width": 24, "height": 18})
        second_map = app.create_map_record("Lower Level", second_settings, project["layers"], [app.legend_obj(second_settings)], {"rooms": []})
        project["maps"].append(second_map)

        validated = app.validate_project(project)

        self.assertEqual(len(validated["maps"]), 2)
        self.assertEqual(validated["objects"][-1]["kind"], "stairs")
        active_record = next(item for item in validated["maps"] if item["id"] == validated["activeMapId"])
        self.assertEqual(active_record["objects"][-1]["id"], active_symbol["id"])
        self.assertEqual(validated["maps"][1]["name"], "Lower Level")

    def test_measurement_summary_reports_distance_path_and_area(self) -> None:
        settings = app.validate_settings({"cellScale": 5, "cellScaleUnit": "ft."})
        summary = app.measurement_summary([(0, 0), (3, 4), (3, 0)], settings)

        self.assertIn("segment 4 cells (20 ft.)", summary)
        self.assertIn("path 9 cells (45 ft.)", summary)
        self.assertIn("area 6 cells^2 (150 sq ft.)", summary)

    def test_campaign_report_includes_toc_status_legend_and_tables(self) -> None:
        project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        room["roomNumber"] = "A1"
        room["roomName"] = "Guard Room"
        room["roomStatus"] = "dangerous"
        room["lootTable"] = "1-2 coins"
        project["objects"].append(room)
        project["objects"].append(app.validate_object(app.symbol("door", 2, 1, 1), 3))
        project["campaign"]["encounterTable"] = "1 goblins"

        report = app.campaign_report_markdown(project)

        self.assertIn("## Contents", report)
        self.assertIn("Symbol Legend", report)
        self.assertIn("Gefaehrlich", report)
        self.assertIn("Loot Table", report)
        self.assertIn("Map Encounter Table", report)

    def test_auto_door_symbols_can_cycle_door_types(self) -> None:
        objects = [app.rect("room", 1, 1, 6, 6)]
        objects.extend(
            [
                app.rect("corridor", 3, 0, 1, 3),
                app.rect("corridor", 6, 3, 3, 1),
                app.rect("corridor", 3, 6, 1, 3),
                app.rect("corridor", 0, 3, 3, 1),
            ]
        )

        doors = app.auto_door_symbols(objects, ["normal", "secret", "locked", "trapdoor"])

        self.assertEqual([door["kind"] for door in doors[:4]], ["door", "secret_door", "locked_door", "trap_floor"])

    def test_parse_dungeon_and_keyword_specs(self) -> None:
        options = app.parse_dungeon_options("12; 3-8x2-6; 4; 5")
        self.assertEqual(options["density"], 12)
        self.assertEqual((options["min_w"], options["max_w"], options["min_h"], options["max_h"]), (3, 8, 2, 6))
        self.assertEqual(options["loops"], 4)
        self.assertEqual(options["dead_ends"], 5)
        self.assertEqual(app.parse_keyword_spec("temple; cult; lava"), ("temple", "cult", "lava"))

    def test_player_export_hides_numbers_linked_to_hidden_rooms(self) -> None:
        project = app.create_project()
        hidden_room = app.validate_object(app.rect("room", 1, 1, 3, 3), 2)
        hidden_room["playerVisible"] = False
        room_number = app.text_obj("1", 2, 2, 1)
        room_number["textRole"] = "number"
        room_number["roomId"] = hidden_room["id"]
        project["objects"].extend([hidden_room, app.validate_object(room_number, 3)])
        project["settings"]["exportAudience"] = "Player"

        rendered_ids = {obj["id"] for obj in project["objects"] if app.should_render_object(project, obj, for_export=True)}

        self.assertNotIn(hidden_room["id"], rendered_ids)
        self.assertNotIn(room_number["id"], rendered_ids)

    def test_bounds_for_shapes(self) -> None:
        self.assertEqual(app.bounds({"type": "room", "x": 1, "y": 2, "width": 3, "height": 4}), (1, 2, 3, 4))
        self.assertEqual(app.bounds({"type": "symbol", "x": 5, "y": 6, "size": 2}), (4, 5, 2, 2))
        self.assertEqual(app.bounds({"type": "diagonal_corridor", "x": 1, "y": 1, "x2": 4, "y2": 5, "width": 1}), (0.5, 0.5, 4, 5))
        self.assertEqual(app.bounds({"type": "shape", "kind": "rectangle", "x": 1, "y": 2, "width": 3, "height": 4}), (1, 2, 3, 4))
        self.assertEqual(app.bounds({"type": "shape", "kind": "line", "x": 1, "y": 1, "x2": 4, "y2": 5, "lineWidth": 0.2}), (0.85, 0.85, 3.3, 4.3))
        self.assertEqual(
            app.bounds({"type": "shape", "kind": "polygon", "points": [{"x": 1, "y": 1}, {"x": 4, "y": 1}, {"x": 2, "y": 5}], "lineWidth": 0.2}),
            (0.9, 0.9, 3.2, 4.2),
        )

    def test_validate_shape_objects(self) -> None:
        rectangle = app.validate_object({**app.shape("rectangle", 1, 2, 3, 4), "lineStyle": "dash", "opacity": 0.5}, 1)
        polygon = app.validate_object({"type": "shape", "kind": "polygon", "points": [[1, 2], [4, 2], [2, 5]]}, 2)
        line = app.validate_object({**app.shape("line", 1, 2, 0, 0, 4, 6), "arrow": "both", "curve": True}, 3)

        self.assertEqual(rectangle["layer"], "shapes")
        self.assertEqual(rectangle["lineStyle"], "dash")
        self.assertEqual(rectangle["opacity"], 0.5)
        self.assertEqual(len(polygon["points"]), 3)
        self.assertEqual((polygon["x"], polygon["y"], polygon["width"], polygon["height"]), (1.0, 2.0, 3.0, 3.0))
        self.assertEqual((line["x2"], line["y2"]), (4.0, 6.0))
        self.assertEqual(line["arrow"], "both")
        self.assertTrue(line["curve"])

    def test_shape_defaults_apply_to_new_shape_drafts(self) -> None:
        draft = app.Draft("shape_line", 1, 2, 0, 0, 4, 6)
        obj = app.shape_from_draft_data(draft)
        app.apply_shape_defaults(obj, {"defaultShapeLineWidth": 0.5, "defaultShapeStrokeColor": "#123456"})

        self.assertEqual(obj["lineWidth"], 0.5)
        self.assertEqual(obj["strokeColor"], "#123456")

    def test_free_polygon_draft_closes_without_preview_point(self) -> None:
        draft = app.Draft("shape_polygon", 1, 1, 0.25, 0.25, 3, 3, [(1, 1), (4, 1), (2, 5)])

        preview = app.shape_from_draft_data(draft, include_preview=True)
        closed = app.shape_from_draft_data(draft)

        self.assertEqual(len(preview["points"]), 4)
        self.assertEqual(len(closed["points"]), 3)

    def test_diagonal_corridor_grid_segments_stay_orthogonal(self) -> None:
        polygon = app.corridor_polygon_points(10, 10, 44, 28, 10)
        segments = app.orthogonal_grid_segments(polygon, 10)
        self.assertGreater(len(segments), 0)
        self.assertTrue(all(x1 == x2 or y1 == y2 for x1, y1, x2, y2 in segments))
        self.assertTrue(any(x1 == x2 for x1, _y1, x2, _y2 in segments))
        self.assertTrue(any(y1 == y2 for _x1, y1, _x2, y2 in segments))

    def test_svg_diagonal_corridor_uses_polygon_and_grid_lines(self) -> None:
        project = app.create_project()
        parts = app.svg_for_object(project, {"type": "diagonal_corridor", "x": 1, "y": 1, "x2": 4, "y2": 3, "width": 1}, 1)
        self.assertTrue(any(part.startswith("<polygon") for part in parts))
        self.assertTrue(any(part.startswith("<line") for part in parts))

    def test_svg_symbols_and_legend_render_shapes_and_entries(self) -> None:
        project = app.create_project()
        project["objects"].append(app.validate_object(app.symbol("door", 3, 2, 1), 2))

        symbol_parts = app.svg_for_object(project, project["objects"][-1], 1)
        legend_parts = app.svg_for_object(project, project["objects"][0], 1)

        self.assertTrue(any(part.startswith("<rect") for part in symbol_parts))
        self.assertTrue(any("LEGEND" in part for part in legend_parts))
        self.assertTrue(any("Door" in part for part in legend_parts))

    def test_symbol_legend_sorts_groups_and_uses_overrides(self) -> None:
        project = app.create_project()
        trap = app.validate_object(app.symbol("trap", 4, 4, 1), 2)
        door = app.validate_object(app.symbol("door", 2, 2, 1), 3)
        door["legendLabel"] = "Dungeon Door"
        project["objects"].extend([trap, door])

        entries = app.legend_entries(project, project["objects"][0])

        self.assertEqual(entries[1], ("door", "Dungeon Door"))
        self.assertEqual(entries[2], ("trap", "Trap"))

    def test_report_lists_missing_custom_symbol_files(self) -> None:
        project = app.create_project()
        project["customSymbols"] = {"custom_skull": {"label": "Skull", "sourceType": "png", "path": "missing.png", "variants": []}}
        project["customSymbolGroups"] = [{"name": "Custom", "entries": [{"kind": "custom_skull", "label": "Skull"}]}]
        project["objects"].append(app.validate_object(app.symbol("custom_skull", 3, 3, 1), 2))

        report = app.campaign_report_markdown(project)

        self.assertIn("Missing Custom Symbol Files", report)
        self.assertIn("missing.png", report)

    def test_svg_symbol_style_overrides_render(self) -> None:
        project = app.create_project()
        styled = app.validate_object({**app.symbol("door", 3, 2, 1), "color": "#cc0000", "opacity": 0.5, "shadow": True, "outline": True}, 2)
        project["objects"].append(styled)

        parts = " ".join(app.svg_for_object(project, styled, 1))

        self.assertIn("#cc0000", parts)
        self.assertIn('opacity="0.500"', parts)
        self.assertIn("#000000", parts)

    def test_svg_basic_shapes(self) -> None:
        project = app.create_project()
        shapes = [
            app.validate_object(app.shape("rectangle", 1, 1, 2, 3), 1),
            app.validate_object(app.shape("circle", 1, 1, 2, 2), 2),
            app.validate_object(app.shape("polygon", 1, 1, 2, 2), 3),
            app.validate_object(app.shape("line", 1, 1, 0, 0, 3, 4), 4),
        ]
        shapes[0]["strokeColor"] = "#123456"
        shapes[0]["lineWidth"] = 0.5
        parts = [part for item in shapes for part in app.svg_for_object(project, item, 1)]

        self.assertTrue(any(part.startswith("<rect") for part in parts))
        self.assertTrue(any(part.startswith("<ellipse") for part in parts))
        self.assertTrue(any(part.startswith("<polygon") for part in parts))
        self.assertTrue(any(part.startswith("<line") for part in parts))
        self.assertTrue(any('stroke="#123456"' in part and 'stroke-width="9"' in part for part in parts))

    def test_export_frame_crops_project_to_named_bounds(self) -> None:
        project = app.create_project()
        inside = app.validate_object(app.rect("room", 2, 2, 3, 3), 2)
        outside = app.validate_object(app.rect("room", 20, 20, 3, 3), 3)
        project["objects"].extend([inside, outside])
        frame = {"id": "frame_1", "name": "Inset", "x": 1, "y": 1, "width": 6, "height": 6}

        framed = app.export_project_for_frame(project, frame)

        self.assertEqual(framed["settings"]["width"], 6)
        self.assertEqual(framed["settings"]["height"], 6)
        self.assertIn(inside["id"], {obj["id"] for obj in framed["objects"]})
        self.assertNotIn(outside["id"], {obj["id"] for obj in framed["objects"]})

    def test_vtt_scene_exports_walls_doors_and_lights(self) -> None:
        project = app.create_project()
        project["objects"].append(app.validate_object(app.rect("room", 1, 1, 4, 4), 2))
        project["objects"].append(app.validate_object(app.symbol("door", 3, 1, 1), 3))
        project["objects"].append(app.validate_object(app.symbol("light_source", 3, 3, 1), 4))

        foundry = app.foundry_scene_data(project)
        roll20 = app.roll20_page_data(project)

        self.assertGreaterEqual(len(foundry["walls"]), 5)
        self.assertEqual(len(foundry["lights"]), 1)
        self.assertTrue(any(item.get("door") for item in foundry["walls"]))
        self.assertEqual(len(roll20["doors"]), 1)
        self.assertEqual(len(roll20["lights"]), 1)

    def test_svg_shape_styles(self) -> None:
        project = app.create_project()
        styled = app.validate_object(
            {
                **app.shape("line", 1, 1, 0, 0, 4, 3),
                "lineStyle": "dot",
                "arrow": "end",
                "curve": True,
                "opacity": 0.4,
            },
            1,
        )

        parts = app.svg_for_object(project, styled, 1)

        self.assertTrue(parts[0].startswith("<path"))
        self.assertTrue(any("stroke-dasharray" in part for part in parts))
        self.assertTrue(any(part.startswith("<polygon") for part in parts))
        self.assertTrue(any('stroke-opacity="0.400"' in part for part in parts))

    def test_polygon_point_handles_include_insert_points(self) -> None:
        polygon = app.validate_object({"type": "shape", "kind": "polygon", "points": [[1, 1], [4, 1], [2, 5]]}, 1)
        names = [name for name, _x, _y in app.selection_handles(polygon)]

        self.assertIn("point:0", names)
        self.assertIn("insert:0", names)

    def test_rotate_shape_geometry_updates_line_and_polygon(self) -> None:
        line = app.validate_object(app.shape("line", 0, 0, 0, 0, 2, 0), 1)
        polygon = app.validate_object({"type": "shape", "kind": "rectangle", "x": 0, "y": 0, "width": 2, "height": 1}, 2)

        app.rotate_shape_geometry(line, 90)
        app.rotate_shape_geometry(polygon, 45)

        self.assertAlmostEqual(line["x"], 1.0)
        self.assertAlmostEqual(line["y"], -1.0)
        self.assertEqual(polygon["kind"], "polygon")
        self.assertEqual(len(polygon["points"]), 4)

    def test_align_and_distribute_selection(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        items = [
            app.validate_object(app.rect("room", 4, 2, 2, 2), 2),
            app.validate_object(app.rect("room", 8, 5, 2, 2), 3),
            app.validate_object(app.rect("room", 14, 9, 2, 2), 4),
        ]
        maker.project["objects"].extend(items)
        maker.selected_ids = {item["id"] for item in items}
        maker.selected_id = items[0]["id"]
        maker.history = []
        maker.future = []
        maker.redraw = lambda: None

        app.OSRMapMaker.align_selection(maker, "left")
        self.assertEqual({app.bounds(item)[0] for item in items}, {4})

        items[1]["x"] = 10
        items[2]["x"] = 20
        app.OSRMapMaker.distribute_selection(maker, "horizontal")
        centers = [app.object_center(item)[0] for item in items]
        self.assertAlmostEqual(centers[1] - centers[0], centers[2] - centers[1])

    def test_legend_uses_configured_cell_scale(self) -> None:
        project = app.create_project()
        project["settings"]["cellScale"] = 5
        entries = app.legend_entries(project, project["objects"][0])
        self.assertEqual(entries[0], ("cell", "5 ft. by 5 ft."))

    def test_command_snapshot_round_trip(self) -> None:
        before = app.create_project()
        after = copy.deepcopy(before)
        after["objects"].append(app.validate_object(app.rect("room", 1, 1, 2, 2), 2))
        command = app.HistoryCommand("Add room", before, after)
        self.assertEqual(command.before["objects"][0]["type"], "legend")
        self.assertEqual(command.after["objects"][-1]["type"], "room")

    def test_hit_detection_uses_topmost_visible_unlocked_object(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        bottom = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        top = app.validate_object(app.rect("room", 2, 2, 4, 4), 3)
        maker.project["objects"].extend([bottom, top])
        self.assertEqual(app.OSRMapMaker.find_hit(maker, 3, 3)["id"], top["id"])
        top["locked"] = True
        self.assertEqual(app.OSRMapMaker.find_hit(maker, 3, 3)["id"], bottom["id"])

    def test_undo_redo_restores_snapshots(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        before = app.create_project()
        after = copy.deepcopy(before)
        after["objects"].append(app.validate_object(app.rect("room", 1, 1, 2, 2), 2))
        maker.project = after
        maker.history = [app.HistoryCommand("Add room", before, after)]
        maker.future = []
        maker.selected_ids = set()
        maker.selected_id = None
        maker.status = type("Status", (), {"set": lambda self, value: None})()
        maker.mouse_grid = None
        maker.set_selection = lambda ids, primary=None: None
        maker.sync_vars = lambda: None
        maker.redraw = lambda: None
        app.OSRMapMaker.undo(maker)
        self.assertEqual(len(maker.project["objects"]), len(before["objects"]))
        app.OSRMapMaker.redo(maker)
        self.assertEqual(len(maker.project["objects"]), len(after["objects"]))


class ExportSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        if app.Image is None:
            self.skipTest("Pillow is not installed")
        self.project = app.create_project()
        self.project["objects"].append(app.validate_object(app.rect("room", 1, 1, 4, 3), 2))
        self.project["objects"].append(app.validate_object(app.symbol("door", 3, 1, 1), 3))
        self.project["objects"].append(app.validate_object(app.shape("circle", 6, 1, 2, 2), 4))
        self.project["objects"].append(app.validate_object(app.shape("rectangle", 9, 1, 2, 2), 5))
        self.project["objects"].append(app.validate_object(app.shape("polygon", 12, 1, 2, 2), 6))
        self.project["objects"].append(app.validate_object(app.shape("line", 15, 1, 0, 0, 18, 3), 7))

    def render(self):
        image = app.Image.new("RGBA", tuple(int(v) for v in app.canvas_size(self.project, 1)), self.project["settings"]["backgroundColor"])
        draw = app.ImageDraw.Draw(image)
        app.render_pillow(draw, self.project, 1, None, None)
        return image

    def test_png_export_smoke(self) -> None:
        image = self.render()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.png"
            image.save(path)
            self.assertGreater(path.stat().st_size, 0)

    def test_floor_overlaps_hide_internal_corridor_outline(self) -> None:
        project = app.create_project()
        settings = project["settings"]
        settings["width"] = 24
        settings["height"] = 18
        settings["cellSize"] = 24
        project["objects"] = [app.rect("room", 2, 2, 8, 6), app.diagonal_corridor(9, 4, 18, 9)]
        image = app.Image.new("RGBA", tuple(int(v) for v in app.canvas_size(project, 1, False)), settings["backgroundColor"])
        draw = app.ImageDraw.Draw(image)
        app.render_pillow(draw, project, 1, None, None, include_legend=False)
        self.assertEqual(image.getpixel((230, 97)), app.Image.new("RGBA", (1, 1), settings["floorColor"]).getpixel((0, 0)))

    def test_jpeg_export_smoke(self) -> None:
        image = app.flatten_rgba(self.render(), "#ffffff")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.jpg"
            image.save(path, quality=85)
            self.assertGreater(path.stat().st_size, 0)

    def test_webp_export_smoke(self) -> None:
        image = self.render()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.webp"
            image.save(path, quality=85)
            self.assertGreater(path.stat().st_size, 0)

    def test_svg_export_smoke_with_page_chrome(self) -> None:
        self.project["meta"]["title"] = "Test Dungeon"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.svg"
            app.save_svg(
                str(path),
                self.project,
                {
                    "scale": 1,
                    "include_legend": True,
                    "export_grid": True,
                    "audience": "GM",
                    "scope": "page",
                    "print_margin_cells": 1,
                    "title_area": True,
                },
            )
            svg = path.read_text(encoding="utf-8")
            self.assertIn("Test Dungeon", svg)
            self.assertIn("LEGEND", svg)
            self.assertIn('transform="translate(', svg)
            self.assertIn("data-object-id", svg)
            self.assertGreater(path.stat().st_size, 0)

    def test_pillow_symbol_coverage(self) -> None:
        image = app.Image.new("RGBA", (80, 80), (0, 0, 0, 0))
        draw = app.ImageDraw.Draw(image)
        for kind in app.SYMBOL_LABELS:
            app.draw_pillow_symbol(draw, kind, 40, 40, 24, "#000000", "#ffffff", 1)


class TkCoverageTests(unittest.TestCase):
    def test_tk_symbol_coverage_when_display_available(self) -> None:
        try:
            root = app.tk.Tk()
        except app.tk.TclError:
            self.skipTest("Tk display is not available")
        try:
            root.withdraw()
            canvas = app.tk.Canvas(root, width=80, height=80)
            canvas.pack()
            for kind in app.SYMBOL_LABELS:
                canvas.delete("all")
                app.draw_tk_symbol(canvas, kind, 40, 40, 24, "#000000", "#ffffff")
        finally:
            root.destroy()

    def test_project_restore_refreshes_custom_symbol_ui_state(self) -> None:
        try:
            maker = app.OSRMapMaker()
        except app.tk.TclError:
            self.skipTest("Tk display is not available")
        try:
            maker.withdraw()
            before = maker.project_snapshot()
            maker.project.setdefault("customSymbols", {})["custom_skull"] = {
                "label": "Skull",
                "sourceType": "png",
                "path": "missing.png",
                "tags": [],
                "variants": [],
            }
            maker.project.setdefault("customSymbolGroups", []).append(
                {"name": "Bones", "entries": [{"kind": "custom_skull", "label": "Skull"}]}
            )
            maker.active_symbol_group.set("Bones")
            maker.tool.set("custom_skull")
            maker.refresh_symbol_browser()
            after = maker.project_snapshot()
            maker.history = [app.HistoryCommand("Import custom symbol", before, after)]
            maker.future = []

            maker.undo()

            self.assertEqual(maker.active_symbol_group.get(), app.SYMBOL_GROUPS[0][0])
            self.assertEqual(maker.tool.get(), "select")
            self.assertNotIn("custom_skull", maker.tool_buttons)

            maker.redo()
            self.assertIn("Bones", maker.group_buttons)
            maker.select_symbol_group("Bones")
            self.assertIn("custom_skull", maker.tool_buttons)
        finally:
            maker.destroy()


if __name__ == "__main__":
    unittest.main()
