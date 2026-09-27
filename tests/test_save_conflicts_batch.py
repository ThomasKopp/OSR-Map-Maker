from __future__ import annotations

import copy
import os
import tempfile
import unittest
from pathlib import Path

import osr_map_maker as app
from tests.test_storage_recovery import CallRecorder, headless_maker, replace_attr


class SaveConflictTests(unittest.TestCase):
    def prepare(self, root: Path, suffix: str = ".osrmap.json"):
        path = root / f"map{suffix}"
        project = app.create_project()
        project["meta"]["title"] = "Initial"
        app.write_project_data(path, project)
        maker = headless_maker(root / "autosaves")
        maker.load_project_path(path)
        maker.project["meta"]["title"] = "Local changes"
        maker.bump_project_revision()
        maker.ask_file_conflict = CallRecorder(return_value="cancel")
        external = copy.deepcopy(project)
        external["meta"]["title"] = "External changes"
        return maker, path, external

    def test_external_edit_or_removal_is_not_silently_overwritten(self):
        for suffix in (".osrmap.json", ".osrmapz"):
            for removed in (False, True):
                with (
                    self.subTest(suffix=suffix, removed=removed),
                    tempfile.TemporaryDirectory() as tmp,
                ):
                    maker, path, external = self.prepare(Path(tmp), suffix)
                    maker.run_autosave()
                    if removed:
                        path.unlink()
                    else:
                        app.write_project_data(path, external)
                    expected = None if removed else path.read_bytes()
                    self.assertFalse(maker.save_project())
                    self.assertEqual(None if removed else path.read_bytes(), expected)
                    self.assertEqual(path.exists(), not removed)
                    self.assertEqual(maker.project["meta"]["title"], "Local changes")
                    self.assertTrue(maker.is_dirty())
                    self.assertTrue(maker.autosave_file.exists())
                    self.assertEqual(
                        maker.ask_file_conflict.calls[0][1], {"missing": removed}
                    )

    def test_hash_detects_same_size_and_timestamp_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker, path, _external = self.prepare(Path(tmp))
            stat = path.stat()
            original = path.read_bytes()
            path.write_bytes(original.replace(b"Initial", b"Changed"))
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            self.assertFalse(maker.save_project())
            self.assertEqual(len(maker.ask_file_conflict.calls), 1)

    def test_explicit_overwrite_updates_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker, path, external = self.prepare(Path(tmp))
            app.write_project_data(path, external)
            maker.ask_file_conflict.return_value = "overwrite"
            self.assertTrue(maker.save_project())
            self.assertEqual(
                app.read_project_file(path)["meta"]["title"], "Local changes"
            )
            self.assertEqual(maker._file_fingerprint, app.file_fingerprint(path))
            self.assertTrue(maker.save_project())
            self.assertEqual(len(maker.ask_file_conflict.calls), 1)

    def test_copy_keeps_external_file_and_switches_to_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker, path, external = self.prepare(Path(tmp))
            app.write_project_data(path, external)
            original = path.read_bytes()
            destination = Path(tmp) / "copy.osrmap.json"
            maker.ask_file_conflict.return_value = "copy"
            with replace_attr(
                app.filedialog, "asksaveasfilename", lambda **_kw: str(destination)
            ):
                self.assertTrue(maker.save_project())
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(maker.current_file, destination)
            self.assertEqual(
                app.read_project_file(destination)["meta"]["title"], "Local changes"
            )

    def test_copy_cannot_choose_conflicting_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker, path, external = self.prepare(Path(tmp))
            app.write_project_data(path, external)
            original = path.read_bytes()
            maker.ask_file_conflict.return_value = "copy"
            with replace_attr(
                app.filedialog, "asksaveasfilename", lambda **_kw: str(path)
            ):
                self.assertFalse(maker.save_project())
            self.assertEqual(path.read_bytes(), original)
            self.assertTrue(maker.is_dirty())

    def test_reload_requires_decision_and_does_not_complete_pending_save(self):
        for decision in (None, False, True):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as tmp:
                maker, path, external = self.prepare(Path(tmp))
                app.write_project_data(path, external)
                destination = Path(tmp) / "local-copy.osrmap.json"
                maker.ask_file_conflict.return_value = "reload"
                with (
                    replace_attr(
                        app.messagebox, "askyesnocancel", lambda *_a, **_kw: decision
                    ),
                    replace_attr(
                        app.filedialog,
                        "asksaveasfilename",
                        lambda **_kw: str(destination),
                    ),
                ):
                    self.assertFalse(maker.save_project())
                self.assertEqual(
                    maker.project["meta"]["title"],
                    "Local changes" if decision is None else "External changes",
                )
                self.assertEqual(destination.exists(), decision is True)
                if decision is True:
                    self.assertEqual(
                        app.read_project_file(destination)["meta"]["title"],
                        "Local changes",
                    )

    def test_change_during_write_is_checked_again_before_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker, path, external = self.prepare(Path(tmp))
            original_fsync = app.os.fsync

            def concurrent_edit(fd):
                original_fsync(fd)
                # Simulate a different process changing the destination after preflight.
                path.write_text(
                    '{"objects":[],"meta":{"title":"Another writer"}}', encoding="utf-8"
                )

            with replace_attr(app.os, "fsync", concurrent_edit):
                self.assertFalse(maker.save_project())
            self.assertEqual(
                app.read_project_file(path)["meta"]["title"], "Another writer"
            )
            self.assertTrue(maker.is_dirty())
            self.assertTrue(maker.show_error.calls)
            self.assertFalse(list(path.parent.glob("*.tmp")))

    def test_new_target_created_during_write_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "new.osrmap.json"
            original_fsync = app.os.fsync

            def concurrent_create(fd):
                original_fsync(fd)
                path.write_bytes(b"external")

            with replace_attr(app.os, "fsync", concurrent_create):
                with self.assertRaises(app.ProjectFileConflictError):
                    app.write_project_data(
                        path, app.create_project(), check_conflict=True
                    )
            self.assertEqual(path.read_bytes(), b"external")

    def test_conflict_dialog_offers_choices_and_disables_reload_for_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp))
            try:
                app.tk.Tk.__init__(maker)
            except app.tk.TclError as exc:
                self.skipTest(str(exc))
            maker.withdraw()
            errors = []

            def interact():
                dialog = next(
                    w for w in maker.winfo_children() if isinstance(w, app.tk.Toplevel)
                )
                try:
                    buttons = {
                        w.cget("text"): w
                        for frame in dialog.winfo_children()
                        for w in frame.winfo_children()
                        if isinstance(w, app.ttk.Button)
                    }
                    self.assertEqual(
                        set(buttons),
                        {"Cancel", "Save a copy", "Reload", "Overwrite explicitly"},
                    )
                    self.assertTrue(buttons["Reload"].instate(["disabled"]))
                    buttons["Cancel"].invoke()
                except BaseException as exc:
                    errors.append(exc)
                finally:
                    if dialog.winfo_exists():
                        dialog.destroy()

            try:
                maker.after(30, interact)
                self.assertEqual(
                    maker.ask_file_conflict(Path(tmp) / "missing.json", missing=True),
                    "cancel",
                )
                if errors:
                    raise errors[0]
            finally:
                app.tk.Tk.destroy(maker)


