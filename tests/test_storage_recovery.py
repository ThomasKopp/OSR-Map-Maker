from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from contextlib import contextmanager

from pytest import MonkeyPatch

import osr_map_maker as app
import storage


class CallRecorder:
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.return_value


@contextmanager
def replace_attr(owner, name, value):
    with MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(owner, name, value)
        yield


def fail(error):
    def raise_error(*_args, **_kwargs):
        raise error

    return raise_error


def headless_maker(root: Path, project: dict | None = None) -> app.OSRMapMaker:
    maker = app.OSRMapMaker.__new__(app.OSRMapMaker)
    maker.project = (
        copy.deepcopy(project) if project is not None else app.create_project()
    )
    maker._autosave_root = root
    maker.current_file = None
    maker._project_revision = 1
    maker._saved_revision = 0
    maker.performance_profiler = app.PerformanceProfiler(False)
    maker.history = []
    maker.future = []
    for name in (
        "sync_campaign_from_rooms",
        "sync_active_map_storage",
        "show_status",
        "show_toast",
        "show_error",
        "update_window_title",
        "set_selection",
        "sync_vars",
        "refresh_symbol_browser",
        "refresh_history_panel",
        "redraw",
        "show_validation_warnings",
        "remember_recent_project",
        "schedule_autosave",
        "offer_missing_custom_symbol_repair",
        "save_recent_projects",
        "rebuild_recent_projects_menu",
    ):
        setattr(maker, name, CallRecorder())
    maker.winfo_exists = CallRecorder(return_value=True)
    maker.confirm_discard_changes = CallRecorder(return_value=True)
    maker.recent_projects = []
    maker.start_autosave_session()
    return maker


