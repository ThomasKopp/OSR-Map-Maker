# VTT reference export and import check

The `examples/vtt-export.osrmap.json` project is the reference scene for this
workflow. It contains a square grid, a room, a door, a light and player-visible
content. Run `python scripts/export_vtt_reference.py` to regenerate the checked
reference files under `examples/vtt-reference/`: two JSON files and the Fantasy
Grounds XML sidecar. Export it once as an image and once as the target data.
Keep the image pixel size equal to the target grid size before importing.

## Foundry VTT (data contract: v12+; live import still to be recorded)

1. Export a PNG with a grid cell size of at least 50 pixels and export Foundry
   Scene JSON.
2. Create or select a scene, set the PNG as its background and enter its width,
   height, grid size and offset from the JSON.
3. In the Scene directory use **Import Data** for the JSON, then inspect the
   Walls and Lighting layers. Verify the room boundary, door and light align
   with the raster grid.

Foundry documents Scene-directory **Import Data** and the Scene document's
wall/light collections in its [Scenes guide](https://foundryvtt.com/article/scenes/)
and [v12 Scene API](https://foundryvtt.com/api/v12/interfaces/foundry.types.SceneData.html).
Background image uploads and token setup remain user-side steps. Recheck
alignment after changing scene dimensions or padding.

## Roll20 (current Page Settings / Dynamic Lighting)

1. Export a PNG and Roll20 Page JSON. The JSON is a transparent interchange
   reference, not a native Roll20 import file.
2. Drag the PNG to the Map layer, choose **Adjust Page Size**, then set the
   `page` width, height, cell size and scale from the JSON in Page Settings.
3. On the Dynamic Lighting layer reproduce `walls` and `doors`; create light
   tokens from `lights`. Enable Dynamic Lighting and test with a player token.

Roll20 documents its Dynamic-Lighting layer and UVTT handling in
[How To Set Up Dynamic Lighting](https://help.roll20.net/hc/en-us/articles/4403861702679-How-To-Set-Up-Dynamic-Lighting).
This application does not generate UVTT, so its JSON deliberately reports this
limitation instead of claiming one-click wall/light import.

## Fantasy Grounds Unity

1. Export the PNG/JPEG and the **Fantasy Grounds Image XML**.
2. Rename or save the XML so it has the identical base name as the image, for
   example `dungeon.png` and `dungeon.xml`, and put both files in the same
   folder.
3. Import the image. Fantasy Grounds reads the XML sidecar's native `grid`,
   `gridsize` and `occluders` data. Verify the grid and room-boundary LOS in the
   image's controls.
4. Add pins, toggleable doors and lights in Fantasy Grounds as needed; their
   records are not part of this documented image-sidecar schema.

The XML uses Fantasy Grounds' documented image line-of-sight sidecar structure
(`root`, `grid`, `gridsize`, `occluders`, `occluder`, `id`, `points`), not a
custom campaign-data format. Record the Fantasy Grounds Unity version and a
screenshot of the verified grid/LOS setup with the reference scene before
checking off this platform.

## Recording the live acceptance

For each target, record the application version, a screenshot with the grid
visible, and the observed raster scale/origin plus wall, door and light counts.
The checked files in `examples/vtt-reference/` provide the expected values.
Only mark the VTT backlog task complete after those three application-specific
records exist; automated contract tests do not substitute for a live import.

## Player data

Set export audience to **Player** before creating any VTT data. Player exports
omits objects marked `playerVisible: false`, secret-door symbols, fog/session
state and encounter starts. The Fantasy Grounds sidecar contains only grid and
LOS data; always inspect the generated target file as a final pre-share check.