@unittest.skipIf(app.Image is None, "Pillow unavailable")
class BatchExportTests(unittest.TestCase):
    def targets(self, root: Path):
        return [
            (
                {"name": "Same", "index": index},
                "gm",
                {"format": "png", "scale": 1},
                root / "same.png",
            )
            for index in range(3)
        ]

    def render(self, item):
        return app.Image.new(
            "RGB", (2, 2), (item.record["index"] * 80, 0, 0)
        ), "#ffffff"

    def test_same_sanitized_map_names_keep_all_outputs_for_all_policies(self):
        for policy in ("Rename", "Skip", "Overwrite"):
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                project = app.create_project()
                maps = [
                    {"name": name, "index": index}
                    for index, name in enumerate(("a/b", "a?b", "a:b"))
                ]
                targets = app.batch_export_targets(
                    project,
                    maps,
                    maps[0],
                    root,
                    True,
                    [("gm", {"format": "png", "scale": 1})],
                )
                self.assertEqual(len({item[3] for item in targets}), 1)
                plan = app.plan_batch_export(targets, policy)
                self.assertEqual(len({item.path for item in plan}), 3)
                results = app.execute_batch_export(plan, self.render)
                self.assertTrue(all(item.status == "Saved" for item in results))
                for index, result in enumerate(results):
                    with app.Image.open(result.path) as image:
                        self.assertEqual(image.getpixel((0, 0)), (index * 80, 0, 0))

    def test_existing_file_policy_is_explicit(self):
        for policy in ("Rename", "Skip", "Overwrite"):
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                existing = root / "same.png"
                existing.write_bytes(b"keep me")
                plan = app.plan_batch_export(self.targets(root)[:1], policy)
                results = app.execute_batch_export(plan, self.render)
                self.assertEqual(
                    results[0].status, "Skipped" if policy == "Skip" else "Saved"
                )
                if policy != "Overwrite":
                    self.assertEqual(existing.read_bytes(), b"keep me")
                else:
                    with app.Image.open(existing) as image:
                        self.assertEqual(image.size, (2, 2))

    def test_partial_export_failure_keeps_prior_and_later_successes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = app.plan_batch_export(self.targets(root))
            original_save = app.save_export_image

            def fail_second(path, image, *args):
                if image.getpixel((0, 0))[0] == 80:
                    Path(path).write_bytes(b"partial")
                    raise OSError("disk write failed")
                original_save(path, image, *args)

            with replace_attr(app, "save_export_image", fail_second):
                results = app.execute_batch_export(plan, self.render)
            self.assertEqual([r.status for r in results], ["Saved", "Error", "Saved"])
            self.assertFalse(plan[1].path.exists())
            self.assertEqual(set(root.iterdir()), {plan[0].path, plan[2].path})
            self.assertIn("disk write failed", results[1].detail)

    def test_changed_destination_during_render_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "same.png"
            existing.write_bytes(b"reviewed contents")
            plan = app.plan_batch_export(self.targets(root)[:1], "Overwrite")

            def concurrent_edit(item):
                item.path.write_bytes(b"new external contents")
                return self.render(item)

            results = app.execute_batch_export(plan, concurrent_edit)
            self.assertEqual(results[0].status, "Error")
            self.assertEqual(existing.read_bytes(), b"new external contents")
            self.assertEqual(list(root.iterdir()), [existing])

    def test_failed_replace_keeps_existing_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "same.png"
            existing.write_bytes(b"previous output")
            plan = app.plan_batch_export(self.targets(root)[:1], "Overwrite")

            def locked(*_args):
                raise PermissionError("locked")

            with replace_attr(app.os, "replace", locked):
                results = app.execute_batch_export(plan, self.render)
            self.assertEqual(results[0].status, "Error")
            self.assertEqual(existing.read_bytes(), b"previous output")
            self.assertEqual(list(root.iterdir()), [existing])

    def test_batch_preserves_active_project_and_map_after_render_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp) / "autosaves")
            before = copy.deepcopy(maker.project)
            maker._saved_revision = maker._project_revision
            original_revision = maker._project_revision
            original = maker.project
            other = copy.deepcopy(maker.project["maps"][0])
            other["name"] = "Other map"
            other["id"] = "other"
            plan = app.plan_batch_export(
                [(other, "gm", {"scale": 1}, Path(tmp) / "export.png")]
            )

            def bad_render(**_kwargs):
                maker.project["meta"]["title"] = "temporary export state"
                raise ValueError("render failed")

            maker.render_image = bad_render
            results = maker.run_batch_export_plan(plan)
            self.assertEqual(results[0].status, "Error")
            self.assertIs(maker.project, original)
            self.assertEqual(maker.project, before)
            self.assertEqual(maker._project_revision, original_revision)
            self.assertFalse(maker.is_dirty())

    def test_batch_dialog_displays_plan_and_keeps_results_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp) / "autosaves")
            try:
                app.tk.Tk.__init__(maker)
            except app.tk.TclError as exc:
                self.skipTest(str(exc))
            maker.withdraw()
            maker.current_file = Path(tmp) / "map.osrmap.json"
            maker.export_scale = app.tk.IntVar(master=maker, value=1)
            maker.render_image = lambda **_kwargs: app.Image.new("RGB", (2, 2), "red")
            first = maker.project["maps"][0]
            first["name"] = "same"
            second = copy.deepcopy(first)
            second["id"] = "second"
            maker.project["maps"].append(second)

            def descendants(widget):
                for child in widget.winfo_children():
                    yield child
                    yield from descendants(child)

            try:
                maker.batch_export()
                dialog = next(
                    w for w in maker.winfo_children() if isinstance(w, app.tk.Toplevel)
                )
                widgets = list(descendants(dialog))
                checkbox = next(
                    w for w in widgets if isinstance(w, app.ttk.Checkbutton)
                )
                checkbox.invoke()
                preview = next(w for w in widgets if isinstance(w, app.tk.Listbox))
                self.assertEqual(preview.size(), 6)
                self.assertTrue(any("Rename" in row for row in preview.get(0, "end")))
                export_button = next(
                    w
                    for w in widgets
                    if isinstance(w, app.ttk.Button)
                    and w.cget("text") == "Export planned files"
                )
                export_button.invoke()
                self.assertTrue(dialog.winfo_exists())
                self.assertEqual(preview.size(), 6)
                self.assertTrue(
                    all(row.startswith("Saved |") for row in preview.get(0, "end"))
                )
                self.assertEqual(len(list(Path(tmp).glob("*.png"))), 6)
                self.assertTrue(export_button.instate(["disabled"]))
                self.assertEqual(maker.project["activeMapId"], first["id"])
            finally:
                app.tk.Tk.destroy(maker)


if __name__ == "__main__":
    unittest.main()