class AtomicStorageTests(unittest.TestCase):
    def test_failed_flush_or_replace_preserves_json_and_zip(self) -> None:
        for suffix in (".osrmap.json", ".osrmapz"):
            for failure in ("fsync", "replace"):
                with (
                    self.subTest(suffix=suffix, failure=failure),
                    tempfile.TemporaryDirectory() as tmp,
                ):
                    target = Path(tmp) / f"project{suffix}"
                    old = app.create_project()
                    app.write_project_data(target, old)
                    original = target.read_bytes()
                    new = copy.deepcopy(old)
                    new["meta"]["title"] = "New contents"
                    with replace_attr(app.os, failure, fail(OSError("disk failure"))):
                        with self.assertRaises(OSError):
                            app.write_project_data(target, new)
                    self.assertEqual(target.read_bytes(), original)
                    self.assertEqual(app.read_project_file(target), old)
                    self.assertEqual(list(Path(tmp).iterdir()), [target])

    def test_partial_write_preserves_both_formats(self) -> None:
        real_temporary_file = tempfile.NamedTemporaryFile

        class FailingWriter:
            def __init__(self, wrapped):
                self.wrapped = wrapped

            def __enter__(self):
                self.wrapped.__enter__()
                return self

            def __exit__(self, *args):
                return self.wrapped.__exit__(*args)

            def __getattr__(self, name):
                return getattr(self.wrapped, name)

            def write(self, data):
                self.wrapped.write(data[:4])
                raise OSError("disk full after partial write")

        for suffix in (".osrmap.json", ".osrmapz"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / f"project{suffix}"
                project = app.create_project()
                app.write_project_data(target, project)
                original = target.read_bytes()
                with replace_attr(
                    app.tempfile,
                    "NamedTemporaryFile",
                    lambda **kw: FailingWriter(real_temporary_file(**kw)),
                ):
                    with self.assertRaises(OSError):
                        app.write_project_data(target, project)
                self.assertEqual(target.read_bytes(), original)
                self.assertEqual(list(Path(tmp).iterdir()), [target])

    def test_serialization_failure_does_not_touch_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project.osrmap.json"
            app.write_project_data(target, app.create_project())
            original = target.read_bytes()
            with self.assertRaises(TypeError):
                app.write_project_data(target, {"bad": object()})
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(Path(tmp).iterdir()), [target])

    def test_replace_happens_with_complete_closed_file_in_target_directory(
        self,
    ) -> None:
        for suffix in (".osrmap.json", ".osrmapz"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / f"project{suffix}"
                old = app.create_project()
                new = copy.deepcopy(old)
                new["meta"]["title"] = "Complete replacement"
                app.write_project_data(target, old)
                original = target.read_bytes()
                replace = os.replace

                def inspect_then_replace(source, destination):
                    self.assertEqual(Path(source).parent, target.parent)
                    self.assertEqual(target.read_bytes(), original)
                    # Renaming succeeds on Windows only after closing the writer.
                    renamed = Path(tmp) / f"inspection{suffix}"
                    replace(source, renamed)
                    self.assertEqual(app.read_project_file(renamed), new)
                    replace(renamed, destination)

                with replace_attr(app.os, "replace", inspect_then_replace):
                    app.write_project_data(target, new)
                self.assertEqual(app.read_project_file(target), new)

    def test_storage_api_leaves_metadata_unchanged_on_failure(self) -> None:
        project = app.create_project()
        original = copy.deepcopy(project)
        with replace_attr(
            storage, "write_project_data", fail(PermissionError("denied"))
        ):
            with self.assertRaises(PermissionError):
                storage.save_project("unwritable.osrmap.json", project)
        self.assertEqual(project, original)

    def test_gui_failed_save_retains_dirty_state_current_path_and_recovery(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp) / "autosaves")
            maker.current_file = Path(tmp) / "original.osrmap.json"
            app.write_project_data(maker.current_file, maker.project)
            original = maker.current_file.read_bytes()
            maker.run_autosave()
            recovery = {p: p.read_bytes() for p in maker._autosave_root.rglob("*.json")}
            metadata = copy.deepcopy(maker.project["meta"])
            maker.show_toast.calls.clear()
            maker.show_status.calls.clear()
            with replace_attr(app.os, "replace", fail(PermissionError("locked"))):
                self.assertFalse(maker.save_project())
                self.assertFalse(maker.write_project_file(Path(tmp) / "new.osrmapz"))
            self.assertEqual(maker.current_file.name, "original.osrmap.json")
            self.assertEqual(maker.current_file.read_bytes(), original)
            self.assertTrue(maker.is_dirty())
            self.assertEqual(maker.project["meta"], metadata)
            self.assertEqual({p: p.read_bytes() for p in recovery}, recovery)
            self.assertEqual(len(maker.show_error.calls), 2)
            self.assertFalse(maker.show_toast.calls)
            self.assertFalse(maker.show_status.calls)

    def test_failed_save_prevents_closing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp))
            maker.confirm_discard_changes = lambda action: (
                app.OSRMapMaker.confirm_discard_changes(maker, action)
            )
            maker.save_project = CallRecorder(return_value=False)
            maker.clear_autosave = CallRecorder()
            maker.destroy = CallRecorder()
            with replace_attr(
                app.messagebox, "askyesnocancel", lambda *_args, **_kwargs: True
            ):
                maker.on_close()
            self.assertFalse(maker.destroy.calls)
            self.assertFalse(maker.clear_autosave.calls)

    def test_autosave_failure_preserves_old_file_and_retries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp))
            maker.run_autosave()
            original = maker.autosave_file.read_bytes()
            maker.project["meta"]["title"] = "Unsaved edit"
            maker._project_revision = 2
            maker.show_status.calls.clear()
            with replace_attr(app.os, "replace", fail(OSError("full"))):
                maker.run_autosave()
            self.assertEqual(maker.autosave_file.read_bytes(), original)
            self.assertEqual(maker._autosave_revision, 1)
            self.assertFalse(maker.autosave_matches_revision())
            self.assertTrue(maker.is_dirty())
            self.assertIn("failed", maker.show_status.calls[-1][0][0])
            self.assertEqual(len(maker.schedule_autosave.calls), 2)
            maker.run_autosave()
            self.assertEqual(maker._autosave_revision, 2)
            self.assertEqual(
                app.read_project_file(maker.autosave_file)["meta"]["title"],
                "Unsaved edit",
            )

    def test_failed_version_write_keeps_previous_versions_and_retry_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp))
            maker.run_autosave()
            old_versions = {
                p: p.read_bytes() for p in maker.autosave_versions_dir.glob("*.json")
            }
            maker._project_revision = 2
            real_write = app.write_project_data

            def fail_version(path, project, **kwargs):
                if path.parent == maker.autosave_versions_dir:
                    raise OSError("version write failed")
                real_write(path, project, **kwargs)

            with replace_attr(app, "write_project_data", fail_version):
                maker.run_autosave()
            self.assertEqual(maker._autosave_revision, 1)
            self.assertEqual(maker._autosave_version_revision, 1)
            self.assertEqual({p: p.read_bytes() for p in old_versions}, old_versions)
            maker.run_autosave()
            self.assertEqual(maker._autosave_revision, 2)


