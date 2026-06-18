# OSR Map Maker UI Specification

## Theme

The default theme is a quiet light Windows desktop theme. The map canvas stays
visually central; panels use neutral surfaces, compact spacing, and Segoe UI.

- App background: `#eef2f4`
- Panel background: `#f7f9fa`
- Canvas work area: `#e6eaed`
- Surface: `#ffffff`
- Alternate surface: `#f9fcfd`
- Text: `#1f2d35`
- Muted text: `#53666f`
- Accent: `#2d7fc1`
- Accent soft: `#d9ecff`
- Warning: `#9a5b00`
- Error: `#a12b2b`
- Focus: `#f6c85f`

## Metrics

- Minimum window: 1050 x 720 px.
- Base font: Segoe UI 9.
- Panel headings: Segoe UI 11 bold.
- Brand label: Segoe UI 13 bold.
- Button padding: 7 x 4 px.
- Entry padding: 4 x 3 px.
- Dialog padding: 12 px.
- Focus ring: 1 px with the focus color.
- Icon buttons should stay at least 28 px high at 100 percent scaling and keep
  their text/icon label inside the button at 125 and 150 percent scaling.

## Command Bar

The top bar is reserved for global actions: New, Load, Save, Undo, Redo, Zoom,
Fit, Search, Command Palette, and Export. These actions use the centralized
`GLOBAL_ACTION_ICONS` map, short labels, and tooltips. Tool-specific controls
belong in the contextual tool-options bar.

## Panels

Maps use thumbnail tabs with map name, object count, dirty marker, and a context
menu. Layers and History remain visible dock panels in normal drawing workspaces.
History separates undo and redo stacks and shows an empty state when no command
is available. Object and Navigator lists also show concise empty states.

## Status And Warnings

The status bar shows coordinate, cell, zoom, tool, layer, selection count, snap
state, save/autosave state, and validation count. Validation warnings are a
clickable status hint that opens Project Validation. Review comments stay in the
Review Comments dialog and are not merged into validation warnings.

## Dialogs

Dialogs use 12 px outer padding, primary actions on the right, Cancel/Close as
the leftmost or final neutral action depending on the existing dialog pattern,
and short title labels. Destructive or repair actions should be explicit buttons
and remain disabled or no-op when no target exists.

## Keyboard And DPI

Focusable controls opt into `takefocus` and keep a visible focus ring. Tooltips
and the Command Palette should expose shortcuts where available. The app clamps
Tk scaling to at least 1.0 and avoids viewport-based font scaling so text remains
predictable on 100, 125, and 150 percent displays.

## Performance Notes

UI feedback should stay immediate: canvas redraws are scheduled, minimap redraws
are throttled, object lists rebuild only when their data or filters change, and
large embedded assets throttle autosave version files. Undo/redo was reviewed
for targeted diffs; a full diff command engine would touch most mutation paths,
so the current safe optimization is to avoid JSON round-trips for snapshots,
reuse deep copies, cap history, and rely on revision checks for dirty/autosave
state. A later diff engine should start with object-level commands for map
objects before covering settings, campaign data, and multi-map operations.
