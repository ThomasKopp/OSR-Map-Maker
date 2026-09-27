from __future__ import annotations

import copy
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import osr_map_maker as app


class Variable:
    def __init__(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


def headless_maker() -> app.OSRMapMaker:
    maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
    maker.project = app.create_project()
    maker._project_revision = 1
    maker.current_layer_var = Variable("Rooms")
    maker.selected_ids = set()
    maker.selected_id = None
    maker.show_status = lambda _message: None
    maker.show_toast = lambda *_args, **_kwargs: None
    maker.redraw = lambda: None
    maker.sync_campaign_from_rooms = lambda: None
    maker.project_snapshot = lambda: copy.deepcopy(maker.project)
    maker.commit_history = lambda _before, _description: None
    maker.reveal_context_panel_by_title = lambda _title: None
    maker.rebuild_layers_panel = lambda: None
    maker.rebuild_contextual_tool_options = lambda: None
    return maker


class ContextSelectionTests(unittest.TestCase):
    def test_context_hit_list_keeps_order_and_includes_locked_items(self) -> None:
        maker = headless_maker()
        bottom = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        top = app.validate_object(app.rect("room", 2, 2, 4, 4), 3)
        top["locked"] = True
        maker.project["objects"].extend([bottom, top])

        self.assertEqual(
            [item["id"] for item in maker.find_hits(3, 3, include_locked=True)],
            [top["id"], bottom["id"]],
        )
        self.assertEqual(
            [item["id"] for item in maker.find_hits(3, 3)], [bottom["id"]]
        )
        room_layer = next(item for item in maker.project["layers"] if item["id"] == "rooms")
        room_layer["visible"] = False
        maker._project_revision += 1  # Matches the history commit after a layer edit.
        self.assertEqual(maker.find_hits(3, 3, include_locked=True), [])
        room_layer["visible"] = True

        maker.select_inspectable_object(top)

        self.assertEqual(maker.selected_ids, {top["id"]})
        self.assertEqual(maker.selected_id, top["id"])


class EditBlockTests(unittest.TestCase):
    def test_locked_active_layer_rejects_new_objects_without_mutation(self) -> None:
        maker = headless_maker()
        room_layer = next(item for item in maker.project["layers"] if item["id"] == "rooms")
        room_layer["locked"] = True
        before = copy.deepcopy(maker.project)

        maker.add_object(app.rect("room", 2, 2, 2, 2))

        self.assertEqual(maker.project, before)

    def test_locked_selected_object_rejects_inspector_changes(self) -> None:
        maker = headless_maker()
        room = app.validate_object(app.rect("room", 2, 2, 2, 2), 2)
        room["locked"] = True
        maker.project["objects"].append(room)
        maker.selected_ids = {room["id"]}
        maker.selected_id = room["id"]

        changed = maker.change_selected("width", "9")

        self.assertFalse(changed)
        self.assertEqual(room["width"], 2)


class InspectorScrollTests(unittest.TestCase):
    def test_wheel_routes_only_to_the_visible_panel_under_the_pointer(self) -> None:
        class Canvas:
            def __init__(self, left: int, top: int) -> None:
                self.left = left
                self.top = top
                self.scrolled: list[tuple[int, str]] = []

            def winfo_exists(self) -> bool:
                return True

            def winfo_ismapped(self) -> bool:
                return True

            def winfo_rootx(self) -> int:
                return self.left

            def winfo_rooty(self) -> int:
                return self.top

            def winfo_width(self) -> int:
                return 100

            def winfo_height(self) -> int:
                return 100

            def yview_scroll(self, amount: int, unit: str) -> None:
                self.scrolled.append((amount, unit))

        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        left = Canvas(10, 10)
        right = Canvas(150, 10)
        maker._panel_scroll_canvases = [left, right]
        event = type("Event", (), {"x_root": 170, "y_root": 30, "delta": -120})()

        self.assertEqual(maker.route_inspector_mousewheel(event), "break")
        self.assertEqual(left.scrolled, [])
        self.assertEqual(right.scrolled, [(1, "units")])


class NumericInspectorTests(unittest.TestCase):
    def test_decimal_comma_is_accepted_for_single_field(self) -> None:
        self.assertEqual(app.normalize_inspector_field_value("width", "1,5")[1], 1.5)
        self.assertEqual(app.normalize_inspector_field_value("width", "1.5")[1], 1.5)

    def test_relative_multi_edit_preserves_each_objects_starting_size(self) -> None:
        maker = headless_maker()
        first = app.validate_object(app.rect("room", 1, 1, 2, 2), 2)
        second = app.validate_object(app.rect("room", 5, 1, 5, 2), 3)
        maker.project["objects"].extend([first, second])
        maker.selected_ids = {first["id"], second["id"]}
        maker.selected_id = first["id"]

        maker.change_selection_field("width", "2", relative=True)

        self.assertEqual((first["width"], second["width"]), (4.0, 7.0))


class NavigationHistoryTests(unittest.TestCase):
    def test_back_and_forward_keep_navigation_out_of_document_history(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        first = {"mapId": "map-one", "zoom": 1.0, "xview": 0.1, "yview": 0.2}
        second = {"mapId": "map-two", "zoom": 1.5, "xview": 0.3, "yview": 0.4}
        maker.navigation_back_stack = [first]
        maker.navigation_forward_stack = []
        maker.navigation_location = lambda: second
        restored: list[dict[str, object]] = []
        maker.restore_navigation_location = lambda location: restored.append(location) or True
        maker.refresh_navigation_buttons = lambda: None
        maker.show_status = lambda _message: None

        maker.navigate_back()

        self.assertEqual(restored, [first])
        self.assertEqual(maker.navigation_back_stack, [])
        self.assertEqual(maker.navigation_forward_stack, [second])

        maker.navigation_location = lambda: first
        maker.navigate_forward()

        self.assertEqual(restored, [first, second])
        self.assertEqual(maker.navigation_back_stack, [first])
        self.assertEqual(maker.navigation_forward_stack, [])

    def test_missing_history_target_is_skipped(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        missing = {"mapId": "deleted", "zoom": 1.0, "xview": 0.0, "yview": 0.0}
        valid = {"mapId": "map-one", "zoom": 1.0, "xview": 0.2, "yview": 0.2}
        maker.navigation_back_stack = [valid, missing]
        maker.navigation_forward_stack = []
        maker.navigation_location = lambda: {"mapId": "map-two", "zoom": 1.0, "xview": 0.0, "yview": 0.0}
        restored: list[dict[str, object]] = []
        maker.restore_navigation_location = lambda location: (
            restored.append(location) or location is valid
        )
        maker.refresh_navigation_buttons = lambda: None
        maker.show_status = lambda _message: None

        maker.navigate_back()

        self.assertEqual(restored, [missing, valid])


class InspectorVisibilityTests(unittest.TestCase):
    def test_basic_filter_favorites_and_search_keep_relevant_fields_available(self) -> None:
        maker = headless_maker()
        maker.selection_property_search_var = Variable("")
        maker.selection_inspector_mode_var = Variable("Basic")
        fields = ["roomName", "width", "gmNotes", "description"]
        room = {"type": "room"}

        self.assertEqual(maker.visible_selection_fields(room, fields), ["roomName", "width"])
        maker.settings["selectionFieldFavorites"] = {"room": ["description"]}
        self.assertEqual(
            maker.visible_selection_fields(room, fields), ["roomName", "width", "description"]
        )
        maker.selection_property_search_var.set("gm")
        self.assertEqual(maker.visible_selection_fields(room, fields), ["gmNotes"])


class ProjectMapOverviewTests(unittest.TestCase):
    def test_map_search_considers_names_folders_and_chapters(self) -> None:
        maker = headless_maker()
        maker.map_search_var = Variable("crypt")
        maker.map_sort_var = Variable("Folder, name")
        maker.project["maps"] = [
            {"id": "map-one", "name": "Entry", "folder": "Chapter 1"},
            {"id": "map-two", "name": "Flooded Hall", "folder": "Crypt"},
            {"id": "map-three", "name": "Vault", "chapter": "Crypt"},
        ]

        self.assertEqual(
            [item["id"] for item in maker.filtered_project_maps()], ["map-two", "map-three"]
        )


class WorkspacePanelStateTests(unittest.TestCase):
    def test_pinned_panel_survives_workspace_changes_and_manual_hide_blocks_auto_open(self) -> None:
        maker = headless_maker()
        maker.workspace_var = Variable("Drawing")
        maker.toolbar_visible_var = Variable(True)
        maker.minimap_visible_var = Variable(True)
        maker.minimap_docked_var = Variable(False)
        maker.color_picker_visible_var = Variable(False)
        maker.dock_panels = {}
        maker.dock_panel_content = {}
        maker.dock_panel_grips = {}
        maker.dock_panel_rows = {}
        maker.dock_panel_buttons = {}
        maker.dock_panel_visible_vars = {"history": Variable(True)}
        maker.compact_mode_var = Variable(False)
        maker.toggle_toolbar_visibility = lambda: None
        maker.apply_minimap_visibility = lambda: None
        maker.toggle_color_picker_panel = lambda: None
        maker.redraw_minimap = lambda **_kwargs: None
        maker.after_idle = lambda callback: callback()
        maker.focus_workspace_target = lambda _name: None

        maker.toggle_dock_panel_pinned("history")
        maker.apply_workspace_preset("Symbols")
        self.assertTrue(maker.panel_state("history")["visible"])
        self.assertTrue(maker.panel_state("history")["pinned"])

        maker.toggle_dock_panel_pinned("history")
        maker.set_dock_panel_visible("history", False)
        maker.reveal_context_panel_by_title("History")
        self.assertFalse(maker.panel_state("history")["visible"])
        self.assertTrue(maker.panel_state("history")["manualHidden"])


class VisibilitySummaryTests(unittest.TestCase):
    def test_summary_uses_rendering_rules_and_names_the_exclusion(self) -> None:
        project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 2, 2), 1)
        project["objects"].append(room)

        summary = app.object_visibility_summary(project, room)
        self.assertTrue(summary["editor"][0])
        self.assertTrue(summary["gm"][0])
        self.assertTrue(summary["player"][0])

        room["playerVisible"] = False
        self.assertFalse(app.object_visibility_summary(project, room)["player"][0])
        self.assertIn("Player visibility", app.object_visibility_summary(project, room)["player"][1])

        room_layer = next(layer for layer in project["layers"] if layer["id"] == "rooms")
        room_layer["visible"] = False
        hidden = app.object_visibility_summary(project, room)
        self.assertFalse(hidden["editor"][0])
        self.assertIn("hidden", hidden["editor"][1])


class SmallWindowLayoutTests(unittest.TestCase):
    def test_narrow_command_bar_keeps_primary_actions_and_uses_more_menu(self) -> None:
        self.assertTrue(app.command_bar_uses_overflow(1050))
        self.assertTrue(app.command_bar_uses_overflow(1179))
        self.assertFalse(app.command_bar_uses_overflow(1180))


class GlobalProjectSearchTests(unittest.TestCase):
    def test_project_scope_finds_objects_on_inactive_maps_without_gm_note_leaks(self) -> None:
        maker = headless_maker()
        active = maker.active_map_record()
        active["name"] = "Upper level"
        active["folder"] = "Keep"
        active_room = app.validate_object(app.rect("room", 1, 1, 2, 2), 1)
        active_room["roomName"] = "Guard room"
        maker.project["objects"] = [active_room]
        inactive_room = app.validate_object(app.rect("room", 3, 3, 2, 2), 2)
        inactive_room["roomName"] = "Guard room"
        inactive_room["gmNotes"] = "Only the GM should find this phrase"
        inactive = app.create_map_record(
            "Lower level", maker.settings, maker.project["layers"], [inactive_room]
        )
        inactive["folder"] = "Crypt"
        maker.project["maps"].append(inactive)
        maker.project["settings"]["sessionMode"] = "Player"

        items = maker.global_search_items("Whole project")
        rooms = [label for kind, label, _action in items if kind == "Object" and "Guard room" in label]
        self.assertEqual(len(rooms), 2)
        self.assertTrue(any("Upper level · Keep" in label for label in rooms))
        self.assertTrue(any("Lower level · Crypt" in label for label in rooms))
        self.assertFalse(any("Only the GM" in label for _kind, label, _action in items))


class ToolPresetTests(unittest.TestCase):
    def test_presets_validate_persist_and_apply_without_changing_existing_objects(self) -> None:
        maker = headless_maker()
        maker.tool = Variable("shape_rect")
        maker.settings["defaultShapeLineWidth"] = 0.25
        maker.settings["defaultShapeStrokeColor"] = "#123456"
        existing = app.validate_object(app.shape("rectangle", 1, 1, 2, 2), 1)
        maker.project["objects"] = [existing]
        before_object = copy.deepcopy(existing)

        self.assertTrue(maker.save_tool_preset("Fine line", "shape_rect"))
        persisted = app.validate_project(copy.deepcopy(maker.project))
        self.assertEqual(persisted["toolPresets"][0]["name"], "Fine line")
        maker.project["toolPresets"] = persisted["toolPresets"]
        maker.settings["defaultShapeLineWidth"] = 0.8
        maker.rebuild_contextual_tool_options = lambda: None
        maker.refresh_toolbar = lambda: None

        self.assertTrue(maker.apply_tool_preset(0))
        self.assertEqual(maker.settings["defaultShapeLineWidth"], 0.25)
        self.assertEqual(existing, before_object)


class UnderlayCalibrationTests(unittest.TestCase):
    def test_two_points_scale_without_mutating_the_original_underlay(self) -> None:
        underlay = {"id": "scan", "name": "Scan", "x": 2, "y": 3, "width": 20, "height": 10}
        calibrated = app.calibrate_underlay_two_points(
            underlay, (0.0, 0.0), (1.0, 0.0), 5
        )
        self.assertEqual(underlay["width"], 20)
        self.assertEqual(calibrated["width"], 5)
        self.assertEqual(calibrated["height"], 2.5)
        self.assertEqual((calibrated["x"], calibrated["y"]), (2, 3))


class AssetRepairSafetyTests(unittest.TestCase):
    def test_duplicate_filenames_are_left_for_explicit_assignment(self) -> None:
        project = app.create_project()
        project["customSymbols"] = {
            "custom_key": {"label": "Key", "path": "key.png", "variants": []}
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("first", "second"):
                folder = root / name
                folder.mkdir()
                (folder / "key.png").write_bytes(b"png")
            self.assertEqual(app.repair_missing_custom_symbols_from_directory(project, root), 0)

    def test_explicit_choices_repair_a_symbol_and_underlay_together(self) -> None:
        project = app.create_project()
        project["customSymbols"] = {"custom_key": {"label": "Key", "path": "key.png", "variants": []}}
        project["underlays"] = [{"id": "scan", "name": "Scan", "path": "scan.png"}]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            key, scan = root / "key.png", root / "scan.png"
            key.write_bytes(b"png")
            scan.write_bytes(b"png")
            items = app.missing_asset_records(project)
            choices = {items[0]["target"]: key, items[1]["target"]: scan}
            self.assertEqual(app.apply_asset_repair_choices(project, choices), 2)
        self.assertEqual(project["customSymbols"]["custom_key"]["path"], str(key))
        self.assertEqual(project["underlays"][0]["path"], str(scan))


class ExportJobTests(unittest.TestCase):
    def test_named_job_survives_project_validation_and_keeps_profiles(self) -> None:
        project = app.create_project()
        jobs = app.default_batch_export_jobs(2, True)
        project["exportJobs"] = [{
            "name": "Release", "folder": "exports", "allMaps": True,
            "policy": "Rename", "jobs": jobs,
        }]
        validated = app.validate_project(project)
        job = validated["exportJobs"][0]
        self.assertEqual(job["name"], "Release")
        self.assertTrue(job["allMaps"])
        self.assertEqual([label for label, _options in job["jobs"]], [label for label, _options in jobs])


class FantasyGroundsXmlTests(unittest.TestCase):
    def test_xml_sidecar_uses_the_native_image_los_structure(self) -> None:
        project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 2, 2), 2)
        project["objects"].append(room)
        root = ET.fromstring(app.fantasy_grounds_xml(project))
        self.assertEqual(root.tag, "root")
        self.assertEqual(root.findtext("grid"), "on")
        cell = project["settings"]["cellSize"]
        self.assertEqual(root.findtext("gridsize"), f"{cell},{cell}")
        occluders = root.findall("occluders/occluder")
        self.assertEqual(len(occluders), 1)
        self.assertEqual(occluders[0].findtext("id"), "1")
        self.assertEqual(len(occluders[0].findtext("points", "").split(",")), 10)