class RecoveryIsolationTests(unittest.TestCase):
    def test_discarding_current_snapshot_invalidates_autosave_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp))
            maker.run_autosave()
            versions = list(maker.autosave_versions_dir.glob("*.json"))
            self.assertTrue(maker.autosave_matches_revision())
            maker.discard_autosave_snapshot(maker.autosave_file)
            self.assertFalse(maker.autosave_matches_revision())
            self.assertTrue(all(path.exists() for path in versions))
            maker.run_autosave()
            self.assertTrue(maker.autosave_matches_revision())
            self.assertTrue(maker.autosave_file.exists())

    def test_project_identity_persists_and_legacy_identity_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = app.create_project()
            identity = project["meta"]["projectId"]
            for suffix in (".osrmap.json", ".osrmapz"):
                target = Path(tmp) / f"project{suffix}"
                storage.save_project(target, project)
                self.assertEqual(
                    storage.load_project(target)["meta"]["projectId"], identity
                )
            del project["meta"]["projectId"]
            legacy = Path(tmp) / "legacy.json"
            legacy.write_text(json.dumps(project), encoding="utf-8")
            first = storage.load_project(legacy)
            second = storage.load_project(legacy)
            self.assertEqual(first["meta"]["projectId"], second["meta"]["projectId"])
            self.assertNotIn("projectId", json.loads(legacy.read_text())["meta"])
            first["meta"]["projectId"] = "../../outside"
            self.assertRegex(app.ensure_project_id(first), r"^[0-9a-f]{32}$")

    def test_saving_one_project_cleans_only_its_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "autosaves"
            first = headless_maker(root)
            same_project = headless_maker(root, first.project)
            other_project = headless_maker(root)
            for maker in (first, same_project, other_project):
                maker.run_autosave()
            legacy = Path(tmp) / "autosave.osrmap.json"
            app.write_project_data(legacy, app.create_project())
            untouched = {
                p: p.read_bytes()
                for maker in (same_project, other_project)
                for p in maker.autosave_file.parent.rglob("*.json")
            }
            untouched[legacy] = legacy.read_bytes()
            self.assertNotEqual(first.autosave_file, same_project.autosave_file)
            self.assertEqual(
                first.autosave_file.parent.parent,
                same_project.autosave_file.parent.parent,
            )
            self.assertTrue(first.write_project_file(Path(tmp) / "saved.osrmap.json"))
            self.assertFalse(first.is_dirty())
            self.assertFalse(first.autosave_file.exists())
            self.assertFalse(list(first.autosave_versions_dir.glob("*.json")))
            self.assertEqual({p: p.read_bytes() for p in untouched}, untouched)

    def test_new_and_load_rotate_session_without_deleting_other_project(self) -> None:
        for action in ("new", "load", "close"):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "autosaves"
                maker = headless_maker(root)
                other = headless_maker(root)
                maker.run_autosave()
                other.run_autosave()
                old_current = maker.autosave_file
                untouched = {
                    p: p.read_bytes()
                    for p in other.autosave_file.parent.rglob("*.json")
                }
                if action == "new":
                    maker.new_project()
                elif action == "load":
                    path = Path(tmp) / "loaded.osrmap.json"
                    app.write_project_data(path, other.project)
                    maker.load_project_path(path)
                else:
                    maker.destroy = CallRecorder()
                    maker.on_close()
                    self.assertEqual(len(maker.destroy.calls), 1)
                self.assertFalse(old_current.exists())
                if action != "close":
                    self.assertNotEqual(maker.autosave_file, old_current)
                self.assertEqual({p: p.read_bytes() for p in untouched}, untouched)

    def test_corrupt_newest_does_not_block_older_project_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "autosaves"
            first = headless_maker(root)
            first.project["meta"]["title"] = "Dungeon A"
            second = headless_maker(root)
            second.project["meta"]["title"] = "Dungeon B"
            first.run_autosave()
            second.run_autosave()
            old = next(first.autosave_versions_dir.glob("*.json"))
            os.utime(old, (2000000000, 2000000000))
            first.autosave_file.write_text('{"broken":', encoding="utf-8")
            os.utime(first.autosave_file, (2000000010, 2000000010))
            candidates = app.discover_autosaves(root, Path(tmp) / "legacy.json")
            self.assertEqual(candidates[0].path, first.autosave_file)
            self.assertTrue(candidates[0].error)
            preferred = app.preferred_autosave(candidates)
            self.assertEqual(preferred.path, old)
            self.assertEqual(preferred.title, "Dungeon A")
            self.assertTrue(any(item.title == "Dungeon B" for item in candidates))
            recovering = headless_maker(root)
            recovering.history = [object()]
            self.assertTrue(recovering.recover_autosave_file(preferred.path))
            self.assertEqual(recovering.project["meta"]["title"], "Dungeon A")
            self.assertTrue(recovering.is_dirty())
            self.assertIsNone(recovering.current_file)
            self.assertEqual(recovering.history, [])
            self.assertNotEqual(
                recovering.autosave_file.parent, first.autosave_file.parent
            )
            self.assertTrue(old.exists())
            self.assertTrue(first.autosave_file.exists())
            self.assertTrue(second.autosave_file.exists())

    def test_failed_recovery_keeps_current_project_and_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp) / "autosaves")
            maker.run_autosave()
            original = copy.deepcopy(maker.project)
            candidate = Path(tmp) / "broken.json"
            candidate.write_text("not JSON", encoding="utf-8")
            old_session = maker.autosave_file
            self.assertFalse(maker.recover_autosave_file(candidate))
            self.assertEqual(maker.project, original)
            self.assertEqual(maker.autosave_file, old_session)
            self.assertTrue(old_session.exists())
            self.assertEqual(len(maker.show_error.calls), 1)

    def test_discovery_includes_legacy_and_ignores_temp_or_invalid_layouts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "autosaves"
            root.mkdir()
            legacy = Path(tmp) / "autosave.osrmap.json"
            version = root / "autosave-old.osrmap.json"
            for path in (legacy, version):
                app.write_project_data(path, app.create_project())
            (root / ".autosave-incomplete.tmp").write_text("broken")
            invalid = root / "invalid" / "session" / "autosave.osrmap.json"
            invalid.parent.mkdir(parents=True)
            invalid.write_text("broken")
            candidates = app.discover_autosaves(root, legacy)
            self.assertEqual({item.path for item in candidates}, {legacy, version})
            self.assertTrue(all(item.session == "Legacy" for item in candidates))


