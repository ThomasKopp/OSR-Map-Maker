from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

import osr_map_maker as app


class ProjectModelTests(unittest.TestCase):
    def test_validate_project_adds_missing_fields(self) -> None:
        project = {
            "objects": [{"type": "room", "x": 1, "y": 2, "width": 3, "height": 4}]
        }
        validated = app.validate_project(project)
        self.assertEqual(validated["schemaVersion"], app.CURRENT_SCHEMA_VERSION)
        self.assertIn("layers", validated)
        self.assertIn("exportProfiles", validated)
        self.assertIn("exportFrames", validated)
        self.assertIn("colorPalettes", validated)
        self.assertIn("symbolColorPalettes", validated)
        self.assertIn("symbolAliases", validated)
        self.assertIn("symbolVttRoles", validated)
        self.assertIn("legendCategories", validated)
        self.assertIn("assetLibrary", validated)
        self.assertIn("symbolPackManifests", validated)
        self.assertIn("reviewComments", validated)
        self.assertIn("changeLog", validated)
        self.assertIn("snapshots", validated)
        self.assertIn("shortcuts", validated["settings"])
        self.assertTrue(validated["settings"]["showTooltips"])
        self.assertEqual(validated["settings"]["cellScale"], 10.0)
        self.assertTrue(validated["objects"][0]["playerVisible"])
        self.assertEqual(validated["objects"][0]["roomStatus"], "undiscovered")
        self.assertIn("encounterTable", validated["campaign"])

    def test_validate_settings_preserves_tooltip_preference(self) -> None:
        self.assertTrue(app.validate_settings({})["showTooltips"])
        self.assertFalse(app.validate_settings({"showTooltips": False})["showTooltips"])

    def test_compressed_project_file_round_trips(self) -> None:
        project = app.create_project()
        project["meta"]["title"] = "Compressed Test"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.osrmapz"
            app.write_project_data(path, project)
            loaded = app.read_project_file(path)

        self.assertEqual(loaded["meta"]["title"], "Compressed Test")
        self.assertEqual(
            app.compressed_project_path(Path("map.osrmap.json")),
            Path("map.osrmapz"),
        )

    def test_embedded_custom_symbol_satisfies_missing_file_validation(self) -> None:
        project = app.create_project()
        project["customSymbols"] = {
            "custom_skull": {
                "label": "Skull",
                "sourceType": "png",
                "path": "missing.png",
                "embeddedData": "aGVsbG8=",
            }
        }

        self.assertEqual(app.missing_custom_symbol_files(project), [])
        validated = app.validate_project(project)
        self.assertFalse(
            any(
                "Custom symbol file missing" in item
                for item in validated["validationWarnings"]
            )
        )

    def test_repair_and_remove_missing_custom_symbols(self) -> None:
        project = app.create_project()
        project["objects"].append(app.symbol("custom_skull", 1, 1, 1))
        project["customSymbols"] = {
            "custom_skull": {
                "label": "Skull",
                "sourceType": "png",
                "path": "skull.png",
                "variants": [],
            }
        }
        project["customSymbolGroups"] = [
            {"name": "Custom", "entries": [{"kind": "custom_skull", "label": "Skull"}]}
        ]
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "nested" / "skull.png"
            asset.parent.mkdir()
            asset.write_bytes(b"fake")

            repaired = app.repair_missing_custom_symbols_from_directory(
                project, Path(tmp)
            )

        self.assertEqual(repaired, 1)
        self.assertTrue(
            project["customSymbols"]["custom_skull"]["path"].endswith("skull.png")
        )
        project["customSymbols"]["custom_skull"]["path"] = "missing.png"
        removed = app.remove_missing_custom_symbols(project)
        self.assertGreaterEqual(removed, 1)
        self.assertNotIn("custom_skull", project["customSymbols"])
        self.assertFalse(
            any(obj.get("kind") == "custom_skull" for obj in project["objects"])
        )

    def test_validate_project_collects_warnings_and_keeps_valid_objects(self) -> None:
        project = {
            "objects": [
                {"type": "room", "x": 1, "y": 1, "width": 2, "height": 2},
                {"type": "unknown", "x": 0, "y": 0},
            ]
        }
        validated = app.validate_project(project)

        self.assertTrue(
            any("unknown" in warning for warning in validated["validationWarnings"])
        )
        self.assertTrue(any(obj["type"] == "room" for obj in validated["objects"]))

    def test_export_profiles_frames_palettes_and_layer_opacity_validate(self) -> None:
        project = app.create_project()
        project["layers"][1]["opacity"] = 0.35
        project["exportProfiles"] = [
            {
                "name": "My Player",
                "format": "jpg",
                "scope": "frame",
                "audience": "Player",
                "is_default": True,
                "filename_template": "{project}_{map}_{profile}",
            }
        ]
        project["exportFrames"] = [
            {
                "name": "Boss Room",
                "preset": "A4 landscape",
                "x": 2,
                "y": 3,
                "width": 8,
                "height": 6,
            }
        ]
        project["colorPalettes"] = [
            {
                "name": "Night",
                "colors": {"backgroundColor": "#101010", "gridColor": "#eeeeee"},
            }
        ]

        validated = app.validate_project(project)

        self.assertAlmostEqual(validated["layers"][1]["opacity"], 0.35)
        profile = next(
            item for item in validated["exportProfiles"] if item["name"] == "My Player"
        )
        self.assertEqual(profile["format"], "jpeg")
        self.assertTrue(profile["is_default"])
        self.assertEqual(profile["filename_template"], "{project}_{map}_{profile}")
        self.assertEqual(
            sum(1 for item in validated["exportProfiles"] if item.get("is_default")), 1
        )
        self.assertEqual(validated["exportFrames"][0]["name"], "Boss Room")
        self.assertEqual(validated["exportFrames"][0]["preset"], "A4 landscape")
        self.assertEqual(
            validated["colorPalettes"][0]["colors"]["backgroundColor"], "#101010"
        )

    def test_symbol_color_palettes_validate_built_in_symbols_only(self) -> None:
        palettes = app.validate_symbol_color_palettes(
            [
                {
                    "name": "Door Colors",
                    "symbols": {
                        "door": {"color": "#ff0000"},
                        "custom_skull": {"color": "#00ff00"},
                    },
                }
            ]
        )

        self.assertEqual(palettes[0]["symbols"]["door"]["color"], "#ff0000")
        self.assertNotIn("custom_skull", palettes[0]["symbols"])

    def test_map_structure_zone_hierarchy_and_overlay_validate(self) -> None:
        project = app.create_project()
        project["settings"]["floorOverlayMapId"] = "missing"
        project["settings"]["floorOverlayOpacity"] = 2
        project["zones"] = [
            {
                "id": "zone_a",
                "name": "Temple",
                "parentId": "root",
                "scale": 30,
                "scaleUnit": "ft.",
                "x": 1,
                "y": 2,
                "width": 3,
                "height": 4,
            }
        ]
        project["maps"][0]["folder"] = "Dungeon"
        project["maps"][0]["chapter"] = "Krypta"
        project["maps"][0]["template"] = "Dungeon"

        validated = app.validate_project(project)

        self.assertEqual(validated["settings"]["floorOverlayOpacity"], 1.0)
        self.assertEqual(validated["zones"][0]["parentId"], "root")
        self.assertEqual(validated["zones"][0]["scale"], 30)
        self.assertEqual(validated["maps"][0]["folder"], "Dungeon")
        self.assertEqual(validated["maps"][0]["chapter"], "Krypta")

    def test_transform_objects_about_custom_pivot_scales_rotates_and_mirrors(
        self,
    ) -> None:
        room = app.rect("room", 1, 1, 2, 2)
        line = app.shape("line", 2, 1, 0, 0, 4, 1)

        transformed = app.transform_objects_about_pivot(
            [room, line], (1, 1), scale_x=2, scale_y=1, rotation=90
        )

        room_box = app.bounds(transformed[0])
        self.assertAlmostEqual(room_box[0], -1)
        self.assertAlmostEqual(room_box[1], 1)
        self.assertAlmostEqual(room_box[2], 2)
        self.assertAlmostEqual(room_box[3], 4)
        self.assertAlmostEqual(transformed[1]["x"], 1)
        self.assertAlmostEqual(transformed[1]["y"], 3)

    def test_exact_floor_merge_groups_and_shared_edges(self) -> None:
        left = app.rect("room", 0, 0, 4, 4)
        right = app.rect("corridor", 4, 0, 2, 4)

        groups = app.floor_rect_exact_merge_groups([left, right])

        self.assertEqual(len(groups), 1)
        merge_id = "floor_test"
        left["floorMergeGroup"] = merge_id
        right["floorMergeGroup"] = merge_id
        edges = app.shared_exact_floor_edges([left, right])
        self.assertEqual(edges[0][:4], (4, 0, 4, 4))

    def test_export_filename_template_formats_safe_names(self) -> None:
        filename = app.export_filename_from_template(
            "The Lost Vault",
            "Level 2 / Shrine",
            "Foundry Player",
            {
                "format": "jpeg",
                "audience": "Player",
                "scope": "frame",
                "filename_template": "{project}_{map}_{audience}_{profile}_{scope}",
            },
        )

        self.assertEqual(
            filename, "the-lost-vault-level-2-shrine-player-foundry-player-frame.jpg"
        )

    def test_autosave_candidates_sort_latest_version_first_and_prune(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "autosave.osrmap.json"
            versions = root / "autosaves"
            versions.mkdir()
            old = versions / "autosave-20260101-010101-a.osrmap.json"
            mid = versions / "autosave-20260101-020202-b.osrmap.json"
            latest = versions / "autosave-20260101-030303-c.osrmap.json"
            for index, path in enumerate([old, current, mid, latest], start=1):
                path.write_text("{}", encoding="utf-8")
                timestamp = 1_700_000_000 + index
                path.touch()
                os.utime(path, (timestamp, timestamp))

            candidates = app.autosave_candidates(current, versions)

            self.assertEqual(candidates[0], latest)
            self.assertIn(current, candidates)

            app.prune_autosave_versions(versions, keep=2)

            self.assertEqual(
                {path.name for path in versions.glob("*.json")}, {mid.name, latest.name}
            )

    def test_autosave_recovery_metadata_counts_maps_and_objects(self) -> None:
        current = app.create_project()
        current["meta"]["title"] = "Current"
        autosave = app.create_project()
        autosave["meta"]["title"] = "Recovered"
        autosave["meta"]["updatedAt"] = "2026-01-02T03:04:05+00:00"
        autosave["maps"].append(
            app.create_map_record(
                "Second",
                autosave["settings"],
                autosave["layers"],
                [app.rect("room", 1, 1, 2, 2)],
            )
        )

        metadata = app.autosave_recovery_metadata(current, autosave, 1760000000)

        self.assertEqual(metadata["currentTitle"], "Current")
        self.assertEqual(metadata["autosaveTitle"], "Recovered")
        self.assertEqual(metadata["autosaveUpdated"], "2026-01-02T03:04:05+00:00")
        self.assertEqual(metadata["autosaveMaps"], 2)
        self.assertGreaterEqual(metadata["autosaveObjects"], 2)

    def test_inspector_field_normalization_is_gui_independent(self) -> None:
        def color_ok(value: str) -> bool:
            return value.startswith("#") and len(value) == 7

        self.assertEqual(
            app.normalize_inspector_field_value("export", "nein")[1], False
        )
        self.assertEqual(
            app.normalize_inspector_field_value(
                "manualEntries", "Torch\nRope; Chalk"
            )[1],
            ["Torch", "Rope", "Chalk"],
        )
        self.assertEqual(app.normalize_inspector_field_value("opacity", "2")[1], 2.0)
        self.assertTrue(
            app.normalize_inspector_field_value("color", "#123456", color_ok)[0]
        )
        self.assertFalse(
            app.normalize_inspector_field_value("color", "not-a-color", color_ok)[0]
        )

    def test_shortcut_presets_are_complete_and_conflict_free(self) -> None:
        for name in app.SHORTCUT_PRESETS:
            preset = app.shortcut_preset(name)
            self.assertEqual(set(preset), set(app.DEFAULT_SHORTCUTS))
            assigned = [value.lower() for value in preset.values() if value]
            self.assertEqual(len(assigned), len(set(assigned)), name)

    def test_review_fields_validate_diff_and_markdown(self) -> None:
        before = app.create_project()
        after = copy.deepcopy(before)
        after["objects"].append(app.validate_object(app.rect("room", 1, 1, 3, 3), 2))
        after["reviewComments"] = [
            {"text": "Check this room", "targetId": after["objects"][-1]["id"]}
        ]
        after["changeLog"] = [{"description": "Added room"}]
        after["snapshots"] = [
            {"name": "Baseline", "project": app.snapshot_project_payload(before)}
        ]

        validated = app.validate_project(after)
        diff = app.project_diff_lines(before, validated)
        report = app.review_export_markdown(validated, before)

        self.assertTrue(any("room" in line for line in diff))
        self.assertEqual(validated["reviewComments"][0]["text"], "Check this room")
        self.assertEqual(validated["snapshots"][0]["name"], "Baseline")
        self.assertIn("Differences Since Snapshot", report)
        self.assertIn("Check this room", report)
        self.assertIn("Added room", report)

    def test_commit_history_records_change_log_entry(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        before = app.create_project()
        after = copy.deepcopy(before)
        after["objects"].append(app.validate_object(app.rect("room", 1, 1, 2, 2), 2))
        maker.project = after
        maker.history = []
        maker.future = []
        maker.refresh_history_panel = lambda: None
        maker.sync_campaign_from_rooms = lambda: None
        maker.sync_active_map_storage = lambda: None

        app.OSRMapMaker.commit_history(maker, before, "Add test room")

        self.assertEqual(maker.history[-1].description, "Add test room")
        self.assertEqual(maker.project["changeLog"][-1]["description"], "Add test room")

    def test_validate_project_migrates_legacy_symbols(self) -> None:
        project = {
            "schemaVersion": 1,
            "settings": {},
            "objects": [
                {"type": "symbol", "kind": "secret", "x": 2, "y": 3, "size": 1}
            ],
        }
        validated = app.validate_project(project)
        self.assertEqual(validated["objects"][0]["kind"], "secret_door")

    def test_validate_project_preserves_custom_symbol_keys(self) -> None:
        project = app.create_project()
        project["customSymbols"] = {
            "custom_skull": {
                "label": "Skull",
                "sourceType": "png",
                "path": "missing.png",
            }
        }
        project["customSymbolGroups"] = [
            {"name": "Custom", "entries": [{"kind": "custom_skull", "label": "Skull"}]}
        ]
        project["objects"].append(app.symbol("custom_skull", 2, 3, 1))

        validated = app.validate_project(project)

        self.assertIn("custom_skull", validated["customSymbols"])
        self.assertEqual(
            validated["customSymbolGroups"][0]["entries"][0]["kind"], "custom_skull"
        )
        self.assertEqual(validated["objects"][-1]["kind"], "custom_skull")
        self.assertTrue(app.is_custom_symbol(validated, "custom_skull"))

    def test_symbol_metadata_search_variants_and_style_validation(self) -> None:
        project = app.create_project()
        self.assertIn("door", app.symbol_tags(project, "door"))
        self.assertIn(
            "open_door",
            [item["id"] for item in app.symbol_variant_options(project, "door")],
        )
        self.assertIn("barred", app.symbol_search_blob(project, "door", "Door"))
        self.assertIn(
            "one way secret door",
            app.symbol_search_blob(
                project, "one_way_secret_door", "One Way Secret Door"
            ),
        )
        self.assertEqual(app.symbol_vtt_role(project, "light_source"), "Light")

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

    def test_symbol_vtt_roles_legend_categories_and_asset_library_validate(
        self,
    ) -> None:
        project = app.create_project()
        project["symbolAliases"] = {"one_way_secret_door": ["private entrance"]}
        project["symbolVttRoles"] = {"hazard_marker": "Note", "lever": "Door"}
        project["legendCategories"] = {"door": "Entrances"}
        project["assetLibrary"] = [
            {"id": "my_frame", "name": "My Frame", "type": "frame", "tags": ["print"]}
        ]
        validated = app.validate_project(project)

        self.assertIn(
            "private entrance",
            app.symbol_search_blob(
                validated, "one_way_secret_door", "One Way Secret Door"
            ),
        )
        self.assertEqual(app.symbol_vtt_role(validated, "lever"), "Door")
        self.assertEqual(app.symbol_group_name(validated, "door"), "Entrances")
        self.assertTrue(
            any(asset["id"] == "custom_my_frame" for asset in validated["assetLibrary"])
        )

    def test_symbol_set_import_export_merges_custom_symbols(self) -> None:
        source = app.create_project()
        source["meta"]["title"] = "Bones Pack"
        source["meta"]["author"] = "Mapper"
        source["customSymbols"] = {
            "custom_skull": {
                "label": "Skull",
                "sourceType": "png",
                "path": "missing.png",
                "tags": ["undead"],
                "variants": [
                    {
                        "id": "custom_skull_red",
                        "label": "Red Skull",
                        "sourceType": "png",
                        "path": "missing-red.png",
                    }
                ],
            }
        }
        source["customSymbolGroups"] = [
            {"name": "Bones", "entries": [{"kind": "custom_skull", "label": "Skull"}]}
        ]

        target = app.create_project()
        data = app.export_symbol_set_data(source)
        count = app.import_symbol_set_data(target, data)

        self.assertEqual(data["manifest"]["name"], "Bones Pack")
        self.assertEqual(data["manifest"]["author"], "Mapper")
        self.assertEqual(count, 1)
        self.assertIn("custom_skull", target["customSymbols"])
        self.assertEqual(
            target["customSymbols"]["custom_skull"]["variants"][0]["id"],
            "custom_skull_red",
        )
        self.assertEqual(target["customSymbolGroups"][-1]["name"], "Bones")
        self.assertEqual(target["symbolPackManifests"][0]["name"], "Bones Pack")

    def test_validate_project_keeps_active_map_and_extra_maps(self) -> None:
        project = app.create_project()
        active_symbol = app.validate_object(app.symbol("stairs", 2, 3, 1), 2)
        project["objects"].append(active_symbol)
        second_settings = app.validate_settings(
            {**project["settings"], "width": 24, "height": 18}
        )
        second_map = app.create_map_record(
            "Lower Level",
            second_settings,
            project["layers"],
            [app.legend_obj(second_settings)],
            {"rooms": []},
        )
        project["maps"].append(second_map)

        validated = app.validate_project(project)

        self.assertEqual(len(validated["maps"]), 2)
        self.assertEqual(validated["objects"][-1]["kind"], "stairs")
        active_record = next(
            item for item in validated["maps"] if item["id"] == validated["activeMapId"]
        )
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

    def test_handout_export_hides_gm_only_information(self) -> None:
        project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        room["roomName"] = "Shrine"
        room["readAloud"] = "You see a cracked altar."
        room["handoutText"] = "A public inscription."
        room["secrets"] = "The idol is cursed."
        room["gmNotes"] = "Move the ambush here."
        project["objects"].append(room)

        handout = app.handout_export_markdown(project)

        self.assertIn("A public inscription.", handout)
        self.assertIn("cracked altar", handout)
        self.assertNotIn("cursed", handout)
        self.assertNotIn("ambush", handout)

    def test_campaign_audit_reports_todos_missing_numbers_and_unused_symbol_notes(
        self,
    ) -> None:
        project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        room["roomName"] = "Unnumbered Room"
        room["description"] = "TODO stock this room"
        note = app.validate_object(app.symbol("clue_marker", 20, 20, 1), 3)
        note["gmNotes"] = "Unused clue"
        project["objects"].extend([room, note])

        audit = app.campaign_audit(project)
        report = app.campaign_report_markdown(project)

        self.assertIn("Unnumbered Room", audit["missing_numbers"])
        self.assertTrue(audit["todos"])
        self.assertTrue(audit["unused_symbol_notes"])
        self.assertIn("Campaign Audit", report)
        self.assertIn("Missing Room Numbers", report)

    def test_room_number_prefix_suffix_relationships_and_tables_validate(self) -> None:
        project = app.create_project()
        project["settings"]["numberPrefix"] = "R-"
        project["settings"]["numberArea"] = "A"
        project["settings"]["numberSuffix"] = "b"
        room = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        room["relationshipFaction"] = "Moth cult"
        room["relationshipKey"] = "bronze key"
        project["objects"].append(room)
        project["campaign"]["lootTable"] = "1 coins"
        project["campaign"]["generatorHistory"] = [
            {"tool": "dungeon", "seed": "123", "scope": "Map", "summary": "Generated"}
        ]

        validated = app.validate_project(project)
        report = app.campaign_report_markdown(validated)

        self.assertEqual(app.room_number_token(validated["settings"], 7), "R-A7b")
        self.assertIn("Moth cult", report)
        self.assertIn("Map Loot Table", report)
        self.assertIn("Procedural History", report)

    def test_roll_table_import_and_seeded_generators_are_reproducible(self) -> None:
        settings = app.validate_settings({"width": 40, "height": 30})
        first = app.generated_dungeon_objects(
            settings, app.parse_dungeon_options("4; 4-6x4-6; 1; 1"), "seed-1", "mine"
        )
        second = app.generated_dungeon_objects(
            settings, app.parse_dungeon_options("4; 4-6x4-6; 1; 1"), "seed-1", "mine"
        )
        table = app.import_roll_table_text("d6,result\n1,goblins\n2,ooze")

        self.assertEqual(
            [(obj["type"], obj.get("x"), obj.get("y")) for obj in first],
            [(obj["type"], obj.get("x"), obj.get("y")) for obj in second],
        )
        self.assertIn("1 goblins", table)

    def test_vtt_fantasy_grounds_and_inferred_lights(self) -> None:
        project = app.create_project()
        room = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        room["roomName"] = "Torch Hall"
        room["description"] = "A torch burns here."
        project["objects"].append(room)

        foundry = app.foundry_scene_data(project)
        fg = app.fantasy_grounds_data(project)

        self.assertTrue(any(light.get("inferred") for light in foundry["lights"]))
        self.assertEqual(fg["format"], "OSR Map Maker Fantasy Grounds Reference")
        self.assertEqual(fg["rooms"][0]["name"], "Torch Hall")

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

        doors = app.auto_door_symbols(
            objects, ["normal", "secret", "locked", "trapdoor"]
        )

        self.assertEqual(
            [door["kind"] for door in doors[:4]],
            ["door", "secret_door", "locked_door", "trap_floor"],
        )

    def test_parse_dungeon_and_keyword_specs(self) -> None:
        options = app.parse_dungeon_options("12; 3-8x2-6; 4; 5")
        self.assertEqual(options["density"], 12)
        self.assertEqual(
            (options["min_w"], options["max_w"], options["min_h"], options["max_h"]),
            (3, 8, 2, 6),
        )
        self.assertEqual(options["loops"], 4)
        self.assertEqual(options["dead_ends"], 5)
        self.assertEqual(
            app.parse_keyword_spec("temple; cult; lava"), ("temple", "cult", "lava")
        )

    def test_player_export_hides_numbers_linked_to_hidden_rooms(self) -> None:
        project = app.create_project()
        hidden_room = app.validate_object(app.rect("room", 1, 1, 3, 3), 2)
        hidden_room["playerVisible"] = False
        room_number = app.text_obj("1", 2, 2, 1)
        room_number["textRole"] = "number"
        room_number["roomId"] = hidden_room["id"]
        project["objects"].extend([hidden_room, app.validate_object(room_number, 3)])
        project["settings"]["exportAudience"] = "Player"

        rendered_ids = {
            obj["id"]
            for obj in project["objects"]
            if app.should_render_object(project, obj, for_export=True)
        }

        self.assertNotIn(hidden_room["id"], rendered_ids)
        self.assertNotIn(room_number["id"], rendered_ids)

    def test_bounds_for_shapes(self) -> None:
        self.assertEqual(
            app.bounds({"type": "room", "x": 1, "y": 2, "width": 3, "height": 4}),
            (1, 2, 3, 4),
        )
        self.assertEqual(
            app.bounds({"type": "symbol", "x": 5, "y": 6, "size": 2}), (4, 5, 2, 2)
        )
        self.assertEqual(
            app.bounds(
                {
                    "type": "diagonal_corridor",
                    "x": 1,
                    "y": 1,
                    "x2": 4,
                    "y2": 5,
                    "width": 1,
                }
            ),
            (0.5, 0.5, 4, 5),
        )
        self.assertEqual(
            app.bounds(
                {
                    "type": "shape",
                    "kind": "rectangle",
                    "x": 1,
                    "y": 2,
                    "width": 3,
                    "height": 4,
                }
            ),
            (1, 2, 3, 4),
        )
        self.assertEqual(
            app.bounds(
                {
                    "type": "shape",
                    "kind": "line",
                    "x": 1,
                    "y": 1,
                    "x2": 4,
                    "y2": 5,
                    "lineWidth": 0.2,
                }
            ),
            (0.85, 0.85, 3.3, 4.3),
        )
        self.assertEqual(
            app.bounds(
                {
                    "type": "shape",
                    "kind": "polygon",
                    "points": [{"x": 1, "y": 1}, {"x": 4, "y": 1}, {"x": 2, "y": 5}],
                    "lineWidth": 0.2,
                }
            ),
            (0.9, 0.9, 3.2, 4.2),
        )

    def test_validate_shape_objects(self) -> None:
        rectangle = app.validate_object(
            {**app.shape("rectangle", 1, 2, 3, 4), "lineStyle": "dash", "opacity": 0.5},
            1,
        )
        polygon = app.validate_object(
            {"type": "shape", "kind": "polygon", "points": [[1, 2], [4, 2], [2, 5]]}, 2
        )
        line = app.validate_object(
            {**app.shape("line", 1, 2, 0, 0, 4, 6), "arrow": "both", "curve": True}, 3
        )

        self.assertEqual(rectangle["layer"], "shapes")
        self.assertEqual(rectangle["lineStyle"], "dash")
        self.assertEqual(rectangle["opacity"], 0.5)
        self.assertEqual(len(polygon["points"]), 3)
        self.assertEqual(
            (polygon["x"], polygon["y"], polygon["width"], polygon["height"]),
            (1.0, 2.0, 3.0, 3.0),
        )
        self.assertEqual((line["x2"], line["y2"]), (4.0, 6.0))
        self.assertEqual(line["arrow"], "both")
        self.assertTrue(line["curve"])

    def test_shape_defaults_apply_to_new_shape_drafts(self) -> None:
        draft = app.Draft("shape_line", 1, 2, 0, 0, 4, 6)
        obj = app.shape_from_draft_data(draft)
        app.apply_shape_defaults(
            obj, {"defaultShapeLineWidth": 0.5, "defaultShapeStrokeColor": "#123456"}
        )

        self.assertEqual(obj["lineWidth"], 0.5)
        self.assertEqual(obj["strokeColor"], "#123456")

    def test_free_polygon_draft_closes_without_preview_point(self) -> None:
        draft = app.Draft(
            "shape_polygon", 1, 1, 0.25, 0.25, 3, 3, [(1, 1), (4, 1), (2, 5)]
        )

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
        parts = app.svg_for_object(
            project,
            {"type": "diagonal_corridor", "x": 1, "y": 1, "x2": 4, "y2": 3, "width": 1},
            1,
        )
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
        project["customSymbols"] = {
            "custom_skull": {
                "label": "Skull",
                "sourceType": "png",
                "path": "missing.png",
                "variants": [],
            }
        }
        project["customSymbolGroups"] = [
            {"name": "Custom", "entries": [{"kind": "custom_skull", "label": "Skull"}]}
        ]
        project["objects"].append(
            app.validate_object(app.symbol("custom_skull", 3, 3, 1), 2)
        )

        report = app.campaign_report_markdown(project)

        self.assertIn("Missing Custom Symbol Files", report)
        self.assertIn("missing.png", report)

    def test_svg_symbol_style_overrides_render(self) -> None:
        project = app.create_project()
        styled = app.validate_object(
            {
                **app.symbol("door", 3, 2, 1),
                "color": "#cc0000",
                "opacity": 0.5,
                "shadow": True,
                "outline": True,
            },
            2,
        )
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
        parts = [
            part for item in shapes for part in app.svg_for_object(project, item, 1)
        ]

        self.assertTrue(any(part.startswith("<rect") for part in parts))
        self.assertTrue(any(part.startswith("<ellipse") for part in parts))
        self.assertTrue(any(part.startswith("<polygon") for part in parts))
        self.assertTrue(any(part.startswith("<line") for part in parts))
        self.assertTrue(
            any(
                'stroke="#123456"' in part and 'stroke-width="9"' in part
                for part in parts
            )
        )

    def test_export_frame_crops_project_to_named_bounds(self) -> None:
        project = app.create_project()
        inside = app.validate_object(app.rect("room", 2, 2, 3, 3), 2)
        outside = app.validate_object(app.rect("room", 20, 20, 3, 3), 3)
        project["objects"].extend([inside, outside])
        frame = {
            "id": "frame_1",
            "name": "Inset",
            "x": 1,
            "y": 1,
            "width": 6,
            "height": 6,
        }

        framed = app.export_project_for_frame(project, frame)

        self.assertEqual(framed["settings"]["width"], 6)
        self.assertEqual(framed["settings"]["height"], 6)
        self.assertIn(inside["id"], {obj["id"] for obj in framed["objects"]})
        self.assertNotIn(outside["id"], {obj["id"] for obj in framed["objects"]})

    def test_vtt_scene_exports_walls_doors_and_lights(self) -> None:
        project = app.create_project()
        project["objects"].append(app.validate_object(app.rect("room", 1, 1, 4, 4), 2))
        project["objects"].append(app.validate_object(app.symbol("door", 3, 1, 1), 3))
        project["objects"].append(
            app.validate_object(app.symbol("light_source", 3, 3, 1), 4)
        )
        project["objects"].append(
            app.validate_object(app.symbol("vision_blocker", 5, 3, 1), 5)
        )
        project["objects"].append(
            app.validate_object(app.symbol("hazard_marker", 4, 4, 1), 6)
        )

        foundry = app.foundry_scene_data(project)
        roll20 = app.roll20_page_data(project)

        self.assertGreaterEqual(len(foundry["walls"]), 5)
        self.assertEqual(len(foundry["lights"]), 1)
        self.assertTrue(
            any(
                str(item.get("text", "")).startswith("Hazard")
                for item in foundry["notes"]
            )
        )
        self.assertTrue(any(item.get("door") for item in foundry["walls"]))
        self.assertEqual(len(roll20["doors"]), 1)
        self.assertEqual(len(roll20["lights"]), 1)
        self.assertGreater(len(roll20["walls"]), len(foundry["walls"]) - 2)

    def test_feature_extensions_validate_map_modes_underlays_and_print_layouts(
        self,
    ) -> None:
        project = app.create_project()
        project["settings"]["mapMode"] = "Hexmap"
        project["settings"]["hexOrientation"] = "flat"
        project["settings"]["showHexCoordinates"] = True
        project["underlays"] = [
            {
                "name": "Scan",
                "path": "missing.png",
                "x": 2,
                "y": 3,
                "width": 12,
                "height": 8,
                "gridCellWidth": 6,
                "gridCellHeight": 4,
            }
        ]
        project["exportFrames"] = [
            {"id": "frame_a", "name": "A", "x": 0, "y": 0, "width": 8, "height": 6}
        ]
        project["printLayouts"] = [
            {
                "name": "Atlas",
                "type": "atlas",
                "frameIds": ["frame_a"],
                "bleedCells": 0.5,
            }
        ]

        validated = app.validate_project(project)
        transform = app.underlay_alignment_transform(validated["underlays"][0])
        plan = app.print_layout_plan(validated, validated["printLayouts"][0])

        self.assertEqual(validated["settings"]["mapMode"], "Hexmap")
        self.assertEqual(app.hex_coordinate_label(2, 3), "q2 r3")
        self.assertAlmostEqual(transform["scaleX"], 2.0)
        self.assertEqual(plan["pages"][0]["frameId"], "frame_a")

    def test_vtt_helpers_cover_fog_los_light_encounter_and_session(self) -> None:
        project = app.create_project()
        room = app.validate_object(
            {
                **app.rect("room", 1, 1, 4, 4),
                "fogRevealed": True,
                "textureFill": "stone",
            },
            2,
        )
        wall = app.validate_object(
            {**app.symbol("vision_blocker", 3, 1, 1), "sightBlocks": True},
            3,
        )
        light = app.validate_object(app.symbol("light_source", 3, 3, 1), 4)
        spawn = app.validate_object(
            {
                **app.symbol("party_start", 5, 5, 1),
                "encounterStart": True,
                "tokenCount": 6,
                "faction": "Delvers",
            },
            5,
        )
        project["objects"].extend([room, wall, light, spawn])

        state = app.apply_session_update(
            project, reveal_room_id=room["id"], roll="Wandering monster: 2"
        )
        foundry = app.foundry_scene_data(project)

        self.assertIn(room["id"], state["revealedRoomIds"])
        self.assertTrue(app.fog_of_war_masks(project)[0]["revealed"])
        self.assertFalse(app.line_of_sight_clear(project, (3, 0), (3, 4)))
        self.assertGreaterEqual(len(app.light_zones(project)), 1)
        self.assertEqual(app.encounter_start_points(project)[0]["tokens"], 6)
        self.assertIn("fog", foundry)
        self.assertIn("encounterStarts", foundry)

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
        polygon = app.validate_object(
            {"type": "shape", "kind": "polygon", "points": [[1, 1], [4, 1], [2, 5]]}, 1
        )
        names = [name for name, _x, _y in app.selection_handles(polygon)]

        self.assertIn("point:0", names)
        self.assertIn("insert:0", names)

    def test_rotate_shape_geometry_updates_line_and_polygon(self) -> None:
        line = app.validate_object(app.shape("line", 0, 0, 0, 0, 2, 0), 1)
        polygon = app.validate_object(
            {
                "type": "shape",
                "kind": "rectangle",
                "x": 0,
                "y": 0,
                "width": 2,
                "height": 1,
            },
            2,
        )

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

    def test_group_transform_and_multi_selection_helpers_are_stable(self) -> None:
        first = app.validate_object(
            {**app.rect("room", 1, 1, 2, 2), "group": "grp_a"}, 2
        )
        second = app.validate_object(
            {**app.rect("room", 4, 1, 2, 2), "group": "grp_a"}, 3
        )

        transformed = app.transform_objects_about_pivot(
            [first, second], (1, 1), scale_x=2, scale_y=2, rotation=0
        )
        box = app.union_bounds(transformed)

        self.assertIsNotNone(box)
        self.assertAlmostEqual(box[2], 10)
        self.assertEqual({obj.get("group") for obj in transformed}, {"grp_a"})

    def test_clipboard_package_carries_custom_symbols(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        maker.project["customSymbols"] = {
            "custom_skull": {
                "label": "Skull",
                "sourceType": "png",
                "path": "skull.png",
                "tags": ["undead"],
                "variants": [],
            }
        }
        maker.project["customSymbolGroups"] = [
            {"name": "Bones", "entries": [{"kind": "custom_skull", "label": "Skull"}]}
        ]
        item = app.validate_object(app.symbol("custom_skull", 2, 3, 1), 2)

        package = app.OSRMapMaker.selection_clipboard_package(maker, [item])

        self.assertEqual(package["format"], app.CLIPBOARD_FORMAT)
        self.assertIn("custom_skull", package["customSymbols"])
        self.assertEqual(package["customSymbolGroups"][0]["name"], "Bones")

        target = app.OSRMapMaker.__new__(app.OSRMapMaker)
        target.project = app.create_project()
        app.OSRMapMaker.import_clipboard_custom_symbols(
            target, package, package["objects"]
        )

        self.assertIn("custom_skull", target.project["customSymbols"])
        self.assertEqual(target.project["customSymbolGroups"][-1]["name"], "Bones")

    def test_copy_paste_preserves_selection_and_remaps_groups(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        first = app.validate_object(
            {**app.rect("room", 1, 1, 2, 2), "group": "grp_a"}, 2
        )
        second = app.validate_object(
            {**app.rect("room", 4, 1, 2, 2), "group": "grp_a"}, 3
        )
        maker.project["objects"].extend([first, second])
        maker.selected_ids = {first["id"], second["id"]}
        maker.clipboard_objects = []
        maker.clipboard_package = None
        maker.project_snapshot = lambda: copy.deepcopy(maker.project)
        maker.commit_history = lambda before, description: None
        maker.set_selection = lambda ids, primary=None: setattr(
            maker, "selected_ids", set(ids)
        )
        maker.redraw = lambda: None
        maker.show_status = lambda message: None
        maker.clipboard_clear = lambda: None
        maker.clipboard_append = lambda value: None
        maker.clipboard_get = lambda: json.dumps(maker.clipboard_package)
        maker.snap_step = lambda: 1.0
        maker.mouse_grid = None
        maker.snap_point = lambda x, y, exclude_ids=None: (x, y)

        app.OSRMapMaker.copy_selected(maker)
        app.OSRMapMaker.paste_clipboard(maker)

        pasted = [
            obj for obj in maker.project["objects"] if obj["id"] in maker.selected_ids
        ]
        self.assertEqual(len(pasted), 2)
        self.assertEqual(len({obj.get("group") for obj in pasted}), 1)
        self.assertNotEqual(pasted[0].get("group"), "grp_a")

    def test_paste_delta_centers_selection_on_cursor(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        maker.mouse_grid = (10, 8)
        maker.selected_ids = set()
        maker.snap_point = lambda x, y, exclude_ids=None: (x, y)
        maker.snap_step = lambda: 1.0
        objects = [app.validate_object(app.rect("room", 2, 2, 4, 2), 2)]

        self.assertEqual(app.OSRMapMaker.paste_delta(maker, objects, True), (6.0, 5.0))
        self.assertEqual(app.OSRMapMaker.paste_delta(maker, objects, False), (1.0, 1.0))

    def test_nudge_selection_moves_unlocked_objects_only(self) -> None:
        maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
        maker.project = app.create_project()
        unlocked = app.validate_object(app.rect("room", 2, 2, 2, 2), 2)
        locked = app.validate_object(
            {**app.rect("room", 6, 6, 2, 2), "locked": True}, 3
        )
        maker.project["objects"].extend([unlocked, locked])
        maker.selected_ids = {unlocked["id"], locked["id"]}
        maker.selected_id = unlocked["id"]
        maker.project_snapshot = lambda: copy.deepcopy(maker.project)
        maker.commit_history = lambda before, description: None
        maker.redraw = lambda: None
        maker.show_status = lambda message: None

        app.OSRMapMaker.nudge_selection(maker, 0.5, -1)

        self.assertEqual((unlocked["x"], unlocked["y"]), (2.5, 1.0))
        self.assertEqual((locked["x"], locked["y"]), (6, 6))

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

    def test_spatial_hit_detection_matches_linear_topmost_result(self) -> None:
        project = app.create_project()
        bottom = app.validate_object(app.rect("room", 1, 1, 4, 4), 2)
        top = app.validate_object(app.rect("room", 2, 2, 4, 4), 3)
        project["objects"].extend([bottom, top])
        index = app.build_spatial_index(project["objects"], bucket_size=2)

        hit = app.topmost_hit_object(project, 3, 3, index=index, bucket_size=2)

        self.assertEqual(hit["id"], top["id"])

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
        self.project["objects"].append(
            app.validate_object(app.rect("room", 1, 1, 4, 3), 2)
        )
        self.project["objects"].append(
            app.validate_object(app.symbol("door", 3, 1, 1), 3)
        )
        self.project["objects"].append(
            app.validate_object(app.shape("circle", 6, 1, 2, 2), 4)
        )
        self.project["objects"].append(
            app.validate_object(app.shape("rectangle", 9, 1, 2, 2), 5)
        )
        self.project["objects"].append(
            app.validate_object(app.shape("polygon", 12, 1, 2, 2), 6)
        )
        self.project["objects"].append(
            app.validate_object(app.shape("line", 15, 1, 0, 0, 18, 3), 7)
        )

    def render(self):
        image = app.Image.new(
            "RGBA",
            tuple(int(v) for v in app.canvas_size(self.project, 1)),
            self.project["settings"]["backgroundColor"],
        )
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
        project["objects"] = [
            app.rect("room", 2, 2, 8, 6),
            app.diagonal_corridor(9, 4, 18, 9),
        ]
        image = app.Image.new(
            "RGBA",
            tuple(int(v) for v in app.canvas_size(project, 1, False)),
            settings["backgroundColor"],
        )
        draw = app.ImageDraw.Draw(image)
        app.render_pillow(draw, project, 1, None, None, include_legend=False)
        self.assertEqual(
            image.getpixel((230, 97)),
            app.Image.new("RGBA", (1, 1), settings["floorColor"]).getpixel((0, 0)),
        )

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

    def test_svg_output_uses_stable_object_ids(self) -> None:
        project = app.create_project()
        room = app.validate_object(
            {**app.rect("room", 1, 1, 2, 2), "id": "room_fixed"}, 2
        )

        first = " ".join(
            app.svg_object_group(project, room, app.svg_for_object(project, room, 1))
        )
        second = " ".join(
            app.svg_object_group(project, room, app.svg_for_object(project, room, 1))
        )

        self.assertEqual(first, second)
        self.assertIn("room_fixed", first)

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
                {
                    "name": "Bones",
                    "entries": [{"kind": "custom_skull", "label": "Skull"}],
                }
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
