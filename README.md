# OSR Map Maker Handbook

OSR Map Maker is a Python desktop application for drawing, annotating,
organizing, and exporting old-school roleplaying maps. It can be used as a
simple dungeon mapper, a campaign room notebook, a print layout tool, and a VTT
export helper for Foundry, Roll20, and Fantasy Grounds workflows.

The application is intentionally local-first: projects are saved as JSON files
on disk, custom symbols can be embedded for portability, and exports are created
from the same project data you edit in the desktop UI.

## Contents

- [Quick Start](#quick-start)
- [Installing Optional Dependencies](#installing-optional-dependencies)
- [Project Files](#project-files)
- [The Workspace](#the-workspace)
- [Your First Map](#your-first-map)
- [Drawing Tools](#drawing-tools)
- [Selecting and Editing Objects](#selecting-and-editing-objects)
- [Symbols and Custom Assets](#symbols-and-custom-assets)
- [Rooms and Campaign Notes](#rooms-and-campaign-notes)
- [Layers, Objects, Maps, and Navigation](#layers-objects-maps-and-navigation)
- [Map Settings and Visual Style](#map-settings-and-visual-style)
- [Procedural Tools](#procedural-tools)
- [VTT and Session Features](#vtt-and-session-features)
- [Exporting](#exporting)
- [Review, Snapshots, and Validation](#review-snapshots-and-validation)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Autosave and Recovery](#autosave-and-recovery)
- [Example Projects](#example-projects)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Architecture Notes](#architecture-notes)

## Quick Start

Run the application from the project directory:

```powershell
python osr_map_maker.py
```

The app uses Tkinter for the interface. Tkinter is included with most standard
Python installations. Pillow is recommended for image export:

```powershell
python -m pip install pillow
```

To verify the project in a development checkout:

```powershell
.\scripts\quality.ps1
```

The quality script compiles the main modules, runs the test suite, and runs
`ruff` and `mypy` when those tools are installed.

## Installing Optional Dependencies

Only Python and Tkinter are required to open the app and edit maps. Optional
libraries unlock additional export and asset workflows.

| Dependency | Use |
| --- | --- |
| `pillow` | PNG, JPEG, WebP, PDF rendering and image export |
| `cairosvg` | Better preview/rendering for imported SVG custom symbols |
| `ruff` | Linting during development |
| `mypy` | Optional type checking during development |
| `pytest` | Test execution |

Install the common development set with:

```powershell
python -m pip install pillow pytest ruff mypy
```

SVG custom symbols remain stored in the project even if `cairosvg` is not
installed. Without it, the app falls back to a simpler symbol representation.

## Project Files

OSR Map Maker supports two project file formats:

- `.osrmap.json`: readable JSON project files.
- `.osrmapz`: compressed project archives for larger projects or embedded
  custom symbol libraries.

Use `File > Save`, `File > Save As`, or `File > Save Compressed` to choose the
format. If a project contains many embedded custom symbols, the app may suggest
the compressed format.

Project files include:

- Project metadata such as title, author, timestamps, and schema version.
- One or more maps/floors.
- Per-map settings, layers, objects, campaign room data, underlays, print
  layouts, navigation links, and session state.
- Export profiles and named export frames.
- Custom symbols, symbol groups, color palettes, asset metadata, comments,
  snapshots, and change log entries.

The current project schema is migrated and validated on load. Older legacy
symbol names such as `secret`, `pit`, and `column` are migrated automatically.
For larger schema migrations, the app can create backups in `.osr_map_backups`.

## The Workspace

The main window has four major areas.

### Canvas

The canvas is the drawing surface. You draw rooms, corridors, shapes, symbols,
text, notes, and measurements here. The canvas also shows selection handles,
hover highlights, smart guides, snap previews, map boundaries, print proof
guides, and optional player/GM preview information.

Useful canvas gestures:

- Drag with drawing tools to create rooms, corridors, caves, rounds, and box
  shapes.
- Click with symbol, text, number, and note tools to place objects.
- Click or drag with `Select` to choose objects.
- Use `Shift` with `Select` to build a multi-selection.
- Drag on empty space with `Select` to create a selection rectangle.
- Use the middle or right mouse button to pan.
- Hold Space for temporary panning.
- Use the mouse wheel or arrow-up/arrow-down keys to zoom.

### Floating or Docked Toolbar

The toolbar contains basic drawing tools, grouped tool sections, recent tools,
tool option controls, and shortcuts to common actions. It can be floating, docked
to the top, or docked to the left with `View > Toolbar Dock`.

Each tool button is keyboard focusable. Double-click a tool button to open tool
options for that tool.

### Inspector

The inspector on the right is divided into grouped tabs:

- `Build`: map settings, style, grid, procedural actions, export defaults.
- `Inspect`: selected object properties and multi-selection controls.
- `Campaign`: room forms, room lists, tables, reports, and handouts.
- `Export`: export profiles, frames, layouts, and VTT-related options.
- `Project`: maps, layers, objects, navigation, history, review, and validation.

The inspector width is resizable and saved in project settings. `View > Compact
Mode` hides the inspector for small screens.

### Status Bar

The status bar shows the active tool, grid position, selected object count, zoom
level, and save state. Toast messages and validation warnings also appear during
workflows that do not need a modal dialog.

## Your First Map

1. Start the app with `python osr_map_maker.py`.
2. Use `File > Project Settings` to set the project title and author.
3. In the `Build` tab, set map width, height, cell size, and cell scale.
4. Choose a visual style such as Blueprint, Print, Parchment, or Dark VTT.
5. Press `r` or select `Room`, then drag a rectangle on the canvas.
6. Press `c` or select `Corridor`, then drag from one room edge to another.
7. Select a door symbol from the `Symbols` tab and click on a wall.
8. Press `n` or select `Number`, then click inside a room.
9. Open the `Campaign` tab and fill in room notes, monsters, treasure, or
   read-aloud text.
10. Save with `File > Save As`.
11. Export with `File > Export` or use `File > Player Export` for a player-safe
   version.

## Drawing Tools

The built-in basic tools are:

| Shortcut | Tool | Use |
| --- | --- | --- |
| `v` | Select | Select, move, resize, rotate, edit, and inspect objects |
| `r` | Room | Draw rectangular room/floor areas |
| `c` | Corridor | Draw straight or diagonal corridors |
| `o` | Round | Draw rounded room areas |
| `h` | Cave | Draw irregular cave-like areas |
| `e` | Rect | Draw rectangle shape overlays |
| `i` | Circle | Draw circle or ellipse shape overlays |
| `p` | Polygon | Place polygon points and close the shape at the first point |
| `l` | Line | Draw straight line shapes |
| `t` | Text | Place exportable text |
| `n` | Number | Place room numbers using the configured numbering pattern |
| `m` | Note | Place non-exportable GM notes |
| `d` | Measure | Measure distance, path length, and area |

Additional tools include freehand drawing and brush workflows for sketching
caves, water, wall style, floor markings, or difficult terrain.

### Rooms, Corridors, Rounds, and Caves

Room-like objects are floor objects. They participate in floor merging, internal
outline cleanup, grid rendering, campaign room data, fog masks, and VTT exports.

- Rooms are rectangular.
- Corridors are rectangular when dragged horizontally or vertically.
- Diagonal corridors are created when the corridor drag is diagonal.
- Round rooms render as circles or ellipses.
- Caves use irregular edge treatment and can be roughened by procedural tools.

### Shapes

Shapes are overlay drawing objects and are useful for annotations, borders,
arrows, hand-drawn marks, water boundaries, and publishing markup.

Shape properties include:

- Stroke color.
- Stroke width.
- Fill color where applicable.
- Opacity.
- Line style: solid, dash, or dot.
- Arrow style: none, start, end, or both.
- Curved line option.

Polygon points can be edited directly on the canvas and through a point list.

### Text, Numbers, and Notes

Text objects are exportable by default. They support font, size, color,
alignment, rotation, opacity, and optional text box width.

Number objects use the map's configured numbering settings:

- Start value.
- Area code.
- Prefix.
- Suffix.

When a number is placed over a room, it can be linked to that room. This helps
campaign reports and room forms stay synchronized.

Note objects are meant for GM reminders and review notes. They are not exported
in player-facing exports unless you deliberately change object export settings.

### Measure Tool

The Measure tool tracks:

- Segment distance.
- Total path length.
- Polygon area when enough points exist.
- Real-world distance based on cell scale and unit.

Configure scale in the `Build` tab with `Cell scale` and `Cell scale unit`.

## Selecting and Editing Objects

Use `Select` to click objects on the canvas. The topmost visible and unlocked
object under the cursor is selected.

Common selection actions:

- `Delete`: delete selected objects.
- `Ctrl+D`: duplicate.
- `Ctrl+C`: copy.
- `Ctrl+V`: paste at cursor.
- `.`: repeat the last placed object with the duplicate offset.
- `Ctrl+]`: bring selection forward.
- `Ctrl+[`: send selection backward.
- `Ctrl+L`: lock or unlock.

Multi-selection supports:

- Group and ungroup.
- Batch layer changes.
- Batch export/player-visible changes.
- Align left, center, right, top, middle, or bottom.
- Distribute horizontally or vertically.
- Transform selection: scale, rotate, mirror, and choose pivot behavior.
- Save the selection as a reusable template.

### Handles

Handles vary by object type:

- Room-like objects have resize handles.
- Diagonal corridors have endpoint handles.
- Lines have endpoint handles.
- Polygons have point handles and insert handles.
- Symbols have scale and rotation handles.
- Groups can be transformed together.

### Snapping and Guides

The `Build` tab controls snapping:

- Snap to grid.
- Snap step: 1 cell, 1/2 cell, or 1/4 cell.
- Snap to object edges.
- Main grid and subgrid visibility.
- Coordinates, zones, ruler, print grid, and tooltips.

Smart guides help align selected objects to edges, centers, and equal spacing.

## Symbols and Custom Assets

Symbols live in the `Symbols` tab and in the tool menus. They are organized into
groups such as:

- Doors.
- Traps & Hazards.
- Magic & Mystery.
- Features.
- Natural.
- Dungeon Objects.
- Gameplay Markers.
- Urban & Overland.

The symbol browser supports:

- Grid and list views.
- Text search by name, aliases, and tags.
- Filters for all, favorites, recent, and custom.
- Favorite toggling.
- Recently used symbols.
- Custom symbol groups.
- Drag-and-drop from browser to map.
- Symbol group reordering.
- Hover preview popovers with variants, tags, legend name, and default size.
- Optional hover tooltips, controlled by `View > Tooltips` or the `Build` tab.

### Symbol Properties

Symbols can store:

- Size preset.
- Manual scale.
- Rotation.
- Variant.
- Color override.
- Opacity.
- Shadow.
- Outline.
- Legend label.
- VTT role.
- GM notes, clues, secrets, rumors, handout text, and links.

The app includes VTT roles for doors, walls, lights, hazards, spawns, and notes.
These roles are used by Foundry, Roll20, and Fantasy Grounds JSON exports.

### Custom Symbols

Custom symbols can be imported from PNG or SVG. Use the `Symbols` tab actions:

- `PNG`: import a PNG custom symbol.
- `SVG`: import an SVG custom symbol.
- `Var`: import a custom variant.
- `Edit`: edit custom symbol metadata.
- `Repair`: repair a missing file path.
- `Del Var`: delete a variant.
- `+ Group`: create a custom symbol group.
- `Set+`: import a symbol set.
- `Set`: export a symbol set.

Use `Tools > Embed Custom Symbols` to store custom symbol image data inside the
project. Embedded symbols make project files portable across machines.

If a custom symbol file is missing, the browser marks it and validation reports
the problem. The repair action can search a folder and relink matching files.

### Symbol Color Palettes and Legend Categories

Use `Tools > Symbol Color Palettes` to save and apply color choices for built-in
symbols. Use `Tools > Legend Categories` to customize how symbols are grouped in
the generated legend.

## Rooms and Campaign Notes

The `Campaign` tab turns a map into a usable adventure document. Room-like
objects can store structured notes:

- Room number.
- Room name.
- Status: undiscovered, discovered, looted, secured, or dangerous.
- Description.
- Contents.
- Monsters.
- Treasure.
- Loot table.
- Traps.
- Read-aloud text.
- Rumors.
- Clues.
- Secrets.
- Player handout text.
- GM notes.
- Faction, key, quest, secret door, and clue relationships.
- Player visibility.

Room templates help fill common OSR room patterns such as empty clue rooms,
monster lairs, trap rooms, treasure caches, and faction rooms.

### Room Lists and Numbering

The room list can sort and inspect rooms by number, zone, status, danger, and
player visibility. Automatic numbering can use configured prefix, area, and
suffix fields. The app can detect missing number gaps.

### Encounter and Loot Tables

Encounter and loot tables can be imported from Markdown or CSV-style text. The
app can roll random table results from a room or zone and store the result in
session state or reports.

### Reports, Booklets, and Handouts

Campaign exports include:

- Room report as Markdown.
- GM booklet.
- Player handouts.
- Encounter tables.
- Symbol legend.
- Linked symbol notes.
- TODOs and missing room information.
- Missing custom symbol files.

Player handouts exclude GM-only material and hidden information.

## Layers, Objects, Maps, and Navigation

### Layers

Layers can be shown, hidden, locked, reordered, and assigned export opacity.
Objects can be moved between layers from the selection inspector or context menu.

Layer features include:

- Visibility.
- Lock state.
- Export opacity.
- Object counts.
- Static cache flag for faster rendering of unchanged layers.

### Object List

The Objects tab provides:

- Search.
- Type filter.
- Layer filter.
- Direct selection.
- Double-click jump-to-object behavior.
- Select all visible and invert selection actions.
- Context-menu batch actions.

### Maps and Floors

Projects can contain multiple maps/floors. Use the maps panel to:

- Create maps.
- Duplicate maps.
- Rename maps.
- Delete maps.
- Switch active map.
- Group maps by folder or chapter.
- Assign templates such as Dungeon, City, Overland, Hexmap, or Empty Sketch.

Each map stores its own settings, layers, objects, campaign data, navigation
data, underlays, print layouts, and session state.

### Navigation

The Navigator stores:

- Saved views.
- Jump markers.
- Zones.
- Export frames.
- Floor links.

Linkable symbols such as stairs, portals, ladders, slides, teleporters, party
starts, and escape routes can target another map. The Nav tab can follow links
and highlight broken targets.

### Zones

Zones can be created from the current view or selection. They can have names,
colors, hierarchy, scale, and map-specific meaning. Procedural tools and reports
can optionally respect the active zone.

## Map Settings and Visual Style

The `Build` tab contains core map settings:

- Title.
- Width and height.
- Cell size.
- Real-world cell scale and unit.
- Legend visibility.
- Style template.
- Colors for background, floor, line, text, selection, and legend.
- Saved color palettes.
- Snap, grid, coordinates, zones, ruler, print grid, and tooltips.
- Default text and shape settings.
- Export defaults.

Style templates provide quick looks for blueprint maps, black-and-white print,
parchment, and dark VTT maps. You can still customize all colors afterward.

### Map Modes

Supported map modes:

- Dungeon.
- City.
- Overland.
- Hexmap.
- Sketch.

Hexmap mode uses a hex grid with pointy or flat orientation and axial or offset
coordinates. City and Overland modes can use terrain, district, POI, road, river,
height, and landmark symbol metadata.

### Underlays

Image underlays are useful for tracing scanned sketches or reference maps. They
can store:

- Path.
- Position.
- Size.
- Rotation.
- Opacity.
- Alignment grid dimensions.
- Trace/reference/print mode.

Underlays are saved in the project and can be shown, hidden, snapped, and used
for print proof workflows.

### Texture Fills

Room and floor objects support procedural texture fills:

- Stone.
- Earth.
- Water.
- Wood.
- Lava.

Texture fills render in Tk, Pillow, and SVG/PDF export paths where supported.

## Procedural Tools

The `Build` tab includes procedural actions:

- Random rooms.
- Random corridors.
- Suggest links.
- Roughen caves.
- Generate dungeon.
- Keyword dungeon.
- Natural caves.
- Check walls.
- Auto doors.
- Auto walls.
- Patrol routes.
- Map cleanup.
- Room report.

Generator settings can include:

- Seed.
- Scope: map, selection, or active zone.
- Theme profile: crypt, mine, fortress, sewer, or wizard lab.
- Density, room size ranges, loops, and dead-end controls.

Many procedural actions show a preview or diff summary before committing changes.
This makes generated results easier to inspect and undo.

## VTT and Session Features

OSR Map Maker can prepare data for virtual tabletops.

VTT-related features include:

- Player and GM audience modes.
- Gridless export.
- Foundry, Roll20, and Fantasy Grounds presets.
- VTT roles for doors, walls, lights, hazards, spawns, and notes.
- Fog-of-war masks from rooms, doors, and visibility state.
- Line-of-sight blockers.
- Light zones.
- Encounter start points with token count and faction.
- Session modes: GM, Player, and Split.
- Quick status updates for revealed rooms and random rolls.

### Player Visibility

Objects and rooms can be marked player-visible or GM-only. Player exports hide
non-exportable notes and GM-only information. GM exports include all visible
layers and objects unless filtered by export settings.

### VTT JSON Exports

Use the File menu:

- `File > Foundry Scene JSON`.
- `File > Roll20 Page JSON`.
- `File > Fantasy Grounds JSON`.

These JSON exports are intended as structured handoff data. They include map
dimensions, grid information, walls, doors, lights, notes, fog, encounter starts,
and session metadata where relevant.

## Exporting

Open the export dialog with `File > Export`.

Supported image/document formats:

- PNG.
- JPEG.
- WebP.
- PDF.
- SVG.

Export options include:

- Scale: 1x to 4x.
- Scope: map, page, selection, or named frame.
- Audience: GM or Player.
- Export grid.
- Include legend.
- Transparent PNG/WebP background.
- JPEG/WebP quality.
- Print margin.
- Title area.
- Named export frame.
- Filename template.
- Export profile.

Default export profiles:

- `Print A4`: PDF, 2x, GM audience, page scope, grid and legend enabled.
- `Foundry Player`: PNG, transparent, player audience, map scope, grid disabled.
- `Roll20 GM`: PNG, GM audience, map scope, grid disabled.
- `Fantasy Grounds`: JPEG, player audience, map scope, grid disabled.

Profiles can be saved, duplicated, deleted, marked as default, and applied from
the command palette or export dialog.

### Export Scopes

- `Map`: the active map area.
- `Page`: map plus page chrome such as title area and legend.
- `Selection`: only selected objects.
- `Frame`: a named export frame saved in the Navigator.

Named frames can be created from the current view or selected objects. Frames
can use presets such as A4, Letter, Foundry Scene, and Roll20 Page sizes.

### Batch Export

`File > Batch Export` creates multiple standard outputs in one pass, such as GM,
Player, and gridless PNG exports. Batch export uses profiles and filename
templates to keep repeated exports consistent.

### Legend Export

`File > Legend Export` exports the generated legend separately. The legend is
built from the map scale and used symbols, grouped by legend categories. It can
also include manual entries and custom labels.

### SVG Export

SVG export writes:

- Title and description metadata.
- CSS classes.
- Stable object groups.
- Layer metadata.
- `data-object-id` attributes.

This is useful when you want to post-process a map in vector tools.

### PDF and Print Layouts

PDF export supports page chrome, title areas, legends, print margins, and large
map atlas tiling. Print layouts can store:

- Title.
- Legend settings.
- Scale.
- Copyright.
- Page numbers.
- DPI.
- Bleed.
- Safe margin.
- Atlas, one-page dungeon, and handout page plans.

## Review, Snapshots, and Validation

The Tools menu contains project QA and review features:

- `Validate Project`: inspect warnings, missing assets, broken links, and skipped
  invalid objects.
- `Embed Custom Symbols`: make external custom symbols portable.
- `Symbol Color Palettes`: save and apply built-in symbol colors.
- `Legend Categories`: customize legend grouping.
- `Asset Library`: manage reusable asset metadata.
- `Review Comments`: create non-exportable review notes.
- `Create Snapshot Bookmark`: store an internal project snapshot.
- `Compare Project File`: compare the current project to another file.
- `Export Review Report`: export change notes since a snapshot.

The history panel shows undo and redo steps. Change log entries can be recorded
when history commits occur.

## Keyboard Shortcuts

Open `View > Shortcuts` or use the `Shortcuts` button in the Build tab to edit
shortcuts. Changes are rebound immediately after saving.

Default shortcuts:

| Shortcut | Action |
| --- | --- |
| `v` | Select tool |
| `r` | Room tool |
| `c` | Corridor tool |
| `o` | Round tool |
| `h` | Cave tool |
| `e` | Rectangle shape tool |
| `i` | Circle shape tool |
| `p` | Polygon shape tool |
| `l` | Line shape tool |
| `t` | Text tool |
| `n` | Number tool |
| `m` | Note tool |
| `d` | Measure tool |
| `Ctrl+D` | Duplicate selection |
| `Ctrl+C` | Copy selection |
| `Ctrl+V` | Paste at cursor |
| `Ctrl+]` | Bring forward |
| `Ctrl+[` | Send backward |
| `Ctrl+L` | Toggle lock |
| `Ctrl+K` | Command palette |
| `Ctrl+0` | Fit map |
| `Ctrl+Shift+0` | Fit selection |
| `Ctrl+1` | 100 percent zoom |
| `.` | Repeat last placed object |

Shortcut presets:

- Drawing.
- VTT Workflow.
- Laptop.

The shortcut editor warns about conflicts and can reset values to defaults.

## Autosave and Recovery

Autosave protects unsaved work. The app stores autosave versions with timestamps
and offers recovery on startup when a newer autosave exists.

Recovery metadata includes:

- Current project title.
- Autosave title.
- Last updated timestamp.
- Map count.
- Object count.

Autosave versions are pruned to avoid unlimited growth. Unsaved changes are
checked before closing, loading, or creating a new project.

## Example Projects

Example project files live in `examples/`:

- `examples/dungeon.osrmap.json`.
- `examples/city.osrmap.json`.
- `examples/hexmap.osrmap.json`.
- `examples/vtt-export.osrmap.json`.

Open them with `File > Load` to explore different map modes and export setups.

## Troubleshooting

### The app starts, but image export is unavailable

Install Pillow:

```powershell
python -m pip install pillow
```

Restart the app after installing.

### SVG custom symbols do not preview correctly

Install CairoSVG:

```powershell
python -m pip install cairosvg
```

The project can still store SVG definitions without CairoSVG, but preview and
raster export quality may be limited.

### A custom symbol is missing

Use the warning in the symbol browser or run `Tools > Validate Project`. Then:

1. Select the custom symbol in the `Symbols` tab.
2. Use `Repair` to search for the file in a folder.
3. Or use validation repair actions to remove missing symbols and placed
   instances.
4. Consider `Tools > Embed Custom Symbols` once paths are repaired.

### Player export shows too much or too little

Check:

- Object `export` setting.
- Object `playerVisible` setting.
- Room GM-only/player-visible fields.
- Layer visibility and export opacity.
- Export audience in the export dialog.
- Whether notes are intentionally non-exportable.

### Export is very large

Reduce export scale, switch from PNG to JPEG/WebP where transparency is not
needed, export a named frame instead of the full map, or use PDF atlas tiling for
large print maps.

### Tooltips are distracting

Turn them off with `View > Tooltips` or the `Tooltips` checkbox in the `Build`
tab. This disables both small text tooltips and symbol hover previews.

### Quality script cannot find optional tools

`scripts/quality.ps1` uses `ruff` and `mypy` only when installed. Missing
optional tools do not prevent syntax checks and tests from running.

## Development

Run checks:

```powershell
.\scripts\quality.ps1
```

Run tests directly:

```powershell
python -m pytest -q
```

Compile the main modules:

```powershell
python -m py_compile osr_map_maker.py models.py constants.py renderers.py project_services.py
```

The repository includes:

- `osr_map_maker.py`: main Tk application and most implementation code.
- `constants.py`: stable constants facade.
- `models.py`: model constructors, validation, geometry, and VTT helper facade.
- `renderers.py`: Tk, Pillow, SVG, PDF, and static-layer rendering facade.
- `project_services.py`: project operations, reports, spatial index, print
  layout, underlay, and VTT/session facade.
- `tests/`: regression, smoke, and performance tests.
- `examples/`: small example projects.
- `docs/architecture.md`: architectural notes.
- `scripts/quality.ps1`: local quality pipeline.

## Architecture Notes

The project is being gradually modularized. `osr_map_maker.py` still contains
the Tk UI and most core implementation, while smaller modules provide stable
import facades for constants, models, renderers, and services.

Important design points:

- Validation is centralized in `validate_project`, `validate_settings`, and
  `validate_object`.
- New persistent fields should be added to defaults and validators in the same
  change.
- Rendering supports Tk canvas, Pillow image export, SVG export, PDF export, and
  static layer caching.
- Hit detection uses a bucketed spatial index for large maps.
- Exports operate on scoped project copies so map, page, selection, and frame
  exports share the same rendering pipeline.
- VTT exports derive walls, doors, lights, fog masks, notes, encounter starts,
  and session data from the same map objects used by visual exports.

See `docs/architecture.md` for more implementation detail.