class RecoveryDialogTests(unittest.TestCase):
    def test_real_dialog_disables_corrupt_snapshot_and_recovers_older_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "autosaves"
            original = headless_maker(root)
            original.project["meta"]["title"] = "Older valid dungeon"
            original.run_autosave()
            old = next(original.autosave_versions_dir.glob("*.json"))
            os.utime(old, (2000000000, 2000000000))
            original.autosave_file.write_text("broken", encoding="utf-8")
            os.utime(original.autosave_file, (2000000010, 2000000010))
            other = headless_maker(root)
            other.run_autosave()
            candidates = app.discover_autosaves(root, Path(tmp) / "legacy.json")
            maker = headless_maker(root)
            try:
                app.tk.Tk.__init__(maker)
            except app.tk.TclError as exc:
                self.skipTest(f"Tk display unavailable: {exc}")
            maker.withdraw()
            errors = []

            def descendants(widget):
                for child in widget.winfo_children():
                    yield child
                    yield from descendants(child)

            def interact():
                dialog = next(
                    w for w in maker.winfo_children() if isinstance(w, app.tk.Toplevel)
                )
                try:
                    widgets = list(descendants(dialog))
                    table = next(w for w in widgets if isinstance(w, app.ttk.Treeview))
                    buttons = {
                        w.cget("text"): w
                        for w in widgets
                        if isinstance(w, app.ttk.Button)
                    }
                    self.assertEqual(table.selection(), ("1",))
                    self.assertFalse(buttons["Recover"].instate(["disabled"]))
                    table.selection_set("0")
                    table.event_generate("<<TreeviewSelect>>")
                    dialog.update()
                    self.assertTrue(buttons["Recover"].instate(["disabled"]))
                    buttons["Discard selected snapshot"].invoke()
                    self.assertFalse(original.autosave_file.exists())
                    self.assertTrue(old.exists())
                    self.assertTrue(other.autosave_file.exists())
                    self.assertFalse(buttons["Recover"].instate(["disabled"]))
                    buttons["Recover"].invoke()
                    self.assertEqual(
                        maker.project["meta"]["title"], "Older valid dungeon"
                    )
                    self.assertTrue(maker.is_dirty())
                except BaseException as exc:
                    errors.append(exc)
                finally:
                    if dialog.winfo_exists():
                        dialog.destroy()

            try:
                maker.after(50, interact)
                maker.ask_autosave_recovery(candidates)
                if errors:
                    raise errors[0]
                self.assertTrue(old.exists())
                self.assertTrue(other.autosave_file.exists())
            finally:
                app.tk.Tk.destroy(maker)

    def test_real_dialog_cancel_preserves_all_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            maker = headless_maker(Path(tmp) / "autosaves")
            maker.run_autosave()
            candidates = app.discover_autosaves(
                maker._autosave_root, Path(tmp) / "legacy.json"
            )
            snapshots = {item.path: item.path.read_bytes() for item in candidates}
            project = copy.deepcopy(maker.project)
            try:
                app.tk.Tk.__init__(maker)
            except app.tk.TclError as exc:
                self.skipTest(f"Tk display unavailable: {exc}")
            maker.withdraw()

            cancelled = []

            def cancel():
                dialog = next(
                    w for w in maker.winfo_children() if isinstance(w, app.tk.Toplevel)
                )
                for frame in dialog.winfo_children():
                    for widget in frame.winfo_children():
                        if (
                            isinstance(widget, app.ttk.Button)
                            and widget.cget("text") == "Cancel"
                        ):
                            cancelled.append(True)
                            widget.invoke()
                            return
                dialog.destroy()

            try:
                maker.after(50, cancel)
                maker.ask_autosave_recovery(candidates)
                self.assertTrue(cancelled, "Cancel button missing")
                self.assertEqual(maker.project, project)
                self.assertEqual({p: p.read_bytes() for p in snapshots}, snapshots)
            finally:
                app.tk.Tk.destroy(maker)


if __name__ == "__main__":
    unittest.main()
