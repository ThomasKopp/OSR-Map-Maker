# OSR Map Maker Architecture Notes

## Project Format

Project files are JSON (`.osrmap.json`) or compressed JSON (`.osrmapz`). The root
document stores shared metadata, export profiles, asset metadata, snapshots, and
the active map mirror. Each entry in `maps` stores its own settings, layers,
objects, campaign data, navigation data, underlays, print layouts, and session
state.

`schemaVersion` is the migration gate. Validation is centralized in
`validate_project`, `validate_settings`, `validate_object`, and the focused
validators for exports, symbols, print layouts, underlays, review data, and
session data. New persistent fields should be added to defaults and validators
in the same change.

`meta.projectId` is a persistent UUID hex string. New projects receive a random
ID; legacy files without a valid ID receive a deterministic ID derived from their
normalized absolute path when read. Saving persists that identity. This additive
metadata field does not change the schema version.

## Storage and Recovery

`storage.py` owns `read_project_with_fingerprint`, `write_project_data`,
fingerprints and the independently importable input/resource limits.
`write_project_data` uses a temporary file in the destination directory for both
JSON and ZIP, then flushes, calls `fsync`, closes, and publishes via `os.replace`.
Its `compact` option is used by autosave. Timestamp changes in the live model,
saved revisions, and recovery cleanup are committed only after a successful save.

`read_project_with_fingerprint` hashes the exact bytes it decodes. The UI stores
that SHA-256 together with the normalized path and checks it on the next save.
`write_project_data` returns the hash of the completed temporary file and supports
an expected destination hash checked immediately before replacement. Conflict
decisions can save a copy, reload with a local-changes decision, overwrite the
reviewed version, or cancel. Reload returns a non-save outcome so a pending
close/new operation does not continue automatically.

Under `app_state_dir()/autosaves`, each editing session owns
`<projectId>/<sessionId>/autosave.osrmap.json` and timestamped files in its
`versions/` subdirectory. A new/load/recover operation allocates a fresh session;
save and close never clean other sessions. Legacy flat autosaves remain readable.

`discover_autosaves` validates known snapshot paths and returns lightweight
`AutosaveCandidate` metadata including errors and warning counts. The recovery
picker prefers the newest readable candidate and revalidates the selected file
before replacing in-memory state. Recovery clears edit history, sets dirty state,
and retains the source snapshot. Discard removes only the selected file.
Autosaves and batch export run from detached project snapshots in worker threads;
their queues are consumed through Tk `after()` callbacks, and a late autosave
result cannot advance a newer project revision.

## Module Boundaries

`osr_map_maker.py` still contains the Tk application and most rendering
implementation. `storage.py`, `validation.py`, `geometry.py` and `rendering.py`
are dependency-free production modules; their tests import them without loading
Tk. The remaining compatibility facades preserve existing imports while further
renderer extraction proceeds:

- `constants.py`: schema, default profiles, map modes, symbol and layer constants.
- `models.py`: project model constructors, validation, geometry, and VTT helpers.
- `renderers.py`: Tk, Pillow, SVG, PDF, and static-layer rendering entry points.
- `project_services.py`: project operations, reports, spatial index, VTT/session,
  print layout, and underlay helpers.

## Export Format

Image export renders a scoped project: map, page, selection, or named frame.
Pillow handles PNG/JPEG/WebP/PDF, while SVG export writes object groups with
stable IDs, CSS classes, layer metadata, and object IDs for post-processing.
Foundry and Roll20 JSON exports include walls, doors, lights, notes, fog masks,
line-of-sight blockers, encounter starts, and session state for GM exports.
The Fantasy Grounds image XML sidecar uses its native grid and LOS-occluder
schema. Player exports remove player-hidden and secret objects plus GM-only
runtime state. Target-specific import limits are shown before export and
documented in `docs/vtt-import.md`.

Batch export uses `plan_batch_export` to reserve unique paths and capture the
reviewed destinations' hashes. Existing-file policy is Rename, Skip, or Overwrite;
within-batch collisions always receive unique suffixes. `execute_batch_export`
records a result for each job, continues after failures, and publishes images
through `save_batch_image` using temporary files and a final destination check.
The UI renders from a detached snapshot in a cancellable worker. The main thread
only receives progress/results through a queue; cancellation takes effect between
atomic file outputs, and the result list remains visible until closed or replaced
by a refreshed plan.

## Performance

Canvas redraws can use a visible viewport. Hit detection uses a bucketed spatial
index. Pillow export can cache layers marked with `staticCache`; the cache key
is derived from layer objects, scale, and render-relevant settings.

`tests/fixtures/visual/` contains reviewed Pillow, Tk-Canvas and SVG renderer
baselines. `tests/test_visual_regression.py` compares the same scene through
Pillow, a real Tk Canvas rasterized by Ghostscript, and optional CairoSVG; it
writes inspectable reference/result/diff artifacts on a mismatch. A documented
per-channel tolerance of 16 covers font anti-aliasing only.

Undo/redo still stores before/after project snapshots, but snapshots no longer
round-trip through JSON for routine history work. Dirty state and autosave use
project revisions, autosave files are compact JSON, and large embedded assets
throttle autosave version writes. Targeted command diffs were reviewed; they are
best introduced gradually, starting with object-level map edits before settings,
campaign data, layer changes, and multi-map operations.
