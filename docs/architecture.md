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

## Module Boundaries

`osr_map_maker.py` still contains the Tk application and most implementation
code. The smaller modules are stable import facades for gradual extraction:

- `constants.py`: schema, default profiles, map modes, symbol and layer constants.
- `models.py`: project model constructors, validation, geometry, and VTT helpers.
- `renderers.py`: Tk, Pillow, SVG, PDF, and static-layer rendering entry points.
- `project_services.py`: project operations, reports, spatial index, VTT/session,
  print layout, and underlay helpers.

## Export Format

Image export renders a scoped project: map, page, selection, or named frame.
Pillow handles PNG/JPEG/WebP/PDF, while SVG export writes object groups with
stable IDs, CSS classes, layer metadata, and object IDs for post-processing.
Foundry, Roll20, and Fantasy Grounds JSON exports include walls, doors, lights,
notes, fog masks, line-of-sight blockers, encounter starts, and session state.

## Performance

Canvas redraws can use a visible viewport. Hit detection uses a bucketed spatial
index. Pillow export can cache layers marked with `staticCache`; the cache key
is derived from layer objects, scale, and render-relevant settings.

Undo/redo still stores before/after project snapshots, but snapshots no longer
round-trip through JSON for routine history work. Dirty state and autosave use
project revisions, autosave files are compact JSON, and large embedded assets
throttle autosave version writes. Targeted command diffs were reviewed; they are
best introduced gradually, starting with object-level map edits before settings,
campaign data, layer changes, and multi-map operations.
