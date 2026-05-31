from __future__ import annotations

import io
import base64
import json
import math
import random
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk
from typing import Any
from uuid import uuid4

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - handled at runtime for users.
    Image = None
    ImageDraw = None
    ImageFont = None


BLUE = "#4398bd"
WHITE = "#ffffff"
SELECT = "#f6c85f"
CURRENT_SCHEMA_VERSION = 7
RECTLIKE_TYPES = {"room", "corridor", "round", "cave"}
FLOOR_TYPES = RECTLIKE_TYPES | {"diagonal_corridor"}
RESIZABLE_TYPES = RECTLIKE_TYPES | {"legend"}
SHAPE_TOOLS = {"shape_rect", "shape_circle", "shape_polygon", "shape_line"}
DRAG_SHAPE_TOOLS = SHAPE_TOOLS - {"shape_polygon"}
BOX_SHAPES = {"rectangle", "circle", "polygon"}
LINE_SHAPES = {"line"}
SHAPE_KINDS = BOX_SHAPES | LINE_SHAPES
LINE_STYLES = {"solid", "dash", "dot"}
ARROW_STYLES = {"none", "start", "end", "both"}
RECENT_TOOL_LIMIT = 8
LEGACY_SYMBOL_KINDS = {"secret": "secret_door", "pit": "covered_pit", "column": "pillar"}
SNAP_STEP_LABELS = {"1 cell": 1.0, "1/2 cell": 0.5, "1/4 cell": 0.25}
SNAP_LABEL_BY_STEP = {value: label for label, value in SNAP_STEP_LABELS.items()}
CELL_SCALE_UNITS = ("ft.", "m", "yd.")
HANDLE_PIXEL_SIZE = 8
OBJECT_SNAP_TOLERANCE = 0.18
CUSTOM_GROUP_NAME = "Custom"
SYMBOL_SET_FORMAT = "osr-symbol-set"
SYMBOL_SIZE_PRESETS = {
    "Small": 0.75,
    "Normal": 1.15,
    "Large": 1.65,
    "Room filling": 2.5,
}
DEFAULT_SYMBOL_SIZE_PRESET = "Normal"
LINKABLE_SYMBOL_KINDS = {"stairs", "spiral_stairs", "natural_stairs", "ladder", "slide", "teleporter", "portal", "one_way_portal", "teleport_destination", "party_start", "escape_route"}
ROOM_STATUSES = ("undiscovered", "discovered", "looted", "secured", "dangerous")
ROOM_STATUS_LABELS = {
    "undiscovered": "Unentdeckt",
    "discovered": "Entdeckt",
    "looted": "Gepluendert",
    "secured": "Gesichert",
    "dangerous": "Gefaehrlich",
}
DOOR_PLACEMENT_TYPES = ("normal", "secret", "locked", "trapdoor")
WALL_TYPES = ("standard", "thin", "thick", "natural", "ruined")
RANDOM_ROOM_CONTENTS = (
    ("empty", "Leer", "Dust, echoes, and a useful clue to the next area."),
    ("monster", "Monster", "Hostile creatures guard the obvious route."),
    ("trap", "Falle", "A pressure trigger threatens anyone crossing the room."),
    ("treasure", "Schatz", "A hidden cache rewards careful searching."),
    ("special", "Spezial", "An odd feature changes the local situation."),
)
DEFAULT_SHORTCUTS = {
    "select_tool": "v",
    "room_tool": "r",
    "corridor_tool": "c",
    "round_tool": "o",
    "cave_tool": "h",
    "shape_rect_tool": "e",
    "shape_circle_tool": "i",
    "shape_polygon_tool": "p",
    "shape_line_tool": "l",
    "text_tool": "t",
    "number_tool": "n",
    "note_tool": "m",
    "measure_tool": "d",
    "duplicate": "<Control-d>",
    "copy": "<Control-c>",
    "paste": "<Control-v>",
    "bring_front": "<Control-bracketright>",
    "send_back": "<Control-bracketleft>",
    "toggle_lock": "<Control-l>",
}
TOOL_ACTIONS = {
    "select": "select_tool",
    "room": "room_tool",
    "corridor": "corridor_tool",
    "round": "round_tool",
    "cave": "cave_tool",
    "shape_rect": "shape_rect_tool",
    "shape_circle": "shape_circle_tool",
    "shape_polygon": "shape_polygon_tool",
    "shape_line": "shape_line_tool",
    "text": "text_tool",
    "number": "number_tool",
    "note": "note_tool",
    "measure": "measure_tool",
}
TOOL_DESCRIPTIONS = {
    "select": "Objekte auswaehlen, verschieben und bearbeiten",
    "room": "Rechteckigen Raum ziehen",
    "corridor": "Geraden oder diagonalen Korridor ziehen",
    "round": "Runden Raum ziehen",
    "cave": "Hoehle mit unregelmaessigem Rand ziehen",
    "shape_rect": "Einfaches Rechteck ziehen",
    "shape_circle": "Einfachen Kreis ziehen",
    "shape_polygon": "Polygon punktweise zeichnen und am Startpunkt schliessen",
    "shape_line": "Einfache Linie ziehen",
    "text": "Beschriftung platzieren",
    "number": "Automatische Raumnummer platzieren",
    "note": "Nicht exportierbare GM-Notiz platzieren",
    "measure": "Distanz, Weglaenge und Flaeche messen",
}
CURSOR_BY_TOOL = {
    "select": "arrow",
    "room": "crosshair",
    "corridor": "crosshair",
    "round": "crosshair",
    "cave": "crosshair",
    "shape_rect": "crosshair",
    "shape_circle": "crosshair",
    "shape_polygon": "crosshair",
    "shape_line": "crosshair",
    "text": "xterm",
    "number": "tcross",
    "note": "pencil",
    "measure": "crosshair",
}

LAYER_DEFS = [
    ("background", "Background"),
    ("rooms", "Rooms"),
    ("corridors", "Corridors"),
    ("symbols", "Symbols"),
    ("shapes", "Shapes"),
    ("text", "Text"),
    ("legend", "Legend"),
    ("notes", "Notes"),
]

STYLE_TEMPLATES = {
    "Blueprint": {
        "backgroundColor": BLUE,
        "gridColor": BLUE,
        "floorColor": WHITE,
        "textColor": BLUE,
        "selectionColor": SELECT,
        "legendColor": BLUE,
    },
    "Black/White Print": {
        "backgroundColor": "#ffffff",
        "gridColor": "#111111",
        "floorColor": "#ffffff",
        "textColor": "#111111",
        "selectionColor": "#c28f00",
        "legendColor": "#111111",
    },
    "Parchment": {
        "backgroundColor": "#d8c28d",
        "gridColor": "#4f3523",
        "floorColor": "#f3e2b3",
        "textColor": "#2c2118",
        "selectionColor": "#0a6c78",
        "legendColor": "#4f3523",
    },
    "Dark VTT": {
        "backgroundColor": "#11161a",
        "gridColor": "#8bd3dd",
        "floorColor": "#283238",
        "textColor": "#e9f4f6",
        "selectionColor": "#f0b84a",
        "legendColor": "#e9f4f6",
    },
}

SYMBOL_GROUPS = [
    (
        "Doors",
        [
            ("door", "▯", "Door"),
            ("double_door", "▯▯", "Double Door"),
            ("secret_door", "S", "Secret Door"),
            ("one_way_door", "▼", "One Way Door"),
            ("false_door", "⌒", "False Door"),
            ("locked_door", "▣", "Locked Door"),
            ("archway", "┬", "Archway"),
            ("concealed_door", "C", "Concealed Door"),
            ("barred_door", "≡", "Barred Door"),
            ("portcullis", "⋯", "Portcullis or Bars"),
            ("one_way_secret_door", "↧", "One Way Secret Door"),
            ("window", "▬", "Window"),
            ("arrow_slit", "◢", "Arrow Slit"),
            ("open_door", "⌜", "Open Door"),
            ("revolving_door", "↻", "Revolving Door"),
            ("archway_door", "┴", "Archway Door"),
            ("magic_sealed_door", "✦", "Magic Sealed Door"),
            ("cursed_door", "☠", "Cursed Door"),
            ("directional_portcullis", "⇅", "Directional Portcullis"),
            ("broken_door", "⌁", "Broken Door"),
            ("heavy_stone_door", "▰", "Heavy Stone Door"),
            ("illusion_passage", "⋱", "Illusion Passage"),
            ("revolving_wall", "⟳", "Revolving Wall"),
            ("collapse_barrier", "▲", "Collapse Barrier"),
            ("barricade", "≡", "Barricade"),
            ("force_barrier", "◇", "Force Barrier"),
        ],
    ),
    (
        "Traps & Hazards",
        [
            ("covered_pit", "☒", "Covered Pit"),
            ("open_pit", "▣", "Open Pit"),
            ("trap", "T", "Trap"),
            ("trap_ceiling", "C", "Trap Door in Ceiling"),
            ("trap_floor", "F", "Trap Door in Floor"),
            ("secret_trap_door", "S", "Secret Trap Door"),
            ("stairs", "▥", "Stairs"),
            ("stair_slide_trap", "≋", "Stairs/Slide Trap"),
            ("spiral_stairs", "◉", "Spiral Stairs"),
            ("natural_stairs", "◠", "Natural Stairs"),
            ("ladder", "↕", "Ladder"),
            ("slide", "→", "Slide"),
            ("spear_trap", "♜", "Spear Trap"),
            ("arrow_trap", "➤", "Arrow Trap"),
            ("blade_trap", "✂", "Blade Trap"),
            ("pendulum_blade", "⌒", "Pendulum Blade"),
            ("fire_jet", "♨", "Fire Jet"),
            ("poison_gas_jet", "☁", "Poison Gas Jet"),
            ("pressure_plate", "□", "Pressure Plate"),
            ("tripwire", "─", "Tripwire"),
            ("falling_block", "▥", "Falling Block"),
            ("rolling_boulder", "●", "Rolling Boulder"),
            ("trap_rune", "ᚱ", "Trap Rune"),
            ("alarm_glyph", "!", "Alarm Glyph"),
            ("teleport_trap", "⇄", "Teleport Trap"),
            ("collapse_hazard", "△", "Collapse Hazard"),
            ("slippery_floor", "≈", "Slippery Floor"),
            ("deep_chasm", "╳", "Deep Chasm"),
            ("lava_field", "♨", "Lava Field"),
            ("acid_pool", "☣", "Acid Pool"),
        ],
    ),
    (
        "Magic & Mystery",
        [
            ("magic_circle", "○", "Magic Circle"),
            ("summoning_circle", "☉", "Summoning Circle"),
            ("runestone", "ᚱ", "Runestone"),
            ("obelisk", "▴", "Obelisk"),
            ("portal", "◌", "Portal"),
            ("one_way_portal", "⇥", "One Way Portal"),
            ("teleport_destination", "◎", "Teleport Destination"),
            ("antimagic_field", "⊘", "Antimagic Field"),
            ("crystal_focus", "◆", "Crystal Focus"),
            ("cursed_idol", "☠", "Cursed Idol"),
            ("talking_statue", "☽", "Talking Statue"),
            ("invisible_wall", "⋯", "Invisible Wall"),
            ("time_warp_zone", "⌛", "Time Warp Zone"),
            ("dream_vision_site", "☾", "Dream or Vision Site"),
        ],
    ),
    (
        "Features",
        [
            ("statue", "☆", "Statue"),
            ("pillar", "●", "Pillar"),
            ("fountain", "○", "Fountain"),
            ("well", "◉", "Well"),
            ("pool", "≋", "Pool"),
            ("dais", "▣", "Dais"),
            ("altar", "▥", "Altar"),
            ("fireplace", "▔", "Fireplace"),
            ("table_chest", "▤", "Table, Chest"),
            ("bed", "▭", "Bed"),
            ("curtain", "〰", "Curtain"),
            ("railing", "••", "Railing"),
            ("illusory_wall", "┄", "Illusory Wall"),
            ("rock_wall", "▤", "Rock Wall"),
            ("teleporter", "▦", "Teleporter"),
        ],
    ),
    (
        "Natural",
        [
            ("rock_column", "♣", "Rock Column"),
            ("stalactite", "♢", "Stalactite"),
            ("stalagmite", "♧", "Stalagmite"),
            ("rubble", "✣", "Rubble"),
            ("crevasse", "⌁", "Crevasse"),
            ("sinkhole", "◎", "Sinkhole"),
            ("submerged_path", "≈", "Submerged Path"),
            ("subterranean_passage", "▒", "Subterranean Passage"),
            ("depression", "◌", "Depression"),
            ("pool_lake", "≋", "Pool or Lake"),
            ("stream", "〰", "Stream"),
            ("elevated_ledge", "▰", "Elevated Ledge"),
            ("natural_chimney", "✺", "Natural Chimney"),
            ("fungus_colony", "♧", "Fungus Colony"),
            ("giant_mushroom", "♤", "Giant Mushroom"),
            ("root_tangle", "⌘", "Root Tangle"),
            ("thorn_vines", "⌁", "Thorn Vines"),
            ("underground_tree", "♣", "Underground Tree"),
            ("waterfall", "⇊", "Waterfall"),
            ("directed_stream", "⇒", "Directed Stream"),
            ("bog_hole", "◍", "Bog Hole"),
            ("quicksand", "◌", "Quicksand"),
            ("ice_sheet", "❄", "Ice Sheet"),
            ("snowdrift", "∿", "Snowdrift"),
            ("scree_slope", "▵", "Scree Slope"),
            ("climbing_wall", "▥", "Climbing Wall"),
            ("narrow_squeeze", "><", "Narrow Squeeze"),
            ("natural_arch", "∩", "Natural Arch"),
            ("animal_burrow", "⌾", "Animal Burrow"),
            ("nest", "◔", "Nest"),
            ("bone_field", "☠", "Bone Field"),
        ],
    ),
    (
        "Dungeon Objects",
        [
            ("throne", "♛", "Throne"),
            ("sarcophagus", "▱", "Sarcophagus"),
            ("coffin", "▭", "Coffin"),
            ("urn", "∪", "Urn"),
            ("facing_statue", "➤", "Facing Statue"),
            ("bookshelf", "▥", "Bookshelf"),
            ("writing_desk", "✎", "Writing Desk"),
            ("alchemy_table", "⚗", "Alchemy Table"),
            ("weapon_rack", "⚔", "Weapon Rack"),
            ("armor_stand", "♙", "Armor Stand"),
            ("cage", "▦", "Cage"),
            ("stocks", "⊓", "Stocks"),
            ("rope_well", "◉", "Well with Rope"),
            ("lever", "┐", "Lever"),
            ("pull_chain", "╎", "Pull Chain"),
            ("switch", "▣", "Switch"),
            ("pressure_wheel", "⊕", "Pressure Wheel"),
            ("bell", "♩", "Bell"),
            ("gong", "◯", "Gong"),
            ("cauldron", "♨", "Cauldron"),
            ("oven", "▤", "Oven"),
            ("forge", "⚒", "Forge"),
            ("market_stall", "⌂", "Market Stall"),
            ("supply_crates", "▧", "Supply Crates"),
            ("barrel_group", "◍", "Barrel Group"),
        ],
    ),
    (
        "Gameplay Markers",
        [
            ("party_start", "★", "Party Start"),
            ("enemy_spawn", "✖", "Enemy Spawn"),
            ("patrol_point", "•", "Patrol Point"),
            ("patrol_route", "➝", "Patrol Route"),
            ("light_source", "☼", "Light Source"),
            ("darkness_zone", "●", "Darkness Zone"),
            ("vision_blocker", "▮", "Vision Blocker"),
            ("high_cover", "▰", "High Cover"),
            ("low_cover", "▱", "Low Cover"),
            ("difficult_terrain", "▒", "Difficult Terrain"),
            ("noise_source", "♪", "Noise Source"),
            ("scent_trail", "∴", "Scent Trail"),
            ("clue_marker", "?", "Clue Marker"),
            ("quest_goal", "⚑", "Quest Goal"),
            ("hazard_marker", "!", "Hazard Marker"),
            ("loot_marker", "$", "Loot Marker"),
            ("rest_site", "☽", "Rest Site"),
            ("escape_route", "↗", "Escape Route"),
        ],
    ),
    (
        "Urban & Overland",
        [
            ("house", "⌂", "House"),
            ("tower", "♜", "Tower"),
            ("gatehouse", "▤", "Gatehouse"),
            ("bridge", "═", "Bridge"),
            ("drawbridge", "⇵", "Drawbridge"),
            ("city_wall", "▥", "City Wall"),
            ("road", "━", "Road"),
            ("alley", "┄", "Alley"),
            ("market", "⚖", "Market"),
            ("fountain_square", "◎", "Fountain Square"),
            ("temple", "♁", "Temple"),
            ("tavern", "♬", "Tavern"),
            ("stable", "♞", "Stable"),
            ("harbor_pier", "┬", "Harbor Pier"),
            ("boat", "◁", "Boat"),
            ("campfire", "♨", "Campfire"),
            ("tent", "△", "Tent"),
            ("ruin", "▧", "Ruin"),
            ("signpost", "↦", "Signpost"),
            ("boundary_stone", "▴", "Boundary Stone"),
        ],
    ),
]

SYMBOL_LABELS = {kind: label for _group, entries in SYMBOL_GROUPS for kind, _icon, label in entries}
SYMBOL_LABELS.update({"secret": "Secret Door", "pit": "Covered Pit", "column": "Pillar"})
SYMBOL_ICONS = {kind: icon for _group, entries in SYMBOL_GROUPS for kind, icon, _label in entries}
SYMBOL_GROUP_BY_KIND = {kind: group for group, entries in SYMBOL_GROUPS for kind, _icon, _label in entries}
SYMBOL_GROUP_ORDER = {group: index for index, (group, _entries) in enumerate(SYMBOL_GROUPS)}
SYMBOL_GROUP_TAGS = {
    "Doors": {"door", "barrier", "passage", "vtt"},
    "Traps & Hazards": {"trap", "hazard", "danger", "vtt"},
    "Magic & Mystery": {"magic", "mystery", "portal", "vtt"},
    "Features": {"feature", "furniture", "dungeon"},
    "Natural": {"natural", "cave", "terrain"},
    "Dungeon Objects": {"furniture", "object", "dungeon"},
    "Gameplay Markers": {"marker", "gameplay", "vtt"},
    "Urban & Overland": {"urban", "overland", "settlement"},
}
SYMBOL_TAGS = {
    kind: sorted(SYMBOL_GROUP_TAGS.get(group, set()) | set(kind.split("_")) | {group.lower().replace(" & ", "-").replace(" ", "-")})
    for group, entries in SYMBOL_GROUPS
    for kind, _icon, _label in entries
}
for _kind in ("magic_sealed_door", "force_barrier", "portal", "one_way_portal", "teleport_destination", "teleporter", "trap_rune", "alarm_glyph"):
    SYMBOL_TAGS.setdefault(_kind, []).extend(tag for tag in ("magic",) if tag not in SYMBOL_TAGS.setdefault(_kind, []))
for _kind in ("table_chest", "bed", "throne", "bookshelf", "writing_desk", "alchemy_table", "weapon_rack", "armor_stand", "market_stall", "supply_crates", "barrel_group"):
    SYMBOL_TAGS.setdefault(_kind, []).extend(tag for tag in ("furniture",) if tag not in SYMBOL_TAGS.setdefault(_kind, []))
SYMBOL_VARIANT_SETS = {
    "door": [
        ("door", "Closed"),
        ("open_door", "Open"),
        ("locked_door", "Locked"),
        ("barred_door", "Barred"),
        ("broken_door", "Broken"),
    ],
    "secret_door": [
        ("secret_door", "Secret"),
        ("one_way_secret_door", "One way"),
        ("concealed_door", "Concealed"),
        ("illusion_passage", "Illusion"),
    ],
    "portcullis": [
        ("portcullis", "Bars"),
        ("directional_portcullis", "Directional"),
        ("force_barrier", "Force"),
        ("collapse_barrier", "Collapsed"),
    ],
    "trap": [
        ("trap", "Generic"),
        ("pressure_plate", "Pressure plate"),
        ("tripwire", "Tripwire"),
        ("trap_floor", "Floor"),
        ("trap_ceiling", "Ceiling"),
    ],
    "stairs": [
        ("stairs", "Stairs"),
        ("spiral_stairs", "Spiral"),
        ("natural_stairs", "Natural"),
        ("ladder", "Ladder"),
        ("slide", "Slide"),
    ],
    "portal": [
        ("portal", "Portal"),
        ("one_way_portal", "One way"),
        ("teleporter", "Teleporter"),
        ("teleport_destination", "Destination"),
    ],
    "light_source": [
        ("light_source", "Light"),
        ("campfire", "Campfire"),
        ("fireplace", "Fireplace"),
        ("darkness_zone", "Darkness"),
    ],
    "table_chest": [
        ("table_chest", "Table/chest"),
        ("supply_crates", "Crates"),
        ("barrel_group", "Barrels"),
        ("market_stall", "Stall"),
    ],
    "statue": [
        ("statue", "Statue"),
        ("facing_statue", "Facing"),
        ("talking_statue", "Talking"),
        ("cursed_idol", "Idol"),
    ],
}

SYMBOL_GROUP_ICONS = {
    "Doors": "▯",
    "Traps & Hazards": "☒",
    "Magic & Mystery": "✦",
    "Features": "●",
    "Natural": "〰",
    "Dungeon Objects": "▤",
    "Gameplay Markers": "★",
    "Urban & Overland": "⌂",
}

BASIC_TOOLS = [
    ("select", "↖", "Select"),
    ("room", "□", "Room"),
    ("corridor", "▭", "Corridor"),
    ("round", "○", "Round"),
    ("cave", "〰", "Cave"),
    ("shape_rect", "▱", "Rect"),
    ("shape_circle", "◯", "Circle"),
    ("shape_polygon", "⬡", "Polygon"),
    ("shape_line", "╱", "Line"),
    ("text", "A", "Text"),
    ("number", "#", "Number"),
    ("note", "N", "Note"),
    ("measure", "⌖", "Measure"),
]

SYMBOL_TOOLS = set(SYMBOL_LABELS)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def object_id() -> str:
    return f"obj_{uuid4().hex[:12]}"


def map_id() -> str:
    return f"map_{uuid4().hex[:10]}"


def nav_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


def json_clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def default_settings() -> dict[str, Any]:
    return {
        "width": 70,
        "height": 52,
        "cellSize": 18,
        "backgroundColor": BLUE,
        "gridColor": BLUE,
        "floorColor": WHITE,
        "textColor": BLUE,
        "selectionColor": SELECT,
        "legendColor": BLUE,
        "styleTemplate": "Blueprint",
        "showLegend": True,
        "cellScale": 10.0,
        "cellScaleUnit": "ft.",
        "snapToGrid": True,
        "snapStep": 1.0,
        "showMainGrid": True,
        "showSubGrid": True,
        "showCoordinates": False,
        "showZones": True,
        "showRuler": True,
        "snapToObjects": False,
        "defaultTextFont": "Arial",
        "defaultTextSize": 1.0,
        "defaultShapeLineWidth": 0.12,
        "defaultShapeStrokeColor": BLUE,
        "defaultSymbolSizePreset": DEFAULT_SYMBOL_SIZE_PRESET,
        "randomSymbolVariants": False,
        "defaultSymbolShadow": False,
        "defaultSymbolOutline": False,
        "recentTools": [],
        "numberStart": 1,
        "numberArea": "",
        "exportGrid": True,
        "vttPreset": "Generic",
        "exportAudience": "GM",
        "shortcuts": dict(DEFAULT_SHORTCUTS),
    }


def create_map_record(
    name: str,
    settings: dict[str, Any],
    layers: list[dict[str, Any]],
    objects: list[dict[str, Any]],
    campaign: dict[str, Any] | None = None,
    zones: list[dict[str, Any]] | None = None,
    markers: list[dict[str, Any]] | None = None,
    views: list[dict[str, Any]] | None = None,
    map_id_value: str | None = None,
) -> dict[str, Any]:
    return {
        "id": map_id_value or map_id(),
        "name": name.strip() or "Map",
        "settings": json_clone(settings),
        "layers": json_clone(layers),
        "objects": json_clone(objects),
        "campaign": json_clone(campaign or {"rooms": []}),
        "zones": json_clone(zones or []),
        "markers": json_clone(markers or []),
        "views": json_clone(views or []),
    }


def create_project() -> dict[str, Any]:
    settings = default_settings()
    layers = default_layers()
    objects = [legend_obj(settings)]
    campaign = {"rooms": []}
    map_record = create_map_record("Level 1", settings, layers, objects, campaign)
    return {
        "schemaVersion": CURRENT_SCHEMA_VERSION,
        "meta": {
            "title": "Untitled Dungeon",
            "author": "",
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        },
        "settings": settings,
        "layers": layers,
        "symbolFavorites": [],
        "objectTemplates": [],
        "customSymbolGroups": [{"name": CUSTOM_GROUP_NAME, "entries": []}],
        "customSymbols": {},
        "campaign": campaign,
        "objects": objects,
        "zones": [],
        "markers": [],
        "views": [],
        "maps": [map_record],
        "activeMapId": map_record["id"],
    }


def rect(kind: str, x: float, y: float, width: float, height: float) -> dict[str, Any]:
    obj = {"id": object_id(), "type": kind, "x": x, "y": y, "width": width, "height": height}
    if kind in {"room", "round", "cave"}:
        obj.update(campaign_room_fields())
    return obj


def diagonal_corridor(x: float, y: float, x2: float, y2: float) -> dict[str, Any]:
    return {"id": object_id(), "type": "diagonal_corridor", "x": x, "y": y, "x2": x2, "y2": y2, "width": 1}


def symbol(kind: str, x: float, y: float, size: float) -> dict[str, Any]:
    return {
        "id": object_id(),
        "type": "symbol",
        "kind": kind,
        "x": x,
        "y": y,
        "size": size,
        "variant": "",
        "sizePreset": "",
        "color": "",
        "opacity": 1.0,
        "shadow": False,
        "outline": False,
        "legendLabel": "",
    }


def shape(kind: str, x: float, y: float, width: float, height: float, x2: float | None = None, y2: float | None = None) -> dict[str, Any]:
    obj = {
        "id": object_id(),
        "type": "shape",
        "kind": kind,
        "x": x,
        "y": y,
        "lineWidth": 0.12,
        "strokeColor": "",
        "fillColor": "",
        "opacity": 1.0,
        "lineStyle": "solid",
        "curve": False,
        "arrow": "none",
        "rotation": 0.0,
        "layer": "shapes",
    }
    if kind == "line":
        obj["x2"] = x2 if x2 is not None else x + width
        obj["y2"] = y2 if y2 is not None else y + height
    else:
        obj["width"] = width
        obj["height"] = height
        if kind == "polygon":
            obj["points"] = [{"x": px, "y": py} for px, py in regular_polygon_points(x, y, width, height, 6)]
    return obj


def text_obj(value: str, x: float, y: float, size: float = 1.0) -> dict[str, Any]:
    return {
        "id": object_id(),
        "type": "text",
        "text": value,
        "x": x,
        "y": y,
        "size": size,
        "width": 0,
        "height": 0,
        "align": "center",
        "font": "Arial",
        "color": "",
        "export": True,
        "textRole": "text",
        "numberArea": "",
    }


def note_obj(value: str, x: float, y: float) -> dict[str, Any]:
    obj = text_obj(value, x, y, 0.9)
    obj["textRole"] = "note"
    obj["export"] = False
    obj["width"] = 8
    obj["align"] = "left"
    obj["layer"] = "notes"
    return obj


def legend_obj(settings: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": object_id(),
        "type": "legend",
        "x": 2,
        "y": settings["height"] + 1,
        "width": max(8, settings["width"] - 4),
        "height": 5,
        "columns": 4,
        "scale": 1.0,
        "manualEntries": [],
        "layer": "legend",
    }


def default_layers() -> list[dict[str, Any]]:
    return [{"id": layer_id, "name": name, "visible": True, "locked": layer_id == "background"} for layer_id, name in LAYER_DEFS]


def campaign_room_fields() -> dict[str, Any]:
    return {
        "roomNumber": "",
        "roomName": "",
        "description": "",
        "contents": "",
        "monsters": "",
        "treasure": "",
        "traps": "",
        "readAloud": "",
        "roomStatus": "undiscovered",
        "lootTable": "",
        "rumors": "",
        "clues": "",
        "secrets": "",
        "handoutText": "",
        "gmNotes": "",
        "playerVisible": True,
    }


def validate_settings(value: Any) -> dict[str, Any]:
    settings = default_settings()
    if isinstance(value, dict):
        settings.update(value)
    settings["width"] = max(12, int(settings.get("width") or 70))
    settings["height"] = max(12, int(settings.get("height") or 52))
    settings["cellSize"] = max(8, int(settings.get("cellSize") or 18))
    settings["backgroundColor"] = settings.get("backgroundColor") or BLUE
    settings["gridColor"] = settings.get("gridColor") or settings["backgroundColor"]
    settings["floorColor"] = settings.get("floorColor") or WHITE
    settings["textColor"] = settings.get("textColor") or settings["gridColor"]
    settings["selectionColor"] = settings.get("selectionColor") or SELECT
    settings["legendColor"] = settings.get("legendColor") or settings["gridColor"]
    settings["styleTemplate"] = settings.get("styleTemplate") or "Blueprint"
    settings["showLegend"] = bool(settings.get("showLegend", True))
    settings["cellScale"] = max(0.01, coerce_float(settings.get("cellScale"), 10.0))
    settings["cellScaleUnit"] = str(settings.get("cellScaleUnit") or "ft.").strip() or "ft."
    settings["snapToGrid"] = bool(settings.get("snapToGrid", True))
    settings["snapStep"] = normalize_snap_step(settings.get("snapStep", 1.0))
    settings["showMainGrid"] = bool(settings.get("showMainGrid", True))
    settings["showSubGrid"] = bool(settings.get("showSubGrid", True))
    settings["showCoordinates"] = bool(settings.get("showCoordinates", False))
    settings["showZones"] = bool(settings.get("showZones", True))
    settings["showRuler"] = bool(settings.get("showRuler", True))
    settings["snapToObjects"] = bool(settings.get("snapToObjects", False))
    settings["defaultTextFont"] = settings.get("defaultTextFont") or "Arial"
    settings["defaultTextSize"] = max(0.25, coerce_float(settings.get("defaultTextSize"), 1.0))
    settings["defaultShapeLineWidth"] = max(0.01, coerce_float(settings.get("defaultShapeLineWidth"), 0.12))
    settings["defaultShapeStrokeColor"] = settings.get("defaultShapeStrokeColor") or settings["gridColor"]
    settings["defaultSymbolSizePreset"] = str(settings.get("defaultSymbolSizePreset") or DEFAULT_SYMBOL_SIZE_PRESET)
    if settings["defaultSymbolSizePreset"] not in SYMBOL_SIZE_PRESETS:
        settings["defaultSymbolSizePreset"] = DEFAULT_SYMBOL_SIZE_PRESET
    settings["randomSymbolVariants"] = bool(settings.get("randomSymbolVariants", False))
    settings["defaultSymbolShadow"] = bool(settings.get("defaultSymbolShadow", False))
    settings["defaultSymbolOutline"] = bool(settings.get("defaultSymbolOutline", False))
    settings["recentTools"] = [str(tool) for tool in settings.get("recentTools", []) if str(tool)] if isinstance(settings.get("recentTools"), list) else []
    settings["recentTools"] = settings["recentTools"][:RECENT_TOOL_LIMIT]
    settings["numberStart"] = max(1, int(coerce_float(settings.get("numberStart"), 1)))
    settings["numberArea"] = str(settings.get("numberArea") or "")
    settings["exportGrid"] = bool(settings.get("exportGrid", True))
    settings["vttPreset"] = str(settings.get("vttPreset") or "Generic")
    settings["exportAudience"] = str(settings.get("exportAudience") or "GM")
    shortcuts = settings.get("shortcuts") if isinstance(settings.get("shortcuts"), dict) else {}
    settings["shortcuts"] = {**DEFAULT_SHORTCUTS, **{str(key): str(value) for key, value in shortcuts.items() if value}}
    return settings


def validate_project(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Dieses Projektformat wird nicht unterstuetzt.")
    if not isinstance(value.get("objects"), list) and isinstance(value.get("maps"), list) and value["maps"]:
        first_map = next((item for item in value["maps"] if isinstance(item, dict) and isinstance(item.get("objects"), list)), {})
        value["objects"] = json_clone(first_map.get("objects", []))
        value["settings"] = json_clone(first_map.get("settings", value.get("settings", {})))
        value["layers"] = json_clone(first_map.get("layers", value.get("layers", [])))
        value["campaign"] = json_clone(first_map.get("campaign", value.get("campaign", {})))
    if not isinstance(value.get("objects"), list):
        raise ValueError("Dieses Projektformat wird nicht unterstuetzt.")
    schema_version = int(value.get("schemaVersion") or 1)
    if schema_version > CURRENT_SCHEMA_VERSION:
        raise ValueError(f"Dieses Projektformat ist neuer als die App ({schema_version}).")
    settings = value.setdefault("settings", {})
    meta = value.setdefault("meta", {})
    meta.setdefault("title", "Imported Dungeon")
    meta.setdefault("author", "")
    meta.setdefault("createdAt", now_iso())
    meta["updatedAt"] = now_iso()
    value["settings"] = validate_settings(settings)
    settings = value["settings"]
    value["layers"] = validate_layers(value.get("layers"))
    value["symbolFavorites"] = [str(kind) for kind in value.get("symbolFavorites", [])]
    value["objectTemplates"] = validate_object_templates(value.get("objectTemplates", []))
    value["customSymbols"] = validate_custom_symbols(value.get("customSymbols", {}))
    value["customSymbolGroups"] = validate_custom_symbol_groups(value.get("customSymbolGroups", []), value["customSymbols"])
    value["objects"] = [validate_object(obj, index) for index, obj in enumerate(value["objects"], start=1)]
    ensure_legend_object(value)
    value["campaign"] = validate_campaign(value.get("campaign", {}), value["objects"])
    value["zones"] = validate_zones(value.get("zones", []))
    value["markers"] = validate_markers(value.get("markers", []))
    value["views"] = validate_views(value.get("views", []))
    if isinstance(value.get("maps"), list) and value["maps"]:
        active_id = str(value.get("activeMapId") or value["maps"][0].get("id") or "")
        for item in value["maps"]:
            if isinstance(item, dict) and str(item.get("id") or "") == active_id:
                item["settings"] = json_clone(value["settings"])
                item["layers"] = json_clone(value["layers"])
                item["objects"] = json_clone(value["objects"])
                item["campaign"] = json_clone(value["campaign"])
                item["zones"] = json_clone(value["zones"])
                item["markers"] = json_clone(value["markers"])
                item["views"] = json_clone(value["views"])
                break
    value["maps"] = validate_maps(value.get("maps"), value["settings"], value["layers"], value["objects"], value["campaign"], value["zones"], value["markers"], value["views"])
    active_id = str(value.get("activeMapId") or "")
    map_ids = {item["id"] for item in value["maps"]}
    if active_id not in map_ids:
        active_id = value["maps"][0]["id"]
    value["activeMapId"] = active_id
    active_map = next(item for item in value["maps"] if item["id"] == active_id)
    value["settings"] = json_clone(active_map["settings"])
    value["layers"] = json_clone(active_map["layers"])
    value["objects"] = json_clone(active_map["objects"])
    value["campaign"] = json_clone(active_map["campaign"])
    value["zones"] = json_clone(active_map["zones"])
    value["markers"] = json_clone(active_map["markers"])
    value["views"] = json_clone(active_map["views"])
    value["schemaVersion"] = CURRENT_SCHEMA_VERSION
    return value


def validate_campaign(value: Any, objects: list[dict[str, Any]]) -> dict[str, Any]:
    campaign = value if isinstance(value, dict) else {}
    room_records = {str(room.get("id")): dict(room) for room in campaign.get("rooms", []) if isinstance(room, dict) and room.get("id")}
    rooms = []
    for obj in objects:
        if obj.get("type") not in {"room", "round", "cave"}:
            continue
        record = room_records.get(obj["id"], {})
        for key, default in campaign_room_fields().items():
            obj[key] = obj.get(key, record.get(key, default))
        rooms.append(campaign_record_for_room(obj))
    return {
        "rooms": rooms,
        "encounterTable": str(campaign.get("encounterTable") or ""),
        "bookletNotes": str(campaign.get("bookletNotes") or ""),
    }


def validate_zones(value: Any) -> list[dict[str, Any]]:
    zones: list[dict[str, Any]] = []
    if not isinstance(value, list):
        return zones
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        width = max(0.25, coerce_float(item.get("width"), 1.0))
        height = max(0.25, coerce_float(item.get("height"), 1.0))
        zones.append(
            {
                "id": str(item.get("id") or nav_id("zone")),
                "name": str(item.get("name") or f"Zone {index}"),
                "x": coerce_float(item.get("x")),
                "y": coerce_float(item.get("y")),
                "width": width,
                "height": height,
                "color": str(item.get("color") or SELECT),
                "visible": bool(item.get("visible", True)),
                "encounterTable": str(item.get("encounterTable") or ""),
                "wallType": str(item.get("wallType") or "standard") if str(item.get("wallType") or "standard") in WALL_TYPES else "standard",
                "wallThickness": max(0.02, coerce_float(item.get("wallThickness"), 0.16)),
            }
        )
    return zones


def validate_markers(value: Any) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    if not isinstance(value, list):
        return markers
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        markers.append(
            {
                "id": str(item.get("id") or nav_id("mark")),
                "name": str(item.get("name") or f"Marker {index}"),
                "x": coerce_float(item.get("x")),
                "y": coerce_float(item.get("y")),
            }
        )
    return markers


def validate_views(value: Any) -> list[dict[str, Any]]:
    views: list[dict[str, Any]] = []
    if not isinstance(value, list):
        return views
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        views.append(
            {
                "id": str(item.get("id") or nav_id("view")),
                "name": str(item.get("name") or f"View {index}"),
                "x": coerce_float(item.get("x")),
                "y": coerce_float(item.get("y")),
                "zoom": max(0.35, min(2.2, coerce_float(item.get("zoom"), 0.9))),
            }
        )
    return views


def validate_map_record(
    value: Any,
    index: int,
    fallback_settings: dict[str, Any],
    fallback_layers: list[dict[str, Any]],
    fallback_objects: list[dict[str, Any]],
    fallback_campaign: dict[str, Any],
    fallback_zones: list[dict[str, Any]],
    fallback_markers: list[dict[str, Any]],
    fallback_views: list[dict[str, Any]],
) -> dict[str, Any]:
    record = value if isinstance(value, dict) else {}
    raw_settings = json_clone(fallback_settings)
    if isinstance(record.get("settings"), dict):
        raw_settings.update(record["settings"])
    settings = validate_settings(raw_settings)
    layers = validate_layers(record.get("layers", fallback_layers))
    raw_objects = record.get("objects") if isinstance(record.get("objects"), list) else fallback_objects
    objects = [validate_object(obj, item_index) for item_index, obj in enumerate(raw_objects, start=1)]
    map_project = {"settings": settings, "objects": objects}
    ensure_legend_object(map_project)
    objects = map_project["objects"]
    campaign = validate_campaign(record.get("campaign", fallback_campaign), objects)
    return {
        "id": str(record.get("id") or map_id()),
        "name": str(record.get("name") or f"Level {index}"),
        "settings": settings,
        "layers": layers,
        "objects": objects,
        "campaign": campaign,
        "zones": validate_zones(record.get("zones", fallback_zones)),
        "markers": validate_markers(record.get("markers", fallback_markers)),
        "views": validate_views(record.get("views", fallback_views)),
    }


def validate_maps(
    value: Any,
    root_settings: dict[str, Any],
    root_layers: list[dict[str, Any]],
    root_objects: list[dict[str, Any]],
    root_campaign: dict[str, Any],
    root_zones: list[dict[str, Any]],
    root_markers: list[dict[str, Any]],
    root_views: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        return [create_map_record("Level 1", root_settings, root_layers, root_objects, root_campaign, root_zones, root_markers, root_views)]
    maps = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value, start=1):
        fallback_objects = root_objects if index == 1 else [legend_obj(root_settings)]
        record = validate_map_record(item, index, root_settings, root_layers, fallback_objects, root_campaign, root_zones if index == 1 else [], root_markers if index == 1 else [], root_views if index == 1 else [])
        if record["id"] in seen_ids:
            record["id"] = map_id()
        seen_ids.add(record["id"])
        maps.append(record)
    return maps or [create_map_record("Level 1", root_settings, root_layers, root_objects, root_campaign, root_zones, root_markers, root_views)]


def validate_layers(value: Any) -> list[dict[str, Any]]:
    by_id = {layer["id"]: dict(layer) for layer in value if isinstance(layer, dict) and layer.get("id")} if isinstance(value, list) else {}
    layers = []
    for layer_id, name in LAYER_DEFS:
        layer = by_id.get(layer_id, {})
        layers.append(
            {
                "id": layer_id,
                "name": str(layer.get("name") or name),
                "visible": bool(layer.get("visible", True)),
                "locked": bool(layer.get("locked", layer_id == "background")),
            }
        )
    return layers


def validate_object_templates(value: Any) -> list[dict[str, Any]]:
    templates: list[dict[str, Any]] = []
    if not isinstance(value, list):
        return templates
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or f"Template {index}").strip()
        raw_objects = item.get("objects")
        if raw_objects is None and isinstance(item.get("object"), dict):
            raw_objects = [item["object"]]
        if not isinstance(raw_objects, list):
            continue
        objects: list[dict[str, Any]] = []
        for raw in raw_objects:
            try:
                objects.append(validate_object(raw, index))
            except ValueError:
                continue
        if objects:
            templates.append({"name": name or f"Template {index}", "objects": objects})
    return templates


def normalize_tags(value: Any) -> list[str]:
    if isinstance(value, str):
        raw = value.replace(",", " ").split()
    elif isinstance(value, list):
        raw = [str(item) for item in value]
    else:
        raw = []
    tags: list[str] = []
    for item in raw:
        tag = "".join(char.lower() if char.isalnum() else "-" for char in item.strip())
        tag = "-".join(part for part in tag.split("-") if part)
        if tag and tag not in tags:
            tags.append(tag)
    return tags


def validate_custom_symbol_variants(value: Any, default_label: str) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    if not isinstance(value, list):
        return variants
    used: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or f"{default_label} {index}").strip() or f"Variant {index}"
        variant_id = str(item.get("id") or safe_symbol_key(label)).strip()
        if not variant_id or variant_id in used:
            variant_id = f"variant_{index}"
        used.add(variant_id)
        variants.append(
            {
                "id": variant_id,
                "label": label,
                "sourceType": str(item.get("sourceType") or item.get("type") or "png").lower(),
                "path": str(item.get("path") or ""),
                "tags": normalize_tags(item.get("tags", [])),
            }
        )
    return variants


def validate_custom_symbols(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        return {}
    clean = {}
    for key, item in value.items():
        if not isinstance(item, dict):
            continue
        kind = str(key or "").strip()
        if not kind:
            kind = unique_custom_symbol_key(str(item.get("label") or "Custom Symbol"), clean)
        clean[kind] = {
            "label": str(item.get("label") or key),
            "legendLabel": str(item.get("legendLabel") or ""),
            "sourceType": str(item.get("sourceType") or item.get("type") or "png").lower(),
            "path": str(item.get("path") or ""),
            "tags": normalize_tags(item.get("tags", [])),
            "variants": validate_custom_symbol_variants(item.get("variants", []), str(item.get("label") or key)),
        }
    return clean


def validate_custom_symbol_groups(value: Any, custom_symbols: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    if isinstance(value, list):
        for group in value:
            if not isinstance(group, dict):
                continue
            entries = []
            for entry in group.get("entries", []):
                kind = entry.get("kind") if isinstance(entry, dict) else entry
                kind = str(kind or "")
                if kind in custom_symbols:
                    entries.append({"kind": kind, "icon": "◇", "label": custom_symbols[kind]["label"]})
            groups.append({"name": str(group.get("name") or CUSTOM_GROUP_NAME), "entries": entries})
    if not groups:
        groups.append({"name": CUSTOM_GROUP_NAME, "entries": []})
    return groups


def ensure_legend_object(project: dict[str, Any]) -> None:
    if any(obj.get("type") == "legend" for obj in project["objects"]):
        return
    project["objects"].append(legend_obj(project["settings"]))


def normalize_layer_id(value: Any, obj_type: str | None = None) -> str:
    layer_id = str(value or "")
    valid = {layer_id for layer_id, _name in LAYER_DEFS}
    if layer_id in valid:
        return layer_id
    if obj_type in {"room", "round", "cave"}:
        return "rooms"
    if obj_type in {"corridor", "diagonal_corridor"}:
        return "corridors"
    if obj_type == "symbol":
        return "symbols"
    if obj_type == "shape":
        return "shapes"
    if obj_type == "legend":
        return "legend"
    if obj_type == "text":
        return "text"
    return "symbols"


def normalize_snap_step(value: Any) -> float:
    try:
        step = float(value)
    except (TypeError, ValueError):
        return 1.0
    return min(SNAP_STEP_LABELS.values(), key=lambda allowed: abs(allowed - step))


def normalize_symbol_kind(kind: str) -> str:
    return LEGACY_SYMBOL_KINDS.get(kind, kind)


def coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate_shape_points(value: Any) -> list[dict[str, float]]:
    points: list[dict[str, float]] = []
    if not isinstance(value, list):
        return points
    for item in value:
        if isinstance(item, dict):
            points.append({"x": coerce_float(item.get("x")), "y": coerce_float(item.get("y"))})
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            points.append({"x": coerce_float(item[0]), "y": coerce_float(item[1])})
    return points


def bounds_from_points(points: list[dict[str, float]]) -> tuple[float, float, float, float]:
    if not points:
        return 0.0, 0.0, 0.25, 0.25
    xs = [point["x"] for point in points]
    ys = [point["y"] for point in points]
    left, top = min(xs), min(ys)
    right, bottom = max(xs), max(ys)
    return left, top, max(0.25, right - left), max(0.25, bottom - top)


def validate_object(obj: Any, index: int) -> dict[str, Any]:
    if not isinstance(obj, dict) or not obj.get("type"):
        raise ValueError(f"Objekt {index} ist ungueltig.")
    clean = dict(obj)
    clean["id"] = str(clean.get("id") or object_id())
    obj_type = clean["type"]
    if obj_type in RECTLIKE_TYPES:
        clean["x"] = coerce_float(clean.get("x"))
        clean["y"] = coerce_float(clean.get("y"))
        clean["width"] = max(0.25, coerce_float(clean.get("width"), 1.0))
        clean["height"] = max(0.25, coerce_float(clean.get("height"), 1.0))
        clean["wallThickness"] = max(0.02, coerce_float(clean.get("wallThickness"), 0.16))
        clean["wallType"] = str(clean.get("wallType") or "standard")
        if clean["wallType"] not in WALL_TYPES:
            clean["wallType"] = "standard"
        if obj_type == "cave":
            clean["seed"] = int(clean.get("seed") or 1)
        if obj_type in {"room", "round", "cave"}:
            for key, default in campaign_room_fields().items():
                if isinstance(default, bool):
                    clean[key] = bool(clean.get(key, default))
                else:
                    clean[key] = str(clean.get(key, default) or "")
            if clean["roomStatus"] not in ROOM_STATUSES:
                clean["roomStatus"] = "undiscovered"
    elif obj_type == "diagonal_corridor":
        clean["x"] = coerce_float(clean.get("x"))
        clean["y"] = coerce_float(clean.get("y"))
        clean["x2"] = coerce_float(clean.get("x2"), clean["x"] + 1)
        clean["y2"] = coerce_float(clean.get("y2"), clean["y"] + 1)
        clean["width"] = max(0.25, coerce_float(clean.get("width"), 1.0))
        clean["wallThickness"] = max(0.02, coerce_float(clean.get("wallThickness"), 0.16))
        clean["wallType"] = str(clean.get("wallType") or "standard")
        if clean["wallType"] not in WALL_TYPES:
            clean["wallType"] = "standard"
    elif obj_type == "symbol":
        clean["kind"] = normalize_symbol_kind(str(clean.get("kind") or "door"))
        clean["x"] = coerce_float(clean.get("x"))
        clean["y"] = coerce_float(clean.get("y"))
        clean["size"] = max(0.25, coerce_float(clean.get("size"), 1.0))
        clean["variant"] = str(clean.get("variant") or "")
        clean["sizePreset"] = str(clean.get("sizePreset") or "")
        if clean["sizePreset"] and clean["sizePreset"] not in SYMBOL_SIZE_PRESETS:
            clean["sizePreset"] = ""
        clean["color"] = str(clean.get("color") or "")
        clean["opacity"] = max(0.0, min(1.0, coerce_float(clean.get("opacity"), 1.0)))
        clean["shadow"] = bool(clean.get("shadow", False))
        clean["outline"] = bool(clean.get("outline", False))
        clean["legendLabel"] = str(clean.get("legendLabel") or "")
        clean["rotation"] = coerce_float(clean.get("rotation"), 0.0) % 360
        clean["targetMapId"] = str(clean.get("targetMapId") or "")
        clean["targetObjectId"] = str(clean.get("targetObjectId") or "")
        clean["linkLabel"] = str(clean.get("linkLabel") or "")
        clean["rumors"] = str(clean.get("rumors") or "")
        clean["clues"] = str(clean.get("clues") or "")
        clean["secrets"] = str(clean.get("secrets") or "")
        clean["handoutText"] = str(clean.get("handoutText") or "")
        clean["gmNotes"] = str(clean.get("gmNotes") or "")
        clean.setdefault("layer", "symbols")
    elif obj_type == "shape":
        clean["kind"] = str(clean.get("kind") or "rectangle")
        if clean["kind"] == "rect":
            clean["kind"] = "rectangle"
        if clean["kind"] not in SHAPE_KINDS:
            clean["kind"] = "rectangle"
        clean["x"] = coerce_float(clean.get("x"))
        clean["y"] = coerce_float(clean.get("y"))
        clean["lineWidth"] = max(0.01, coerce_float(clean.get("lineWidth"), 0.12))
        clean["strokeColor"] = str(clean.get("strokeColor") or clean.get("foregroundColor") or "")
        clean["fillColor"] = str(clean.get("fillColor") or clean.get("backgroundColor") or "")
        clean["opacity"] = max(0.0, min(1.0, coerce_float(clean.get("opacity"), 1.0)))
        clean["lineStyle"] = str(clean.get("lineStyle") or "solid").lower()
        if clean["lineStyle"] not in LINE_STYLES:
            clean["lineStyle"] = "solid"
        clean["curve"] = bool(clean.get("curve", False))
        clean["arrow"] = str(clean.get("arrow") or "none").lower()
        if clean["arrow"] not in ARROW_STYLES:
            clean["arrow"] = "none"
        clean["rotation"] = coerce_float(clean.get("rotation"), 0.0) % 360
        if clean["kind"] == "line":
            clean["x2"] = coerce_float(clean.get("x2"), clean["x"] + 1)
            clean["y2"] = coerce_float(clean.get("y2"), clean["y"])
        else:
            clean["width"] = max(0.25, coerce_float(clean.get("width"), 1.0))
            clean["height"] = max(0.25, coerce_float(clean.get("height"), 1.0))
            if clean["kind"] == "polygon":
                points = validate_shape_points(clean.get("points"))
                if len(points) < 3:
                    sides = max(3, min(24, int(coerce_float(clean.get("sides"), 6))))
                    points = [{"x": px, "y": py} for px, py in regular_polygon_points(clean["x"], clean["y"], clean["width"], clean["height"], sides)]
                clean["points"] = points
                clean["x"], clean["y"], clean["width"], clean["height"] = bounds_from_points(points)
                clean.pop("sides", None)
        clean.setdefault("layer", "shapes")
    elif obj_type == "text":
        clean["text"] = str(clean.get("text", ""))
        clean["x"] = coerce_float(clean.get("x"))
        clean["y"] = coerce_float(clean.get("y"))
        clean["size"] = max(0.25, coerce_float(clean.get("size"), 1.0))
        clean["width"] = max(0.0, coerce_float(clean.get("width"), 0.0))
        clean["height"] = max(0.0, coerce_float(clean.get("height"), 0.0))
        clean["align"] = clean.get("align") or "center"
        clean["font"] = str(clean.get("font") or "Arial")
        clean["color"] = str(clean.get("color") or "")
        clean["rotation"] = coerce_float(clean.get("rotation"), 0.0) % 360
        clean["export"] = bool(clean.get("export", True))
        clean["textRole"] = str(clean.get("textRole") or "text")
        clean["numberArea"] = str(clean.get("numberArea") or "")
        clean["roomId"] = str(clean.get("roomId") or "")
        clean.setdefault("layer", "notes" if clean["textRole"] == "note" or not clean["export"] else "text")
    elif obj_type == "legend":
        clean["x"] = coerce_float(clean.get("x"), 2)
        clean["y"] = coerce_float(clean.get("y"), 53)
        clean["width"] = max(4, coerce_float(clean.get("width"), 20))
        clean["height"] = max(2, coerce_float(clean.get("height"), 5))
        clean["columns"] = max(1, int(coerce_float(clean.get("columns"), 4)))
        clean["scale"] = max(0.35, coerce_float(clean.get("scale"), 1.0))
        manual = clean.get("manualEntries", [])
        if isinstance(manual, str):
            manual = [item.strip() for item in manual.split(";") if item.strip()]
        clean["manualEntries"] = [str(item) for item in manual] if isinstance(manual, list) else []
        clean.setdefault("layer", "legend")
    else:
        raise ValueError(f"Objekt {index} hat einen unbekannten Typ: {obj_type}.")
    if clean.get("group") is not None:
        clean["group"] = str(clean["group"])
    clean["locked"] = bool(clean.get("locked", False))
    clean["layer"] = normalize_layer_id(clean.get("layer"), obj_type)
    return clean


@dataclass
class Draft:
    kind: str
    x: float
    y: float
    width: float
    height: float
    x2: float | None = None
    y2: float | None = None
    points: list[tuple[float, float]] | None = None


@dataclass
class HistoryCommand:
    description: str
    before: dict[str, Any]
    after: dict[str, Any]


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, _event: tk.Event | None = None) -> None:
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        y = self.widget.winfo_rooty() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tip,
            text=self.text,
            background="#17384a",
            foreground="#ffffff",
            borderwidth=0,
            padx=8,
            pady=4,
            font=("Segoe UI", 9),
        )
        label.pack()

    def hide(self, _event: tk.Event | None = None) -> None:
        if self.tip:
            self.tip.destroy()
            self.tip = None


class SymbolPreview:
    def __init__(self, widget: tk.Widget, app: "OSRMapMaker", kind: str, label: str) -> None:
        self.widget = widget
        self.app = app
        self.kind = kind
        self.label = label
        self.tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, _event: tk.Event | None = None) -> None:
        if self.tip:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        y = self.widget.winfo_rooty() + 34
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        canvas = tk.Canvas(self.tip, width=128, height=112, bg="#f9fcfd", highlightthickness=1, highlightbackground="#9bb8c4")
        canvas.pack()
        draw_symbol_preview_canvas(canvas, self.app.project, self.kind, self.label)

    def hide(self, _event: tk.Event | None = None) -> None:
        if self.tip:
            self.tip.destroy()
            self.tip = None


class OSRMapMaker(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("OSR Map Maker")
        self.geometry("1280x860")
        self.minsize(1050, 720)

        self.project = create_project()
        self.tool = tk.StringVar(value="select")
        self.zoom = tk.DoubleVar(value=0.9)
        self.export_format = tk.StringVar(value="png")
        self.export_scale = tk.IntVar(value=2)
        self.selected_id: str | None = None
        self.selected_ids: set[str] = set()
        self.draft: Draft | None = None
        self.drag_start: tuple[float, float, dict[str, Any] | None] | None = None
        self.drag_snapshot: dict[str, Any] | None = None
        self.drag_mode: str | None = None
        self.drag_handle: str | None = None
        self.drag_originals: dict[str, dict[str, Any]] = {}
        self.selection_box: tuple[float, float, float, float] | None = None
        self.is_panning = False
        self.history: list[HistoryCommand] = []
        self.future: list[HistoryCommand] = []
        self.current_file: Path | None = None
        self.tool_buttons: dict[str, tk.Button] = {}
        self.group_buttons: dict[str, tk.Button] = {}
        self.active_symbol_group = tk.StringVar(value=SYMBOL_GROUPS[0][0])
        self.symbol_search_var = tk.StringVar(value="")
        self.symbol_favorites_only_var = tk.BooleanVar(value=False)
        self.symbol_random_variant_var = tk.BooleanVar(value=self.settings.get("randomSymbolVariants", False))
        self.symbol_size_preset_var = tk.StringVar(value=self.settings.get("defaultSymbolSizePreset", DEFAULT_SYMBOL_SIZE_PRESET))
        self.symbol_panel: ttk.Frame | None = None
        self.symbol_group_frame: ttk.Frame | None = None
        self.recent_tools_frame: ttk.Frame | None = None
        self.clipboard_objects: list[dict[str, Any]] = []
        self.selected_polygon_point: int | None = None
        self.preview_photo: Any = None
        self.canvas_image_refs: list[Any] = []
        self.measure_points: list[tuple[float, float]] = []
        self.measure_preview: tuple[float, float] | None = None

        self.status = tk.StringVar(value="Ready")
        self.error_status = tk.StringVar(value="")
        self.mouse_grid: tuple[float, float] | None = None
        self.context_menu: tk.Menu | None = None
        self.minimap_photo: Any = None
        self.map_var = tk.StringVar(value=self.active_map_name())
        self.title_var = tk.StringVar(value=self.project["meta"]["title"])
        self.width_var = tk.IntVar(value=self.settings["width"])
        self.height_var = tk.IntVar(value=self.settings["height"])
        self.cell_var = tk.IntVar(value=self.settings["cellSize"])
        self.legend_var = tk.BooleanVar(value=self.settings["showLegend"])
        self.cell_scale_var = tk.DoubleVar(value=self.settings.get("cellScale", 10.0))
        self.cell_scale_unit_var = tk.StringVar(value=self.settings.get("cellScaleUnit", "ft."))
        self.snap_var = tk.BooleanVar(value=self.settings["snapToGrid"])
        self.snap_step_var = tk.StringVar(value=snap_step_label(self.settings["snapStep"]))
        self.main_grid_var = tk.BooleanVar(value=self.settings["showMainGrid"])
        self.sub_grid_var = tk.BooleanVar(value=self.settings["showSubGrid"])
        self.coordinate_var = tk.BooleanVar(value=self.settings.get("showCoordinates", False))
        self.zone_overlay_var = tk.BooleanVar(value=self.settings.get("showZones", True))
        self.ruler_overlay_var = tk.BooleanVar(value=self.settings.get("showRuler", True))
        self.snap_objects_var = tk.BooleanVar(value=self.settings["snapToObjects"])
        self.style_var = tk.StringVar(value=self.settings["styleTemplate"])
        self.export_grid_var = tk.BooleanVar(value=self.settings.get("exportGrid", True))
        self.vtt_preset_var = tk.StringVar(value=self.settings.get("vttPreset", "Generic"))
        self.export_audience_var = tk.StringVar(value=self.settings.get("exportAudience", "GM"))
        self.text_font_var = tk.StringVar(value=self.settings["defaultTextFont"])
        self.text_size_var = tk.DoubleVar(value=self.settings["defaultTextSize"])
        self.shape_line_width_var = tk.DoubleVar(value=self.settings.get("defaultShapeLineWidth", 0.12))
        self.number_start_var = tk.IntVar(value=self.settings["numberStart"])
        self.number_area_var = tk.StringVar(value=self.settings["numberArea"])
        self.shortcuts = dict(self.settings.get("shortcuts", DEFAULT_SHORTCUTS))
        self.current_layer_var = tk.StringVar(value="Symbols")
        self.layer_visible_vars: dict[str, tk.BooleanVar] = {}
        self.layer_locked_vars: dict[str, tk.BooleanVar] = {}
        self.object_search_var = tk.StringVar(value="")
        self.object_type_filter_var = tk.StringVar(value="All")
        self.object_layer_filter_var = tk.StringVar(value="All")
        self.object_list_ids: list[str] = []
        self.nav_list_items: list[tuple[str, str]] = []
        self.link_target_map_var = tk.StringVar(value="")
        self.object_listbox: tk.Listbox | None = None
        self.navigator_listbox: tk.Listbox | None = None
        self.map_combo: ttk.Combobox | None = None

        self._build_ui()
        self._bind_events()
        self.redraw()

    @property
    def settings(self) -> dict[str, Any]:
        return self.project["settings"]

    @property
    def cell(self) -> float:
        return self.settings["cellSize"] * self.zoom.get()

    def maps(self) -> list[dict[str, Any]]:
        maps = self.project.setdefault("maps", [])
        if not maps:
            maps.append(create_map_record("Level 1", self.settings, self.project.get("layers", default_layers()), self.project.get("objects", []), self.project.get("campaign", {"rooms": []})))
            self.project["activeMapId"] = maps[0]["id"]
        return maps

    def active_map_record(self) -> dict[str, Any]:
        active_id = self.project.get("activeMapId")
        for record in self.maps():
            if record.get("id") == active_id:
                return record
        record = self.maps()[0]
        self.project["activeMapId"] = record["id"]
        return record

    def active_map_name(self) -> str:
        return str(self.active_map_record().get("name") or "Level 1")

    def sync_active_map_storage(self) -> None:
        if not hasattr(self, "project") or not isinstance(self.project, dict):
            return
        record = self.active_map_record()
        record["settings"] = json_clone(self.project.get("settings", default_settings()))
        record["layers"] = json_clone(self.project.get("layers", default_layers()))
        record["objects"] = json_clone(self.project.get("objects", []))
        record["campaign"] = json_clone(self.project.get("campaign", {"rooms": []}))
        record["zones"] = json_clone(self.project.get("zones", []))
        record["markers"] = json_clone(self.project.get("markers", []))
        record["views"] = json_clone(self.project.get("views", []))

    def load_map_record(self, record: dict[str, Any]) -> None:
        self.project["activeMapId"] = record["id"]
        self.project["settings"] = json_clone(record["settings"])
        self.project["layers"] = json_clone(record["layers"])
        self.project["objects"] = json_clone(record["objects"])
        self.project["campaign"] = json_clone(record.get("campaign", {"rooms": []}))
        self.project["zones"] = json_clone(record.get("zones", []))
        self.project["markers"] = json_clone(record.get("markers", []))
        self.project["views"] = json_clone(record.get("views", []))

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=(8, 6))
        top.grid(row=0, column=0, columnspan=3, sticky="ew")
        ttk.Label(top, text="OSR Map Maker", font=("Segoe UI", 15, "bold")).pack(side="left", padx=(0, 12))
        for label, command in [
            ("New", self.new_project),
            ("Save", self.save_project),
            ("Load", self.load_project),
            ("Undo", self.undo),
            ("Redo", self.redo),
        ]:
            ttk.Button(top, text=label, command=command).pack(side="left", padx=2)
        ttk.Label(top, text="Zoom").pack(side="left", padx=(12, 4))
        ttk.Scale(top, from_=0.35, to=2.2, variable=self.zoom, command=lambda _v: self.redraw()).pack(side="left", fill="x", expand=True, padx=4)
        ttk.Combobox(top, textvariable=self.export_format, values=("png", "jpeg", "webp", "pdf", "svg"), width=6, state="readonly").pack(side="left", padx=2)
        ttk.Combobox(top, textvariable=self.export_scale, values=(1, 2, 3, 4), width=4, state="readonly").pack(side="left", padx=2)
        ttk.Button(top, text="Export", command=self.export_image).pack(side="left", padx=2)
        ttk.Button(top, text="Player Export", command=lambda: self.quick_export_audience("Player")).pack(side="left", padx=2)
        ttk.Button(top, text="GM Export", command=lambda: self.quick_export_audience("GM")).pack(side="left", padx=2)

        toolbar_outer = ttk.Frame(self, padding=8, width=236)
        toolbar_outer.grid(row=1, column=0, sticky="ns")
        toolbar_outer.grid_propagate(False)
        toolbar_outer.columnconfigure(0, weight=1)
        self._build_toolbar(toolbar_outer)

        canvas_frame = ttk.Frame(self)
        canvas_frame.grid(row=1, column=1, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(canvas_frame, bg="#c6dce4", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.minimap = tk.Canvas(canvas_frame, width=180, height=130, bg="#eef6f8", highlightthickness=1, highlightbackground="#7fa7b5")
        self.minimap.place(relx=1.0, rely=1.0, x=-18, y=-18, anchor="se")
        self.minimap.bind("<ButtonPress-1>", self.on_minimap_press)
        y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        inspector = ttk.Frame(self, padding=12)
        inspector.grid(row=1, column=2, sticky="nsew")
        inspector.columnconfigure(0, weight=1)
        inspector.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(inspector)
        notebook.grid(row=0, column=0, sticky="nsew")

        map_tab = ttk.Frame(notebook, padding=8)
        map_tab.columnconfigure(0, weight=1)
        notebook.add(map_tab, text="Map")
        ttk.Label(map_tab, text="Map", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        self._entry(map_tab, "Title", self.title_var, 1)
        self._entry(map_tab, "Width", self.width_var, 2)
        self._entry(map_tab, "Height", self.height_var, 3)
        self._entry(map_tab, "Cell", self.cell_var, 4)
        self._scale_entry(map_tab, 5)
        ttk.Checkbutton(map_tab, text="Legend", variable=self.legend_var, command=self.apply_settings).grid(row=6, column=0, sticky="w", pady=4)
        style_row = ttk.Frame(map_tab)
        style_row.grid(row=7, column=0, sticky="ew", pady=2)
        style_row.columnconfigure(1, weight=1)
        ttk.Label(style_row, text="Style", width=8).grid(row=0, column=0, sticky="w")
        ttk.Combobox(style_row, textvariable=self.style_var, values=tuple(STYLE_TEMPLATES), state="readonly", width=16).grid(row=0, column=1, sticky="ew")
        ttk.Button(style_row, text="Apply", command=self.apply_style_template).grid(row=0, column=2, padx=(4, 0))
        for offset, (label, key) in enumerate(
            [
                ("Background", "backgroundColor"),
                ("Floor", "floorColor"),
                ("Line", "gridColor"),
                ("Text", "textColor"),
                ("Selection", "selectionColor"),
                ("Legend", "legendColor"),
            ],
            start=8,
        ):
            ttk.Button(map_tab, text=f"{label} color", command=lambda value=key: self.pick_color(value)).grid(row=offset, column=0, sticky="ew", pady=1)
        ttk.Separator(map_tab).grid(row=14, column=0, sticky="ew", pady=8)
        ttk.Label(map_tab, text="Snap & Grid", font=("Segoe UI", 11, "bold")).grid(row=15, column=0, sticky="w")
        ttk.Checkbutton(map_tab, text="Snap to grid", variable=self.snap_var, command=self.apply_settings).grid(row=16, column=0, sticky="w")
        snap_row = ttk.Frame(map_tab)
        snap_row.grid(row=17, column=0, sticky="ew", pady=2)
        snap_row.columnconfigure(1, weight=1)
        ttk.Label(snap_row, text="Step", width=8).grid(row=0, column=0, sticky="w")
        snap_combo = ttk.Combobox(snap_row, textvariable=self.snap_step_var, values=tuple(SNAP_STEP_LABELS), width=10, state="readonly")
        snap_combo.grid(row=0, column=1, sticky="ew")
        snap_combo.bind("<<ComboboxSelected>>", lambda _e: self.apply_settings())
        ttk.Checkbutton(map_tab, text="Main grid", variable=self.main_grid_var, command=self.apply_settings).grid(row=18, column=0, sticky="w")
        ttk.Checkbutton(map_tab, text="Subgrid", variable=self.sub_grid_var, command=self.apply_settings).grid(row=19, column=0, sticky="w")
        overlay_opts = ttk.Frame(map_tab)
        overlay_opts.grid(row=20, column=0, sticky="ew")
        ttk.Checkbutton(overlay_opts, text="Snap to object edges", variable=self.snap_objects_var, command=self.apply_settings).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(overlay_opts, text="Coordinates", variable=self.coordinate_var, command=self.apply_settings).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(overlay_opts, text="Zones", variable=self.zone_overlay_var, command=self.apply_settings).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(overlay_opts, text="Ruler", variable=self.ruler_overlay_var, command=self.apply_settings).grid(row=3, column=0, sticky="w")
        ttk.Separator(map_tab).grid(row=21, column=0, sticky="ew", pady=8)
        ttk.Label(map_tab, text="Text Defaults", font=("Segoe UI", 11, "bold")).grid(row=22, column=0, sticky="w")
        self._entry(map_tab, "Font", self.text_font_var, 23)
        self._entry(map_tab, "Size", self.text_size_var, 24)
        self._entry(map_tab, "Start", self.number_start_var, 25)
        self._entry(map_tab, "Area", self.number_area_var, 26)
        self._entry(map_tab, "Shape W", self.shape_line_width_var, 27)
        ttk.Button(map_tab, text="Shape line color", command=lambda: self.pick_color("defaultShapeStrokeColor")).grid(row=28, column=0, sticky="ew", pady=1)
        ttk.Separator(map_tab).grid(row=29, column=0, sticky="ew", pady=8)
        ttk.Label(map_tab, text="Procedural", font=("Segoe UI", 11, "bold")).grid(row=30, column=0, sticky="w")
        proc = ttk.Frame(map_tab)
        proc.grid(row=31, column=0, sticky="ew")
        proc.columnconfigure(0, weight=1)
        proc.columnconfigure(1, weight=1)
        for index, (label, command) in enumerate(
            [
                ("Random rooms", self.generate_random_rooms),
                ("Random corridors", self.generate_random_corridors),
                ("Suggest links", self.suggest_room_connections),
                ("Roughen caves", self.roughen_caves),
                ("Generate dungeon", self.generate_dungeon),
                ("Keyword dungeon", self.generate_keyword_dungeon),
                ("Natural caves", self.generate_natural_caves),
                ("Check walls", self.check_auto_walls),
                ("Auto doors", self.auto_place_doors),
                ("Auto walls", self.auto_wall_styles),
                ("Patrol routes", self.generate_patrol_routes),
                ("Room report", self.export_campaign_report),
            ]
        ):
            ttk.Button(proc, text=label, command=command).grid(row=index // 2, column=index % 2, sticky="ew", padx=1, pady=1)
        export_opts = ttk.Frame(map_tab)
        export_opts.grid(row=32, column=0, sticky="ew", pady=(8, 0))
        export_opts.columnconfigure(1, weight=1)
        ttk.Checkbutton(export_opts, text="Export grid", variable=self.export_grid_var, command=self.apply_settings).grid(row=0, column=0, sticky="w")
        ttk.Label(export_opts, text="VTT").grid(row=1, column=0, sticky="w")
        preset = ttk.Combobox(export_opts, textvariable=self.vtt_preset_var, values=("Generic", "Foundry", "Roll20"), state="readonly", width=10)
        preset.grid(row=1, column=1, sticky="ew")
        preset.bind("<<ComboboxSelected>>", lambda _e: self.apply_vtt_preset())
        ttk.Label(export_opts, text="Audience").grid(row=2, column=0, sticky="w")
        audience = ttk.Combobox(export_opts, textvariable=self.export_audience_var, values=("GM", "Player"), state="readonly", width=10)
        audience.grid(row=2, column=1, sticky="ew")
        audience.bind("<<ComboboxSelected>>", lambda _e: self.apply_settings())
        ttk.Button(export_opts, text="Shortcuts", command=self.open_shortcuts_dialog).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Separator(map_tab).grid(row=33, column=0, sticky="ew", pady=8)
        self.maps_frame = ttk.Frame(map_tab)
        self.maps_frame.grid(row=34, column=0, sticky="ew")
        self.maps_frame.columnconfigure(0, weight=1)
        self.rebuild_maps_panel()

        layers_tab = ttk.Frame(notebook, padding=8)
        layers_tab.columnconfigure(0, weight=1)
        notebook.add(layers_tab, text="Layers")
        self.layers_frame = ttk.Frame(layers_tab)
        self.layers_frame.grid(row=0, column=0, sticky="ew")
        self.rebuild_layers_panel()

        selection_tab = ttk.Frame(notebook, padding=8)
        selection_tab.columnconfigure(0, weight=1)
        notebook.add(selection_tab, text="Selection")
        ttk.Label(selection_tab, text="Selection", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.selection_frame = ttk.Frame(selection_tab)
        self.selection_frame.grid(row=1, column=0, sticky="ew")

        campaign_tab = ttk.Frame(notebook, padding=8)
        campaign_tab.columnconfigure(0, weight=1)
        notebook.add(campaign_tab, text="Campaign")
        ttk.Label(campaign_tab, text="Rooms & Campaign", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        campaign_actions = ttk.Frame(campaign_tab)
        campaign_actions.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        campaign_actions.columnconfigure(0, weight=1)
        campaign_actions.columnconfigure(1, weight=1)
        for index, (label, command) in enumerate(
            [
                ("Room form", self.open_room_form),
                ("Renumber", self.renumber_rooms),
                ("Find gaps", self.find_room_number_gaps),
                ("Encounters", self.open_encounters_dialog),
                ("Random contents", self.randomize_room_contents),
                ("GM booklet", self.export_gm_booklet),
            ]
        ):
            ttk.Button(campaign_actions, text=label, command=command).grid(row=index // 2, column=index % 2, sticky="ew", padx=1, pady=1)

        objects_tab = ttk.Frame(notebook, padding=8)
        objects_tab.columnconfigure(0, weight=1)
        objects_tab.rowconfigure(3, weight=1)
        notebook.add(objects_tab, text="Objects")
        ttk.Label(objects_tab, text="Objects", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        object_search = ttk.Entry(objects_tab, textvariable=self.object_search_var)
        object_search.grid(row=1, column=0, sticky="ew", pady=(2, 4))
        object_search.bind("<KeyRelease>", lambda _e: self.refresh_object_list())
        filters = ttk.Frame(objects_tab)
        filters.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        filters.columnconfigure(0, weight=1)
        filters.columnconfigure(1, weight=1)
        self.object_type_combo = ttk.Combobox(filters, textvariable=self.object_type_filter_var, values=("All", "room", "corridor", "diagonal_corridor", "round", "cave", "symbol", "shape", "text", "legend"), state="readonly", width=12)
        self.object_type_combo.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.object_type_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_object_list())
        self.object_layer_combo = ttk.Combobox(filters, textvariable=self.object_layer_filter_var, values=("All",), state="readonly", width=12)
        self.object_layer_combo.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        self.object_layer_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_object_list())
        object_list_frame = ttk.Frame(objects_tab)
        object_list_frame.grid(row=3, column=0, sticky="nsew")
        object_list_frame.columnconfigure(0, weight=1)
        object_list_frame.rowconfigure(0, weight=1)
        self.object_listbox = tk.Listbox(object_list_frame, height=16, exportselection=False)
        self.object_listbox.grid(row=0, column=0, sticky="nsew")
        self.object_listbox.bind("<<ListboxSelect>>", self.on_object_list_select)
        self.object_listbox.bind("<Double-Button-1>", lambda _e: self.jump_to_selected_object())
        object_scroll = ttk.Scrollbar(object_list_frame, orient="vertical", command=self.object_listbox.yview)
        object_scroll.grid(row=0, column=1, sticky="ns")
        self.object_listbox.configure(yscrollcommand=object_scroll.set)
        ttk.Button(objects_tab, text="Show selected", command=self.jump_to_selected_object).grid(row=4, column=0, sticky="ew", pady=(6, 0))

        nav_tab = ttk.Frame(notebook, padding=8)
        nav_tab.columnconfigure(0, weight=1)
        nav_tab.rowconfigure(2, weight=1)
        notebook.add(nav_tab, text="Nav")
        ttk.Label(nav_tab, text="Navigator", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        nav_actions = ttk.Frame(nav_tab)
        nav_actions.grid(row=1, column=0, sticky="ew", pady=(2, 4))
        nav_actions.columnconfigure(0, weight=1)
        nav_actions.columnconfigure(1, weight=1)
        ttk.Button(nav_actions, text="Save view", command=self.save_current_view).grid(row=0, column=0, sticky="ew", padx=(0, 2), pady=1)
        ttk.Button(nav_actions, text="Add marker", command=self.add_jump_marker).grid(row=0, column=1, sticky="ew", padx=(2, 0), pady=1)
        ttk.Button(nav_actions, text="Zone from selection", command=self.define_zone_from_selection).grid(row=1, column=0, sticky="ew", padx=(0, 2), pady=1)
        ttk.Button(nav_actions, text="Clear measure", command=self.clear_measurement).grid(row=1, column=1, sticky="ew", padx=(2, 0), pady=1)
        nav_list_frame = ttk.Frame(nav_tab)
        nav_list_frame.grid(row=2, column=0, sticky="nsew")
        nav_list_frame.columnconfigure(0, weight=1)
        nav_list_frame.rowconfigure(0, weight=1)
        self.navigator_listbox = tk.Listbox(nav_list_frame, height=12, exportselection=False)
        self.navigator_listbox.grid(row=0, column=0, sticky="nsew")
        self.navigator_listbox.bind("<Double-Button-1>", lambda _e: self.jump_to_nav_item())
        nav_scroll = ttk.Scrollbar(nav_list_frame, orient="vertical", command=self.navigator_listbox.yview)
        nav_scroll.grid(row=0, column=1, sticky="ns")
        self.navigator_listbox.configure(yscrollcommand=nav_scroll.set)
        nav_buttons = ttk.Frame(nav_tab)
        nav_buttons.grid(row=3, column=0, sticky="ew", pady=(6, 4))
        nav_buttons.columnconfigure(0, weight=1)
        nav_buttons.columnconfigure(1, weight=1)
        ttk.Button(nav_buttons, text="Jump", command=self.jump_to_nav_item).grid(row=0, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(nav_buttons, text="Delete", command=self.delete_nav_item).grid(row=0, column=1, sticky="ew", padx=(2, 0))
        link_frame = ttk.LabelFrame(nav_tab, text="Floor link", padding=4)
        link_frame.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        link_frame.columnconfigure(0, weight=1)
        self.link_target_combo = ttk.Combobox(link_frame, textvariable=self.link_target_map_var, state="readonly")
        self.link_target_combo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        ttk.Button(link_frame, text="Link selected", command=self.link_selected_to_map).grid(row=1, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(link_frame, text="Follow", command=self.follow_selected_link).grid(row=1, column=1, sticky="ew", padx=(2, 0))
        self.rebuild_navigator_panel()

        status = ttk.Frame(self, padding=(8, 4))
        status.grid(row=2, column=0, columnspan=3, sticky="ew")
        ttk.Label(status, textvariable=self.status).pack(side="left")
        ttk.Label(status, textvariable=self.error_status, foreground="#a12b2b").pack(side="right")

    def _entry(self, parent: ttk.Frame, label: str, variable: tk.Variable, row: int) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=2)
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text=label, width=8).grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=variable)
        entry.grid(row=0, column=1, sticky="ew")
        entry.bind("<Return>", lambda _e: self.apply_settings())
        entry.bind("<FocusOut>", lambda _e: self.apply_settings())

    def _scale_entry(self, parent: ttk.Frame, row: int) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=2)
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Scale", width=8).grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.cell_scale_var, width=8)
        entry.grid(row=0, column=1, sticky="ew")
        unit = ttk.Combobox(frame, textvariable=self.cell_scale_unit_var, values=CELL_SCALE_UNITS, width=6)
        unit.grid(row=0, column=2, sticky="ew", padx=(4, 0))
        entry.bind("<Return>", lambda _e: self.apply_settings())
        entry.bind("<FocusOut>", lambda _e: self.apply_settings())
        unit.bind("<Return>", lambda _e: self.apply_settings())
        unit.bind("<FocusOut>", lambda _e: self.apply_settings())
        unit.bind("<<ComboboxSelected>>", lambda _e: self.apply_settings())

    def map_option(self, record: dict[str, Any]) -> str:
        return f"{record.get('name', 'Map')} [{str(record.get('id', ''))[-4:]}]"

    def map_from_option(self, value: str) -> dict[str, Any] | None:
        for record in self.maps():
            if self.map_option(record) == value:
                return record
        return next((record for record in self.maps() if record.get("name") == value), None)

    def rebuild_maps_panel(self) -> None:
        if not hasattr(self, "maps_frame"):
            return
        for child in self.maps_frame.winfo_children():
            child.destroy()
        maps = self.maps()
        active = self.active_map_record()
        options = [self.map_option(record) for record in maps]
        self.map_var.set(self.map_option(active))
        ttk.Label(self.maps_frame, text="Maps & Floors", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=4, sticky="w")
        self.map_combo = ttk.Combobox(self.maps_frame, textvariable=self.map_var, values=options, state="readonly")
        self.map_combo.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(2, 4))
        self.map_combo.bind("<<ComboboxSelected>>", lambda _e: self.set_active_map_from_var())
        for index, (label, command) in enumerate(
            [
                ("Add", self.add_map),
                ("Duplicate", self.duplicate_map),
                ("Rename", self.rename_map),
                ("Delete", self.delete_map),
            ]
        ):
            ttk.Button(self.maps_frame, text=label, command=command).grid(row=2, column=index, sticky="ew", padx=1)
            self.maps_frame.columnconfigure(index, weight=1)
        self.refresh_link_target_options()

    def refresh_link_target_options(self) -> None:
        if not hasattr(self, "link_target_combo"):
            return
        options = [self.map_option(record) for record in self.maps() if record["id"] != self.project.get("activeMapId")]
        self.link_target_combo.configure(values=options)
        if options and self.link_target_map_var.get() not in options:
            self.link_target_map_var.set(options[0])
        elif not options:
            self.link_target_map_var.set("")

    def set_active_map_from_var(self) -> None:
        record = self.map_from_option(self.map_var.get())
        if record:
            self.set_active_map(record["id"], commit=True)

    def set_active_map(self, target_map_id: str, commit: bool = True) -> None:
        if target_map_id == self.project.get("activeMapId"):
            return
        before = self.project_snapshot() if commit else None
        record = next((item for item in self.maps() if item["id"] == target_map_id), None)
        if not record:
            return
        self.load_map_record(record)
        self.set_selection(set())
        self.measure_points = []
        self.measure_preview = None
        self.sync_vars()
        self.populate_group_buttons()
        self.populate_symbol_panel()
        self.rebuild_maps_panel()
        self.rebuild_navigator_panel()
        if commit and before:
            self.commit_history(before, "Switch map")
        self.redraw()

    def add_map(self) -> None:
        name = simpledialog.askstring("New map", "Name", initialvalue=f"Level {len(self.maps()) + 1}", parent=self)
        if not name:
            return
        before = self.project_snapshot()
        settings = validate_settings(json_clone(self.settings))
        settings["showLegend"] = self.settings.get("showLegend", True)
        objects = [legend_obj(settings)]
        record = create_map_record(name, settings, self.project.get("layers", default_layers()), objects, {"rooms": []})
        self.project["maps"].append(record)
        self.load_map_record(record)
        self.set_selection(set())
        self.sync_vars()
        self.rebuild_maps_panel()
        self.rebuild_navigator_panel()
        self.commit_history(before, "Add map")
        self.redraw()

    def duplicate_map(self) -> None:
        source = self.active_map_record()
        name = simpledialog.askstring("Duplicate map", "Name", initialvalue=f"{source.get('name', 'Map')} copy", parent=self)
        if not name:
            return
        before = self.project_snapshot()
        record = create_map_record(
            name,
            source["settings"],
            source["layers"],
            source["objects"],
            source.get("campaign", {"rooms": []}),
            source.get("zones", []),
            source.get("markers", []),
            source.get("views", []),
        )
        self.project["maps"].append(record)
        self.load_map_record(record)
        self.set_selection(set())
        self.sync_vars()
        self.rebuild_maps_panel()
        self.rebuild_navigator_panel()
        self.commit_history(before, "Duplicate map")
        self.redraw()

    def rename_map(self) -> None:
        record = self.active_map_record()
        name = simpledialog.askstring("Rename map", "Name", initialvalue=str(record.get("name") or "Map"), parent=self)
        if not name:
            return
        before = self.project_snapshot()
        self.active_map_record()["name"] = name.strip() or "Map"
        self.rebuild_maps_panel()
        self.commit_history(before, "Rename map")
        self.show_status(f"Renamed map to {self.active_map_name()}")

    def delete_map(self) -> None:
        if len(self.maps()) <= 1:
            self.show_status("At least one map is required.")
            return
        record = self.active_map_record()
        if not messagebox.askyesno("Delete map", f"Delete {record.get('name', 'Map')}?", parent=self):
            return
        before = self.project_snapshot()
        self.project["maps"] = [item for item in self.maps() if item["id"] != record["id"]]
        self.load_map_record(self.project["maps"][0])
        self.set_selection(set())
        self.sync_vars()
        self.rebuild_maps_panel()
        self.rebuild_navigator_panel()
        self.commit_history(before, "Delete map")
        self.redraw()

    def _build_toolbar(self, toolbar: ttk.Frame) -> None:
        basic = ttk.LabelFrame(toolbar, text="Tools", padding=4)
        basic.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        basic.columnconfigure(0, weight=1)
        basic.columnconfigure(1, weight=1)
        for index, (tool, icon, label) in enumerate(BASIC_TOOLS):
            self._add_tool_button(basic, tool, icon, label, index // 2, index % 2)

        recent = ttk.LabelFrame(toolbar, text="Recent", padding=4)
        recent.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        recent.columnconfigure(0, weight=1)
        recent.columnconfigure(1, weight=1)
        self.recent_tools_frame = recent
        self.refresh_recent_tools()

        parents = ttk.LabelFrame(toolbar, text="Symbol Groups", padding=4)
        parents.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        parents.columnconfigure(0, weight=1)
        parents.columnconfigure(1, weight=1)
        self.symbol_group_frame = parents
        self.populate_group_buttons()

        self.symbol_panel = ttk.LabelFrame(toolbar, text=self.active_symbol_group.get(), padding=4)
        self.symbol_panel.grid(row=3, column=0, sticky="nsew")
        self.symbol_panel.columnconfigure(0, weight=1)
        self.symbol_panel.columnconfigure(1, weight=1)
        toolbar.rowconfigure(3, weight=1)
        self.populate_symbol_panel()
        self.refresh_toolbar()

    def refresh_recent_tools(self) -> None:
        if self.recent_tools_frame is None:
            return
        for child in self.recent_tools_frame.winfo_children():
            child.destroy()
        recent = [tool for tool in self.settings.get("recentTools", []) if tool in {item[0] for item in BASIC_TOOLS} or self.is_symbol_tool(tool)]
        if not recent:
            ttk.Label(self.recent_tools_frame, text="No recent tools").grid(row=0, column=0, columnspan=2, sticky="w")
            return
        labels = {tool: (icon, label) for tool, icon, label in BASIC_TOOLS}
        for group_entries in self.all_symbol_groups():
            for tool, icon, label in group_entries[1]:
                labels[tool] = (icon, label)
        for index, tool in enumerate(recent[:RECENT_TOOL_LIMIT]):
            icon, label = labels.get(tool, ("?", tool))
            button = tk.Button(
                self.recent_tools_frame,
                text=icon,
                width=4,
                height=1,
                font=("Segoe UI Symbol", 13, "bold"),
                command=lambda value=tool: self.select_tool(value),
                relief="raised",
                borderwidth=1,
                background="#f9fcfd",
                activebackground="#e8f4f8",
            )
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=2, pady=2)
            ToolTip(button, f"{label}\nZuletzt verwendet")

    def _add_tool_button(self, parent: ttk.Frame, tool: str, icon: str, label: str, row: int, column: int) -> None:
        button = tk.Button(
            parent,
            text=icon,
            width=4,
            height=1,
            font=("Segoe UI Symbol", 14, "bold"),
            command=lambda value=tool: self.select_tool(value),
            relief="raised",
            borderwidth=1,
            background="#f9fcfd",
            activebackground="#e8f4f8",
        )
        button.grid(row=row, column=column, sticky="ew", padx=2, pady=2)
        ToolTip(button, self.tooltip_text(tool, label))
        if tool in self.symbol_tools():
            SymbolPreview(button, self, tool, label)
        self.tool_buttons[tool] = button

    def populate_group_buttons(self) -> None:
        if self.symbol_group_frame is None:
            return
        for child in self.symbol_group_frame.winfo_children():
            child.destroy()
        self.group_buttons.clear()
        for index, (group_name, _entries) in enumerate(self.all_symbol_groups()):
            button = tk.Button(
                self.symbol_group_frame,
                text=SYMBOL_GROUP_ICONS.get(group_name, "◇"),
                width=4,
                height=2,
                font=("Segoe UI Symbol", 16, "bold"),
                command=lambda value=group_name: self.select_symbol_group(value),
                relief="raised",
                borderwidth=1,
                background="#f9fcfd",
                activebackground="#e8f4f8",
            )
            button.grid(row=index // 2, column=index % 2, sticky="nsew", padx=2, pady=2)
            ToolTip(button, f"{group_name}\nSymbolgruppe oeffnen")
            self.group_buttons[group_name] = button

    def select_symbol_group(self, value: str) -> None:
        self.active_symbol_group.set(value)
        self.populate_symbol_panel()
        self.refresh_toolbar()

    def populate_symbol_panel(self) -> None:
        if self.symbol_panel is None:
            return
        for symbol_tool in self.symbol_tools():
            self.tool_buttons.pop(symbol_tool, None)
        for child in self.symbol_panel.winfo_children():
            child.destroy()
        group_name = self.active_symbol_group.get()
        self.symbol_panel.configure(text=group_name)
        search_row = ttk.Frame(self.symbol_panel)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        search_row.columnconfigure(0, weight=1)
        search_entry = ttk.Entry(search_row, textvariable=self.symbol_search_var, width=10)
        search_entry.grid(row=0, column=0, sticky="ew")
        search_entry.bind("<KeyRelease>", lambda _e: self.populate_symbol_panel())
        ttk.Checkbutton(search_row, text="Fav", variable=self.symbol_favorites_only_var, command=self.populate_symbol_panel).grid(row=0, column=1, padx=(4, 0))
        actions = ttk.Frame(self.symbol_panel)
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        ttk.Button(actions, text="★", width=3, command=self.toggle_current_favorite).pack(side="left", padx=(0, 2))
        ttk.Button(actions, text="+ Group", command=self.add_custom_symbol_group).pack(side="left", padx=2)
        ttk.Button(actions, text="PNG", command=lambda: self.import_custom_symbol("png")).pack(side="left", padx=2)
        ttk.Button(actions, text="SVG", command=lambda: self.import_custom_symbol("svg")).pack(side="left", padx=2)
        ttk.Button(actions, text="Var", command=self.import_custom_symbol_variant).pack(side="left", padx=2)
        ttk.Button(actions, text="Set+", command=self.import_symbol_set).pack(side="left", padx=2)
        ttk.Button(actions, text="Set", command=self.export_symbol_set).pack(side="left", padx=2)
        options = ttk.Frame(self.symbol_panel)
        options.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        options.columnconfigure(1, weight=1)
        ttk.Checkbutton(options, text="Rand", variable=self.symbol_random_variant_var, command=self.apply_symbol_options).grid(row=0, column=0, sticky="w")
        preset = ttk.Combobox(options, textvariable=self.symbol_size_preset_var, values=tuple(SYMBOL_SIZE_PRESETS), state="readonly", width=12)
        preset.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        preset.bind("<<ComboboxSelected>>", lambda _e: self.apply_symbol_options())
        entries = next((entries for name, entries in self.all_symbol_groups() if name == group_name), [])
        query = self.symbol_search_var.get().strip().lower()
        favorites = set(self.project.get("symbolFavorites", []))
        if query:
            seen = set()
            entries = []
            for _name, group_entries in self.all_symbol_groups():
                for entry in group_entries:
                    if entry[0] not in seen:
                        seen.add(entry[0])
                        entries.append(entry)
        if self.symbol_favorites_only_var.get():
            entries = [entry for entry in entries if entry[0] in favorites]
        if query:
            entries = [entry for entry in entries if query in symbol_search_blob(self.project, entry[0], entry[2])]
        for index, (tool, icon, label) in enumerate(entries):
            self._add_tool_button(self.symbol_panel, tool, icon, label, 3 + index // 2, index % 2)

    def all_symbol_groups(self) -> list[tuple[str, list[tuple[str, str, str]]]]:
        groups = [(name, list(entries)) for name, entries in SYMBOL_GROUPS]
        custom_symbols = self.project.get("customSymbols", {})
        for group in self.project.get("customSymbolGroups", []):
            entries = []
            for entry in group.get("entries", []):
                kind = entry.get("kind")
                if kind in custom_symbols:
                    entries.append((kind, entry.get("icon", "◇"), custom_symbols[kind].get("label", kind)))
            groups.append((group.get("name", CUSTOM_GROUP_NAME), entries))
        return groups

    def symbol_tools(self) -> set[str]:
        return set(SYMBOL_LABELS) | set(self.project.get("customSymbols", {}))

    def is_symbol_tool(self, value: str) -> bool:
        return value in self.symbol_tools()

    def toggle_current_favorite(self) -> None:
        tool = self.tool.get()
        if not self.is_symbol_tool(tool):
            return
        before = self.project_snapshot()
        favorites = set(self.project.get("symbolFavorites", []))
        if tool in favorites:
            favorites.remove(tool)
        else:
            favorites.add(tool)
        self.project["symbolFavorites"] = sorted(favorites)
        self.commit_history(before, "Toggle symbol favorite")
        self.populate_symbol_panel()

    def add_custom_symbol_group(self) -> None:
        name = simpledialog.askstring("Symbol group", "Name", parent=self)
        if not name:
            return
        before = self.project_snapshot()
        groups = self.project.setdefault("customSymbolGroups", [])
        if not any(group.get("name") == name for group in groups):
            groups.append({"name": name, "entries": []})
        self.active_symbol_group.set(name)
        self.commit_history(before, "Add symbol group")
        self.populate_group_buttons()
        self.populate_symbol_panel()

    def import_custom_symbol(self, source_type: str) -> None:
        filetypes = [("PNG images", "*.png")] if source_type == "png" else [("SVG images", "*.svg")]
        path = filedialog.askopenfilename(title=f"Import {source_type.upper()} symbol", filetypes=filetypes, parent=self)
        if not path:
            return
        label = simpledialog.askstring("Symbol label", "Label", initialvalue=Path(path).stem, parent=self) or Path(path).stem
        group_name = self.active_symbol_group.get()
        if group_name not in [name for name, _entries in self.all_symbol_groups() if name not in {name for name, _entries in SYMBOL_GROUPS}]:
            group_name = CUSTOM_GROUP_NAME
        before = self.project_snapshot()
        kind = unique_custom_symbol_key(label, self.project.get("customSymbols", {}))
        self.project.setdefault("customSymbols", {})[kind] = {"label": label, "legendLabel": "", "sourceType": source_type, "path": path, "tags": normalize_tags([source_type, group_name, label]), "variants": []}
        groups = self.project.setdefault("customSymbolGroups", [{"name": CUSTOM_GROUP_NAME, "entries": []}])
        target = next((group for group in groups if group.get("name") == group_name), None)
        if target is None:
            target = {"name": group_name, "entries": []}
            groups.append(target)
        target.setdefault("entries", []).append({"kind": kind, "icon": "◇", "label": label})
        self.active_symbol_group.set(group_name)
        self.commit_history(before, f"Import {source_type.upper()} symbol")
        self.populate_group_buttons()
        self.populate_symbol_panel()

    def import_custom_symbol_variant(self) -> None:
        tool = self.tool.get()
        if not is_custom_symbol(self.project, tool):
            self.show_status("Select a custom symbol tool before importing a variant.")
            return
        path = filedialog.askopenfilename(title="Import symbol variant", filetypes=[("Images", "*.png *.svg"), ("PNG images", "*.png"), ("SVG images", "*.svg")], parent=self)
        if not path:
            return
        source_type = "svg" if Path(path).suffix.lower() == ".svg" else "png"
        label = simpledialog.askstring("Variant label", "Label", initialvalue=Path(path).stem, parent=self) or Path(path).stem
        before = self.project_snapshot()
        info = self.project.setdefault("customSymbols", {}).setdefault(tool, {"label": tool, "sourceType": source_type, "path": path, "tags": [], "variants": []})
        variant_id = safe_symbol_key(label)
        existing = {item.get("id") for item in info.setdefault("variants", [])}
        counter = 2
        base = variant_id
        while variant_id in existing:
            variant_id = f"{base}_{counter}"
            counter += 1
        info["variants"].append({"id": variant_id, "label": label, "sourceType": source_type, "path": path, "tags": normalize_tags([source_type, label])})
        self.commit_history(before, "Import symbol variant")
        self.populate_symbol_panel()
        self.redraw()

    def apply_symbol_options(self) -> None:
        before = self.project_snapshot()
        self.settings["randomSymbolVariants"] = bool(self.symbol_random_variant_var.get())
        preset = self.symbol_size_preset_var.get()
        self.settings["defaultSymbolSizePreset"] = preset if preset in SYMBOL_SIZE_PRESETS else DEFAULT_SYMBOL_SIZE_PRESET
        self.commit_history(before, "Change symbol options")

    def import_symbol_set(self) -> None:
        path = filedialog.askopenfilename(title="Import symbol set", filetypes=[("OSR Symbol Set", "*.symbols.json"), ("JSON", "*.json")], parent=self)
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            before = self.project_snapshot()
            count = import_symbol_set_data(self.project, data)
        except Exception as exc:
            self.show_error("Import failed", str(exc), parent=self)
            return
        self.commit_history(before, "Import symbol set")
        self.populate_group_buttons()
        self.populate_symbol_panel()
        self.show_status(f"Imported {count} custom symbol(s).")

    def export_symbol_set(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export symbol set",
            defaultextension=".symbols.json",
            filetypes=[("OSR Symbol Set", "*.symbols.json"), ("JSON", "*.json")],
            initialfile=f"{safe_name(self.project['meta']['title'])}.symbols.json",
            parent=self,
        )
        if not path:
            return
        Path(path).write_text(json.dumps(export_symbol_set_data(self.project), indent=2), encoding="utf-8")
        self.show_status(f"Exported {Path(path).name}")

    def select_tool(self, value: str) -> None:
        if value != "shape_polygon" and self.draft and self.draft.kind == "shape_polygon":
            self.draft = None
        self.tool.set(value)
        self.remember_recent_tool(value)
        self.current_layer_var.set(self.layer_name(default_layer_for_tool(value, self.is_symbol_tool(value))))
        self.refresh_toolbar()
        self.update_cursor()
        self.update_status()

    def remember_recent_tool(self, value: str) -> None:
        if value not in {tool for tool, _icon, _label in BASIC_TOOLS} and not self.is_symbol_tool(value):
            return
        recent = [tool for tool in self.settings.get("recentTools", []) if tool != value]
        self.settings["recentTools"] = [value, *recent][:RECENT_TOOL_LIMIT]
        self.refresh_recent_tools()

    def tooltip_text(self, tool: str, label: str) -> str:
        description = TOOL_DESCRIPTIONS.get(tool, f"{label} platzieren")
        shortcut = self.shortcut_for_tool(tool)
        suffix = f"\nShortcut: {shortcut}" if shortcut else ""
        if self.is_symbol_tool(tool):
            tags = ", ".join(symbol_tags(self.project, tool)[:6])
            variants = symbol_variant_options(self.project, tool)
            variant_text = f"\nVariants: {len(variants)}" if len(variants) > 1 else ""
            tag_text = f"\nTags: {tags}" if tags else ""
            return f"{label}\n{description}{tag_text}{variant_text}{suffix}"
        return f"{label}\n{description}{suffix}"

    def shortcut_for_tool(self, tool: str) -> str:
        action = TOOL_ACTIONS.get(tool)
        return self.shortcuts.get(action, "") if action else ""

    def refresh_toolbar(self) -> None:
        active = self.tool.get()
        for tool, button in self.tool_buttons.items():
            if tool == active:
                button.configure(relief="sunken", background=BLUE, foreground=WHITE)
            else:
                button.configure(relief="raised", background="#f9fcfd", foreground="#17384a")
        active_group = self.active_symbol_group.get()
        for group, button in self.group_buttons.items():
            if group == active_group:
                button.configure(relief="sunken", background="#17384a", foreground=WHITE)
            else:
                button.configure(relief="raised", background="#f9fcfd", foreground="#17384a")
        self.refresh_recent_tools()

    def _bind_events(self) -> None:
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_canvas)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)
        self.canvas.bind("<ButtonPress-3>", self.on_context_menu)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel_zoom)
        self.canvas.bind("<Button-4>", self.on_mousewheel_zoom)
        self.canvas.bind("<Button-5>", self.on_mousewheel_zoom)
        self.bind("<Delete>", lambda _e: self.delete_selected())
        self.bind("<Control-z>", lambda _e: self.undo())
        self.bind("<Control-y>", lambda _e: self.redo())
        self.bind("<Control-g>", lambda _e: self.group_selected())
        self.bind("<Control-u>", lambda _e: self.ungroup_selected())
        self.bind("<Escape>", lambda _e: self.clear_measurement())
        self.bind_configured_shortcuts()
        self.bind_all("<Up>", lambda event: self.zoom_by(1.1) if self.should_handle_zoom_key() else None)
        self.bind_all("<Down>", lambda event: self.zoom_by(1 / 1.1) if self.should_handle_zoom_key() else None)
        self.canvas.bind("<Configure>", lambda _e: self.redraw_minimap())

    def bind_configured_shortcuts(self) -> None:
        for action, sequence in self.shortcuts.items():
            if not sequence:
                continue
            callback = self.shortcut_callback(action)
            if callback:
                self.bind_all(sequence if sequence.startswith("<") else sequence.lower(), callback)
                if len(sequence) == 1 and sequence.isalpha():
                    self.bind_all(sequence.upper(), callback)

    def shortcut_callback(self, action: str):
        tool = next((tool for tool, mapped_action in TOOL_ACTIONS.items() if mapped_action == action), None)
        if tool:
            return lambda event, value=tool: self.handle_tool_shortcut(value)
        actions = {
            "duplicate": lambda _event: self.duplicate_selected(),
            "copy": lambda _event: self.copy_selected(),
            "paste": lambda _event: self.paste_clipboard(),
            "bring_front": lambda _event: self.bring_selected_to_front(),
            "send_back": lambda _event: self.send_selected_to_back(),
            "toggle_lock": lambda _event: self.toggle_selected_lock(),
        }
        return actions.get(action)

    def handle_tool_shortcut(self, value: str) -> str | None:
        if not self.should_handle_zoom_key():
            return None
        self.select_tool(value)
        return "break"

    def project_snapshot(self) -> dict[str, Any]:
        self.sync_campaign_from_rooms()
        self.sync_active_map_storage()
        return json.loads(json.dumps(self.project))

    def commit_history(self, before: dict[str, Any], description: str) -> None:
        after = self.project_snapshot()
        if json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True):
            return
        self.history.append(HistoryCommand(description, before, after))
        self.history = self.history[-50:]
        self.future.clear()
        self.project["meta"]["updatedAt"] = now_iso()

    def push_history(self) -> dict[str, Any]:
        return self.project_snapshot()

    def apply_settings(self) -> None:
        before = self.project_snapshot()
        self.project["meta"]["title"] = self.title_var.get() or "Untitled Dungeon"
        self.settings["width"] = max(12, safe_int(self.width_var.get(), self.settings["width"]))
        self.settings["height"] = max(12, safe_int(self.height_var.get(), self.settings["height"]))
        self.settings["cellSize"] = max(8, safe_int(self.cell_var.get(), self.settings["cellSize"]))
        self.settings["showLegend"] = bool(self.legend_var.get())
        self.settings["cellScale"] = max(0.01, coerce_float(self.cell_scale_var.get(), self.settings.get("cellScale", 10.0)))
        self.settings["cellScaleUnit"] = (self.cell_scale_unit_var.get() or "ft.").strip() or "ft."
        self.settings["snapToGrid"] = bool(self.snap_var.get())
        self.settings["snapStep"] = SNAP_STEP_LABELS.get(self.snap_step_var.get(), 1.0)
        self.settings["showMainGrid"] = bool(self.main_grid_var.get())
        self.settings["showSubGrid"] = bool(self.sub_grid_var.get())
        self.settings["showCoordinates"] = bool(self.coordinate_var.get())
        self.settings["showZones"] = bool(self.zone_overlay_var.get())
        self.settings["showRuler"] = bool(self.ruler_overlay_var.get())
        self.settings["snapToObjects"] = bool(self.snap_objects_var.get())
        self.settings["styleTemplate"] = self.style_var.get()
        self.settings["exportGrid"] = bool(self.export_grid_var.get())
        self.settings["vttPreset"] = self.vtt_preset_var.get()
        self.settings["exportAudience"] = self.export_audience_var.get()
        self.settings["defaultTextFont"] = self.text_font_var.get() or "Arial"
        self.settings["defaultTextSize"] = max(0.25, coerce_float(self.text_size_var.get(), self.settings["defaultTextSize"]))
        self.settings["defaultShapeLineWidth"] = max(0.01, coerce_float(self.shape_line_width_var.get(), self.settings.get("defaultShapeLineWidth", 0.12)))
        self.settings["defaultSymbolSizePreset"] = self.symbol_size_preset_var.get() if self.symbol_size_preset_var.get() in SYMBOL_SIZE_PRESETS else DEFAULT_SYMBOL_SIZE_PRESET
        self.settings["randomSymbolVariants"] = bool(self.symbol_random_variant_var.get())
        self.settings["numberStart"] = max(1, safe_int(self.number_start_var.get(), self.settings["numberStart"]))
        self.settings["numberArea"] = self.number_area_var.get().strip()
        self.settings["shortcuts"] = dict(self.shortcuts)
        self.sync_vars()
        self.commit_history(before, "Change map settings")
        self.redraw()

    def open_shortcuts_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Shortcuts")
        dialog.transient(self)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        entries: dict[str, tk.StringVar] = {}
        ttk.Label(frame, text="Action", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Shortcut", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w")
        labels = {
            "select_tool": "Select tool",
            "room_tool": "Room tool",
            "corridor_tool": "Corridor tool",
            "round_tool": "Round tool",
            "cave_tool": "Cave tool",
            "shape_rect_tool": "Rectangle tool",
            "shape_circle_tool": "Circle tool",
            "shape_polygon_tool": "Polygon tool",
            "shape_line_tool": "Line tool",
            "text_tool": "Text tool",
            "number_tool": "Number tool",
            "note_tool": "Note tool",
            "measure_tool": "Measure tool",
            "duplicate": "Duplicate",
            "copy": "Copy",
            "paste": "Paste",
            "bring_front": "Bring front",
            "send_back": "Send back",
            "toggle_lock": "Lock/unlock",
        }
        for row, action in enumerate(DEFAULT_SHORTCUTS, start=1):
            ttk.Label(frame, text=labels.get(action, action)).grid(row=row, column=0, sticky="w", pady=1)
            var = tk.StringVar(value=self.shortcuts.get(action, DEFAULT_SHORTCUTS[action]))
            entries[action] = var
            ttk.Entry(frame, textvariable=var, width=22).grid(row=row, column=1, sticky="ew", pady=1)

        def save() -> None:
            before = self.project_snapshot()
            self.shortcuts = {action: var.get().strip() for action, var in entries.items()}
            self.settings["shortcuts"] = dict(self.shortcuts)
            self.commit_history(before, "Change shortcuts")
            self.populate_symbol_panel()
            self.refresh_toolbar()
            self.show_status("Shortcuts saved. Restart the app to rebind changed keys.")
            dialog.destroy()

        buttons = ttk.Frame(frame)
        buttons.grid(row=len(DEFAULT_SHORTCUTS) + 1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(buttons, text="Save", command=save).pack(side="right", padx=2)
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right", padx=2)

    def apply_vtt_preset(self) -> None:
        before = self.project_snapshot()
        preset = self.vtt_preset_var.get()
        if preset in {"Foundry", "Roll20"}:
            self.settings["cellSize"] = 70
            self.cell_var.set(70)
            self.export_grid_var.set(False)
            self.settings["defaultSymbolShadow"] = True
        self.settings["vttPreset"] = preset
        self.settings["exportGrid"] = bool(self.export_grid_var.get())
        self.commit_history(before, f"Apply {preset} VTT preset")
        self.redraw()

    def apply_style_template(self) -> None:
        template = STYLE_TEMPLATES.get(self.style_var.get())
        if not template:
            return
        before = self.project_snapshot()
        self.settings.update(template)
        self.settings["styleTemplate"] = self.style_var.get()
        self.sync_vars()
        self.commit_history(before, f"Apply {self.style_var.get()} style")
        self.redraw()

    def rebuild_layers_panel(self) -> None:
        if not hasattr(self, "layers_frame"):
            return
        for child in self.layers_frame.winfo_children():
            child.destroy()
        self.layer_visible_vars.clear()
        self.layer_locked_vars.clear()
        layer_names = [layer["name"] for layer in self.project.get("layers", default_layers()) if layer["id"] != "background"]
        ttk.Label(self.layers_frame, text="Active layer", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")
        combo = ttk.Combobox(self.layers_frame, textvariable=self.current_layer_var, values=layer_names, state="readonly")
        combo.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 8))
        combo.bind("<<ComboboxSelected>>", lambda _e: None)
        ttk.Label(self.layers_frame, text="Layer").grid(row=2, column=0, sticky="w")
        ttk.Label(self.layers_frame, text="Visible").grid(row=2, column=1, sticky="w")
        ttk.Label(self.layers_frame, text="Locked").grid(row=2, column=2, sticky="w")
        for row, layer in enumerate(self.project.get("layers", default_layers()), start=3):
            visible = tk.BooleanVar(value=layer.get("visible", True))
            locked = tk.BooleanVar(value=layer.get("locked", False))
            self.layer_visible_vars[layer["id"]] = visible
            self.layer_locked_vars[layer["id"]] = locked
            ttk.Label(self.layers_frame, text=layer.get("name", layer["id"])).grid(row=row, column=0, sticky="w", pady=1)
            ttk.Checkbutton(self.layers_frame, variable=visible, command=self.apply_layer_states).grid(row=row, column=1, sticky="w")
            ttk.Checkbutton(self.layers_frame, variable=locked, command=self.apply_layer_states).grid(row=row, column=2, sticky="w")

    def apply_layer_states(self) -> None:
        before = self.project_snapshot()
        for layer in self.project.get("layers", []):
            layer_id = layer["id"]
            if layer_id in self.layer_visible_vars:
                layer["visible"] = bool(self.layer_visible_vars[layer_id].get())
            if layer_id in self.layer_locked_vars:
                layer["locked"] = bool(self.layer_locked_vars[layer_id].get())
        self.commit_history(before, "Change layer state")
        self.redraw()

    def pick_color(self, key: str) -> None:
        color = colorchooser.askcolor(color=self.settings[key], parent=self)[1]
        if not color:
            return
        before = self.project_snapshot()
        self.settings[key] = color
        self.commit_history(before, f"Change {key}")
        self.redraw()

    def new_project(self) -> None:
        before = self.project_snapshot()
        self.project = create_project()
        self.set_selection(set())
        self.sync_vars()
        self.populate_group_buttons()
        self.populate_symbol_panel()
        self.commit_history(before, "New project")
        self.redraw()

    def save_project(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save OSR map",
            defaultextension=".osrmap.json",
            filetypes=[("OSR Map", "*.osrmap.json"), ("JSON", "*.json")],
            initialfile=f"{safe_name(self.project['meta']['title'])}.osrmap.json",
        )
        if not path:
            return
        self.sync_campaign_from_rooms()
        self.sync_active_map_storage()
        self.project["meta"]["updatedAt"] = now_iso()
        Path(path).write_text(json.dumps(self.project, indent=2), encoding="utf-8")
        self.current_file = Path(path)
        self.show_status(f"Saved {Path(path).name}")

    def load_project(self) -> None:
        path = filedialog.askopenfilename(
            title="Load OSR map",
            filetypes=[("OSR Map", "*.osrmap.json"), ("JSON", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            loaded = validate_project(json.loads(Path(path).read_text(encoding="utf-8")))
        except Exception as exc:
            self.show_error("Load failed", str(exc), parent=self)
            return
        before = self.project_snapshot()
        self.project = loaded
        self.current_file = Path(path)
        self.set_selection(set())
        self.sync_vars()
        self.populate_group_buttons()
        self.populate_symbol_panel()
        self.commit_history(before, "Load project")
        self.redraw()
        self.show_status(f"Loaded {Path(path).name}")

    def export_image(self) -> None:
        if Image is None:
            self.show_error("Export failed", "Pillow ist nicht installiert: python -m pip install pillow", parent=self)
            return
        self.open_export_dialog()

    def quick_export_audience(self, audience: str) -> None:
        before = self.project_snapshot()
        self.settings["exportAudience"] = audience
        self.export_audience_var.set(audience)
        self.commit_history(before, f"Set {audience} export")
        self.open_export_dialog()

    def undo(self) -> None:
        if not self.history:
            return
        command = self.history.pop()
        self.future.insert(0, command)
        self.project = json.loads(json.dumps(command.before))
        self.set_selection(set())
        self.sync_vars()
        self.redraw()
        self.show_status(f"Undid {command.description}")

    def redo(self) -> None:
        if not self.future:
            return
        command = self.future.pop(0)
        self.history.append(command)
        self.project = json.loads(json.dumps(command.after))
        self.set_selection(set())
        self.sync_vars()
        self.redraw()
        self.show_status(f"Redid {command.description}")

    def show_status(self, message: str) -> None:
        self.status.set(self.status_with_mouse(message))

    def show_error(self, title: str, message: str, parent: tk.Widget | None = None) -> None:
        self.error_status.set(f"{title}: {message}")
        self.after(7000, lambda: self.error_status.set(""))
        self.show_status(f"{title}: {message}")
        messagebox.showerror(title, message, parent=parent or self)

    def status_with_mouse(self, base: str) -> str:
        if not self.mouse_grid:
            return base
        x, y = self.mouse_grid
        return f"{base} | grid {x:.2f}, {y:.2f}"

    def update_status(self, base: str | None = None) -> None:
        if base is None:
            if self.tool.get() == "measure":
                base = self.measurement_status()
            else:
                selection = f" | {len(self.selected_ids)} selected" if self.selected_ids else ""
                base = f"{self.tool.get()} | {len(self.project['objects'])} objects{selection}"
        self.status.set(self.status_with_mouse(base))

    def update_cursor(self) -> None:
        if self.is_panning:
            self.canvas.configure(cursor="fleur")
        elif self.tool.get() == "select" and self.selected_ids:
            self.canvas.configure(cursor="hand2")
        else:
            self.canvas.configure(cursor=CURSOR_BY_TOOL.get(self.tool.get(), "arrow"))

    def sync_vars(self) -> None:
        self.map_var.set(self.map_option(self.active_map_record()))
        self.title_var.set(self.project["meta"]["title"])
        self.width_var.set(self.settings["width"])
        self.height_var.set(self.settings["height"])
        self.cell_var.set(self.settings["cellSize"])
        self.legend_var.set(self.settings["showLegend"])
        self.cell_scale_var.set(self.settings.get("cellScale", 10.0))
        self.cell_scale_unit_var.set(self.settings.get("cellScaleUnit", "ft."))
        self.snap_var.set(self.settings.get("snapToGrid", True))
        self.snap_step_var.set(snap_step_label(self.settings.get("snapStep", 1.0)))
        self.main_grid_var.set(self.settings.get("showMainGrid", True))
        self.sub_grid_var.set(self.settings.get("showSubGrid", True))
        self.coordinate_var.set(self.settings.get("showCoordinates", False))
        self.zone_overlay_var.set(self.settings.get("showZones", True))
        self.ruler_overlay_var.set(self.settings.get("showRuler", True))
        self.snap_objects_var.set(self.settings.get("snapToObjects", False))
        self.style_var.set(self.settings.get("styleTemplate", "Blueprint"))
        self.export_grid_var.set(self.settings.get("exportGrid", True))
        self.vtt_preset_var.set(self.settings.get("vttPreset", "Generic"))
        self.export_audience_var.set(self.settings.get("exportAudience", "GM"))
        self.text_font_var.set(self.settings.get("defaultTextFont", "Arial"))
        self.text_size_var.set(self.settings.get("defaultTextSize", 1.0))
        self.shape_line_width_var.set(self.settings.get("defaultShapeLineWidth", 0.12))
        self.symbol_random_variant_var.set(self.settings.get("randomSymbolVariants", False))
        self.symbol_size_preset_var.set(self.settings.get("defaultSymbolSizePreset", DEFAULT_SYMBOL_SIZE_PRESET))
        self.number_start_var.set(self.settings.get("numberStart", 1))
        self.number_area_var.set(self.settings.get("numberArea", ""))
        self.shortcuts = {**DEFAULT_SHORTCUTS, **self.settings.get("shortcuts", {})}
        self.rebuild_layers_panel()
        self.rebuild_maps_panel()
        self.rebuild_navigator_panel()
        self.refresh_recent_tools()
        self.refresh_object_list()

    def on_motion(self, event: tk.Event) -> None:
        self.mouse_grid = self.event_to_grid(event)
        if self.tool.get() == "measure":
            self.measure_preview = self.snap_point(self.mouse_grid[0], self.mouse_grid[1])
            self.redraw()
            return
        self.update_status()
        if self.draft and self.draft.kind == "shape_polygon":
            px, py = self.snap_point(self.mouse_grid[0], self.mouse_grid[1])
            self.draft.x2 = px
            self.draft.y2 = py
            self.redraw()
            return
        if self.tool.get() == "select":
            handle = self.find_handle_hit(*self.mouse_grid)
            if handle == "rotate":
                self.canvas.configure(cursor="exchange")
            elif handle and handle.startswith("insert:"):
                self.canvas.configure(cursor="crosshair")
            elif handle:
                self.canvas.configure(cursor="sizing")
            elif self.find_hit(*self.mouse_grid):
                self.canvas.configure(cursor="hand2")
            else:
                self.update_cursor()

    def on_canvas_leave(self, _event: tk.Event) -> None:
        self.mouse_grid = None
        if self.measure_preview is not None:
            self.measure_preview = None
            self.redraw()
            return
        self.update_status()
        self.update_cursor()

    def on_context_menu(self, event: tk.Event) -> str:
        point = self.event_to_grid(event)
        hit = self.find_hit(*point)
        if hit and hit["id"] not in self.selected_ids:
            self.set_selection(self.ids_for_hit(hit), primary=hit["id"])
            self.redraw()
        menu = tk.Menu(self, tearoff=0)
        has_selection = bool(self.selected_ids)
        handle = self.find_handle_hit(*point) if has_selection else None
        if handle and handle.startswith("point:"):
            index = int(handle.split(":", 1)[1])
            self.selected_polygon_point = index
            menu.add_command(label="Insert polygon point after", command=lambda value=index: self.insert_polygon_midpoint(value))
            menu.add_command(label="Delete polygon point", command=lambda value=index: self.delete_polygon_point(value))
            menu.add_separator()
        menu.add_command(label="Duplicate", command=self.duplicate_selected, state="normal" if has_selection else "disabled")
        menu.add_command(label="Copy", command=self.copy_selected, state="normal" if has_selection else "disabled")
        menu.add_command(label="Paste", command=self.paste_clipboard, state="normal" if self.clipboard_objects else "disabled")
        menu.add_command(label="Bring to front", command=self.bring_selected_to_front, state="normal" if has_selection else "disabled")
        menu.add_command(label="Send to back", command=self.send_selected_to_back, state="normal" if has_selection else "disabled")
        menu.add_command(label="Lock / unlock", command=self.toggle_selected_lock, state="normal" if has_selection else "disabled")
        layer_menu = tk.Menu(menu, tearoff=0)
        for layer in self.project.get("layers", []):
            if layer["id"] == "background":
                continue
            layer_menu.add_command(label=layer.get("name", layer["id"]), command=lambda value=layer["id"]: self.move_selection_to_layer(value), state="normal" if has_selection else "disabled")
        menu.add_cascade(label="Move to layer", menu=layer_menu, state="normal" if has_selection else "disabled")
        align_menu = tk.Menu(menu, tearoff=0)
        for label, mode in [("Left", "left"), ("Right", "right"), ("Top", "top"), ("Bottom", "bottom"), ("Center horizontal", "center_x"), ("Center vertical", "center_y")]:
            align_menu.add_command(label=label, command=lambda value=mode: self.align_selection(value), state="normal" if len(self.selected_ids) > 1 else "disabled")
        menu.add_cascade(label="Align", menu=align_menu, state="normal" if len(self.selected_ids) > 1 else "disabled")
        distribute_menu = tk.Menu(menu, tearoff=0)
        distribute_menu.add_command(label="Horizontal", command=lambda: self.distribute_selection("horizontal"), state="normal" if len(self.selected_ids) > 2 else "disabled")
        distribute_menu.add_command(label="Vertical", command=lambda: self.distribute_selection("vertical"), state="normal" if len(self.selected_ids) > 2 else "disabled")
        menu.add_cascade(label="Distribute", menu=distribute_menu, state="normal" if len(self.selected_ids) > 2 else "disabled")
        template_menu = tk.Menu(menu, tearoff=0)
        template_menu.add_command(label="Save as template", command=self.save_selection_as_template, state="normal" if has_selection else "disabled")
        templates = self.project.get("objectTemplates", [])
        if templates:
            template_menu.add_separator()
            for index, template in enumerate(templates):
                template_menu.add_command(label=str(template.get("name") or f"Template {index + 1}"), command=lambda value=index: self.insert_template(value))
        menu.add_cascade(label="Templates", menu=template_menu)
        menu.add_command(label="Fit view to selection", command=self.fit_view_to_selection, state="normal" if has_selection else "disabled")
        linked = bool(self.selected_object() and self.selected_object().get("targetMapId"))
        menu.add_command(label="Follow floor link", command=self.follow_selected_link, state="normal" if linked else "disabled")
        menu.add_separator()
        menu.add_command(label="Delete", command=self.delete_selected, state="normal" if has_selection else "disabled")
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def on_press(self, event: tk.Event) -> None:
        self.canvas.focus_set()
        self.drag_mode = None
        self.drag_handle = None
        self.drag_originals = {}
        self.selection_box = None
        point = self.event_to_grid(event)
        snapped = self.snap_point(point[0], point[1])
        tool = self.tool.get()
        if tool == "shape_polygon":
            self.handle_polygon_click(snapped)
            return
        if tool == "measure":
            self.add_measure_point(snapped)
            return
        if tool == "select":
            handle = self.find_handle_hit(*point)
            if handle:
                obj = self.selected_object()
                if obj:
                    if handle.startswith("insert:"):
                        self.insert_polygon_midpoint(int(handle.split(":", 1)[1]))
                        return
                    if handle.startswith("point:"):
                        self.selected_polygon_point = int(handle.split(":", 1)[1])
                    self.drag_mode = "rotate" if handle == "rotate" else "resize"
                    if handle.startswith("point:"):
                        self.drag_mode = "polygon_point"
                    self.drag_handle = handle
                    self.drag_start = (point[0], point[1], json.loads(json.dumps(obj)))
                    self.drag_snapshot = self.project_snapshot()
                    self.drag_originals = {obj["id"]: json.loads(json.dumps(obj))}
                    self.redraw()
                return
            hit = self.find_hit(*point)
            shift = shift_pressed(event)
            if not hit:
                if not shift:
                    self.set_selection(set())
                self.drag_mode = "select_box"
                self.selection_box = (point[0], point[1], point[0], point[1])
                self.drag_start = (point[0], point[1], None)
                self.drag_snapshot = None
                self.redraw()
                return
            if shift:
                self.toggle_hit_selection(hit)
            else:
                if hit["id"] not in self.selected_ids:
                    self.set_selection(self.ids_for_hit(hit), primary=hit["id"])
            if hit["id"] in self.selected_ids:
                self.drag_mode = "move"
                self.drag_handle = None
                self.drag_start = (point[0], point[1], None)
                self.drag_snapshot = self.project_snapshot()
                self.drag_originals = {
                    obj["id"]: json.loads(json.dumps(obj))
                    for obj in self.project["objects"]
                    if obj["id"] in self.selected_ids
                }
            self.redraw()
            return
        if tool in {"room", "corridor", "round", "cave"} | DRAG_SHAPE_TOOLS:
            min_size = self.snap_step()
            self.draft = Draft(tool, snapped[0], snapped[1], min_size, min_size, snapped[0], snapped[1])
            self.drag_start = (snapped[0], snapped[1], None)
            self.redraw()
            return
        if self.is_symbol_tool(tool):
            offset = 0.5 if self.settings.get("snapToGrid", True) and self.snap_step() == 1.0 else 0
            variant = choose_symbol_variant(self.project, tool, self.settings.get("randomSymbolVariants", False))
            preset = self.settings.get("defaultSymbolSizePreset", DEFAULT_SYMBOL_SIZE_PRESET)
            obj = symbol(tool, snapped[0] + offset, snapped[1] + offset, symbol_size_for_preset(preset))
            obj["sizePreset"] = preset
            obj["shadow"] = bool(self.settings.get("defaultSymbolShadow", False))
            obj["outline"] = bool(self.settings.get("defaultSymbolOutline", False))
            if is_custom_symbol(self.project, tool):
                obj["variant"] = variant["id"]
            else:
                obj["variant"] = variant["id"] if variant["kind"] != normalize_symbol_kind(tool) else ""
            self.add_object(obj)
            return
        if tool in {"text", "number", "note"}:
            initial = self.next_room_number() if tool == "number" else ""
            value = simpledialog.askstring("Text", "Value", initialvalue=initial, parent=self)
            if value:
                if tool == "note":
                    self.add_object(note_obj(value, snapped[0], snapped[1]))
                else:
                    obj = text_obj(value, snapped[0], snapped[1], 1.45 if tool == "number" else self.settings.get("defaultTextSize", 1.0))
                    obj["font"] = self.settings.get("defaultTextFont", "Arial")
                    obj["color"] = self.settings.get("textColor", self.settings["gridColor"])
                    obj["textRole"] = "number" if tool == "number" else "text"
                    obj["numberArea"] = self.settings.get("numberArea", "") if tool == "number" else ""
                    if tool == "number":
                        room = self.find_room_at(point[0], point[1])
                        if room:
                            obj["roomId"] = room["id"]
                            room["roomNumber"] = value
                    self.add_object(obj)

    def on_drag(self, event: tk.Event) -> None:
        if self.is_panning:
            self.pan_canvas(event)
            return
        if not self.drag_start:
            return
        point = self.event_to_grid(event)
        if self.draft:
            sx, sy, _ = self.drag_start
            px, py = self.snap_point(point[0], point[1])
            if self.draft.kind in {"corridor", "shape_line"}:
                self.draft.x = sx
                self.draft.y = sy
                self.draft.x2 = px
                self.draft.y2 = py
                self.draft.width = max(self.snap_step(), abs(px - sx))
                self.draft.height = max(self.snap_step(), abs(py - sy))
            elif self.draft.kind == "shape_circle":
                x, y, width, height = self.circle_from_points(sx, sy, px, py)
                self.draft.x = x
                self.draft.y = y
                self.draft.width = width
                self.draft.height = height
            else:
                x, y, width, height = self.rect_from_points(sx, sy, px, py)
                self.draft.x = x
                self.draft.y = y
                self.draft.width = width
                self.draft.height = height
            self.redraw()
            return
        if self.drag_mode == "select_box" and self.selection_box:
            sx, sy, _ = self.drag_start
            self.selection_box = (sx, sy, point[0], point[1])
            self.redraw()
            return
        if self.tool.get() == "select" and self.drag_mode == "move":
            sx, sy, _ = self.drag_start
            dx, dy = self.snap_delta(point[0] - sx, point[1] - sy)
            dx, dy = self.snap_move_delta_to_objects(dx, dy)
            for obj in self.project["objects"]:
                original = self.drag_originals.get(obj["id"])
                if original:
                    move_object_to_delta(obj, original, dx, dy)
            self.redraw()
            return
        if self.tool.get() == "select" and self.drag_mode in {"resize", "rotate", "polygon_point"}:
            self.update_handle_drag(point)
            self.redraw()

    def on_release(self, _event: tk.Event) -> None:
        if self.is_panning:
            self.end_pan()
            return
        if self.draft:
            draft = self.draft
            if draft.kind == "shape_polygon":
                return
            if draft.kind in SHAPE_TOOLS:
                obj = self.shape_from_draft(draft)
            elif draft.kind == "corridor" and draft.x2 is not None and draft.y2 is not None and draft.x != draft.x2 and draft.y != draft.y2:
                obj = diagonal_corridor(draft.x, draft.y, draft.x2, draft.y2)
            else:
                if draft.kind == "corridor" and draft.x2 is not None and draft.y2 is not None:
                    x, y, width, height = self.rect_from_points(draft.x, draft.y, draft.x2, draft.y2)
                    obj = rect("corridor", x, y, width, height)
                else:
                    obj = rect(draft.kind, draft.x, draft.y, draft.width, draft.height)
            if draft.kind == "cave":
                obj["seed"] = random.randint(1, 100000)
            self.draft = None
            self.drag_start = None
            self.add_object(obj)
            return
        if self.drag_mode == "select_box" and self.selection_box:
            self.select_objects_in_box(self.selection_box)
        elif self.drag_snapshot:
            description = {"move": "Move selection", "resize": "Resize object", "rotate": "Rotate object", "polygon_point": "Move polygon point"}.get(self.drag_mode or "", "Edit object")
            self.commit_history(self.drag_snapshot, description)
        self.drag_start = None
        self.drag_snapshot = None
        self.drag_mode = None
        self.drag_handle = None
        self.drag_originals = {}
        self.selection_box = None
        self.redraw()

    def start_pan(self, event: tk.Event) -> None:
        self.is_panning = True
        self.canvas.scan_mark(event.x, event.y)
        self.update_cursor()

    def pan_canvas(self, event: tk.Event) -> None:
        if not self.is_panning:
            return
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def end_pan(self, _event: tk.Event | None = None) -> None:
        self.is_panning = False
        self.update_cursor()

    def on_mousewheel_zoom(self, event: tk.Event) -> str:
        if hasattr(event, "delta") and event.delta:
            factor = 1.1 if event.delta > 0 else 1 / 1.1
        else:
            factor = 1.1 if getattr(event, "num", 0) == 4 else 1 / 1.1
        self.zoom_by(factor, event)
        return "break"

    def should_handle_zoom_key(self) -> bool:
        focus = self.focus_get()
        if focus is None:
            return True
        widget_class = focus.winfo_class()
        return widget_class not in {"Entry", "TEntry", "TCombobox", "Spinbox", "TSpinbox"}

    def zoom_by(self, factor: float, event: tk.Event | None = None) -> str:
        old_zoom = self.zoom.get()
        new_zoom = min(2.2, max(0.35, old_zoom * factor))
        if abs(new_zoom - old_zoom) < 0.001:
            return "break"

        if event is not None:
            anchor_x = self.canvas.canvasx(event.x)
            anchor_y = self.canvas.canvasy(event.y)
            screen_x = event.x
            screen_y = event.y
        else:
            screen_x = max(1, self.canvas.winfo_width() / 2)
            screen_y = max(1, self.canvas.winfo_height() / 2)
            anchor_x = self.canvas.canvasx(screen_x)
            anchor_y = self.canvas.canvasy(screen_y)

        ratio = new_zoom / old_zoom
        self.zoom.set(new_zoom)
        self.redraw()
        width, height = canvas_size(self.project, new_zoom)
        view_w = max(1, self.canvas.winfo_width())
        view_h = max(1, self.canvas.winfo_height())
        max_x = max(1, width - view_w)
        max_y = max(1, height - view_h)
        self.canvas.xview_moveto(max(0, min(1, (anchor_x * ratio - screen_x) / max_x)))
        self.canvas.yview_moveto(max(0, min(1, (anchor_y * ratio - screen_y) / max_y)))
        return "break"

    def add_object(self, obj: dict[str, Any]) -> None:
        before = self.project_snapshot()
        obj = validate_object(obj, len(self.project["objects"]) + 1)
        if obj["type"] != "legend" and obj.get("layer") not in {"notes"}:
            obj["layer"] = self.active_layer_id(default=normalize_layer_id(obj.get("layer"), obj["type"]))
        self.project["objects"].append(obj)
        self.set_selection({obj["id"]}, primary=obj["id"])
        self.commit_history(before, f"Add {obj['type']}")
        self.redraw()

    def delete_selected(self) -> None:
        if not self.selected_ids:
            return
        before = self.project_snapshot()
        selected_ids = set(self.selected_ids)
        self.project["objects"] = [obj for obj in self.project["objects"] if obj["id"] not in selected_ids or self.is_object_locked(obj)]
        self.set_selection(set())
        self.commit_history(before, "Delete selection")
        self.redraw()

    def duplicate_selected(self) -> None:
        if not self.selected_ids:
            return
        before = self.project_snapshot()
        new_ids: set[str] = set()
        for obj in list(self.project["objects"]):
            if obj["id"] not in self.selected_ids or self.is_object_locked(obj):
                continue
            copy_obj = json.loads(json.dumps(obj))
            copy_obj["id"] = object_id()
            copy_obj.pop("group", None)
            translate_object(copy_obj, self.snap_step(), self.snap_step())
            self.project["objects"].append(validate_object(copy_obj, len(self.project["objects"]) + 1))
            new_ids.add(copy_obj["id"])
        if new_ids:
            self.set_selection(new_ids)
            self.commit_history(before, "Duplicate selection")
            self.redraw()

    def copy_selected(self) -> str | None:
        if not self.selected_ids:
            return None
        self.clipboard_objects = [json.loads(json.dumps(obj)) for obj in self.project["objects"] if obj["id"] in self.selected_ids]
        self.show_status(f"Copied {len(self.clipboard_objects)} object(s)")
        return "break"

    def paste_clipboard(self) -> str | None:
        if not self.clipboard_objects:
            return None
        before = self.project_snapshot()
        new_ids = self.insert_object_copies(self.clipboard_objects, self.snap_step(), self.snap_step())
        if new_ids:
            self.set_selection(new_ids)
            self.commit_history(before, "Paste objects")
            self.redraw()
            self.show_status(f"Pasted {len(new_ids)} object(s)")
        return "break"

    def insert_object_copies(self, source_objects: list[dict[str, Any]], dx: float = 0.0, dy: float = 0.0) -> set[str]:
        new_ids: set[str] = set()
        group_map: dict[str, str] = {}
        for source in source_objects:
            obj = json.loads(json.dumps(source))
            old_group = obj.get("group")
            obj["id"] = object_id()
            if old_group:
                group_map.setdefault(str(old_group), f"grp_{uuid4().hex[:10]}")
                obj["group"] = group_map[str(old_group)]
            translate_object(obj, dx, dy)
            obj = validate_object(obj, len(self.project["objects"]) + 1)
            self.project["objects"].append(obj)
            new_ids.add(obj["id"])
        return new_ids

    def align_selection(self, mode: str) -> None:
        selected = [obj for obj in self.selected_objects() if not self.is_object_locked(obj)]
        if len(selected) < 2:
            return
        box = union_bounds(selected)
        if not box:
            return
        before = self.project_snapshot()
        left, top, width, height = box
        right, bottom = left + width, top + height
        center_x, center_y = left + width / 2, top + height / 2
        for obj in selected:
            x, y, w, h = bounds(obj)
            dx = dy = 0.0
            if mode == "left":
                dx = left - x
            elif mode == "right":
                dx = right - (x + w)
            elif mode == "top":
                dy = top - y
            elif mode == "bottom":
                dy = bottom - (y + h)
            elif mode == "center_x":
                dx = center_x - (x + w / 2)
            elif mode == "center_y":
                dy = center_y - (y + h / 2)
            translate_object(obj, dx, dy)
            obj.update(validate_object(obj, 1))
        self.commit_history(before, f"Align selection {mode}")
        self.redraw()

    def distribute_selection(self, axis: str) -> None:
        selected = [obj for obj in self.selected_objects() if not self.is_object_locked(obj)]
        if len(selected) < 3:
            self.show_status("Select at least three unlocked objects to distribute.")
            return
        index = 0 if axis == "horizontal" else 1
        selected.sort(key=lambda obj: object_center(obj)[index])
        centers = [object_center(obj)[index] for obj in selected]
        start, end = centers[0], centers[-1]
        if abs(end - start) < 0.000001:
            return
        before = self.project_snapshot()
        step = (end - start) / (len(selected) - 1)
        for order, obj in enumerate(selected):
            cx, cy = object_center(obj)
            target = start + step * order
            dx = target - cx if axis == "horizontal" else 0.0
            dy = target - cy if axis == "vertical" else 0.0
            translate_object(obj, dx, dy)
            obj.update(validate_object(obj, 1))
        self.commit_history(before, f"Distribute selection {axis}")
        self.redraw()

    def save_selection_as_template(self, name: str | None = None) -> None:
        selected = self.selected_objects()
        if not selected:
            return
        if name is None:
            name = simpledialog.askstring("Object template", "Name", parent=self)
        if not name:
            return
        before = self.project_snapshot()
        objects = [json.loads(json.dumps(obj)) for obj in selected]
        self.project.setdefault("objectTemplates", []).append({"name": name.strip(), "objects": objects})
        self.commit_history(before, "Save object template")
        self.show_status(f"Saved template: {name.strip()}")

    def insert_template(self, index: int) -> None:
        templates = self.project.get("objectTemplates", [])
        if index < 0 or index >= len(templates):
            return
        objects = templates[index].get("objects", [])
        if not objects:
            return
        before = self.project_snapshot()
        new_ids = self.insert_object_copies(objects, self.snap_step(), self.snap_step())
        if new_ids:
            self.set_selection(new_ids)
            self.commit_history(before, f"Insert template {templates[index].get('name', index)}")
            self.redraw()

    def selected_polygon(self) -> dict[str, Any] | None:
        obj = self.selected_object()
        if obj and obj.get("type") == "shape" and obj.get("kind") == "polygon":
            return obj
        return None

    def insert_polygon_midpoint(self, edge_index: int | None = None) -> None:
        obj = self.selected_polygon()
        if not obj:
            return
        points = validate_shape_points(obj.get("points"))
        if len(points) < 2:
            return
        if edge_index is None:
            if self.selected_polygon_point is not None:
                edge_index = self.selected_polygon_point
            else:
                edge_index = max(
                    range(len(points)),
                    key=lambda index: math.hypot(points[(index + 1) % len(points)]["x"] - points[index]["x"], points[(index + 1) % len(points)]["y"] - points[index]["y"]),
                )
        edge_index = max(0, min(len(points) - 1, int(edge_index)))
        next_point = points[(edge_index + 1) % len(points)]
        point = points[edge_index]
        before = self.project_snapshot()
        points.insert(edge_index + 1, {"x": (point["x"] + next_point["x"]) / 2, "y": (point["y"] + next_point["y"]) / 2})
        obj["points"] = points
        refresh_polygon_bounds(obj)
        obj.update(validate_object(obj, 1))
        self.selected_polygon_point = edge_index + 1
        self.commit_history(before, "Insert polygon point")
        self.redraw()

    def delete_polygon_point(self, index: int | None = None) -> None:
        obj = self.selected_polygon()
        if not obj:
            return
        points = validate_shape_points(obj.get("points"))
        if len(points) <= 3:
            self.show_status("A polygon needs at least three points.")
            return
        if index is None:
            index = self.selected_polygon_point if self.selected_polygon_point is not None else len(points) - 1
        index = max(0, min(len(points) - 1, int(index)))
        before = self.project_snapshot()
        points.pop(index)
        obj["points"] = points
        refresh_polygon_bounds(obj)
        obj.update(validate_object(obj, 1))
        self.selected_polygon_point = min(index, len(points) - 1)
        self.commit_history(before, "Delete polygon point")
        self.redraw()

    def fit_view_to_selection(self) -> None:
        box = union_bounds(self.selected_objects())
        if not box or not hasattr(self, "canvas"):
            return
        left, top, width, height = box
        canvas_w = max(1, self.canvas.winfo_width() - 24)
        canvas_h = max(1, self.canvas.winfo_height() - 24)
        target_zoom = min(canvas_w / max(1, width * self.settings["cellSize"]), canvas_h / max(1, height * self.settings["cellSize"]))
        self.zoom.set(max(0.35, min(2.2, target_zoom * 0.9)))
        self.redraw()
        total_w, total_h = canvas_size(self.project, self.zoom.get())
        cell = self.cell
        self.canvas.xview_moveto(max(0, min(1, (left * cell - 12) / max(1, total_w - self.canvas.winfo_width()))))
        self.canvas.yview_moveto(max(0, min(1, (top * cell - 12) / max(1, total_h - self.canvas.winfo_height()))))
        self.redraw_minimap()

    def bring_selected_to_front(self) -> None:
        self.reorder_selected(front=True)

    def send_selected_to_back(self) -> None:
        self.reorder_selected(front=False)

    def reorder_selected(self, front: bool) -> None:
        if not self.selected_ids:
            return
        before = self.project_snapshot()
        selected = [obj for obj in self.project["objects"] if obj["id"] in self.selected_ids and not self.is_object_locked(obj)]
        selected_ids = {obj["id"] for obj in selected}
        others = [obj for obj in self.project["objects"] if obj["id"] not in selected_ids]
        if not selected:
            return
        self.project["objects"] = others + selected if front else selected + others
        self.commit_history(before, "Bring selection forward" if front else "Send selection back")
        self.redraw()

    def toggle_selected_lock(self) -> None:
        if not self.selected_ids:
            return
        before = self.project_snapshot()
        selected = self.selected_objects()
        unlock = any(obj.get("locked", False) for obj in selected)
        for obj in selected:
            obj["locked"] = not unlock
        self.commit_history(before, "Toggle selection lock")
        self.redraw()

    def event_to_grid(self, event: tk.Event) -> tuple[float, float]:
        x = self.canvas.canvasx(event.x) / self.cell
        y = self.canvas.canvasy(event.y) / self.cell
        return x, y

    def find_hit(self, x: float, y: float) -> dict[str, Any] | None:
        tolerance = 0.35
        for obj in reversed(self.project["objects"]):
            if not self.is_object_visible(obj) or self.is_object_locked(obj):
                continue
            bx, by, bw, bh = bounds(obj)
            if bx - tolerance <= x <= bx + bw + tolerance and by - tolerance <= y <= by + bh + tolerance:
                return obj
        return None

    def find_room_at(self, x: float, y: float) -> dict[str, Any] | None:
        for obj in reversed(self.project["objects"]):
            if obj.get("type") not in {"room", "round", "cave"}:
                continue
            bx, by, bw, bh = bounds(obj)
            if bx <= x <= bx + bw and by <= y <= by + bh:
                return obj
        return None

    def active_layer_id(self, default: str = "symbols") -> str:
        name = self.current_layer_var.get()
        for layer in self.project.get("layers", []):
            if layer.get("name") == name:
                return layer["id"]
        return default

    def layer_name(self, layer_id: str) -> str:
        return next((layer.get("name", layer_id) for layer in self.project.get("layers", []) if layer.get("id") == layer_id), layer_id)

    def layer_id_from_name(self, name: str) -> str:
        return next((layer["id"] for layer in self.project.get("layers", []) if layer.get("name") == name), normalize_layer_id(name))

    def layer_state(self, layer_id: str) -> dict[str, Any]:
        return next((layer for layer in self.project.get("layers", []) if layer.get("id") == layer_id), {"visible": True, "locked": False})

    def is_layer_visible(self, layer_id: str) -> bool:
        return bool(self.layer_state(layer_id).get("visible", True))

    def is_layer_locked(self, layer_id: str) -> bool:
        return bool(self.layer_state(layer_id).get("locked", False))

    def is_object_visible(self, obj: dict[str, Any]) -> bool:
        return self.is_layer_visible(obj.get("layer", normalize_layer_id(None, obj.get("type"))))

    def is_object_locked(self, obj: dict[str, Any]) -> bool:
        return bool(obj.get("locked", False)) or self.is_layer_locked(obj.get("layer", normalize_layer_id(None, obj.get("type"))))

    def set_selection(self, ids: set[str], primary: str | None = None) -> None:
        existing = {obj["id"] for obj in self.project["objects"]}
        self.selected_ids = set(ids) & existing
        if primary in self.selected_ids:
            self.selected_id = primary
        else:
            self.selected_id = next(iter(self.selected_ids), None)
        self.selected_polygon_point = None

    def ids_for_hit(self, obj: dict[str, Any]) -> set[str]:
        group = obj.get("group")
        if not group:
            return {obj["id"]}
        return {item["id"] for item in self.project["objects"] if item.get("group") == group and self.is_object_visible(item) and not self.is_object_locked(item)}

    def toggle_hit_selection(self, obj: dict[str, Any]) -> None:
        ids = self.ids_for_hit(obj)
        if ids <= self.selected_ids:
            self.set_selection(self.selected_ids - ids)
        else:
            self.set_selection(self.selected_ids | ids, primary=obj["id"])

    def selected_objects(self) -> list[dict[str, Any]]:
        return [obj for obj in self.project["objects"] if obj["id"] in self.selected_ids]

    def selected_object(self) -> dict[str, Any] | None:
        return next((obj for obj in self.project["objects"] if obj["id"] == self.selected_id), None)

    def group_selected(self) -> None:
        if len(self.selected_ids) < 2:
            return
        before = self.project_snapshot()
        group_id = f"grp_{uuid4().hex[:10]}"
        for obj in self.project["objects"]:
            if obj["id"] in self.selected_ids:
                obj["group"] = group_id
        self.commit_history(before, "Group selection")
        self.redraw()

    def ungroup_selected(self) -> None:
        if not self.selected_ids:
            return
        before = self.project_snapshot()
        groups = {obj.get("group") for obj in self.selected_objects() if obj.get("group")}
        changed = False
        for obj in self.project["objects"]:
            if obj["id"] in self.selected_ids or obj.get("group") in groups:
                if "group" in obj:
                    obj.pop("group", None)
                    changed = True
        if changed:
            self.set_selection({obj["id"] for obj in self.project["objects"] if obj["id"] in self.selected_ids})
            self.commit_history(before, "Ungroup selection")
            self.redraw()

    def select_objects_in_box(self, box: tuple[float, float, float, float]) -> None:
        x1, y1, x2, y2 = box
        left, right = sorted((x1, x2))
        top, bottom = sorted((y1, y2))
        if abs(right - left) < 0.05 and abs(bottom - top) < 0.05:
            return
        selected: set[str] = set()
        for obj in self.project["objects"]:
            if not self.is_object_visible(obj) or self.is_object_locked(obj):
                continue
            bx, by, bw, bh = bounds(obj)
            if bx <= right and bx + bw >= left and by <= bottom and by + bh >= top:
                selected.add(obj["id"])
        if selected:
            self.set_selection(self.selected_ids | selected)

    def next_room_number(self) -> str:
        area = self.settings.get("numberArea", "").strip()
        prefix = f"{area}" if area else ""
        numbers = [
            int(str(obj["text"])[len(prefix):] if prefix and str(obj["text"]).startswith(prefix) else obj["text"])
            for obj in self.project["objects"]
            if obj.get("type") == "text"
            and obj.get("textRole") == "number"
            and obj.get("numberArea", "") == area
            and str(obj.get("text", "")).removeprefix(prefix).isdigit()
        ]
        numbers.extend(
            int(str(obj.get("roomNumber", ""))[len(prefix):] if prefix and str(obj.get("roomNumber", "")).startswith(prefix) else str(obj.get("roomNumber", "")))
            for obj in self.project["objects"]
            if obj.get("type") in {"room", "round", "cave"}
            and str(obj.get("roomNumber", "")).removeprefix(prefix).isdigit()
        )
        number = max(numbers) + 1 if numbers else int(self.settings.get("numberStart", 1))
        return f"{prefix}{number}"

    def redraw(self) -> None:
        self.canvas.delete("all")
        scale = self.zoom.get()
        render_tk(self.canvas, self.project, scale, self.selected_ids, self.selected_id, self.draft, self.selection_box, self.visible_grid_box())
        self.draw_navigation_overlays()
        width, height = canvas_size(self.project, scale)
        self.canvas.configure(scrollregion=(0, 0, width, height))
        self.update_selection_panel()
        self.refresh_object_list()
        self.rebuild_navigator_panel()
        self.refresh_toolbar()
        self.update_cursor()
        self.update_status()
        self.redraw_minimap()

    def draw_navigation_overlays(self) -> None:
        draw_tk_zones(self.canvas, self.project, self.zoom.get())
        draw_tk_markers(self.canvas, self.project, self.zoom.get())
        draw_tk_measure_overlay(self.canvas, self.settings, self.measure_points, self.measure_preview, self.zoom.get())
        draw_tk_ruler_overlay(self.canvas, self.project, self.zoom.get(), self.mouse_grid, self.live_measure_points())

    def visible_grid_box(self) -> tuple[float, float, float, float]:
        c = max(1, self.cell)
        left = self.canvas.canvasx(0) / c
        top = self.canvas.canvasy(0) / c
        width = max(1, self.canvas.winfo_width()) / c
        height = max(1, self.canvas.winfo_height()) / c
        return left - 2, top - 2, width + 4, height + 4

    def redraw_minimap(self) -> None:
        if not hasattr(self, "minimap"):
            return
        self.minimap.delete("all")
        width = max(1, self.minimap.winfo_width())
        height = max(1, self.minimap.winfo_height())
        map_w = max(1.0, canvas_size(self.project, 1.0)[0] / self.settings["cellSize"])
        map_h = max(1.0, canvas_size(self.project, 1.0)[1] / self.settings["cellSize"])
        scale = min((width - 12) / map_w, (height - 12) / map_h)
        ox = (width - map_w * scale) / 2
        oy = (height - map_h * scale) / 2
        self.minimap.create_rectangle(ox, oy, ox + map_w * scale, oy + map_h * scale, fill=self.settings["backgroundColor"], outline="#7fa7b5")
        for obj in self.project["objects"]:
            if not should_render_object(self.project, obj, for_export=False):
                continue
            x, y, w, h = bounds(obj)
            color = self.settings["selectionColor"] if obj["id"] in self.selected_ids else self.settings["gridColor"]
            self.minimap.create_rectangle(ox + x * scale, oy + y * scale, ox + (x + w) * scale, oy + (y + h) * scale, outline=color, fill="")
        vx, vy, vw, vh = self.visible_grid_box()
        self.minimap.create_rectangle(ox + vx * scale, oy + vy * scale, ox + (vx + vw) * scale, oy + (vy + vh) * scale, outline="#d13f3f", width=2)

    def on_minimap_press(self, event: tk.Event) -> str:
        map_px_w, map_px_h = canvas_size(self.project, self.zoom.get())
        width = max(1, self.minimap.winfo_width())
        height = max(1, self.minimap.winfo_height())
        map_w = max(1.0, canvas_size(self.project, 1.0)[0] / self.settings["cellSize"])
        map_h = max(1.0, canvas_size(self.project, 1.0)[1] / self.settings["cellSize"])
        scale = min((width - 12) / map_w, (height - 12) / map_h)
        ox = (width - map_w * scale) / 2
        oy = (height - map_h * scale) / 2
        gx = max(0.0, min(map_w, (event.x - ox) / scale))
        gy = max(0.0, min(map_h, (event.y - oy) / scale))
        view_w = max(1, self.canvas.winfo_width())
        view_h = max(1, self.canvas.winfo_height())
        target_x = gx * self.cell - view_w / 2
        target_y = gy * self.cell - view_h / 2
        self.canvas.xview_moveto(max(0, min(1, target_x / max(1, map_px_w - view_w))))
        self.canvas.yview_moveto(max(0, min(1, target_y / max(1, map_px_h - view_h))))
        self.redraw_minimap()
        return "break"

    def object_label(self, obj: dict[str, Any]) -> str:
        label = obj.get("type", "object")
        if obj.get("type") == "symbol":
            label = legend_label_for_kind(self.project, symbol_legend_key(self.project, obj))
        elif obj.get("type") == "text":
            label = str(obj.get("text") or "Text").replace("\n", " ")[:32]
        elif obj.get("type") in {"room", "round", "cave"} and obj.get("roomName"):
            label = str(obj.get("roomName"))
        bx, by, _bw, _bh = bounds(obj)
        return f"{obj.get('type', 'object')} | {label} | {self.layer_name(obj.get('layer', ''))} | {bx:.1f},{by:.1f}"

    def refresh_object_list(self) -> None:
        if not getattr(self, "object_listbox", None):
            return
        layer_values = ["All"] + [layer.get("name", layer["id"]) for layer in self.project.get("layers", [])]
        current_layer = self.object_layer_filter_var.get()
        self.object_layer_combo.configure(values=tuple(layer_values))
        if current_layer not in layer_values:
            self.object_layer_filter_var.set("All")
        search = self.object_search_var.get().strip().lower()
        type_filter = self.object_type_filter_var.get()
        layer_filter = self.object_layer_filter_var.get()
        layer_id = self.layer_id_from_name(layer_filter) if layer_filter != "All" else ""
        self.object_list_ids = []
        self._refreshing_object_list = True
        try:
            self.object_listbox.delete(0, "end")
            for obj in self.project.get("objects", []):
                if type_filter != "All" and obj.get("type") != type_filter:
                    continue
                if layer_id and obj.get("layer") != layer_id:
                    continue
                label = self.object_label(obj)
                if search and search not in label.lower() and search not in str(obj.get("id", "")).lower():
                    continue
                self.object_list_ids.append(obj["id"])
                self.object_listbox.insert("end", label)
            for index, obj_id in enumerate(self.object_list_ids):
                if obj_id in self.selected_ids:
                    self.object_listbox.selection_set(index)
                    self.object_listbox.see(index)
        finally:
            self._refreshing_object_list = False

    def on_object_list_select(self, _event: tk.Event | None = None) -> None:
        if getattr(self, "_refreshing_object_list", False) or not self.object_listbox:
            return
        selection = self.object_listbox.curselection()
        if not selection:
            return
        obj_id = self.object_list_ids[selection[0]]
        self.set_selection({obj_id}, primary=obj_id)
        self.redraw()

    def jump_to_grid(self, x: float, y: float, zoom: float | None = None) -> None:
        if zoom is not None:
            self.zoom.set(max(0.35, min(2.2, zoom)))
            self.redraw()
        map_px_w, map_px_h = canvas_size(self.project, self.zoom.get())
        view_w = max(1, self.canvas.winfo_width())
        view_h = max(1, self.canvas.winfo_height())
        target_x = x * self.cell - view_w / 2
        target_y = y * self.cell - view_h / 2
        self.canvas.xview_moveto(max(0, min(1, target_x / max(1, map_px_w - view_w))))
        self.canvas.yview_moveto(max(0, min(1, target_y / max(1, map_px_h - view_h))))
        self.redraw_minimap()

    def jump_to_selected_object(self) -> None:
        obj = self.selected_object()
        if not obj and self.object_listbox and self.object_listbox.curselection():
            obj_id = self.object_list_ids[self.object_listbox.curselection()[0]]
            obj = next((item for item in self.project["objects"] if item["id"] == obj_id), None)
            if obj:
                self.set_selection({obj_id}, primary=obj_id)
        if not obj:
            return
        bx, by, bw, bh = bounds(obj)
        self.jump_to_grid(bx + bw / 2, by + bh / 2)
        self.redraw()

    def current_view_box(self) -> tuple[float, float, float, float]:
        c = max(1, self.cell)
        left = max(0.0, self.canvas.canvasx(0) / c)
        top = max(0.0, self.canvas.canvasy(0) / c)
        width = max(1.0, self.canvas.winfo_width() / c)
        height = max(1.0, self.canvas.winfo_height() / c)
        return left, top, width, height

    def current_view_center(self) -> tuple[float, float]:
        left, top, width, height = self.current_view_box()
        return left + width / 2, top + height / 2

    def save_current_view(self) -> None:
        name = simpledialog.askstring("Saved view", "Name", initialvalue=f"View {len(self.project.get('views', [])) + 1}", parent=self)
        if not name:
            return
        before = self.project_snapshot()
        x, y = self.current_view_center()
        self.project.setdefault("views", []).append({"id": nav_id("view"), "name": name.strip() or "View", "x": x, "y": y, "zoom": self.zoom.get()})
        self.commit_history(before, "Save view")
        self.rebuild_navigator_panel()

    def add_jump_marker(self) -> None:
        name = simpledialog.askstring("Jump marker", "Name", initialvalue=f"Marker {len(self.project.get('markers', [])) + 1}", parent=self)
        if not name:
            return
        before = self.project_snapshot()
        x, y = self.mouse_grid if self.mouse_grid else self.current_view_center()
        self.project.setdefault("markers", []).append({"id": nav_id("mark"), "name": name.strip() or "Marker", "x": x, "y": y})
        self.commit_history(before, "Add jump marker")
        self.rebuild_navigator_panel()
        self.redraw()

    def define_zone_from_selection(self) -> None:
        box = union_bounds(self.selected_objects()) if self.selected_ids else self.current_view_box()
        if not box:
            return
        name = simpledialog.askstring("Zone", "Name", initialvalue=f"Zone {len(self.project.get('zones', [])) + 1}", parent=self)
        if not name:
            return
        before = self.project_snapshot()
        x, y, width, height = box
        self.project.setdefault("zones", []).append(
            {
                "id": nav_id("zone"),
                "name": name.strip() or "Zone",
                "x": x,
                "y": y,
                "width": max(0.25, width),
                "height": max(0.25, height),
                "color": self.settings.get("selectionColor", SELECT),
                "visible": True,
            }
        )
        self.commit_history(before, "Define zone")
        self.rebuild_navigator_panel()
        self.redraw()

    def add_measure_point(self, point: tuple[float, float]) -> None:
        if self.measure_points and math.hypot(point[0] - self.measure_points[-1][0], point[1] - self.measure_points[-1][1]) < 0.000001:
            return
        if len(self.measure_points) >= 3 and math.hypot(point[0] - self.measure_points[0][0], point[1] - self.measure_points[0][1]) <= self.polygon_close_tolerance():
            self.measure_preview = None
            self.show_status(self.measurement_status())
            self.redraw()
            return
        self.measure_points.append(point)
        self.measure_preview = None
        self.show_status(self.measurement_status())
        self.redraw()

    def clear_measurement(self) -> None:
        if not self.measure_points and self.measure_preview is None:
            return
        self.measure_points = []
        self.measure_preview = None
        self.redraw()

    def live_measure_points(self) -> list[tuple[float, float]]:
        points = list(self.measure_points)
        if self.measure_preview is not None:
            if not points or math.hypot(points[-1][0] - self.measure_preview[0], points[-1][1] - self.measure_preview[1]) > 0.000001:
                points.append(self.measure_preview)
        return points

    def measurement_status(self) -> str:
        points = self.live_measure_points()
        if len(points) < 2:
            return "measure | click points to measure distance, path length and area"
        return measurement_summary(points, self.settings)

    def rebuild_navigator_panel(self) -> None:
        self.refresh_link_target_options()
        if not getattr(self, "navigator_listbox", None):
            return
        selected = self.navigator_listbox.curselection()
        selected_item = self.nav_list_items[selected[0]] if selected else None
        self.nav_list_items = []
        self.navigator_listbox.delete(0, "end")
        for view in self.project.get("views", []):
            self.nav_list_items.append(("view", view["id"]))
            self.navigator_listbox.insert("end", f"View | {view['name']} | {view['x']:.1f},{view['y']:.1f} @ {view['zoom']:.2f}")
        for marker in self.project.get("markers", []):
            self.nav_list_items.append(("marker", marker["id"]))
            self.navigator_listbox.insert("end", f"Marker | {marker['name']} | {marker['x']:.1f},{marker['y']:.1f}")
        for zone in self.project.get("zones", []):
            self.nav_list_items.append(("zone", zone["id"]))
            self.navigator_listbox.insert("end", f"Zone | {zone['name']} | {zone['width']:.1f} x {zone['height']:.1f}")
        if selected_item and selected_item in self.nav_list_items:
            index = self.nav_list_items.index(selected_item)
            self.navigator_listbox.selection_set(index)
            self.navigator_listbox.see(index)

    def selected_nav_item(self) -> tuple[str, dict[str, Any]] | None:
        if not self.navigator_listbox:
            return None
        selection = self.navigator_listbox.curselection()
        if not selection or selection[0] >= len(self.nav_list_items):
            return None
        kind, item_id = self.nav_list_items[selection[0]]
        source = {"view": "views", "marker": "markers", "zone": "zones"}[kind]
        item = next((entry for entry in self.project.get(source, []) if entry.get("id") == item_id), None)
        return (kind, item) if item else None

    def jump_to_nav_item(self) -> None:
        selected = self.selected_nav_item()
        if not selected:
            return
        kind, item = selected
        if kind == "view":
            self.jump_to_grid(item["x"], item["y"], item.get("zoom", self.zoom.get()))
        elif kind == "marker":
            self.jump_to_grid(item["x"], item["y"])
        elif kind == "zone":
            self.jump_to_grid(item["x"] + item["width"] / 2, item["y"] + item["height"] / 2)
        self.redraw()

    def delete_nav_item(self) -> None:
        selected = self.selected_nav_item()
        if not selected:
            return
        kind, item = selected
        source = {"view": "views", "marker": "markers", "zone": "zones"}[kind]
        before = self.project_snapshot()
        self.project[source] = [entry for entry in self.project.get(source, []) if entry.get("id") != item.get("id")]
        self.commit_history(before, f"Delete {kind}")
        self.rebuild_navigator_panel()
        self.redraw()

    def link_selected_to_map(self) -> None:
        obj = self.selected_object()
        target = self.map_from_option(self.link_target_map_var.get())
        if not obj or obj.get("type") != "symbol":
            self.show_status("Select a stairs, portal or marker symbol first.")
            return
        if not target:
            self.show_status("No target map available.")
            return
        before = self.project_snapshot()
        obj["targetMapId"] = target["id"]
        obj["targetObjectId"] = ""
        obj["linkLabel"] = str(target.get("name") or "")
        self.commit_history(before, "Link floor marker")
        self.redraw()

    def follow_selected_link(self) -> None:
        obj = self.selected_object()
        if not obj or not obj.get("targetMapId"):
            self.show_status("No floor link on the selected object.")
            return
        target_map_id = str(obj.get("targetMapId"))
        target_object_id = str(obj.get("targetObjectId") or "")
        if target_map_id != self.project.get("activeMapId"):
            self.set_active_map(target_map_id, commit=True)
        target = next((item for item in self.project.get("objects", []) if item.get("id") == target_object_id), None)
        if target:
            self.set_selection({target["id"]}, primary=target["id"])
            bx, by, bw, bh = bounds(target)
            self.jump_to_grid(bx + bw / 2, by + bh / 2)
        else:
            self.jump_to_grid(self.settings["width"] / 2, self.settings["height"] / 2)
        self.redraw()

    def update_selection_panel(self) -> None:
        for child in self.selection_frame.winfo_children():
            child.destroy()
        obj = self.selected_object()
        if len(self.selected_ids) > 1:
            ttk.Label(self.selection_frame, text=f"{len(self.selected_ids)} objects selected").grid(row=0, column=0, columnspan=2, sticky="w")
            ttk.Button(self.selection_frame, text="Group", command=self.group_selected).grid(row=1, column=0, sticky="ew", pady=2)
            ttk.Button(self.selection_frame, text="Ungroup", command=self.ungroup_selected).grid(row=1, column=1, sticky="ew", pady=2)
            self._selection_layer_row(2)
            ttk.Button(self.selection_frame, text="Duplicate", command=self.duplicate_selected).grid(row=3, column=0, sticky="ew", pady=2)
            ttk.Button(self.selection_frame, text="Lock", command=self.toggle_selected_lock).grid(row=3, column=1, sticky="ew", pady=2)
            ttk.Button(self.selection_frame, text="Front", command=self.bring_selected_to_front).grid(row=4, column=0, sticky="ew", pady=2)
            ttk.Button(self.selection_frame, text="Back", command=self.send_selected_to_back).grid(row=4, column=1, sticky="ew", pady=2)
            align_row = ttk.Frame(self.selection_frame)
            align_row.grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)
            for index, (label, mode) in enumerate([("L", "left"), ("R", "right"), ("T", "top"), ("B", "bottom"), ("CX", "center_x"), ("CY", "center_y")]):
                ttk.Button(align_row, text=label, width=3, command=lambda value=mode: self.align_selection(value)).grid(row=0, column=index, sticky="ew", padx=1)
                align_row.columnconfigure(index, weight=1)
            dist_row = ttk.Frame(self.selection_frame)
            dist_row.grid(row=6, column=0, columnspan=2, sticky="ew", pady=2)
            ttk.Button(dist_row, text="Distribute H", command=lambda: self.distribute_selection("horizontal")).grid(row=0, column=0, sticky="ew", padx=1)
            ttk.Button(dist_row, text="Distribute V", command=lambda: self.distribute_selection("vertical")).grid(row=0, column=1, sticky="ew", padx=1)
            dist_row.columnconfigure(0, weight=1)
            dist_row.columnconfigure(1, weight=1)
            ttk.Button(self.selection_frame, text="Delete", command=self.delete_selected).grid(row=7, column=0, columnspan=2, sticky="ew", pady=2)
            return
        if not obj:
            ttk.Label(self.selection_frame, text="No object selected.").grid(row=0, column=0, sticky="w")
            return
        ttk.Label(self.selection_frame, text=obj["type"]).grid(row=0, column=0, sticky="w")
        ttk.Button(self.selection_frame, text="Delete", command=self.delete_selected).grid(row=0, column=1, sticky="e")
        self._selection_layer_row(1)
        action_row = ttk.Frame(self.selection_frame)
        action_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(2, 4))
        for index, (label, command) in enumerate(
            [
                ("Duplicate", self.duplicate_selected),
                ("Front", self.bring_selected_to_front),
                ("Back", self.send_selected_to_back),
                ("Unlock" if obj.get("locked") else "Lock", self.toggle_selected_lock),
            ]
        ):
            ttk.Button(action_row, text=label, command=command).grid(row=0, column=index, sticky="ew", padx=1)
            action_row.columnconfigure(index, weight=1)
        fields_start = 3
        if obj.get("type") == "shape" and obj.get("kind") == "polygon":
            point_row = ttk.Frame(self.selection_frame)
            point_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 4))
            ttk.Button(point_row, text="+ Point", command=self.insert_polygon_midpoint).grid(row=0, column=0, sticky="ew", padx=1)
            ttk.Button(point_row, text="- Point", command=self.delete_polygon_point).grid(row=0, column=1, sticky="ew", padx=1)
            point_row.columnconfigure(0, weight=1)
            point_row.columnconfigure(1, weight=1)
            fields_start = 4
        fields = ["x", "y"]
        if obj["type"] == "diagonal_corridor":
            fields += ["x2", "y2"]
        if "width" in obj and "height" in obj:
            fields += ["width", "height"]
        elif obj["type"] == "diagonal_corridor":
            fields += ["width"]
        if obj["type"] in FLOOR_TYPES:
            fields += ["wallThickness", "wallType"]
        if obj["type"] in {"room", "round", "cave"}:
            fields += ["roomNumber", "roomName", "roomStatus", "description", "contents", "monsters", "treasure", "traps", "readAloud", "lootTable", "rumors", "clues", "secrets", "handoutText", "gmNotes", "playerVisible"]
        if obj["type"] == "symbol":
            fields += ["kind", "variant", "sizePreset", "size", "rotation", "color", "opacity", "shadow", "outline", "legendLabel", "targetMapId", "targetObjectId", "linkLabel", "rumors", "clues", "secrets", "handoutText", "gmNotes"]
        if obj["type"] == "shape":
            fields += ["kind", "lineWidth", "lineStyle", "strokeColor", "fillColor", "opacity", "rotation", "curve"]
            if obj.get("kind") == "line":
                fields += ["arrow", "x2", "y2"]
        if obj["type"] == "text":
            fields += ["text", "size", "width", "font", "color", "align", "rotation", "numberArea", "roomId", "export"]
        if obj["type"] == "legend":
            fields += ["columns", "scale", "manualEntries"]
        for row, field in enumerate(fields, start=fields_start):
            ttk.Label(self.selection_frame, text=field).grid(row=row, column=0, sticky="w")
            value = obj.get(field, "")
            if field == "manualEntries" and isinstance(value, list):
                value = "; ".join(value)
            if field in {"color", "strokeColor", "fillColor"}:
                self._selection_color_row(row, field, str(value))
                continue
            if field == "variant" and obj.get("type") == "symbol":
                values = tuple(dict.fromkeys(["", *(option["id"] for option in symbol_variant_options(self.project, obj.get("kind", "door")))]))
                var = tk.StringVar(value=str(value) if str(value) in values else "")
                combo = ttk.Combobox(self.selection_frame, textvariable=var, values=values, width=12, state="readonly")
                combo.grid(row=row, column=1, sticky="ew", pady=1)
                combo.bind("<<ComboboxSelected>>", lambda _e, f=field, v=var: self.change_selected(f, v.get()))
                continue
            var = tk.StringVar(value=str(value))
            if field in {"lineStyle", "arrow", "roomStatus", "wallType", "sizePreset"}:
                if field == "lineStyle":
                    values = tuple(sorted(LINE_STYLES))
                elif field == "arrow":
                    values = tuple(sorted(ARROW_STYLES))
                elif field == "roomStatus":
                    values = ROOM_STATUSES
                elif field == "sizePreset":
                    values = tuple(SYMBOL_SIZE_PRESETS)
                else:
                    values = WALL_TYPES
                combo = ttk.Combobox(self.selection_frame, textvariable=var, values=values, width=12, state="readonly")
                combo.grid(row=row, column=1, sticky="ew", pady=1)
                combo.bind("<<ComboboxSelected>>", lambda _e, f=field, v=var: self.change_selected(f, v.get()))
                continue
            entry = ttk.Entry(self.selection_frame, textvariable=var, width=12)
            entry.grid(row=row, column=1, sticky="ew", pady=1)
            entry.bind("<Return>", lambda _e, f=field, v=var: self.change_selected(f, v.get()))
            entry.bind("<FocusOut>", lambda _e, f=field, v=var: self.change_selected(f, v.get()))

    def _selection_color_row(self, row: int, field: str, value: str) -> None:
        holder = ttk.Frame(self.selection_frame)
        holder.grid(row=row, column=1, sticky="ew", pady=1)
        holder.columnconfigure(1, weight=1)

        swatch_color = self.display_color(value)
        swatch = tk.Label(
            holder,
            width=3,
            relief="sunken",
            borderwidth=1,
            background=swatch_color or "#f9fcfd",
            text="" if swatch_color else "none",
            foreground="#17384a",
            font=("Segoe UI", 7),
        )
        swatch.grid(row=0, column=0, sticky="nsw", padx=(0, 4))

        var = tk.StringVar(value=value)
        entry = ttk.Entry(holder, textvariable=var, width=9)
        entry.grid(row=0, column=1, sticky="ew")
        entry.bind("<Return>", lambda _e, f=field, v=var: self.change_selected(f, v.get()))
        entry.bind("<FocusOut>", lambda _e, f=field, v=var: self.change_selected(f, v.get()))

        ttk.Button(holder, text="Pick", width=5, command=lambda f=field, v=var: self.pick_selected_color(f, v.get())).grid(row=0, column=2, sticky="e", padx=(4, 0))
        if field == "fillColor":
            ttk.Button(holder, text="Clear", width=5, command=lambda: self.change_selected("fillColor", "")).grid(row=0, column=3, sticky="e", padx=(4, 0))

    def display_color(self, value: str) -> str:
        value = str(value or "").strip()
        if not value:
            return ""
        try:
            self.winfo_rgb(value)
        except tk.TclError:
            return ""
        return value

    def pick_selected_color(self, field: str, current: str) -> None:
        initial = self.display_color(current)
        if not initial:
            obj = self.selected_object() or {}
            if field == "fillColor":
                initial = obj.get("fillColor") or self.settings.get("floorColor", WHITE)
            else:
                initial = obj.get(field) or self.settings.get("defaultShapeStrokeColor") or self.settings.get("textColor") or self.settings["gridColor"]
        color = colorchooser.askcolor(color=initial, parent=self)[1]
        if color:
            self.change_selected(field, color)

    def _selection_layer_row(self, row: int) -> None:
        ttk.Label(self.selection_frame, text="layer").grid(row=row, column=0, sticky="w")
        layer_names = [layer["name"] for layer in self.project.get("layers", []) if layer["id"] != "background"]
        current = self.layer_name(self.selected_object().get("layer", "symbols")) if self.selected_object() else ""
        layer_var = tk.StringVar(value=current)
        combo = ttk.Combobox(self.selection_frame, textvariable=layer_var, values=layer_names, state="readonly", width=12)
        combo.grid(row=row, column=1, sticky="ew", pady=1)
        combo.bind("<<ComboboxSelected>>", lambda _e, v=layer_var: self.move_selection_to_layer(self.layer_id_from_name(v.get())))

    def move_selection_to_layer(self, layer_id: str) -> None:
        if not self.selected_ids:
            return
        before = self.project_snapshot()
        for obj in self.project["objects"]:
            if obj["id"] in self.selected_ids and obj.get("type") != "legend":
                obj["layer"] = layer_id
        self.commit_history(before, "Move selection to layer")
        self.redraw()

    def change_selected(self, field: str, value: str) -> None:
        obj = self.selected_object()
        if not obj:
            return
        try:
            if field in {"text", "kind", "variant", "sizePreset", "font", "color", "align", "numberArea", "roomId", "roomNumber", "roomName", "roomStatus", "description", "contents", "monsters", "treasure", "traps", "readAloud", "lootTable", "rumors", "clues", "secrets", "handoutText", "gmNotes", "strokeColor", "fillColor", "lineStyle", "arrow", "wallType", "targetMapId", "targetObjectId", "linkLabel", "legendLabel"}:
                new_value = value
            elif field in {"export", "playerVisible", "curve", "shadow", "outline"}:
                new_value = value.strip().lower() not in {"0", "false", "no", "off", "nein"}
            elif field == "manualEntries":
                new_value = [item.strip() for item in value.split(";") if item.strip()]
            elif field in {"columns", "sides"}:
                new_value = max(1, int(float(value)))
            else:
                new_value = float(value)
        except ValueError:
            return
        if field in {"color", "strokeColor", "fillColor"} and str(new_value).strip() and not self.display_color(str(new_value)):
            self.show_status(f"Invalid color: {new_value}")
            return
        if obj.get(field) == new_value:
            return
        before = self.project_snapshot()
        if field == "rotation" and obj.get("type") == "shape":
            old_rotation = float(obj.get("rotation", 0)) % 360
            target_rotation = float(new_value) % 360
            rotate_shape_geometry(obj, target_rotation - old_rotation)
            new_value = target_rotation
        if field == "kind" and obj.get("type") == "symbol":
            new_value = normalize_symbol_kind(str(new_value))
            obj["variant"] = ""
        if field == "sizePreset" and obj.get("type") == "symbol":
            if str(new_value) not in SYMBOL_SIZE_PRESETS:
                return
            obj["size"] = symbol_size_for_preset(new_value)
        obj[field] = new_value
        if field == "legendLabel" and obj.get("type") == "symbol" and is_custom_symbol(self.project, obj.get("kind", "")):
            self.project.setdefault("customSymbols", {}).setdefault(obj["kind"], {})["legendLabel"] = str(new_value)
        if field in {"width", "height", "size", "scale"}:
            obj[field] = max(0.25, float(obj[field]))
        if field == "rotation":
            obj[field] = float(obj[field]) % 360
        if field == "opacity":
            obj[field] = max(0.0, min(1.0, float(obj[field])))
        if obj.get("type") == "shape":
            obj.update(validate_object(obj, 1))
        if obj.get("type") in FLOOR_TYPES or obj.get("type") == "symbol":
            obj.update(validate_object(obj, 1))
        if obj.get("type") == "text" and field == "export":
            obj["layer"] = "text" if obj["export"] else "notes"
        self.sync_campaign_from_rooms()
        self.commit_history(before, f"Change {field}")
        self.redraw()

    def selected_room(self) -> dict[str, Any] | None:
        obj = self.selected_object()
        if obj and obj.get("type") in {"room", "round", "cave"}:
            return obj
        return next((item for item in self.project.get("objects", []) if item.get("id") in self.selected_ids and item.get("type") in {"room", "round", "cave"}), None)

    def open_room_form(self) -> None:
        room = self.selected_room()
        if not room:
            self.show_status("Select a room, round room, or cave first.")
            return
        dialog = tk.Toplevel(self)
        dialog.title(f"Room - {room.get('roomName') or room.get('roomNumber') or room['id']}")
        dialog.transient(self)
        dialog.grab_set()
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(dialog)
        notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        text_widgets: dict[str, tk.Text] = {}
        entry_vars: dict[str, tk.Variable] = {
            "roomNumber": tk.StringVar(value=room.get("roomNumber", "")),
            "roomName": tk.StringVar(value=room.get("roomName", "")),
            "roomStatus": tk.StringVar(value=room.get("roomStatus", "undiscovered")),
            "playerVisible": tk.BooleanVar(value=room.get("playerVisible", True)),
        }

        def add_text(parent: ttk.Frame, label: str, field: str, row: int, height: int = 5) -> None:
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
            text = tk.Text(parent, width=58, height=height, wrap="word")
            text.grid(row=row + 1, column=0, sticky="nsew", pady=(1, 8))
            text.insert("1.0", str(room.get(field, "")))
            text_widgets[field] = text
            parent.rowconfigure(row + 1, weight=1)

        overview = ttk.Frame(notebook, padding=8)
        overview.columnconfigure(1, weight=1)
        notebook.add(overview, text="Basis")
        for row, (label, field) in enumerate([("Number", "roomNumber"), ("Name", "roomName")]):
            ttk.Label(overview, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(overview, textvariable=entry_vars[field]).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Label(overview, text="Status").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Combobox(overview, textvariable=entry_vars["roomStatus"], values=ROOM_STATUSES, state="readonly").grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Checkbutton(overview, text="Player visible", variable=entry_vars["playerVisible"]).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)

        for tab_label, fields in [
            ("Beschreibung", [("Description", "description", 7), ("Contents", "contents", 5), ("Player handout", "handoutText", 5)]),
            ("Gegner", [("Monsters", "monsters", 8)]),
            ("Schatz", [("Treasure", "treasure", 5), ("Loot table", "lootTable", 7)]),
            ("Fallen", [("Traps", "traps", 8)]),
            ("Vorlesetext", [("Read-aloud text", "readAloud", 10)]),
            ("Hinweise", [("Rumors", "rumors", 4), ("Clues", "clues", 4), ("Secrets", "secrets", 4), ("GM notes", "gmNotes", 5)]),
        ]:
            frame = ttk.Frame(notebook, padding=8)
            frame.columnconfigure(0, weight=1)
            notebook.add(frame, text=tab_label)
            row = 0
            for label, field, height in fields:
                add_text(frame, label, field, row, height)
                row += 2

        actions = ttk.Frame(dialog, padding=(10, 0, 10, 10))
        actions.grid(row=1, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)

        def save() -> None:
            before = self.project_snapshot()
            for field, var in entry_vars.items():
                room[field] = bool(var.get()) if field == "playerVisible" else str(var.get())
            for field, widget in text_widgets.items():
                room[field] = widget.get("1.0", "end-1c")
            room.update(validate_object(room, 1))
            self.sync_campaign_from_rooms()
            self.commit_history(before, "Edit room form")
            self.redraw()
            dialog.destroy()

        ttk.Button(actions, text="Cancel", command=dialog.destroy).grid(row=0, column=1, sticky="e", padx=2)
        ttk.Button(actions, text="Save", command=save).grid(row=0, column=2, sticky="e", padx=2)

    def renumber_rooms(self) -> None:
        rooms = sorted((obj for obj in self.project.get("objects", []) if obj.get("type") in {"room", "round", "cave"}), key=lambda obj: (bounds(obj)[1], bounds(obj)[0]))
        if not rooms:
            self.show_status("No rooms to renumber.")
            return
        before = self.project_snapshot()
        start = max(1, int(self.settings.get("numberStart", 1)))
        prefix = str(self.settings.get("numberArea", ""))
        for offset, room in enumerate(rooms):
            value = f"{prefix}{start + offset}"
            room["roomNumber"] = value
            linked = [obj for obj in self.project["objects"] if obj.get("type") == "text" and obj.get("textRole") == "number" and obj.get("roomId") == room["id"]]
            if linked:
                for number in linked:
                    number["text"] = value
                    number["numberArea"] = prefix
            else:
                x, y = object_center(room)
                number = text_obj(value, x, y, 1.45)
                number["textRole"] = "number"
                number["roomId"] = room["id"]
                number["numberArea"] = prefix
                number["layer"] = "text"
                self.project["objects"].append(validate_object(number, len(self.project["objects"]) + 1))
        self.sync_campaign_from_rooms()
        self.commit_history(before, "Renumber rooms")
        self.redraw()

    def room_number_values(self) -> list[int]:
        values = []
        prefix = str(self.settings.get("numberArea", ""))
        for room in self.project.get("objects", []):
            if room.get("type") not in {"room", "round", "cave"}:
                continue
            value = str(room.get("roomNumber") or "")
            if prefix and value.startswith(prefix):
                value = value[len(prefix) :]
            if value.isdigit():
                values.append(int(value))
        for obj in self.project.get("objects", []):
            if obj.get("type") == "text" and obj.get("textRole") == "number":
                value = str(obj.get("text", ""))
                if prefix and value.startswith(prefix):
                    value = value[len(prefix) :]
                if value.isdigit():
                    values.append(int(value))
        return sorted(set(values))

    def find_room_number_gaps(self) -> None:
        values = self.room_number_values()
        if not values:
            messagebox.showinfo("Room number gaps", "No room numbers found.", parent=self)
            return
        missing = [number for number in range(values[0], values[-1] + 1) if number not in values]
        message = "No gaps found." if not missing else "Missing numbers: " + ", ".join(str(number) for number in missing)
        messagebox.showinfo("Room number gaps", message, parent=self)

    def open_encounters_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Encounter tables")
        dialog.transient(self)
        dialog.grab_set()
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(dialog)
        notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        widgets: dict[str, tk.Text] = {}

        map_frame = ttk.Frame(notebook, padding=8)
        map_frame.columnconfigure(0, weight=1)
        map_frame.rowconfigure(1, weight=1)
        notebook.add(map_frame, text="Map")
        ttk.Label(map_frame, text="Map encounter table").grid(row=0, column=0, sticky="w")
        map_text = tk.Text(map_frame, width=64, height=14, wrap="word")
        map_text.grid(row=1, column=0, sticky="nsew")
        map_text.insert("1.0", str(self.project.get("campaign", {}).get("encounterTable", "")))
        widgets["map"] = map_text

        if self.project.get("zones"):
            for zone in self.project.get("zones", []):
                zone_frame = ttk.Frame(notebook, padding=8)
                zone_frame.columnconfigure(0, weight=1)
                zone_frame.rowconfigure(1, weight=1)
                notebook.add(zone_frame, text=str(zone.get("name", "Zone"))[:16])
                ttk.Label(zone_frame, text=f"Zone encounter table: {zone.get('name', 'Zone')}").grid(row=0, column=0, sticky="w")
                zone_text = tk.Text(zone_frame, width=64, height=14, wrap="word")
                zone_text.grid(row=1, column=0, sticky="nsew")
                zone_text.insert("1.0", str(zone.get("encounterTable", "")))
                widgets[f"zone:{zone['id']}"] = zone_text

        actions = ttk.Frame(dialog, padding=(10, 0, 10, 10))
        actions.grid(row=1, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)

        def save() -> None:
            before = self.project_snapshot()
            self.project.setdefault("campaign", {})["encounterTable"] = widgets["map"].get("1.0", "end-1c")
            for zone in self.project.get("zones", []):
                widget = widgets.get(f"zone:{zone['id']}")
                if widget:
                    zone["encounterTable"] = widget.get("1.0", "end-1c")
            self.commit_history(before, "Edit encounter tables")
            self.redraw()
            dialog.destroy()

        ttk.Button(actions, text="Cancel", command=dialog.destroy).grid(row=0, column=1, sticky="e", padx=2)
        ttk.Button(actions, text="Save", command=save).grid(row=0, column=2, sticky="e", padx=2)

    def randomize_room_contents(self) -> None:
        rooms = [obj for obj in self.project.get("objects", []) if obj.get("type") in {"room", "round", "cave"}]
        if not rooms:
            self.show_status("No rooms to fill.")
            return
        before = self.project_snapshot()
        rng = random.Random()
        for room in rooms:
            kind, label, description = rng.choice(RANDOM_ROOM_CONTENTS)
            room["contents"] = label
            room["description"] = room.get("description") or description
            if kind == "monster":
                room["monsters"] = rng.choice(["2d4 goblins", "1 ogre mercenary", "3 skeletal guards", "1 rival adventurer"])
                room["roomStatus"] = "dangerous"
            elif kind == "trap":
                room["traps"] = rng.choice(["Hidden pit", "Needle lock", "Falling stones", "Poison gas vent"])
                room["roomStatus"] = "dangerous"
            elif kind == "treasure":
                room["treasure"] = rng.choice(["Silver idol", "Locked coffer", "Ancient map", "Potion cache"])
                room["lootTable"] = "1-2 coins\n3-4 useful gear\n5-6 odd relic"
            elif kind == "special":
                room["secrets"] = rng.choice(["Whispering wall", "False floor", "Faction sign", "One-way magic door"])
        self.sync_campaign_from_rooms()
        self.commit_history(before, "Randomize room contents")
        self.redraw()

    def export_gm_booklet(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export GM booklet",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
            initialfile=f"{safe_name(self.project['meta']['title'])}-gm-booklet.md",
            parent=self,
        )
        if not path:
            return
        self.sync_campaign_from_rooms()
        Path(path).write_text(gm_booklet_markdown(self.project), encoding="utf-8")
        self.show_status(f"Exported {Path(path).name}")

    def sync_campaign_from_rooms(self) -> None:
        self.project["campaign"] = {
            **{key: value for key, value in self.project.get("campaign", {}).items() if key != "rooms"},
            "rooms": [campaign_record_for_room(obj) for obj in self.project["objects"] if obj.get("type") in {"room", "round", "cave"}],
        }

    def snap_step(self) -> float:
        return normalize_snap_step(self.settings.get("snapStep", 1.0))

    def snap_delta(self, dx: float, dy: float) -> tuple[float, float]:
        if not self.settings.get("snapToGrid", True):
            return dx, dy
        step = self.snap_step()
        return round(dx / step) * step, round(dy / step) * step

    def snap_point(self, x: float, y: float, exclude_ids: set[str] | None = None) -> tuple[float, float]:
        if self.settings.get("snapToGrid", True):
            step = self.snap_step()
            x = round(x / step) * step
            y = round(y / step) * step
        if self.settings.get("snapToObjects", False):
            x, y = snap_point_to_object_edges(x, y, self.project["objects"], exclude_ids or set())
        return x, y

    def snap_move_delta_to_objects(self, dx: float, dy: float) -> tuple[float, float]:
        if not self.settings.get("snapToObjects", False) or not self.drag_originals:
            return dx, dy
        moving_bounds = union_bounds(self.drag_originals.values())
        guides_x, guides_y = object_edge_guides(self.project["objects"], set(self.drag_originals))
        if moving_bounds:
            left, top, width, height = moving_bounds
            dx = snap_delta_axis(dx, (left, left + width), guides_x)
            dy = snap_delta_axis(dy, (top, top + height), guides_y)
        return dx, dy

    def rect_from_points(self, x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float]:
        min_size = self.snap_step() if self.settings.get("snapToGrid", True) else 0.25
        x, width = span_from_points(x1, x2, min_size)
        y, height = span_from_points(y1, y2, min_size)
        return x, y, width, height

    def handle_polygon_click(self, point: tuple[float, float]) -> None:
        if not self.draft or self.draft.kind != "shape_polygon":
            self.draft = Draft("shape_polygon", point[0], point[1], 0.25, 0.25, point[0], point[1], [point])
            self.show_status("Polygon started. Click points, then click the first point to close.")
            self.redraw()
            return
        points = self.draft.points or []
        if len(points) >= 3 and self.is_polygon_close_hit(point):
            obj = self.shape_from_draft(self.draft)
            self.draft = None
            self.drag_start = None
            self.add_object(obj)
            self.show_status("Polygon closed.")
            return
        if points and math.hypot(point[0] - points[-1][0], point[1] - points[-1][1]) <= self.polygon_close_tolerance() / 2:
            return
        points.append(point)
        self.draft.points = points
        self.draft.x2, self.draft.y2 = point
        if points:
            point_dicts = [{"x": x, "y": y} for x, y in points]
            self.draft.x, self.draft.y, self.draft.width, self.draft.height = bounds_from_points(point_dicts)
        self.show_status(f"Polygon: {len(points)} points. Click the first point to close.")
        self.redraw()

    def polygon_close_tolerance(self) -> float:
        return max(0.2, HANDLE_PIXEL_SIZE / max(1, self.cell))

    def is_polygon_close_hit(self, point: tuple[float, float]) -> bool:
        if not self.draft or not self.draft.points:
            return False
        first = self.draft.points[0]
        return math.hypot(point[0] - first[0], point[1] - first[1]) <= self.polygon_close_tolerance()

    def circle_from_points(self, x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float]:
        min_size = self.snap_step() if self.settings.get("snapToGrid", True) else 0.25
        diameter = max(min_size, abs(x2 - x1), abs(y2 - y1))
        x = x1 - diameter if x2 < x1 else x1
        y = y1 - diameter if y2 < y1 else y1
        return x, y, diameter, diameter

    def shape_from_draft(self, draft: Draft) -> dict[str, Any]:
        obj = shape_from_draft_data(draft)
        apply_shape_defaults(obj, self.settings)
        return obj

    def find_handle_hit(self, x: float, y: float) -> str | None:
        obj = self.selected_object()
        if not obj or len(self.selected_ids) != 1:
            return None
        tolerance = max(0.12, HANDLE_PIXEL_SIZE / max(1, self.cell))
        for name, hx, hy in selection_handles(obj):
            if abs(x - hx) <= tolerance and abs(y - hy) <= tolerance:
                return name
        return None

    def update_handle_drag(self, point: tuple[float, float]) -> None:
        if not self.selected_id or not self.drag_handle:
            return
        obj = self.selected_object()
        original = self.drag_originals.get(self.selected_id)
        if not obj or not original:
            return
        if self.drag_mode == "polygon_point" and original.get("type") == "shape" and original.get("kind") == "polygon" and self.drag_handle.startswith("point:"):
            index = int(self.drag_handle.split(":", 1)[1])
            points = validate_shape_points(original.get("points"))
            if 0 <= index < len(points):
                snapped = self.snap_point(point[0], point[1], {self.selected_id})
                points[index] = {"x": snapped[0], "y": snapped[1]}
                obj["points"] = points
                refresh_polygon_bounds(obj)
                obj.update(validate_object(obj, 1))
                self.selected_polygon_point = index
            return
        if self.drag_mode == "rotate" and obj.get("type") == "symbol":
            angle = math.degrees(math.atan2(point[1] - original["y"], point[0] - original["x"])) + 90
            obj["rotation"] = round(angle / 15) * 15 % 360
            return
        snapped = self.snap_point(point[0], point[1], {self.selected_id})
        if original.get("type") in RESIZABLE_TYPES or is_box_shape(original):
            resize_rectlike_object(obj, original, self.drag_handle, snapped, self.snap_step())
        elif original.get("type") == "diagonal_corridor" or (original.get("type") == "shape" and original.get("kind") == "line"):
            if self.drag_handle == "start":
                obj["x"], obj["y"] = snapped
            elif self.drag_handle == "end":
                obj["x2"], obj["y2"] = snapped
        elif original.get("type") == "symbol" and self.drag_handle == "scale":
            distance = max(abs(point[0] - original["x"]), abs(point[1] - original["y"])) * 2
            obj["size"] = max(0.25, round(distance / 0.25) * 0.25)

    def generate_random_rooms(self) -> None:
        before = self.project_snapshot()
        rng = random.Random()
        added = 0
        for _ in range(18):
            w, h = rng.randint(4, 10), rng.randint(4, 8)
            x = rng.randint(1, max(2, self.settings["width"] - w - 1))
            y = rng.randint(1, max(2, self.settings["height"] - h - 1))
            candidate = rect("room", x, y, w, h)
            if any(rects_overlap(bounds(candidate), bounds(obj), padding=1) for obj in self.project["objects"] if obj.get("type") in RECTLIKE_TYPES):
                continue
            candidate["roomName"] = f"Room {len(self.project.get('campaign', {}).get('rooms', [])) + added + 1}"
            candidate["layer"] = "rooms"
            self.project["objects"].append(candidate)
            added += 1
            if added >= 6:
                break
        self.sync_campaign_from_rooms()
        self.commit_history(before, "Generate random rooms")
        self.redraw()

    def generate_random_corridors(self) -> None:
        before = self.project_snapshot()
        rooms = [obj for obj in self.project["objects"] if obj.get("type") in {"room", "round", "cave"}]
        for first, second in nearest_room_pairs(rooms, limit=6):
            self.project["objects"].append(corridor_between_rooms(first, second))
        self.commit_history(before, "Generate random corridors")
        self.redraw()

    def suggest_room_connections(self) -> None:
        rooms = [obj for obj in self.project["objects"] if obj.get("type") in {"room", "round", "cave"}]
        pairs = nearest_room_pairs(rooms, limit=8)
        if not pairs:
            self.show_status("No connection suggestions available.")
            return
        dialog = tk.Toplevel(self)
        dialog.title("Suggested connections")
        dialog.transient(self)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        vars_by_pair: list[tuple[tk.BooleanVar, dict[str, Any], dict[str, Any]]] = []
        ttk.Label(frame, text="Confirm links").grid(row=0, column=0, sticky="w")
        for row, (first, second) in enumerate(pairs, start=1):
            var = tk.BooleanVar(value=True)
            vars_by_pair.append((var, first, second))
            label = f"{first.get('roomName') or first.get('roomNumber') or first['id']} -> {second.get('roomName') or second.get('roomNumber') or second['id']}"
            ttk.Checkbutton(frame, text=label, variable=var).grid(row=row, column=0, sticky="w")

        def apply() -> None:
            before = self.project_snapshot()
            for var, first, second in vars_by_pair:
                if not var.get():
                    continue
                corridor = corridor_between_rooms(first, second)
                corridor["connectionSuggestion"] = True
                self.project["objects"].append(corridor)
            self.commit_history(before, "Confirm room connections")
            self.redraw()
            dialog.destroy()

        buttons = ttk.Frame(frame)
        buttons.grid(row=len(vars_by_pair) + 1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right", padx=2)
        ttk.Button(buttons, text="Apply", command=apply).pack(side="right", padx=2)

    def add_connection_notes(self) -> None:
        before = self.project_snapshot()
        rooms = [obj for obj in self.project["objects"] if obj.get("type") in {"room", "round", "cave"}]
        for first, second in nearest_room_pairs(rooms, limit=5):
            x1, y1 = object_center(first)
            x2, y2 = object_center(second)
            note = note_obj(f"Link {first.get('roomName') or first['id']} -> {second.get('roomName') or second['id']}", (x1 + x2) / 2, (y1 + y2) / 2)
            note["width"] = 10
            self.project["objects"].append(note)
        self.commit_history(before, "Suggest room connections")
        self.redraw()

    def roughen_caves(self) -> None:
        before = self.project_snapshot()
        for obj in self.project["objects"]:
            if obj.get("type") == "cave":
                obj["seed"] = random.randint(1, 1000000)
        self.commit_history(before, "Roughen cave edges")
        self.redraw()

    def generate_dungeon(self) -> None:
        spec = simpledialog.askstring(
            "Dungeon generator",
            "density; room min-max; loops; dead ends",
            initialvalue="9; 4-10x4-8; 2; 2",
            parent=self,
        )
        if spec is None:
            return
        options = parse_dungeon_options(spec)
        before = self.project_snapshot()
        self.project["objects"] = [obj for obj in self.project["objects"] if obj.get("type") == "legend"]
        rng = random.Random()
        rooms = []
        attempts = max(20, options["density"] * 5)
        for _ in range(attempts):
            w = rng.randint(options["min_w"], options["max_w"])
            h = rng.randint(options["min_h"], options["max_h"])
            x = rng.randint(1, max(2, self.settings["width"] - w - 1))
            y = rng.randint(1, max(2, self.settings["height"] - h - 1))
            candidate = rect("room", x, y, w, h)
            candidate["roomName"] = f"Room {len(rooms) + 1}"
            candidate["description"] = "Generated dungeon room."
            candidate["layer"] = "rooms"
            if not any(rects_overlap(bounds(candidate), bounds(obj), padding=2) for obj in rooms):
                rooms.append(candidate)
            if len(rooms) >= options["density"]:
                break
        self.project["objects"].extend(rooms)
        connection_limit = max(0, len(rooms) - 1 + options["loops"])
        for first, second in nearest_room_pairs(rooms, limit=connection_limit):
            self.project["objects"].append(corridor_between_rooms(first, second))
        for room in rooms[: options["dead_ends"]]:
            x, y = object_center(room)
            length = rng.randint(3, 8)
            direction = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            dead_end = rect("corridor", x, y, max(1, abs(direction[0]) * length), max(1, abs(direction[1]) * length))
            if direction[0] < 0:
                dead_end["x"] = max(0, x - length)
            if direction[1] < 0:
                dead_end["y"] = max(0, y - length)
            dead_end["layer"] = "corridors"
            dead_end["deadEnd"] = True
            self.project["objects"].append(validate_object(dead_end, len(self.project["objects"]) + 1))
        self.auto_place_doors(commit=False)
        self.sync_campaign_from_rooms()
        self.commit_history(before, "Generate dungeon")
        self.redraw()

    def generate_keyword_dungeon(self) -> None:
        spec = simpledialog.askstring(
            "Dungeon from keywords",
            "Theme; faction; danger",
            initialvalue="sunken temple; cultists; flooding",
            parent=self,
        )
        if spec is None:
            return
        theme, faction, danger = parse_keyword_spec(spec)
        before = self.project_snapshot()
        self.project["objects"] = [obj for obj in self.project["objects"] if obj.get("type") == "legend"]
        rng = random.Random()
        rooms = []
        names = ["Gate", "Shrine", "Barracks", "Vault", "Gallery", "Cistern", "Sanctum", "Workroom", "Nest"]
        for index, name in enumerate(names[:8], start=1):
            w, h = rng.randint(4, 9), rng.randint(4, 8)
            x = rng.randint(1, max(2, self.settings["width"] - w - 1))
            y = rng.randint(1, max(2, self.settings["height"] - h - 1))
            candidate = rect("room", x, y, w, h)
            candidate["roomName"] = f"{theme.title()} {name}"
            candidate["description"] = f"{faction.title()} activity marks this {theme}; the main pressure is {danger}."
            candidate["monsters"] = faction
            candidate["traps"] = danger if index % 3 == 0 else ""
            candidate["secrets"] = f"A clue points to how {danger} can be turned against {faction}."
            candidate["layer"] = "rooms"
            if not any(rects_overlap(bounds(candidate), bounds(obj), padding=1) for obj in rooms):
                rooms.append(candidate)
        self.project["objects"].extend(rooms)
        for first, second in nearest_room_pairs(rooms, limit=max(0, len(rooms) - 1 + 2)):
            self.project["objects"].append(corridor_between_rooms(first, second))
        self.auto_place_doors(commit=False, door_types=["normal", "secret"])
        self.sync_campaign_from_rooms()
        self.commit_history(before, "Generate keyword dungeon")
        self.redraw()

    def generate_natural_caves(self) -> None:
        before = self.project_snapshot()
        rng = random.Random()
        caves = []
        for index in range(6):
            w, h = rng.randint(5, 12), rng.randint(4, 9)
            x = rng.randint(1, max(2, self.settings["width"] - w - 1))
            y = rng.randint(1, max(2, self.settings["height"] - h - 1))
            cave = rect("cave", x, y, w, h)
            cave["roomName"] = f"Cavern {index + 1}"
            cave["description"] = "Natural cave chamber."
            cave["seed"] = rng.randint(1, 1000000)
            cave["wallType"] = "natural"
            cave["wallThickness"] = 0.24
            cave["layer"] = "rooms"
            if not any(rects_overlap(bounds(cave), bounds(obj), padding=1) for obj in caves):
                caves.append(cave)
        self.project["objects"].extend(caves)
        for first, second in nearest_room_pairs(caves, limit=max(0, len(caves) - 1)):
            tunnel = corridor_between_rooms(first, second)
            tunnel["type"] = "diagonal_corridor"
            x1, y1 = object_center(first)
            x2, y2 = object_center(second)
            tunnel.update({"x": x1, "y": y1, "x2": x2, "y2": y2, "width": rng.choice([1, 1.5, 2]), "wallType": "natural", "wallThickness": 0.22})
            self.project["objects"].append(validate_object(tunnel, len(self.project["objects"]) + 1))
        if len(caves) >= 2:
            stream = shape("line", *object_center(caves[0]), 0, 0, *object_center(caves[-1]))
            stream["strokeColor"] = "#2f8fbd"
            stream["lineWidth"] = 0.28
            stream["lineStyle"] = "dash"
            stream["curve"] = True
            stream["layer"] = "shapes"
            stream["name"] = "Watercourse"
            self.project["objects"].append(validate_object(stream, len(self.project["objects"]) + 1))
        self.sync_campaign_from_rooms()
        self.commit_history(before, "Generate natural caves")
        self.redraw()

    def check_auto_walls(self) -> None:
        rooms = [obj for obj in self.project["objects"] if obj.get("type") in {"room", "round", "cave"}]
        styled = sum(1 for obj in self.project["objects"] if obj.get("type") in FLOOR_TYPES and obj.get("wallType"))
        messagebox.showinfo("Wall check", f"{len(rooms)} room shapes render with generated walls.\n{styled} areas have stored wall type/thickness.", parent=self)

    def auto_place_doors(self, commit: bool = True, door_types: list[str] | None = None) -> None:
        if commit and door_types is None:
            spec = simpledialog.askstring("Auto doors", "Door types: normal, secret, locked, trapdoor", initialvalue="normal, secret, locked, trapdoor", parent=self)
            if spec is None:
                return
            door_types = [item.strip().lower() for item in spec.replace(";", ",").split(",") if item.strip()]
        before = self.project_snapshot()
        doors = auto_door_symbols(self.project["objects"], door_types)
        existing = {(round(obj.get("x", 0), 1), round(obj.get("y", 0), 1), obj.get("kind")) for obj in self.project["objects"] if obj.get("type") == "symbol"}
        for door in doors:
            key = (round(door["x"], 1), round(door["y"], 1), door["kind"])
            if key not in existing:
                self.project["objects"].append(door)
        if commit:
            self.commit_history(before, "Auto-place doors")
            self.redraw()

    def auto_wall_styles(self) -> None:
        floors = [obj for obj in self.project.get("objects", []) if obj.get("type") in FLOOR_TYPES]
        if not floors:
            self.show_status("No floor areas for wall styling.")
            return
        before = self.project_snapshot()
        for obj in floors:
            cx, cy = object_center(obj)
            zone = next((item for item in self.project.get("zones", []) if item["x"] <= cx <= item["x"] + item["width"] and item["y"] <= cy <= item["y"] + item["height"]), None)
            if zone:
                obj["wallType"] = zone.get("wallType", "standard")
                obj["wallThickness"] = zone.get("wallThickness", 0.16)
            elif obj.get("type") == "cave":
                obj["wallType"] = "natural"
                obj["wallThickness"] = 0.24
            elif obj.get("type") in {"corridor", "diagonal_corridor"}:
                obj["wallType"] = "thin"
                obj["wallThickness"] = 0.12
            elif obj.get("width", 0) * obj.get("height", 0) > 60:
                obj["wallType"] = "thick"
                obj["wallThickness"] = 0.24
            else:
                obj["wallType"] = "standard"
                obj["wallThickness"] = 0.16
            obj.update(validate_object(obj, 1))
        self.commit_history(before, "Auto wall styles")
        self.redraw()

    def generate_patrol_routes(self) -> None:
        rooms = [obj for obj in self.project.get("objects", []) if obj.get("type") in {"room", "round", "cave"}]
        if len(rooms) < 2:
            self.show_status("Need at least two rooms for patrol routes.")
            return
        before = self.project_snapshot()
        rng = random.Random()
        for index in range(min(3, max(1, len(rooms) // 3))):
            route_rooms = rng.sample(rooms, k=min(len(rooms), rng.randint(2, min(5, len(rooms)))))
            points = [object_center(room) for room in route_rooms]
            for start, end in zip(points, points[1:]):
                patrol = shape("line", start[0], start[1], 0, 0, end[0], end[1])
                patrol["lineStyle"] = "dash"
                patrol["arrow"] = "end"
                patrol["strokeColor"] = "#9c3b3b"
                patrol["lineWidth"] = 0.16
                patrol["layer"] = "shapes"
                patrol["name"] = f"Patrol {index + 1}"
                self.project["objects"].append(validate_object(patrol, len(self.project["objects"]) + 1))
        self.commit_history(before, "Generate patrol routes")
        self.redraw()

    def export_campaign_report(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export room report",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
            initialfile=f"{safe_name(self.project['meta']['title'])}-rooms.md",
            parent=self,
        )
        if not path:
            return
        self.sync_campaign_from_rooms()
        Path(path).write_text(campaign_report_markdown(self.project), encoding="utf-8")
        self.show_status(f"Exported {Path(path).name}")

    def open_export_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Export")
        dialog.transient(self)
        dialog.grab_set()
        dialog.columnconfigure(0, weight=1)
        dialog.columnconfigure(1, weight=1)

        fmt_var = tk.StringVar(value=self.export_format.get().lower())
        scale_var = tk.IntVar(value=int(self.export_scale.get()))
        jpeg_quality_var = tk.IntVar(value=92)
        webp_quality_var = tk.IntVar(value=92)
        transparent_var = tk.BooleanVar(value=False)
        legend_var = tk.BooleanVar(value=self.settings.get("showLegend", True))
        grid_var = tk.BooleanVar(value=self.settings.get("exportGrid", True))
        audience_var = tk.StringVar(value=self.settings.get("exportAudience", "GM"))
        scope_var = tk.StringVar(value="page")
        margin_var = tk.IntVar(value=0)
        title_area_var = tk.BooleanVar(value=False)

        controls = ttk.Frame(dialog, padding=12)
        controls.grid(row=0, column=0, sticky="nsew")
        preview = ttk.Label(dialog, padding=12)
        preview.grid(row=0, column=1, sticky="nsew")

        ttk.Label(controls, text="Format").grid(row=0, column=0, sticky="w")
        ttk.Combobox(controls, textvariable=fmt_var, values=("png", "jpeg", "webp", "pdf", "svg"), width=8, state="readonly").grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(controls, text="Scale").grid(row=1, column=0, sticky="w")
        ttk.Combobox(controls, textvariable=scale_var, values=(1, 2, 3, 4), width=8, state="readonly").grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Label(controls, text="JPEG quality").grid(row=2, column=0, sticky="w")
        ttk.Scale(controls, from_=50, to=100, variable=jpeg_quality_var, orient="horizontal").grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Label(controls, text="WebP quality").grid(row=3, column=0, sticky="w")
        ttk.Scale(controls, from_=50, to=100, variable=webp_quality_var, orient="horizontal").grid(row=3, column=1, sticky="ew", pady=2)
        ttk.Checkbutton(controls, text="Transparent background", variable=transparent_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(controls, text="Export legend", variable=legend_var).grid(row=5, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(controls, text="Export grid", variable=grid_var).grid(row=6, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Label(controls, text="Audience").grid(row=7, column=0, sticky="w")
        ttk.Combobox(controls, textvariable=audience_var, values=("GM", "Player"), width=12, state="readonly").grid(row=7, column=1, sticky="ew", pady=2)
        ttk.Label(controls, text="Area").grid(row=8, column=0, sticky="w")
        ttk.Combobox(controls, textvariable=scope_var, values=("map", "page", "selection"), width=12, state="readonly").grid(row=8, column=1, sticky="ew", pady=2)
        ttk.Label(controls, text="Print margin").grid(row=9, column=0, sticky="w")
        ttk.Spinbox(controls, from_=0, to=8, textvariable=margin_var, width=8).grid(row=9, column=1, sticky="ew", pady=2)
        ttk.Checkbutton(controls, text="Title area", variable=title_area_var).grid(row=10, column=0, columnspan=2, sticky="w", pady=2)

        def options() -> dict[str, Any]:
            return {
                "format": fmt_var.get().lower(),
                "scale": int(scale_var.get()),
                "jpeg_quality": int(jpeg_quality_var.get()),
                "webp_quality": int(webp_quality_var.get()),
                "transparent": bool(transparent_var.get()),
                "include_legend": bool(legend_var.get()),
                "export_grid": bool(grid_var.get()),
                "audience": audience_var.get(),
                "scope": scope_var.get(),
                "print_margin_cells": max(0, safe_int(margin_var.get(), 0)),
                "title_area": bool(title_area_var.get()),
            }

        def update_preview(*_args: Any) -> None:
            try:
                image = self.render_image(scale=1, options=options())
            except Exception as exc:
                preview.configure(text=str(exc), image="")
                return
            thumb = image.copy()
            thumb.thumbnail((360, 300))
            try:
                from PIL import ImageTk
            except ImportError:
                preview.configure(text=f"{image.width} x {image.height}px", image="")
                return
            self.preview_photo = ImageTk.PhotoImage(thumb)
            preview.configure(image=self.preview_photo, text="")

        def save() -> None:
            opts = options()
            fmt = opts["format"]
            path = filedialog.asksaveasfilename(
                title="Export image",
                defaultextension=f".{fmt}",
                filetypes=[(fmt.upper(), f"*.{fmt}")],
                initialfile=f"{safe_name(self.project['meta']['title'])}.{fmt}",
                parent=dialog,
            )
            if not path:
                return
            try:
                if fmt == "svg":
                    save_svg(path, self.export_project_for_scope(opts["scope"]), opts)
                    image = None
                else:
                    image = self.render_image(scale=opts["scale"], options=opts)
            except Exception as exc:
                self.show_error("Export failed", str(exc), parent=dialog)
                return
            save_kwargs: dict[str, Any] = {}
            if fmt == "svg":
                pass
            elif fmt == "pdf":
                if image.mode == "RGBA":
                    image = flatten_rgba(image, self.settings["backgroundColor"])
                image.save(path, "PDF", resolution=300)
            elif fmt == "jpeg":
                save_kwargs["quality"] = opts["jpeg_quality"]
                if image.mode == "RGBA":
                    image = flatten_rgba(image, self.settings["backgroundColor"])
            elif fmt == "webp":
                save_kwargs["quality"] = opts["webp_quality"]
            if fmt not in {"pdf", "svg"}:
                image.save(path, fmt.upper() if fmt != "jpeg" else "JPEG", **save_kwargs)
            self.export_format.set(fmt)
            self.export_scale.set(opts["scale"])
            self.settings["exportAudience"] = opts["audience"]
            self.settings["exportGrid"] = opts["export_grid"]
            self.show_status(f"Exported {Path(path).name}")
            dialog.destroy()

        for variable in (fmt_var, scale_var, jpeg_quality_var, webp_quality_var, transparent_var, legend_var, grid_var, audience_var, scope_var, margin_var, title_area_var):
            variable.trace_add("write", update_preview)

        actions = ttk.Frame(controls)
        actions.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        actions.columnconfigure(0, weight=1)
        ttk.Button(actions, text="Cancel", command=dialog.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(actions, text="Save", command=save).grid(row=0, column=1, sticky="ew")
        update_preview()

    def render_image(self, scale: int = 1, include_selection: bool = False, options: dict[str, Any] | None = None):
        if Image is None or ImageDraw is None:
            raise RuntimeError("Pillow is required for export.")
        options = options or {}
        scope = "selection" if include_selection else options.get("scope", "page")
        include_legend = bool(options.get("include_legend", self.settings.get("showLegend", True))) and scope == "page"
        transparent = bool(options.get("transparent", False)) and options.get("format", self.export_format.get()).lower() in {"png", "webp"}
        project = self.export_project_for_scope(scope)
        project["settings"]["exportGrid"] = bool(options.get("export_grid", self.settings.get("exportGrid", True)))
        project["settings"]["exportAudience"] = options.get("audience", self.settings.get("exportAudience", "GM"))
        if scope == "selection":
            include_legend = any(obj.get("type") == "legend" for obj in project.get("objects", []))
        width, height = canvas_size(project, scale, include_legend=include_legend)
        mode = "RGBA" if transparent else "RGB"
        background = (0, 0, 0, 0) if transparent else project["settings"]["backgroundColor"]
        image = Image.new(mode, (max(1, int(math.ceil(width))), max(1, int(math.ceil(height)))), background)
        draw = ImageDraw.Draw(image)
        draw._target_image = image
        render_pillow(draw, project, scale, None, None, include_legend=include_legend)
        margin_cells = max(0, int(options.get("print_margin_cells", 0))) if scope == "page" else 0
        title_area = bool(options.get("title_area", False)) if scope == "page" else False
        if margin_cells or title_area:
            image = add_export_page_chrome(image, project, scale, margin_cells, title_area, transparent)
        return image

    def export_project_for_scope(self, scope: str) -> dict[str, Any]:
        if scope != "selection":
            project = self.project_snapshot()
            project["settings"]["showLegend"] = scope == "page" and self.settings.get("showLegend", True)
            return project
        if not self.selected_ids:
            raise ValueError("Keine Auswahl fuer den Export vorhanden.")
        selected = [json.loads(json.dumps(obj)) for obj in self.project["objects"] if obj["id"] in self.selected_ids]
        box = union_bounds(selected)
        if not box:
            raise ValueError("Keine Auswahl fuer den Export vorhanden.")
        left, top, width, height = box
        padding = 0.5
        offset_x = left - padding
        offset_y = top - padding
        for obj in selected:
            translate_object(obj, -offset_x, -offset_y)
        project = self.project_snapshot()
        project["objects"] = selected
        project["settings"]["width"] = max(1, math.ceil(width + padding * 2))
        project["settings"]["height"] = max(1, math.ceil(height + padding * 2))
        project["settings"]["showLegend"] = False
        return project


def default_layer_for_tool(tool: str, is_symbol: bool = False) -> str:
    if tool in {"room", "round", "cave"}:
        return "rooms"
    if tool == "corridor":
        return "corridors"
    if tool in SHAPE_TOOLS:
        return "shapes"
    if tool in {"text", "number"}:
        return "text"
    if tool == "note":
        return "notes"
    if is_symbol:
        return "symbols"
    return "symbols"


def shape_from_draft_data(draft: Draft, include_preview: bool = False) -> dict[str, Any]:
    if draft.kind == "shape_line":
        return shape("line", draft.x, draft.y, 0, 0, draft.x2, draft.y2)
    if draft.kind == "shape_polygon":
        points = list(draft.points or [])
        if include_preview and draft.x2 is not None and draft.y2 is not None:
            preview = (draft.x2, draft.y2)
            if not points or math.hypot(preview[0] - points[-1][0], preview[1] - points[-1][1]) > 0.000001:
                points.append(preview)
        obj = shape("polygon", draft.x, draft.y, max(0.25, draft.width), max(0.25, draft.height))
        obj["points"] = [{"x": x, "y": y} for x, y in points]
        if include_preview:
            obj["_open"] = True
        if points:
            obj["x"], obj["y"], obj["width"], obj["height"] = bounds_from_points(obj["points"])
        return obj
    kind = {"shape_rect": "rectangle", "shape_circle": "circle", "shape_polygon": "polygon"}.get(draft.kind, "rectangle")
    return shape(kind, draft.x, draft.y, draft.width, draft.height)


def apply_shape_defaults(obj: dict[str, Any], settings: dict[str, Any]) -> None:
    obj["lineWidth"] = max(0.01, coerce_float(settings.get("defaultShapeLineWidth"), obj.get("lineWidth", 0.12)))
    obj["strokeColor"] = settings.get("defaultShapeStrokeColor") or settings.get("gridColor", BLUE)


def campaign_record_for_room(obj: dict[str, Any]) -> dict[str, Any]:
    record = {"id": obj["id"], "number": obj.get("roomNumber", ""), "name": obj.get("roomName", "")}
    for key in campaign_room_fields():
        record[key] = obj.get(key, campaign_room_fields()[key])
    return record


def object_center(obj: dict[str, Any]) -> tuple[float, float]:
    x, y, w, h = bounds(obj)
    return x + w / 2, y + h / 2


def rects_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float], padding: float = 0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax - padding < bx + bw and ax + aw + padding > bx and ay - padding < by + bh and ay + ah + padding > by


def nearest_room_pairs(rooms: list[dict[str, Any]], limit: int) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    if len(rooms) < 2:
        return []
    pairs = []
    for index, first in enumerate(rooms):
        x1, y1 = object_center(first)
        for second in rooms[index + 1 :]:
            x2, y2 = object_center(second)
            pairs.append((math.hypot(x2 - x1, y2 - y1), first, second))
    pairs.sort(key=lambda item: item[0])
    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    used: set[tuple[str, str]] = set()
    for _dist, first, second in pairs:
        key = tuple(sorted((first["id"], second["id"])))
        if key in used:
            continue
        used.add(key)
        result.append((first, second))
        if len(result) >= limit:
            break
    return result


def corridor_between_rooms(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    x1, y1 = object_center(first)
    x2, y2 = object_center(second)
    if random.choice([True, False]):
        x = min(x1, x2)
        corridor = rect("corridor", x, y1 - 0.5, abs(x2 - x1) + 1, 1)
    else:
        y = min(y1, y2)
        corridor = rect("corridor", x1 - 0.5, y, 1, abs(y2 - y1) + 1)
    corridor["layer"] = "corridors"
    return corridor


def parse_dungeon_options(spec: str) -> dict[str, int]:
    options = {"density": 9, "min_w": 4, "max_w": 10, "min_h": 4, "max_h": 8, "loops": 2, "dead_ends": 2}
    parts = [part.strip() for part in str(spec or "").replace(",", ";").split(";") if part.strip()]
    if parts:
        options["density"] = max(1, int(coerce_float(parts[0], options["density"])))
    if len(parts) > 1:
        size = parts[1].lower().replace(" ", "")
        if "x" in size:
            width_part, height_part = size.split("x", 1)
            if "-" in width_part:
                lo, hi = width_part.split("-", 1)
                options["min_w"], options["max_w"] = max(1, int(coerce_float(lo, 4))), max(1, int(coerce_float(hi, 10)))
            if "-" in height_part:
                lo, hi = height_part.split("-", 1)
                options["min_h"], options["max_h"] = max(1, int(coerce_float(lo, 4))), max(1, int(coerce_float(hi, 8)))
    if len(parts) > 2:
        options["loops"] = max(0, int(coerce_float(parts[2], options["loops"])))
    if len(parts) > 3:
        options["dead_ends"] = max(0, int(coerce_float(parts[3], options["dead_ends"])))
    if options["min_w"] > options["max_w"]:
        options["min_w"], options["max_w"] = options["max_w"], options["min_w"]
    if options["min_h"] > options["max_h"]:
        options["min_h"], options["max_h"] = options["max_h"], options["min_h"]
    return options


def parse_keyword_spec(spec: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in str(spec or "").split(";")]
    while len(parts) < 3:
        parts.append("")
    return parts[0] or "dungeon", parts[1] or "faction", parts[2] or "danger"


def door_kind_for_type(value: str, index: int = 0) -> str:
    normalized = str(value or "normal").lower()
    if normalized in {"normal", "door"}:
        return "door"
    if normalized in {"secret", "secret_door"}:
        return "secret_door"
    if normalized in {"locked", "locked_door"}:
        return "locked_door"
    if normalized in {"trapdoor", "trap_door", "falltuer", "trap_floor"}:
        return "trap_floor"
    return ["door", "secret_door", "locked_door", "trap_floor"][index % 4]


def auto_door_symbols(objects: list[dict[str, Any]], door_types: list[str] | None = None) -> list[dict[str, Any]]:
    rooms = [obj for obj in objects if obj.get("type") in {"room", "round", "cave"}]
    corridors = [obj for obj in objects if obj.get("type") == "corridor"]
    door_types = [item for item in (door_types or ["normal"]) if item in DOOR_PLACEMENT_TYPES or item in {"door", "secret_door", "locked_door", "trap_floor"}] or ["normal"]
    doors = []
    door_index = 0
    for room in rooms:
        rx, ry, rw, rh = bounds(room)
        for corridor in corridors:
            cx, cy, cw, ch = bounds(corridor)
            if rects_overlap((rx, ry, rw, rh), (cx, cy, cw, ch), padding=0.05):
                x = max(rx, min(cx + cw / 2, rx + rw))
                y = max(ry, min(cy + ch / 2, ry + rh))
                door = symbol(door_kind_for_type(door_types[door_index % len(door_types)], door_index), x, y, 0.9)
                door["layer"] = "symbols"
                doors.append(door)
                door_index += 1
    return doors[:24]


def campaign_report_markdown(project: dict[str, Any]) -> str:
    lines = [f"# {project.get('meta', {}).get('title', 'Dungeon')} Rooms", "", "## Contents", ""]
    rooms = [obj for obj in project.get("objects", []) if obj.get("type") in {"room", "round", "cave"}]
    for index, room in enumerate(rooms, start=1):
        title = room.get("roomName") or room.get("roomNumber") or f"Room {index}"
        lines.append(f"- [{title}](#room-{index})")
    symbols = [obj for obj in project.get("objects", []) if obj.get("type") == "symbol"]
    if symbols:
        lines.extend(["", "## Symbol Legend", ""])
        used: list[str] = []
        for obj in symbols:
            key = symbol_legend_key(project, obj)
            if key not in used:
                used.append(key)
        for kind in sorted(used, key=lambda value: symbol_group_sort_key(project, value)):
            lines.append(f"- {symbol_group_name(project, kind)}: {legend_label_for_kind(project, kind)}")
    missing_files = missing_custom_symbol_files(project)
    if missing_files:
        lines.extend(["", "## Missing Custom Symbol Files", ""])
        for _kind, label, path_value in missing_files:
            lines.append(f"- {label}: {path_value}")
    encounter_table = str(project.get("campaign", {}).get("encounterTable", "")).strip()
    if encounter_table:
        lines.extend(["", "## Map Encounter Table", "", encounter_table])
    for zone in project.get("zones", []):
        table = str(zone.get("encounterTable", "")).strip()
        if table:
            lines.extend(["", f"## Zone Encounter Table: {zone.get('name', 'Zone')}", "", table])
    lines.append("")
    for index, room in enumerate(rooms, start=1):
        title = room.get("roomName") or room.get("roomNumber") or f"Room {index}"
        lines.extend([f"## Room {index}: {title}", "", f"- Number: {room.get('roomNumber', '') or '-'}", f"- Status: {ROOM_STATUS_LABELS.get(room.get('roomStatus'), room.get('roomStatus', ''))}", f"- Player visible: {room.get('playerVisible', True)}"])
        for label, key in [
            ("Read Aloud", "readAloud"),
            ("Description", "description"),
            ("Contents", "contents"),
            ("Monsters", "monsters"),
            ("Treasure", "treasure"),
            ("Loot Table", "lootTable"),
            ("Traps", "traps"),
            ("Rumors", "rumors"),
            ("Clues", "clues"),
            ("Secrets", "secrets"),
            ("Player Handout", "handoutText"),
            ("GM Notes", "gmNotes"),
        ]:
            value = str(room.get(key, "")).strip()
            if value:
                lines.extend(["", f"### {label}", value])
        linked = [obj for obj in project.get("objects", []) if obj.get("type") == "text" and obj.get("roomId") == room["id"]]
        if linked:
            lines.extend(["", "### Linked Numbers", ", ".join(str(obj.get("text", "")) for obj in linked)])
        linked_lore = [obj for obj in symbols if any(str(obj.get(key, "")).strip() for key in ("rumors", "clues", "secrets", "handoutText", "gmNotes")) and rects_overlap(bounds(room), bounds(obj), padding=0.1)]
        if linked_lore:
            lines.extend(["", "### Linked Symbol Notes"])
            for obj in linked_lore:
                lines.append(f"- {symbol_label(project, obj.get('kind', 'symbol'))}: " + "; ".join(str(obj.get(key, "")).strip() for key in ("rumors", "clues", "secrets", "gmNotes") if str(obj.get(key, "")).strip()))
        lines.append("")
    return "\n".join(lines)


def gm_booklet_markdown(project: dict[str, Any]) -> str:
    settings = project["settings"]
    lines = [
        f"# {project.get('meta', {}).get('title', 'Dungeon')} GM Booklet",
        "",
        "## Map Sheet",
        "",
        f"- Map: {settings.get('width')} x {settings.get('height')} cells",
        f"- Scale: {cell_scale_label(settings)}",
        f"- Objects: {len(project.get('objects', []))}",
        "",
        "Export the map image from the app and place it after this section for print layout.",
        "",
    ]
    notes = str(project.get("campaign", {}).get("bookletNotes", "")).strip()
    if notes:
        lines.extend(["## GM Notes", "", notes, ""])
    lines.append(campaign_report_markdown(project))
    return "\n".join(lines)


def project_layer_visible(project: dict[str, Any], layer_id: str) -> bool:
    return bool(next((layer.get("visible", True) for layer in project.get("layers", []) if layer.get("id") == layer_id), True))


def should_render_object(project: dict[str, Any], obj: dict[str, Any], for_export: bool) -> bool:
    if not project_layer_visible(project, obj.get("layer", normalize_layer_id(None, obj.get("type")))):
        return False
    if obj.get("type") == "legend" and not project["settings"].get("showLegend", True):
        return False
    if for_export and obj.get("type") == "text" and not obj.get("export", True):
        return False
    if for_export and project["settings"].get("exportAudience") == "Player":
        hidden_rooms = hidden_player_room_ids(project)
        if obj.get("type") == "text" and obj.get("textRole") == "note":
            return False
        if obj.get("type") in {"room", "round", "cave"} and not obj.get("playerVisible", True):
            return False
        if obj.get("roomId") in hidden_rooms:
            return False
    return True


def hidden_player_room_ids(project: dict[str, Any]) -> set[str]:
    return {
        str(obj.get("id"))
        for obj in project.get("objects", [])
        if obj.get("type") in {"room", "round", "cave"} and not obj.get("playerVisible", True)
    }


def is_custom_symbol(project: dict[str, Any], kind: str) -> bool:
    return kind in project.get("customSymbols", {})


def symbol_label(project: dict[str, Any], kind: str) -> str:
    if kind in project.get("customSymbols", {}):
        return project["customSymbols"][kind].get("label", kind)
    return SYMBOL_LABELS.get(kind, kind)


def symbol_icon(kind: str) -> str:
    return SYMBOL_ICONS.get(normalize_symbol_kind(kind), str(kind or "?")[:2].upper())


def symbol_size_for_preset(value: Any) -> float:
    preset = str(value or DEFAULT_SYMBOL_SIZE_PRESET)
    return SYMBOL_SIZE_PRESETS.get(preset, SYMBOL_SIZE_PRESETS[DEFAULT_SYMBOL_SIZE_PRESET])


def custom_symbol_variant_info(project: dict[str, Any], kind: str, variant: str = "") -> dict[str, Any] | None:
    info = project.get("customSymbols", {}).get(kind)
    if not info:
        return None
    if variant:
        for item in info.get("variants", []):
            if str(item.get("id") or "") == str(variant):
                return {**info, **item}
    return info


def symbol_tags(project: dict[str, Any], kind: str) -> list[str]:
    kind = normalize_symbol_kind(kind)
    tags = set(SYMBOL_TAGS.get(kind, []))
    info = project.get("customSymbols", {}).get(kind, {})
    tags.update(normalize_tags(info.get("tags", [])))
    for variant in info.get("variants", []) if isinstance(info, dict) else []:
        tags.update(normalize_tags(variant.get("tags", [])))
    return sorted(tags)


def symbol_search_blob(project: dict[str, Any], kind: str, label: str) -> str:
    variants = " ".join(option["label"] for option in symbol_variant_options(project, kind))
    return " ".join([kind, label, " ".join(symbol_tags(project, kind)), variants]).lower()


def symbol_variant_options(project: dict[str, Any], kind: str) -> list[dict[str, str]]:
    kind = normalize_symbol_kind(kind)
    if is_custom_symbol(project, kind):
        info = project.get("customSymbols", {}).get(kind, {})
        options = [{"id": "", "kind": kind, "label": str(info.get("label") or kind)}]
        for item in info.get("variants", []):
            variant_id = str(item.get("id") or "")
            if variant_id:
                options.append({"id": variant_id, "kind": kind, "label": str(item.get("label") or variant_id)})
        return options
    specs = SYMBOL_VARIANT_SETS.get(kind, [(kind, symbol_label(project, kind))])
    options: list[dict[str, str]] = []
    seen: set[str] = set()
    for variant_kind, label in specs:
        variant_kind = normalize_symbol_kind(variant_kind)
        if variant_kind in seen:
            continue
        seen.add(variant_kind)
        options.append({"id": variant_kind, "kind": variant_kind, "label": label})
    return options


def choose_symbol_variant(project: dict[str, Any], kind: str, randomize: bool, rng: random.Random | None = None) -> dict[str, str]:
    options = symbol_variant_options(project, kind)
    if not options:
        return {"id": "", "kind": normalize_symbol_kind(kind), "label": symbol_label(project, kind)}
    if randomize and len(options) > 1:
        return (rng or random).choice(options)
    return options[0]


def effective_symbol_kind(project: dict[str, Any], obj: dict[str, Any]) -> str:
    kind = normalize_symbol_kind(str(obj.get("kind") or "door"))
    if is_custom_symbol(project, kind):
        return kind
    variant = str(obj.get("variant") or "")
    if variant:
        for option in symbol_variant_options(project, kind):
            if option["id"] == variant:
                return normalize_symbol_kind(option["kind"])
    return kind


def symbol_legend_key(project: dict[str, Any], obj: dict[str, Any]) -> str:
    return effective_symbol_kind(project, obj)


def symbol_group_name(project: dict[str, Any], kind: str) -> str:
    kind = normalize_symbol_kind(kind)
    if kind in SYMBOL_GROUP_BY_KIND:
        return SYMBOL_GROUP_BY_KIND[kind]
    for group in project.get("customSymbolGroups", []):
        if any(entry.get("kind") == kind for entry in group.get("entries", [])):
            return str(group.get("name") or CUSTOM_GROUP_NAME)
    return CUSTOM_GROUP_NAME


def symbol_group_sort_key(project: dict[str, Any], kind: str) -> tuple[int, str, str]:
    group = symbol_group_name(project, kind)
    if group in SYMBOL_GROUP_ORDER:
        group_index = SYMBOL_GROUP_ORDER[group]
    else:
        custom_names = [str(item.get("name") or CUSTOM_GROUP_NAME) for item in project.get("customSymbolGroups", [])]
        group_index = len(SYMBOL_GROUP_ORDER) + (custom_names.index(group) if group in custom_names else len(custom_names))
    return group_index, symbol_label(project, kind).lower(), kind


def legend_label_for_kind(project: dict[str, Any], kind: str) -> str:
    for obj in project.get("objects", []):
        if obj.get("type") == "symbol" and symbol_legend_key(project, obj) == kind and str(obj.get("legendLabel", "")).strip():
            return str(obj.get("legendLabel", "")).strip()
    info = project.get("customSymbols", {}).get(kind, {})
    if isinstance(info, dict) and str(info.get("legendLabel", "")).strip():
        return str(info["legendLabel"]).strip()
    return symbol_label(project, kind)


def missing_custom_symbol_files(project: dict[str, Any]) -> list[tuple[str, str, str]]:
    missing: list[tuple[str, str, str]] = []
    for kind, info in project.get("customSymbols", {}).items():
        candidates = [(str(info.get("label") or kind), str(info.get("path") or ""))]
        candidates.extend((str(item.get("label") or info.get("label") or kind), str(item.get("path") or "")) for item in info.get("variants", []))
        for label, path_value in candidates:
            if not path_value or not Path(path_value).exists():
                missing.append((kind, label, path_value or "<missing path>"))
    return missing


def export_symbol_set_data(project: dict[str, Any]) -> dict[str, Any]:
    return {
        "format": SYMBOL_SET_FORMAT,
        "version": 1,
        "exportedAt": now_iso(),
        "customSymbols": json_clone(project.get("customSymbols", {})),
        "customSymbolGroups": json_clone(project.get("customSymbolGroups", [])),
    }


def import_symbol_set_data(project: dict[str, Any], data: dict[str, Any]) -> int:
    if not isinstance(data, dict) or data.get("format") != SYMBOL_SET_FORMAT:
        raise ValueError("Dieses Symbolset-Format wird nicht unterstuetzt.")
    incoming_symbols = validate_custom_symbols(data.get("customSymbols", {}))
    incoming_groups = validate_custom_symbol_groups(data.get("customSymbolGroups", []), incoming_symbols)
    target_symbols = project.setdefault("customSymbols", {})
    key_map: dict[str, str] = {}
    for key, info in incoming_symbols.items():
        target_key = key
        if target_key in target_symbols or target_key in SYMBOL_LABELS:
            target_key = unique_custom_symbol_key(str(info.get("label") or key), target_symbols)
        key_map[key] = target_key
        target_symbols[target_key] = json_clone(info)
    target_groups = project.setdefault("customSymbolGroups", [{"name": CUSTOM_GROUP_NAME, "entries": []}])
    for group in incoming_groups:
        name = str(group.get("name") or CUSTOM_GROUP_NAME)
        target = next((item for item in target_groups if item.get("name") == name), None)
        if target is None:
            target = {"name": name, "entries": []}
            target_groups.append(target)
        existing = {entry.get("kind") for entry in target.get("entries", [])}
        for entry in group.get("entries", []):
            mapped = key_map.get(entry.get("kind"))
            if mapped and mapped not in existing:
                target.setdefault("entries", []).append({"kind": mapped, "icon": entry.get("icon", "◇"), "label": target_symbols[mapped].get("label", mapped)})
                existing.add(mapped)
    return len(key_map)


def format_scale_value(value: Any) -> str:
    scale = max(0.01, coerce_float(value, 10.0))
    if abs(scale - round(scale)) < 0.000001:
        return str(int(round(scale)))
    return f"{scale:g}"


def cell_scale_label(settings: dict[str, Any]) -> str:
    value = format_scale_value(settings.get("cellScale", 10.0))
    unit = str(settings.get("cellScaleUnit") or "ft.").strip() or "ft."
    return f"{value} {unit} by {value} {unit}"


def format_measure_value(value: float) -> str:
    if abs(value - round(value)) < 0.000001:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def real_distance_label(cells: float, settings: dict[str, Any]) -> str:
    scale = max(0.01, coerce_float(settings.get("cellScale"), 10.0))
    unit = str(settings.get("cellScaleUnit") or "ft.").strip() or "ft."
    return f"{format_measure_value(cells * scale)} {unit}"


def real_area_label(cells: float, settings: dict[str, Any]) -> str:
    scale = max(0.01, coerce_float(settings.get("cellScale"), 10.0))
    unit = str(settings.get("cellScaleUnit") or "ft.").strip() or "ft."
    return f"{format_measure_value(cells * scale * scale)} sq {unit}"


def path_length(points: list[tuple[float, float]]) -> float:
    return sum(math.hypot(points[index][0] - points[index - 1][0], points[index][1] - points[index - 1][1]) for index in range(1, len(points)))


def polygon_area(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    area = 0.0
    for index, (x1, y1) in enumerate(points):
        x2, y2 = points[(index + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2


def measurement_summary(points: list[tuple[float, float]], settings: dict[str, Any]) -> str:
    if len(points) < 2:
        return "measure"
    segment = math.hypot(points[-1][0] - points[-2][0], points[-1][1] - points[-2][1])
    total = path_length(points)
    parts = [
        f"segment {format_measure_value(segment)} cells ({real_distance_label(segment, settings)})",
        f"path {format_measure_value(total)} cells ({real_distance_label(total, settings)})",
    ]
    if len(points) >= 3:
        area = polygon_area(points)
        parts.append(f"area {format_measure_value(area)} cells^2 ({real_area_label(area, settings)})")
    return "measure | " + " | ".join(parts)


def legend_entries(project: dict[str, Any], legend: dict[str, Any]) -> list[tuple[str, str]]:
    used: list[str] = []
    for obj in project["objects"]:
        if obj.get("type") == "symbol" and should_render_object(project, obj, for_export=True):
            key = symbol_legend_key(project, obj)
            if key not in used:
                used.append(key)
    entries = [("cell", cell_scale_label(project["settings"]))]
    entries.extend((kind, legend_label_for_kind(project, kind)) for kind in sorted(used, key=lambda value: symbol_group_sort_key(project, value)))
    entries.extend(("manual", entry) for entry in legend.get("manualEntries", []))
    return entries


def safe_symbol_key(value: str) -> str:
    cleaned = safe_name(value).replace("-", "_")
    return f"custom_{cleaned}"


def unique_custom_symbol_key(label: str, existing: dict[str, Any]) -> str:
    base = safe_symbol_key(label)
    key = base
    counter = 2
    while key in existing or key in SYMBOL_LABELS:
        key = f"{base}_{counter}"
        counter += 1
    return key


def load_custom_symbol_image(project: dict[str, Any], kind: str, size: int, rotation: float = 0.0, variant: str = ""):
    if Image is None:
        return None
    info = custom_symbol_variant_info(project, kind, variant)
    if not info:
        return None
    path = Path(info.get("path", ""))
    if not path.exists():
        return None
    return cached_custom_symbol_image(str(path), str(info.get("sourceType", "png")), int(size), round(float(rotation), 2))


@lru_cache(maxsize=128)
def cached_custom_symbol_image(path_value: str, source_type: str, size: int, rotation: float):
    path = Path(path_value)
    try:
        if source_type == "svg":
            image = load_svg_as_image(path)
            if image is None:
                return None
        else:
            image = Image.open(path).convert("RGBA")
    except Exception:
        return None
    image.thumbnail((size, size))
    if abs(rotation % 360) >= 0.01:
        image = image.rotate(-rotation, resample=Image.Resampling.BICUBIC, expand=True)
    return image


def load_svg_as_image(path: Path):
    try:
        import cairosvg
    except Exception:
        return None
    try:
        data = cairosvg.svg2png(url=str(path))
        return Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        return None


def paste_image_onto_draw(draw, image, x: float, y: float) -> None:
    target = getattr(draw, "_target_image", None)
    if target is None:
        return
    left = int(round(x - image.width / 2))
    top = int(round(y - image.height / 2))
    if target.mode == "RGBA":
        target.alpha_composite(image, (left, top))
    else:
        target.paste(image.convert("RGB"), (left, top), image if image.mode == "RGBA" else None)


def text_measure(draw, text: str, font) -> float:
    try:
        box = draw.textbbox((0, 0), text, font=font)
        return box[2] - box[0]
    except Exception:
        return len(text) * 8


def wrap_text_for_draw(text: str, font, max_width: float) -> list[str]:
    probe = Image.new("RGB", (1, 1))
    probe_draw = ImageDraw.Draw(probe)
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if text_measure(probe_draw, candidate, font) <= max_width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def aligned_text_x(draw, line: str, font, x: float, width: float, align: str) -> float:
    if align == "left":
        return x
    line_width = text_measure(draw, line, font)
    if align == "right":
        return x + width - line_width
    return x + (width - line_width) / 2


def draw_symbol_preview_canvas(canvas: tk.Canvas, project: dict[str, Any], kind: str, label: str) -> None:
    settings = project.get("settings", create_project()["settings"])
    canvas.create_text(64, 92, text=label[:18], fill="#17384a", font=("Segoe UI", 8, "bold"))
    if is_custom_symbol(project, kind):
        image = load_custom_symbol_image(project, kind, 72, 0)
        if image is not None:
            try:
                from PIL import ImageTk
            except ImportError:
                image = None
            if image is not None:
                photo = ImageTk.PhotoImage(image)
                canvas.create_image(64, 44, image=photo)
                canvas._preview_image = photo
                return
    draw_tk_symbol(canvas, kind, 64, 44, 56, settings.get("gridColor", BLUE), settings.get("floorColor", WHITE))


def safe_int(value: Any, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError, tk.TclError):
        return default


def snap_step_label(value: Any) -> str:
    return SNAP_LABEL_BY_STEP.get(normalize_snap_step(value), "1 cell")


def shift_pressed(event: tk.Event) -> bool:
    return bool(getattr(event, "state", 0) & 0x0001)


def corridor_polygon_points(x1: float, y1: float, x2: float, y2: float, width: float) -> list[tuple[float, float]]:
    half = width / 2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length <= 0.000001:
        return [(x1 - half, y1 - half), (x1 + half, y1 - half), (x1 + half, y1 + half), (x1 - half, y1 + half)]
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    sx, sy = x1 - ux * half, y1 - uy * half
    ex, ey = x2 + ux * half, y2 + uy * half
    return [
        (sx + nx * half, sy + ny * half),
        (ex + nx * half, ey + ny * half),
        (ex - nx * half, ey - ny * half),
        (sx - nx * half, sy - ny * half),
    ]


def rect_polygon_points(x: float, y: float, width: float, height: float) -> list[tuple[float, float]]:
    return [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]


def ellipse_polygon_points(x: float, y: float, width: float, height: float, segments: int = 72) -> list[tuple[float, float]]:
    cx, cy = x + width / 2, y + height / 2
    rx, ry = width / 2, height / 2
    return [(cx + math.cos(index / segments * math.tau) * rx, cy + math.sin(index / segments * math.tau) * ry) for index in range(segments)]


def regular_polygon_points(x: float, y: float, width: float, height: float, sides: int) -> list[tuple[float, float]]:
    sides = max(3, min(24, int(sides)))
    cx, cy = x + width / 2, y + height / 2
    rx, ry = width / 2, height / 2
    start = -math.pi / 2
    return [(cx + math.cos(start + index / sides * math.tau) * rx, cy + math.sin(start + index / sides * math.tau) * ry) for index in range(sides)]


def shape_polygon_points(obj: dict[str, Any], cell: float = 1.0) -> list[tuple[float, float]]:
    points = validate_shape_points(obj.get("points"))
    if points:
        return [(point["x"] * cell, point["y"] * cell) for point in points]
    return regular_polygon_points(obj["x"] * cell, obj["y"] * cell, obj["width"] * cell, obj["height"] * cell, int(obj.get("sides", 6)))


def floor_polygon_points(obj: dict[str, Any], cell: float) -> list[tuple[float, float]]:
    obj_type = obj.get("type")
    if obj_type == "diagonal_corridor":
        thickness = max(3, int(obj.get("width", 1) * cell))
        return corridor_polygon_points(obj["x"] * cell, obj["y"] * cell, obj["x2"] * cell, obj["y2"] * cell, thickness)
    x, y = obj["x"] * cell, obj["y"] * cell
    width, height = obj["width"] * cell, obj["height"] * cell
    if obj_type == "round":
        return ellipse_polygon_points(x, y, width, height)
    if obj_type == "cave":
        return cave_points(obj["x"], obj["y"], obj["width"], obj["height"], obj.get("seed", 1), cell)
    return rect_polygon_points(x, y, width, height)


def flatten_points(points: list[tuple[float, float]]) -> list[float]:
    return [coord for point in points for coord in point]


def polygon_axis_line_interval(polygon: list[tuple[float, float]], axis: int, value: float) -> tuple[float, float] | None:
    eps = 0.000001
    other = 1 - axis
    coords: list[float] = []
    for index, point in enumerate(polygon):
        next_point = polygon[(index + 1) % len(polygon)]
        a1, a2 = point[axis], next_point[axis]
        b1, b2 = point[other], next_point[other]
        if abs(a1 - a2) <= eps:
            if abs(value - a1) <= eps:
                coords.extend([b1, b2])
            continue
        if min(a1, a2) - eps <= value <= max(a1, a2) + eps:
            t = (value - a1) / (a2 - a1)
            if -eps <= t <= 1 + eps:
                coords.append(b1 + (b2 - b1) * max(0.0, min(1.0, t)))
    unique: list[float] = []
    for coord in sorted(coords):
        if not unique or abs(coord - unique[-1]) > eps:
            unique.append(coord)
    if len(unique) < 2 or abs(unique[-1] - unique[0]) <= eps:
        return None
    return unique[0], unique[-1]


def orthogonal_grid_segments(polygon: list[tuple[float, float]], cell: float) -> list[tuple[float, float, float, float]]:
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    eps = 0.000001
    segments: list[tuple[float, float, float, float]] = []
    start_x = math.ceil((min(xs) - eps) / cell)
    end_x = math.floor((max(xs) + eps) / cell)
    for index in range(start_x, end_x + 1):
        x = index * cell
        interval = polygon_axis_line_interval(polygon, 0, x)
        if interval:
            y1, y2 = interval
            segments.append((x, y1, x, y2))
    start_y = math.ceil((min(ys) - eps) / cell)
    end_y = math.floor((max(ys) + eps) / cell)
    for index in range(start_y, end_y + 1):
        y = index * cell
        interval = polygon_axis_line_interval(polygon, 1, y)
        if interval:
            x1, x2 = interval
            segments.append((x1, y, x2, y))
    return segments


def span_from_points(first: float, second: float, min_size: float) -> tuple[float, float]:
    if abs(first - second) < min_size:
        return min(first, second), min_size
    return min(first, second), abs(second - first)


def move_object_to_delta(obj: dict[str, Any], original: dict[str, Any], dx: float, dy: float) -> None:
    obj["x"] = original["x"] + dx
    obj["y"] = original["y"] + dy
    if obj.get("type") == "diagonal_corridor":
        obj["x2"] = original["x2"] + dx
        obj["y2"] = original["y2"] + dy
    if obj.get("type") == "shape" and obj.get("kind") == "line":
        obj["x2"] = original["x2"] + dx
        obj["y2"] = original["y2"] + dy
    if obj.get("type") == "shape" and obj.get("kind") == "polygon" and original.get("points"):
        obj["points"] = [{"x": point["x"] + dx, "y": point["y"] + dy} for point in validate_shape_points(original.get("points"))]


def translate_object(obj: dict[str, Any], dx: float, dy: float) -> None:
    obj["x"] = obj.get("x", 0) + dx
    obj["y"] = obj.get("y", 0) + dy
    if obj.get("type") == "diagonal_corridor":
        obj["x2"] = obj.get("x2", 0) + dx
        obj["y2"] = obj.get("y2", 0) + dy
    if obj.get("type") == "shape" and obj.get("kind") == "line":
        obj["x2"] = obj.get("x2", 0) + dx
        obj["y2"] = obj.get("y2", 0) + dy
    if obj.get("type") == "shape" and obj.get("kind") == "polygon" and obj.get("points"):
        obj["points"] = [{"x": point["x"] + dx, "y": point["y"] + dy} for point in validate_shape_points(obj.get("points"))]


def refresh_polygon_bounds(obj: dict[str, Any]) -> None:
    points = validate_shape_points(obj.get("points"))
    if points:
        obj["x"], obj["y"], obj["width"], obj["height"] = bounds_from_points(points)


def rotate_point(x: float, y: float, cx: float, cy: float, degrees: float) -> tuple[float, float]:
    radians = math.radians(degrees)
    dx, dy = x - cx, y - cy
    return cx + math.cos(radians) * dx - math.sin(radians) * dy, cy + math.sin(radians) * dx + math.cos(radians) * dy


def curved_line_control(start: tuple[float, float], end: tuple[float, float]) -> tuple[float, float]:
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = math.hypot(dx, dy)
    if length <= 0.000001:
        return (sx + ex) / 2, (sy + ey) / 2
    bend = max(0.25, min(3.0, length * 0.18))
    return (sx + ex) / 2 - dy / length * bend, (sy + ey) / 2 + dx / length * bend


def quadratic_curve_points(start: tuple[float, float], control: tuple[float, float], end: tuple[float, float], steps: int = 18) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for index in range(max(2, steps) + 1):
        t = index / max(2, steps)
        inv = 1 - t
        x = inv * inv * start[0] + 2 * inv * t * control[0] + t * t * end[0]
        y = inv * inv * start[1] + 2 * inv * t * control[1] + t * t * end[1]
        points.append((x, y))
    return points


def rotate_shape_geometry(obj: dict[str, Any], degrees: float) -> None:
    if abs(degrees % 360) < 0.000001 or obj.get("type") != "shape":
        return
    if obj.get("kind") == "line":
        cx = (float(obj.get("x", 0)) + float(obj.get("x2", 0))) / 2
        cy = (float(obj.get("y", 0)) + float(obj.get("y2", 0))) / 2
        obj["x"], obj["y"] = rotate_point(float(obj.get("x", 0)), float(obj.get("y", 0)), cx, cy, degrees)
        obj["x2"], obj["y2"] = rotate_point(float(obj.get("x2", 0)), float(obj.get("y2", 0)), cx, cy, degrees)
        return
    if obj.get("kind") == "circle":
        return
    x, y, width, height = float(obj.get("x", 0)), float(obj.get("y", 0)), float(obj.get("width", 1)), float(obj.get("height", 1))
    cx, cy = x + width / 2, y + height / 2
    if obj.get("kind") == "polygon":
        source = [(point["x"], point["y"]) for point in validate_shape_points(obj.get("points"))]
    else:
        source = rect_polygon_points(x, y, width, height)
        obj["kind"] = "polygon"
    obj["points"] = [{"x": px, "y": py} for px, py in (rotate_point(px, py, cx, cy, degrees) for px, py in source)]
    refresh_polygon_bounds(obj)


def selection_handles(obj: dict[str, Any]) -> list[tuple[str, float, float]]:
    if obj["type"] == "shape" and obj.get("kind") == "polygon" and obj.get("points"):
        points = validate_shape_points(obj.get("points"))
        handles: list[tuple[str, float, float]] = [(f"point:{index}", point["x"], point["y"]) for index, point in enumerate(points)]
        for index, point in enumerate(points):
            next_point = points[(index + 1) % len(points)]
            handles.append((f"insert:{index}", (point["x"] + next_point["x"]) / 2, (point["y"] + next_point["y"]) / 2))
        return handles
    if obj["type"] in RESIZABLE_TYPES or is_box_shape(obj):
        x, y, w, h = bounds(obj)
        cx, cy = x + w / 2, y + h / 2
        return [
            ("nw", x, y),
            ("n", cx, y),
            ("ne", x + w, y),
            ("e", x + w, cy),
            ("se", x + w, y + h),
            ("s", cx, y + h),
            ("sw", x, y + h),
            ("w", x, cy),
        ]
    if obj["type"] == "diagonal_corridor":
        return [("start", obj["x"], obj["y"]), ("end", obj["x2"], obj["y2"])]
    if obj["type"] == "shape" and obj.get("kind") == "line":
        return [("start", obj["x"], obj["y"]), ("end", obj["x2"], obj["y2"])]
    if obj["type"] == "symbol":
        size = float(obj.get("size", 1))
        rotation = math.radians(float(obj.get("rotation", 0)) - 90)
        return [
            ("scale", obj["x"] + size / 2, obj["y"] + size / 2),
            ("rotate", obj["x"] + math.cos(rotation) * size, obj["y"] + math.sin(rotation) * size),
        ]
    return []


def is_box_shape(obj: dict[str, Any]) -> bool:
    return obj.get("type") == "shape" and obj.get("kind") in BOX_SHAPES


def resize_rectlike_object(obj: dict[str, Any], original: dict[str, Any], handle: str, point: tuple[float, float], min_size: float) -> None:
    left = float(original["x"])
    top = float(original["y"])
    right = left + float(original["width"])
    bottom = top + float(original["height"])
    px, py = point
    if "w" in handle:
        left = min(px, right - min_size)
    if "e" in handle:
        right = max(px, left + min_size)
    if "n" in handle:
        top = min(py, bottom - min_size)
    if "s" in handle:
        bottom = max(py, top + min_size)
    obj["x"] = left
    obj["y"] = top
    obj["width"] = max(min_size, right - left)
    obj["height"] = max(min_size, bottom - top)
    if obj.get("type") == "shape" and obj.get("kind") == "polygon" and original.get("points"):
        obj["points"] = scale_polygon_points(original, obj)


def scale_polygon_points(original: dict[str, Any], resized: dict[str, Any]) -> list[dict[str, float]]:
    original_points = validate_shape_points(original.get("points"))
    if not original_points:
        return []
    old_x, old_y = float(original.get("x", 0)), float(original.get("y", 0))
    old_w, old_h = max(0.000001, float(original.get("width", 1))), max(0.000001, float(original.get("height", 1)))
    new_x, new_y = float(resized.get("x", 0)), float(resized.get("y", 0))
    new_w, new_h = float(resized.get("width", 1)), float(resized.get("height", 1))
    return [
        {
            "x": new_x + ((point["x"] - old_x) / old_w) * new_w,
            "y": new_y + ((point["y"] - old_y) / old_h) * new_h,
        }
        for point in original_points
    ]


def union_bounds(objects: Any) -> tuple[float, float, float, float] | None:
    items = list(objects)
    if not items:
        return None
    boxes = [bounds(obj) for obj in items]
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[0] + box[2] for box in boxes)
    bottom = max(box[1] + box[3] for box in boxes)
    return left, top, right - left, bottom - top


def object_edge_guides(objects: list[dict[str, Any]], exclude_ids: set[str]) -> tuple[list[float], list[float]]:
    guides_x: list[float] = []
    guides_y: list[float] = []
    for obj in objects:
        if obj["id"] in exclude_ids:
            continue
        x, y, w, h = bounds(obj)
        guides_x.extend([x, x + w])
        guides_y.extend([y, y + h])
    return guides_x, guides_y


def snap_delta_axis(delta: float, moving_edges: tuple[float, float], guides: list[float]) -> float:
    best_delta = delta
    best_distance = OBJECT_SNAP_TOLERANCE
    for edge in moving_edges:
        moved = edge + delta
        for guide in guides:
            distance = abs(moved - guide)
            if distance < best_distance:
                best_distance = distance
                best_delta = delta + guide - moved
    return best_delta


def snap_point_to_object_edges(x: float, y: float, objects: list[dict[str, Any]], exclude_ids: set[str]) -> tuple[float, float]:
    guides_x, guides_y = object_edge_guides(objects, exclude_ids)
    for guide in guides_x:
        if abs(x - guide) <= OBJECT_SNAP_TOLERANCE:
            x = guide
            break
    for guide in guides_y:
        if abs(y - guide) <= OBJECT_SNAP_TOLERANCE:
            y = guide
            break
    return x, y


def soften_color(color: str, amount: float) -> str:
    color = color.lstrip("#")
    if len(color) != 6:
        return "#d9eef5"
    try:
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    except ValueError:
        return "#d9eef5"
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def parse_hex_color(color: str) -> tuple[int, int, int] | None:
    value = str(color or "").strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        return None
    try:
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    except ValueError:
        return None


def blend_color(color: str, background: str, opacity: float) -> str:
    opacity = max(0.0, min(1.0, float(opacity)))
    if opacity >= 0.999:
        return color
    rgb = parse_hex_color(color)
    bg = parse_hex_color(background)
    if rgb is None or bg is None:
        return color
    r = int(rgb[0] * opacity + bg[0] * (1 - opacity))
    g = int(rgb[1] * opacity + bg[1] * (1 - opacity))
    b = int(rgb[2] * opacity + bg[2] * (1 - opacity))
    return f"#{r:02x}{g:02x}{b:02x}"


def shape_opacity(obj: dict[str, Any]) -> float:
    return max(0.0, min(1.0, coerce_float(obj.get("opacity"), 1.0)))


def shape_line_style(obj: dict[str, Any]) -> str:
    value = str(obj.get("lineStyle") or "solid").lower()
    return value if value in LINE_STYLES else "solid"


def shape_arrow_style(obj: dict[str, Any]) -> str:
    value = str(obj.get("arrow") or "none").lower()
    return value if value in ARROW_STYLES else "none"


def symbol_opacity(obj: dict[str, Any]) -> float:
    return max(0.0, min(1.0, coerce_float(obj.get("opacity"), 1.0)))


def symbol_ink(settings: dict[str, Any], obj: dict[str, Any]) -> str:
    return str(obj.get("color") or settings.get("gridColor", BLUE))


def symbol_outline_color(settings: dict[str, Any], obj: dict[str, Any]) -> str:
    if obj.get("outlineColor"):
        return str(obj["outlineColor"])
    return settings.get("floorColor", WHITE)


def symbol_shadow_color(_settings: dict[str, Any], _obj: dict[str, Any]) -> str:
    return "#000000"


def image_with_opacity(image, opacity: float):
    opacity = max(0.0, min(1.0, coerce_float(opacity, 1.0)))
    if opacity >= 0.999:
        return image
    result = image.copy()
    if result.mode != "RGBA":
        result = result.convert("RGBA")
    alpha = result.getchannel("A").point(lambda value: int(value * opacity))
    result.putalpha(alpha)
    return result


def image_shadow(image, opacity: float = 0.35):
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    alpha = image.getchannel("A").point(lambda value: int(value * opacity))
    shadow.putalpha(alpha)
    return shadow


def tk_shape_dash(obj: dict[str, Any]) -> tuple[int, ...] | None:
    style = shape_line_style(obj)
    if style == "dash":
        return (10, 5)
    if style == "dot":
        return (2, 5)
    return None


def svg_shape_dash(obj: dict[str, Any], width: int) -> str:
    style = shape_line_style(obj)
    if style == "dash":
        return f' stroke-dasharray="{max(4, width * 4)} {max(2, width * 2)}"'
    if style == "dot":
        return f' stroke-dasharray="{max(1, width)} {max(3, width * 3)}"'
    return ""


def tk_arrow_value(obj: dict[str, Any]) -> str | None:
    return {"start": "first", "end": "last", "both": "both"}.get(shape_arrow_style(obj))


def flatten_rgba(image, background: str):
    if image.mode != "RGBA":
        return image.convert("RGB")
    base = Image.new("RGB", image.size, background)
    base.paste(image, mask=image.getchannel("A"))
    return base


def add_export_page_chrome(image, project: dict[str, Any], scale: int, margin_cells: int, title_area: bool, transparent: bool):
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    margin = margin_cells * cell
    title_height = int(cell * 3) if title_area else 0
    mode = "RGBA" if transparent else "RGB"
    background = (0, 0, 0, 0) if transparent else settings["backgroundColor"]
    page = Image.new(mode, (image.width + margin * 2, image.height + margin * 2 + title_height), background)
    draw = ImageDraw.Draw(page)
    if title_area:
        title_box = (margin, margin, margin + image.width, margin + title_height)
        draw.rectangle(title_box, fill=settings["floorColor"], outline=settings["gridColor"], width=max(1, scale * 2))
        title = project.get("meta", {}).get("title") or "Untitled Dungeon"
        draw.text((margin + cell, margin + title_height / 2), title, fill=settings["gridColor"], font=get_font(max(12, int(cell * 1.3))), anchor="lm")
    page.paste(image, (margin, margin + title_height), image if image.mode == "RGBA" else None)
    return page


def save_svg(path: str, project: dict[str, Any], options: dict[str, Any]) -> None:
    scale = int(options.get("scale", 1))
    project = json.loads(json.dumps(project))
    project["settings"]["exportGrid"] = bool(options.get("export_grid", project["settings"].get("exportGrid", True)))
    project["settings"]["exportAudience"] = options.get("audience", project["settings"].get("exportAudience", "GM"))
    content_width, content_height = canvas_size(project, scale, include_legend=options.get("include_legend", True))
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    scope = options.get("scope", "page")
    margin_cells = max(0, int(options.get("print_margin_cells", 0))) if scope == "page" else 0
    margin = margin_cells * cell
    title_area = bool(options.get("title_area", False)) if scope == "page" else False
    title_height = int(cell * 3) if title_area else 0
    width = content_width + margin * 2
    height = content_height + margin * 2 + title_height
    offset_x = margin
    offset_y = margin + title_height
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">',
        f'<rect width="100%" height="100%" fill="{settings["backgroundColor"]}"/>',
    ]
    if title_area:
        title = escape_xml(project.get("meta", {}).get("title") or "Untitled Dungeon")
        parts.append(
            f'<rect x="{margin:.2f}" y="{margin:.2f}" width="{content_width:.2f}" height="{title_height:.2f}" '
            f'fill="{settings["floorColor"]}" stroke="{settings["gridColor"]}" stroke-width="{max(1, scale * 2)}"/>'
        )
        parts.append(
            f'<text x="{margin + cell:.2f}" y="{margin + title_height / 2:.2f}" fill="{settings["gridColor"]}" '
            f'font-size="{max(12, int(cell * 1.3))}" font-family="Arial" font-weight="bold" dominant-baseline="middle">{title}</text>'
        )
    parts.append(f'<g transform="translate({offset_x:.2f},{offset_y:.2f})">')
    if settings.get("exportGrid", True):
        parts.extend(svg_grid_lines(settings, scale))
    renderable_objects = []
    for obj in project["objects"]:
        if not should_render_object(project, obj, for_export=True):
            continue
        if obj.get("type") == "legend" and options.get("include_legend") is False:
            continue
        renderable_objects.append(obj)
    parts.extend(svg_for_floor_objects(project, [obj for obj in renderable_objects if obj.get("type") in FLOOR_TYPES], scale))
    for obj in renderable_objects:
        if obj.get("type") in FLOOR_TYPES:
            continue
        parts.extend(svg_for_object(project, obj, scale))
    parts.append("</g>")
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")


def svg_grid_lines(settings: dict[str, Any], scale: int) -> list[str]:
    cell = settings["cellSize"] * scale
    width = settings["width"] * cell
    height = settings["height"] * cell
    parts: list[str] = []
    if settings.get("showSubGrid", True):
        step = normalize_snap_step(settings.get("snapStep", 1.0))
        if step < 1:
            sub = cell * step
            color = soften_color(settings["backgroundColor"], 0.35)
            for index in range(int(settings["width"] / step) + 2):
                x = index * sub
                parts.append(f'<line x1="{x:.2f}" y1="0" x2="{x:.2f}" y2="{height:.2f}" stroke="{color}" stroke-width="{max(1, scale)}"/>')
            for index in range(int(settings["height"] / step) + 2):
                y = index * sub
                parts.append(f'<line x1="0" y1="{y:.2f}" x2="{width:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="{max(1, scale)}"/>')
    if settings.get("showMainGrid", True):
        color = soften_color(settings["backgroundColor"], 0.55)
        for index in range(settings["width"] + 1):
            x = index * cell
            parts.append(f'<line x1="{x:.2f}" y1="0" x2="{x:.2f}" y2="{height:.2f}" stroke="{color}" stroke-width="{max(1, scale)}"/>')
        for index in range(settings["height"] + 1):
            y = index * cell
            parts.append(f'<line x1="0" y1="{y:.2f}" x2="{width:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="{max(1, scale)}"/>')
    if settings.get("showCoordinates", False):
        font_size = max(7, int(cell * 0.38))
        ink = settings.get("gridColor", BLUE)
        for column in range(settings["width"]):
            x = column * cell + cell / 2
            label = escape_xml(grid_column_label(column + 1))
            top = max(6, cell * 0.28)
            bottom = height - max(6, cell * 0.28)
            parts.append(f'<text x="{x:.2f}" y="{top:.2f}" fill="{ink}" font-size="{font_size}" text-anchor="middle" dominant-baseline="central">{label}</text>')
            parts.append(f'<text x="{x:.2f}" y="{bottom:.2f}" fill="{ink}" font-size="{font_size}" text-anchor="middle" dominant-baseline="central">{label}</text>')
        for row in range(settings["height"]):
            y = row * cell + cell / 2
            label = str(row + 1)
            left = max(8, cell * 0.32)
            right = width - max(8, cell * 0.32)
            parts.append(f'<text x="{left:.2f}" y="{y:.2f}" fill="{ink}" font-size="{font_size}" text-anchor="middle" dominant-baseline="central">{label}</text>')
            parts.append(f'<text x="{right:.2f}" y="{y:.2f}" fill="{ink}" font-size="{font_size}" text-anchor="middle" dominant-baseline="central">{label}</text>')
    return parts


def svg_for_floor_objects(project: dict[str, Any], objects: list[dict[str, Any]], scale: int) -> list[str]:
    parts: list[str] = []
    for obj in objects:
        parts.extend(svg_for_floor_outline(project, obj, scale))
    for obj in objects:
        parts.extend(svg_for_floor_fill(project, obj, scale))
    for obj in objects:
        parts.extend(svg_for_floor_grid(project, obj, scale))
    return parts


def svg_for_floor_outline(project: dict[str, Any], obj: dict[str, Any], scale: int) -> list[str]:
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    ink = settings["gridColor"]
    wall = max(1, int(cell * max(0.02, coerce_float(obj.get("wallThickness"), 0.16)) / 2))
    obj_type = obj.get("type")
    if obj_type == "diagonal_corridor":
        x1, y1 = obj["x"] * cell, obj["y"] * cell
        x2, y2 = obj["x2"] * cell, obj["y2"] * cell
        thickness = max(3, int(obj.get("width", 1) * cell))
        outline = thickness + max(2, int(cell * max(0.02, coerce_float(obj.get("wallThickness"), 0.16))))
        return [f'<polygon points="{svg_points(corridor_polygon_points(x1, y1, x2, y2, outline))}" fill="{ink}"/>']
    x, y = obj["x"] * cell, obj["y"] * cell
    width, height = obj["width"] * cell, obj["height"] * cell
    if obj_type == "round":
        return [f'<ellipse cx="{x + width / 2:.2f}" cy="{y + height / 2:.2f}" rx="{width / 2 + wall:.2f}" ry="{height / 2 + wall:.2f}" fill="{ink}"/>']
    if obj_type == "cave":
        points = floor_polygon_points(obj, cell)
        return [f'<polyline points="{svg_points(points + [points[0]])}" fill="none" stroke="{ink}" stroke-width="{max(1, wall * 2)}" stroke-linejoin="round"/>']
    return [f'<rect x="{x - wall:.2f}" y="{y - wall:.2f}" width="{width + wall * 2:.2f}" height="{height + wall * 2:.2f}" fill="{ink}"/>']


def svg_for_floor_fill(project: dict[str, Any], obj: dict[str, Any], scale: int) -> list[str]:
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    floor = settings["floorColor"]
    obj_type = obj.get("type")
    if obj_type == "diagonal_corridor":
        return [f'<polygon points="{svg_points(floor_polygon_points(obj, cell))}" fill="{floor}"/>']
    x, y = obj["x"] * cell, obj["y"] * cell
    width, height = obj["width"] * cell, obj["height"] * cell
    if obj_type == "round":
        return [f'<ellipse cx="{x + width / 2:.2f}" cy="{y + height / 2:.2f}" rx="{width / 2:.2f}" ry="{height / 2:.2f}" fill="{floor}"/>']
    if obj_type == "cave":
        return [f'<polygon points="{svg_points(floor_polygon_points(obj, cell))}" fill="{floor}"/>']
    return [f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" fill="{floor}"/>']


def svg_for_floor_grid(project: dict[str, Any], obj: dict[str, Any], scale: int) -> list[str]:
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    ink = settings["gridColor"]
    return [
        f'<line x1="{gx1:.2f}" y1="{gy1:.2f}" x2="{gx2:.2f}" y2="{gy2:.2f}" stroke="{ink}" stroke-width="{max(1, scale)}"/>'
        for gx1, gy1, gx2, gy2 in orthogonal_grid_segments(floor_polygon_points(obj, cell), cell)
    ]


def svg_for_object(project: dict[str, Any], obj: dict[str, Any], scale: int) -> list[str]:
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    ink = settings["gridColor"]
    floor = settings["floorColor"]
    if obj["type"] in FLOOR_TYPES:
        return svg_for_floor_objects(project, [obj], scale)
    if obj["type"] == "legend":
        return svg_for_legend_object(project, obj, scale)
    if obj["type"] == "symbol":
        x, y, size = obj["x"] * cell, obj["y"] * cell, obj.get("size", 1) * cell
        custom = svg_for_custom_symbol(project, obj, cell, settings)
        if custom is not None:
            return custom
        return svg_for_styled_symbol(project, obj, x, y, size, ink, floor, scale)
    if obj["type"] == "text":
        x, y = obj["x"] * cell, obj["y"] * cell
        anchor = {"left": "start", "center": "middle", "right": "end"}.get(obj.get("align", "center"), "middle")
        rotation = float(obj.get("rotation", 0)) % 360
        transform = f' transform="rotate({rotation:.2f} {x:.2f} {y:.2f})"' if rotation else ""
        return [f'<text x="{x:.2f}" y="{y:.2f}" fill="{obj.get("color") or settings.get("textColor", ink)}" font-size="{obj.get("size", 1) * cell:.2f}" font-family="{escape_xml(str(obj.get("font") or "Arial"))}" text-anchor="{anchor}"{transform}>{escape_xml(str(obj.get("text", "")))}</text>']
    if obj["type"] == "shape":
        return svg_for_shape(settings, obj, scale)
    return []


def svg_arrowhead_points(tail: tuple[float, float], tip: tuple[float, float], size: float) -> list[tuple[float, float]]:
    angle = math.atan2(tip[1] - tail[1], tip[0] - tail[0])
    left = angle + math.pi * 0.82
    right = angle - math.pi * 0.82
    return [
        tip,
        (tip[0] + math.cos(left) * size, tip[1] + math.sin(left) * size),
        (tip[0] + math.cos(right) * size, tip[1] + math.sin(right) * size),
    ]


def svg_smooth_closed_path(points: list[tuple[float, float]]) -> str:
    if len(points) < 3:
        return ""
    first_mid = ((points[-1][0] + points[0][0]) / 2, (points[-1][1] + points[0][1]) / 2)
    parts = [f"M {first_mid[0]:.2f} {first_mid[1]:.2f}"]
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        mid = ((point[0] + next_point[0]) / 2, (point[1] + next_point[1]) / 2)
        parts.append(f"Q {point[0]:.2f} {point[1]:.2f} {mid[0]:.2f} {mid[1]:.2f}")
    parts.append("Z")
    return " ".join(parts)


def svg_for_shape(settings: dict[str, Any], obj: dict[str, Any], scale: int) -> list[str]:
    cell = settings["cellSize"] * scale
    ink = obj.get("strokeColor") or settings["gridColor"]
    fill = obj.get("fillColor") or "none"
    width = max(1, int(float(obj.get("lineWidth", 0.12)) * cell))
    opacity = shape_opacity(obj)
    opacity_attr = f' stroke-opacity="{opacity:.3f}"' if opacity < 0.999 else ""
    fill_opacity_attr = f' fill-opacity="{opacity:.3f}"' if opacity < 0.999 and fill != "none" else ""
    dash_attr = svg_shape_dash(obj, width)
    linecap = ' stroke-linecap="round"' if shape_line_style(obj) == "dot" else ' stroke-linecap="round"'
    kind = obj.get("kind")
    if kind == "line":
        x1, y1 = obj["x"] * cell, obj["y"] * cell
        x2, y2 = obj["x2"] * cell, obj["y2"] * cell
        if obj.get("curve", False):
            cx, cy = curved_line_control((x1, y1), (x2, y2))
            parts = [f'<path d="M {x1:.2f} {y1:.2f} Q {cx:.2f} {cy:.2f} {x2:.2f} {y2:.2f}" fill="none" stroke="{ink}" stroke-width="{width}"{linecap}{dash_attr}{opacity_attr}/>']
        else:
            parts = [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{ink}" stroke-width="{width}"{linecap}{dash_attr}{opacity_attr}/>']
        arrow = shape_arrow_style(obj)
        size = max(width * 3, cell * 0.35)
        arrow_opacity = f' fill-opacity="{opacity:.3f}"' if opacity < 0.999 else ""
        if arrow in {"start", "both"}:
            parts.append(f'<polygon points="{svg_points(svg_arrowhead_points((x2, y2), (x1, y1), size))}" fill="{ink}"{arrow_opacity}/>')
        if arrow in {"end", "both"}:
            parts.append(f'<polygon points="{svg_points(svg_arrowhead_points((x1, y1), (x2, y2), size))}" fill="{ink}"{arrow_opacity}/>')
        return parts
    x, y = obj["x"] * cell, obj["y"] * cell
    w, h = obj["width"] * cell, obj["height"] * cell
    if kind == "circle":
        return [f'<ellipse cx="{x + w / 2:.2f}" cy="{y + h / 2:.2f}" rx="{w / 2:.2f}" ry="{h / 2:.2f}" fill="{fill}"{fill_opacity_attr} stroke="{ink}" stroke-width="{width}"{dash_attr}{opacity_attr}/>']
    if kind == "polygon":
        points = shape_polygon_points(obj, cell)
        if obj.get("curve", False):
            return [f'<path d="{svg_smooth_closed_path(points)}" fill="{fill}"{fill_opacity_attr} stroke="{ink}" stroke-width="{width}" stroke-linejoin="round"{dash_attr}{opacity_attr}/>']
        return [f'<polygon points="{svg_points(points)}" fill="{fill}"{fill_opacity_attr} stroke="{ink}" stroke-width="{width}" stroke-linejoin="round"{dash_attr}{opacity_attr}/>']
    return [f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}"{fill_opacity_attr} stroke="{ink}" stroke-width="{width}"{dash_attr}{opacity_attr}/>']


def svg_for_legend_object(project: dict[str, Any], obj: dict[str, Any], scale: int) -> list[str]:
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    x, y = obj["x"] * cell, obj["y"] * cell
    width, height = obj["width"] * cell, obj["height"] * cell
    ink = settings.get("legendColor", settings["gridColor"])
    floor = settings["floorColor"]
    legend_scale = float(obj.get("scale", 1.0))
    parts = [
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" fill="{floor}" stroke="{ink}" stroke-width="{max(1, scale * 2)}"/>',
        f'<text x="{x + cell * 0.65:.2f}" y="{y + cell * 0.8:.2f}" fill="{ink}" font-size="{max(12, int(cell * legend_scale * 1.1))}" font-family="Arial" font-weight="bold" dominant-baseline="middle">LEGEND</text>',
    ]
    entries = legend_entries(project, obj)
    columns = max(1, int(obj.get("columns", 4)))
    entry_w = max(cell * 4, (width - cell) / columns)
    entry_h = cell * 1.15 * legend_scale
    for index, (kind, label) in enumerate(entries):
        col = index % columns
        row = index // columns
        ex = x + cell * 0.65 + col * entry_w
        ey = y + cell * 1.8 + row * entry_h
        if ey > y + height - cell * 0.4:
            break
        if kind == "cell":
            parts.append(f'<rect x="{ex:.2f}" y="{ey - cell * 0.35:.2f}" width="{cell * 0.7:.2f}" height="{cell * 0.7:.2f}" fill="{floor}" stroke="{ink}" stroke-width="{max(1, scale)}"/>')
        elif kind == "manual":
            parts.append(f'<text x="{ex + cell * 0.2:.2f}" y="{ey:.2f}" fill="{ink}" font-size="{max(8, int(cell * 0.7))}" font-family="Arial" dominant-baseline="middle">•</text>')
        elif is_custom_symbol(project, kind):
            custom = svg_for_custom_symbol(project, {"kind": kind, "x": (ex + cell * 0.35) / cell, "y": ey / cell, "size": 0.75, "rotation": 0}, cell, settings)
            if custom is not None:
                parts.extend(custom)
            else:
                parts.extend(svg_for_symbol(kind, ex + cell * 0.35, ey, cell * 0.7, ink, floor, scale, 0, symbol_label(project, kind)))
        else:
            parts.extend(svg_for_symbol(kind, ex + cell * 0.35, ey, cell * 0.7, ink, floor, scale, 0, symbol_label(project, kind)))
        parts.append(f'<text x="{ex + cell * 1.1:.2f}" y="{ey:.2f}" fill="{ink}" font-size="{max(7, int(cell * 0.55 * legend_scale))}" font-family="Arial" font-weight="bold" dominant-baseline="middle">{escape_xml(label)}</text>')
    return parts


def svg_wrap_opacity(parts: list[str], opacity: float) -> list[str]:
    if opacity >= 0.999:
        return parts
    return [f'<g opacity="{opacity:.3f}">', *parts, "</g>"]


def svg_for_styled_symbol(project: dict[str, Any], obj: dict[str, Any], x: float, y: float, size: float, ink: str, floor: str, scale: int) -> list[str]:
    ink = symbol_ink(project["settings"], obj) or ink
    kind = effective_symbol_kind(project, obj)
    rotation = float(obj.get("rotation", 0))
    parts: list[str] = []
    if obj.get("shadow"):
        offset = max(1.0, size * 0.08)
        shadow = svg_for_symbol(kind, x + offset, y + offset, size, symbol_shadow_color(project["settings"], obj), floor, scale, rotation, symbol_label(project, kind))
        parts.extend(svg_wrap_opacity(shadow, 0.28))
    if obj.get("outline"):
        outline = svg_for_symbol(kind, x, y, size * 1.12, symbol_outline_color(project["settings"], obj), floor, scale, rotation, symbol_label(project, kind))
        parts.extend(svg_wrap_opacity(outline, 0.75))
    parts.extend(svg_for_symbol(kind, x, y, size, ink, floor, scale, rotation, symbol_label(project, kind)))
    return svg_wrap_opacity(parts, symbol_opacity(obj))


def svg_for_custom_symbol(project: dict[str, Any], obj: dict[str, Any], cell: float, settings: dict[str, Any]) -> list[str] | None:
    size = max(8, int(obj.get("size", 1) * cell))
    image = load_custom_symbol_image(project, obj["kind"], size, float(obj.get("rotation", 0)), str(obj.get("variant", "")))
    if image is None:
        return None
    uri = svg_image_data_uri(image)
    if uri is None:
        return None
    x = obj["x"] * cell - image.width / 2
    y = obj["y"] * cell - image.height / 2
    opacity = symbol_opacity(obj)
    parts: list[str] = []
    if obj.get("shadow"):
        offset = max(1.0, image.width * 0.08)
        parts.append(f'<rect x="{x + offset:.2f}" y="{y + offset:.2f}" width="{image.width:.2f}" height="{image.height:.2f}" fill="{symbol_shadow_color(settings, obj)}" opacity="0.22"/>')
    if obj.get("outline"):
        pad = max(1.0, image.width * 0.04)
        parts.append(f'<rect x="{x - pad:.2f}" y="{y - pad:.2f}" width="{image.width + pad * 2:.2f}" height="{image.height + pad * 2:.2f}" fill="none" stroke="{symbol_outline_color(settings, obj)}" stroke-width="{max(1, int(cell * 0.08))}" opacity="0.75"/>')
    opacity_attr = f' opacity="{opacity:.3f}"' if opacity < 0.999 else ""
    parts.append(f'<image href="{uri}" x="{x:.2f}" y="{y:.2f}" width="{image.width:.2f}" height="{image.height:.2f}"{opacity_attr}/>')
    return parts


def svg_image_data_uri(image) -> str | None:
    try:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
    except Exception:
        return None
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def svg_for_symbol(kind: str, x: float, y: float, s: float, ink: str, floor: str, scale: int, rotation: float = 0.0, fallback_label: str = "") -> list[str]:
    kind = normalize_symbol_kind(kind)
    width = max(1, scale * 2)
    parts: list[str] = []

    def line(x1: float, y1: float, x2: float, y2: float) -> None:
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{ink}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')

    def polyline(points: list[tuple[float, float]], fill: str = "none") -> None:
        parts.append(f'<polyline points="{svg_points(points)}" fill="{fill}" stroke="{ink}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')

    def polygon(points: list[tuple[float, float]], fill: str = ink) -> None:
        parts.append(f'<polygon points="{svg_points(points)}" fill="{fill}" stroke="{ink}" stroke-width="{max(1, width)}" stroke-linejoin="round"/>')

    def rect(left: float, top: float, right: float, bottom: float, fill: str = "none", stroke: str = ink) -> None:
        parts.append(f'<rect x="{left:.2f}" y="{top:.2f}" width="{right - left:.2f}" height="{bottom - top:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def ellipse(cx: float, cy: float, rx: float, ry: float, fill: str = "none") -> None:
        parts.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{fill}" stroke="{ink}" stroke-width="{width}"/>')

    def text(value: str, tx: float = x, ty: float = y, factor: float = 0.65) -> None:
        parts.append(f'<text x="{tx:.2f}" y="{ty:.2f}" fill="{ink}" font-size="{max(7, int(s * factor))}" font-family="Arial" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{escape_xml(value)}</text>')

    if kind in DOOR_SYMBOLS:
        rect(x - s * 0.48, y - s * 0.2, x + s * 0.48, y + s * 0.2, floor)
        line(x - s * 0.48, y, x + s * 0.48, y)
        if kind == "door":
            rect(x - s * 0.16, y - s * 0.09, x + s * 0.16, y + s * 0.09, floor)
        elif kind == "double_door":
            rect(x - s * 0.34, y - s * 0.09, x - s * 0.05, y + s * 0.09, floor)
            rect(x + s * 0.05, y - s * 0.09, x + s * 0.34, y + s * 0.09, floor)
        elif kind in {"secret_door", "concealed_door"}:
            text("S" if kind == "secret_door" else "C", factor=0.55)
        elif kind == "one_way_door":
            polygon([(x - s * 0.12, y - s * 0.02), (x + s * 0.12, y - s * 0.02), (x, y + s * 0.18)])
        elif kind == "false_door":
            parts.append(f'<path d="M {x - s * 0.22:.2f} {y + s * 0.18:.2f} Q {x:.2f} {y - s * 0.08:.2f} {x + s * 0.22:.2f} {y + s * 0.18:.2f}" fill="none" stroke="{ink}" stroke-width="{width}" stroke-linecap="round"/>')
        elif kind == "locked_door":
            rect(x - s * 0.13, y - s * 0.1, x + s * 0.13, y + s * 0.1)
            ellipse(x, y, s * 0.04, s * 0.04, ink)
        elif kind in {"archway", "archway_door"}:
            line(x - s * 0.2, y - s * 0.12, x + s * 0.2, y - s * 0.12)
            line(x, y - s * 0.12, x, y + s * 0.16)
        elif kind == "barred_door":
            for offset in (-0.16, 0, 0.16):
                rect(x + s * offset - s * 0.04, y - s * 0.12, x + s * offset + s * 0.04, y + s * 0.12, ink)
        elif kind == "portcullis":
            for offset in (-0.18, 0, 0.18):
                ellipse(x + s * offset, y, s * 0.035, s * 0.035, ink)
        elif kind == "one_way_secret_door":
            text("S", x - s * 0.12, y, 0.45)
            polygon([(x + s * 0.02, y - s * 0.04), (x + s * 0.22, y - s * 0.04), (x + s * 0.12, y + s * 0.14)])
        elif kind == "window":
            rect(x - s * 0.25, y - s * 0.05, x + s * 0.25, y + s * 0.05, ink)
        elif kind == "arrow_slit":
            polygon([(x - s * 0.25, y - s * 0.1), (x - s * 0.05, y + s * 0.1), (x - s * 0.28, y + s * 0.1)])
            polygon([(x + s * 0.25, y - s * 0.1), (x + s * 0.05, y + s * 0.1), (x + s * 0.28, y + s * 0.1)])
        elif kind == "open_door":
            line(x - s * 0.05, y, x + s * 0.25, y - s * 0.28)
        elif kind == "revolving_door":
            parts.append(f'<path d="M {x + s * 0.22:.2f} {y:.2f} A {s * 0.24:.2f} {s * 0.24:.2f} 0 1 1 {x + s * 0.18:.2f} {y - s * 0.16:.2f}" fill="none" stroke="{ink}" stroke-width="{width}"/>')
            line(x, y, x + s * 0.22, y)
        else:
            text(symbol_icon(kind).strip()[:2], factor=0.52)
    elif kind in HAZARD_SYMBOLS:
        rect(x - s * 0.45, y - s * 0.45, x + s * 0.45, y + s * 0.45)
        if kind == "covered_pit":
            line(x - s * 0.32, y - s * 0.32, x + s * 0.32, y + s * 0.32)
            line(x + s * 0.32, y - s * 0.32, x - s * 0.32, y + s * 0.32)
        elif kind == "open_pit":
            rect(x - s * 0.25, y - s * 0.25, x + s * 0.25, y + s * 0.25, ink)
        else:
            text({"trap": "T", "trap_ceiling": "C", "trap_floor": "F", "secret_trap_door": "S"}.get(kind, symbol_icon(kind).strip()[:2]), factor=0.72)
    elif kind in {"stairs", "stair_slide_trap", "natural_stairs"}:
        for index in range(7):
            line(x - s * 0.55 + index * s * 0.16, y - s * 0.45, x - s * 0.3 + index * s * 0.16, y + s * 0.45)
        if kind == "stair_slide_trap":
            line(x - s * 0.48, y + s * 0.45, x + s * 0.48, y + s * 0.45)
        if kind == "natural_stairs":
            parts.append(f'<path d="M {x - s * 0.5:.2f} {y:.2f} Q {x:.2f} {y - s * 0.45:.2f} {x + s * 0.5:.2f} {y:.2f}" fill="none" stroke="{ink}" stroke-width="{width}"/>')
    elif kind == "spiral_stairs":
        for radius in (0.15, 0.3, 0.45):
            ellipse(x, y, s * radius, s * radius)
        line(x, y, x + s * 0.45, y)
    elif kind == "ladder":
        line(x - s * 0.25, y - s * 0.45, x - s * 0.25, y + s * 0.45)
        line(x + s * 0.25, y - s * 0.45, x + s * 0.25, y + s * 0.45)
        for index in range(5):
            yy = y - s * 0.35 + index * s * 0.18
            line(x - s * 0.25, yy, x + s * 0.25, yy)
    elif kind == "slide":
        line(x - s * 0.45, y, x + s * 0.35, y)
        line(x + s * 0.18, y - s * 0.18, x + s * 0.38, y)
        line(x + s * 0.18, y + s * 0.18, x + s * 0.38, y)
    elif kind in {"pillar", "rock_column"}:
        ellipse(x, y, s * 0.3, s * 0.3, ink)
        if kind == "rock_column":
            text("x", factor=0.6)
    elif kind == "statue":
        ellipse(x, y, s * 0.45, s * 0.45)
        text("*", factor=1.0)
    elif kind in {"fountain", "well"}:
        ellipse(x, y, s * 0.42, s * 0.42)
        ellipse(x, y, s * 0.18, s * 0.18)
    elif kind in {"pool", "pool_lake", "stream", "curtain", "submerged_path"}:
        for index in range(3):
            yy = y - s * 0.25 + index * s * 0.25
            polyline([(x - s * 0.42, yy), (x - s * 0.15, yy + s * 0.08), (x + s * 0.15, yy - s * 0.08), (x + s * 0.42, yy)])
    elif kind in {"dais", "teleporter"}:
        rect(x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42)
        rect(x - s * 0.25, y - s * 0.25, x + s * 0.25, y + s * 0.25)
        if kind == "teleporter":
            for index in range(9):
                px = x - s * 0.25 + (index % 3) * s * 0.25
                py = y - s * 0.25 + (index // 3) * s * 0.25
                rect(px, py, px + s * 0.08, py + s * 0.08, ink)
    elif kind == "altar":
        rect(x - s * 0.2, y - s * 0.48, x + s * 0.2, y + s * 0.48)
        rect(x - s * 0.07, y - s * 0.22, x + s * 0.07, y - s * 0.08, ink)
        rect(x - s * 0.07, y + s * 0.12, x + s * 0.07, y + s * 0.26, ink)
    elif kind == "fireplace":
        rect(x - s * 0.38, y - s * 0.4, x + s * 0.38, y + s * 0.15)
        parts.append(f'<path d="M {x - s * 0.25:.2f} {y + s * 0.2:.2f} Q {x:.2f} {y - s * 0.1:.2f} {x + s * 0.25:.2f} {y + s * 0.2:.2f}" fill="none" stroke="{ink}" stroke-width="{width}"/>')
    elif kind == "table_chest":
        rect(x - s * 0.45, y - s * 0.2, x - s * 0.05, y + s * 0.2)
        rect(x + s * 0.08, y - s * 0.18, x + s * 0.42, y + s * 0.18)
        line(x + s * 0.08, y, x + s * 0.42, y)
    elif kind == "bed":
        rect(x - s * 0.42, y - s * 0.25, x + s * 0.42, y + s * 0.25)
        line(x - s * 0.18, y - s * 0.25, x - s * 0.18, y + s * 0.25)
    elif kind in {"railing", "illusory_wall", "rock_wall", "subterranean_passage"}:
        if kind == "railing":
            for index in range(5):
                ellipse(x - s * 0.41 + index * s * 0.22, y, s * 0.04, s * 0.06, ink)
        elif kind == "illusory_wall":
            for index in range(4):
                line(x - s * 0.45 + index * s * 0.24, y, x - s * 0.32 + index * s * 0.24, y)
        elif kind == "subterranean_passage":
            rect(x - s * 0.45, y - s * 0.28, x + s * 0.45, y + s * 0.28, ink)
        else:
            for index in range(5):
                yy = y - s * 0.3 + index * s * 0.15
                line(x - s * 0.45, yy, x + s * 0.45, yy)
    elif kind in {"stalactite", "stalagmite"}:
        points = (
            [(x - s * 0.35, y - s * 0.35), (x + s * 0.35, y - s * 0.35), (x, y + s * 0.35)]
            if kind == "stalactite"
            else [(x - s * 0.35, y + s * 0.35), (x + s * 0.35, y + s * 0.35), (x, y - s * 0.35)]
        )
        polygon(points, floor)
    elif kind in {"rubble", "depression"}:
        for index in range(9):
            angle = index * math.tau / 9
            radius = s * (0.15 + 0.3 * ((index % 3) / 2))
            ellipse(x + math.cos(angle) * radius, y + math.sin(angle) * radius, s * 0.05, s * 0.05, ink if kind == "rubble" else floor)
    elif kind in {"crevasse", "sinkhole", "elevated_ledge", "natural_chimney"}:
        if kind == "sinkhole":
            for radius in (0.42, 0.27, 0.12):
                ellipse(x, y, s * radius, s * radius)
        elif kind == "natural_chimney":
            for index in range(8):
                angle = index * math.tau / 8
                line(x, y, x + math.cos(angle) * s * 0.42, y + math.sin(angle) * s * 0.42)
        elif kind == "elevated_ledge":
            polyline([(x - s * 0.45, y - s * 0.1), (x - s * 0.2, y + s * 0.25), (x + s * 0.1, y + s * 0.1), (x + s * 0.45, y + s * 0.3)])
            line(x - s * 0.45, y - s * 0.25, x + s * 0.45, y - s * 0.05)
        else:
            polyline([(x - s * 0.4, y - s * 0.4), (x - s * 0.1, y - s * 0.1), (x - s * 0.25, y + s * 0.2), (x + s * 0.15, y), (x + s * 0.4, y + s * 0.35)])
    else:
        text(symbol_icon(kind).strip()[:2], factor=0.7)

    if abs(rotation % 360) < 0.01:
        return parts
    return [f'<g transform="rotate({rotation:.2f} {x:.2f} {y:.2f})">', *parts, "</g>"]


def escape_xml(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def svg_points(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def canvas_size(project: dict[str, Any], scale: float = 1.0, include_legend: bool | None = None) -> tuple[float, float]:
    settings = project["settings"]
    if include_legend is None:
        include_legend = settings.get("showLegend", True)
    max_x = float(settings["width"])
    max_y = float(settings["height"])
    for obj in project.get("objects", []):
        if obj.get("type") == "legend" and not include_legend:
            continue
        if not should_render_object(project, obj, for_export=False):
            continue
        x, y, w, h = bounds(obj)
        max_x = max(max_x, x + w + 1)
        max_y = max(max_y, y + h + 1)
    return max_x * settings["cellSize"] * scale, max_y * settings["cellSize"] * scale


def bounds(obj: dict[str, Any]) -> tuple[float, float, float, float]:
    if obj["type"] == "symbol":
        size = float(obj.get("size", 1))
        return obj["x"] - size / 2, obj["y"] - size / 2, size, size
    if obj["type"] == "text":
        size = float(obj.get("size", 1))
        width = obj.get("width", 0) or max(1.0, len(str(obj.get("text", ""))) * size * 0.55)
        height = obj.get("height", 0) or max(size, (str(obj.get("text", "")).count("\n") + 1) * size * 1.15)
        if obj.get("align") == "left" or obj.get("textRole") == "note":
            return obj["x"], obj["y"], width, height
        if obj.get("align") == "right":
            return obj["x"] - width, obj["y"], width, height
        return obj["x"] - width / 2, obj["y"], width, height
    if obj["type"] == "diagonal_corridor":
        thickness = float(obj.get("width", 1))
        x1, y1 = float(obj["x"]), float(obj["y"])
        x2, y2 = float(obj["x2"]), float(obj["y2"])
        return (
            min(x1, x2) - thickness / 2,
            min(y1, y2) - thickness / 2,
            abs(x2 - x1) + thickness,
            abs(y2 - y1) + thickness,
        )
    if obj["type"] == "shape":
        line_width = float(obj.get("lineWidth", 0.12))
        if obj.get("kind") == "line":
            x1, y1 = float(obj["x"]), float(obj["y"])
            x2, y2 = float(obj["x2"]), float(obj["y2"])
            if obj.get("curve", False):
                cx, cy = curved_line_control((x1, y1), (x2, y2))
                left, top = min(x1, x2, cx), min(y1, y2, cy)
                right, bottom = max(x1, x2, cx), max(y1, y2, cy)
            else:
                left, top = min(x1, x2), min(y1, y2)
                right, bottom = max(x1, x2), max(y1, y2)
            padding = max(0.15, line_width / 2)
            return left - padding, top - padding, right - left + padding * 2, bottom - top + padding * 2
        if obj.get("kind") == "polygon" and obj.get("points"):
            point_bounds = bounds_from_points(validate_shape_points(obj.get("points")))
            padding = max(0.0, line_width / 2)
            return point_bounds[0] - padding, point_bounds[1] - padding, point_bounds[2] + padding * 2, point_bounds[3] + padding * 2
        return obj["x"], obj["y"], obj["width"], obj["height"]
    return obj["x"], obj["y"], obj["width"], obj["height"]


def render_tk(
    canvas: tk.Canvas,
    project: dict[str, Any],
    zoom: float,
    selected_ids: set[str],
    primary_selected_id: str | None,
    draft: Draft | None,
    selection_box: tuple[float, float, float, float] | None,
    viewport: tuple[float, float, float, float] | None = None,
) -> None:
    settings = project["settings"]
    width, height = canvas_size(project, zoom)
    if project_layer_visible(project, "background"):
        canvas.create_rectangle(0, 0, width, height, fill=settings["backgroundColor"], outline="")
        draw_tk_grid(canvas, settings, zoom)
    else:
        canvas.create_rectangle(0, 0, width, height, fill="#f9fcfd", outline="")
    canvas._image_refs = []
    renderable_objects = []
    for obj in project["objects"]:
        if not should_render_object(project, obj, for_export=False):
            continue
        if viewport and obj.get("id") not in selected_ids and not rects_overlap(bounds(obj), viewport):
            continue
        renderable_objects.append(obj)
    draw_tk_floor_objects(canvas, settings, [obj for obj in renderable_objects if obj.get("type") in FLOOR_TYPES], zoom)
    for obj in renderable_objects:
        if obj.get("type") in FLOOR_TYPES:
            continue
        draw_tk_object(canvas, project, settings, obj, zoom)
    if draft:
        if draft.kind in SHAPE_TOOLS:
            draw_tk_shape(canvas, settings, shape_from_draft_data(draft, include_preview=True), zoom, dash=(4, 3))
        elif draft.kind == "corridor" and draft.x2 is not None and draft.y2 is not None and draft.x != draft.x2 and draft.y != draft.y2:
            draw_tk_diagonal_corridor(canvas, settings, {"x": draft.x, "y": draft.y, "x2": draft.x2, "y2": draft.y2, "width": 1}, zoom)
        elif draft.kind == "corridor" and draft.x2 is not None and draft.y2 is not None:
            draw_tk_rectlike(
                canvas,
                settings,
                {
                    "type": "corridor",
                    "x": min(draft.x, draft.x2),
                    "y": min(draft.y, draft.y2),
                    "width": max(0.25, abs(draft.x2 - draft.x)),
                    "height": max(0.25, abs(draft.y2 - draft.y)),
                },
                zoom,
                stipple="gray50",
            )
        else:
            draw_tk_rectlike(canvas, settings, draft.__dict__, zoom, stipple="gray50")
    selected_objects = [obj for obj in project["objects"] if obj["id"] in selected_ids and should_render_object(project, obj, for_export=False)]
    for obj in selected_objects:
        draw_tk_selection(canvas, settings, obj, zoom, show_handles=len(selected_objects) == 1 and obj["id"] == primary_selected_id)
    if len(selected_objects) > 1:
        box = union_bounds(selected_objects)
        if box:
            draw_tk_bounds(canvas, settings, box, zoom, dash=(4, 3))
    if selection_box:
        x1, y1, x2, y2 = selection_box
        c = settings["cellSize"] * zoom
        canvas.create_rectangle(x1 * c, y1 * c, x2 * c, y2 * c, outline=settings.get("selectionColor", SELECT), width=2, dash=(2, 2))


def draw_tk_grid(canvas: tk.Canvas, settings: dict[str, Any], zoom: float) -> None:
    c = settings["cellSize"] * zoom
    width = settings["width"] * c
    height = settings["height"] * c
    if settings.get("showSubGrid", True):
        step = normalize_snap_step(settings.get("snapStep", 1.0))
        if step < 1:
            sub = c * step
            color = soften_color(settings["backgroundColor"], 0.35)
            count_x = int(settings["width"] / step) + 1
            count_y = int(settings["height"] / step) + 1
            for index in range(count_x + 1):
                x = index * sub
                canvas.create_line(x, 0, x, height, fill=color)
            for index in range(count_y + 1):
                y = index * sub
                canvas.create_line(0, y, width, y, fill=color)
    if settings.get("showMainGrid", True):
        color = soften_color(settings["backgroundColor"], 0.55)
        for x in range(settings["width"] + 1):
            px = x * c
            canvas.create_line(px, 0, px, height, fill=color)
        for y in range(settings["height"] + 1):
            py = y * c
            canvas.create_line(0, py, width, py, fill=color)
    if settings.get("showCoordinates", False):
        draw_tk_coordinates(canvas, settings, zoom)


def grid_column_label(index: int) -> str:
    index = max(1, int(index))
    label = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        label = chr(ord("A") + remainder) + label
    return label


def draw_tk_coordinates(canvas: tk.Canvas, settings: dict[str, Any], zoom: float) -> None:
    c = settings["cellSize"] * zoom
    width = settings["width"] * c
    height = settings["height"] * c
    ink = settings.get("gridColor", BLUE)
    bg = soften_color(settings.get("backgroundColor", WHITE), 0.2)
    font_size = max(6, int(c * 0.38))
    font = ("Segoe UI", font_size, "bold")
    for column in range(settings["width"]):
        x = column * c + c / 2
        label = grid_column_label(column + 1)
        canvas.create_text(x, max(6, c * 0.28), text=label, fill=ink, font=font)
        canvas.create_text(x, height - max(6, c * 0.28), text=label, fill=ink, font=font)
    for row in range(settings["height"]):
        y = row * c + c / 2
        label = str(row + 1)
        canvas.create_text(max(8, c * 0.32), y, text=label, fill=ink, font=font)
        canvas.create_text(width - max(8, c * 0.32), y, text=label, fill=ink, font=font)
    canvas.create_rectangle(0, 0, width, height, outline=bg, width=max(1, int(c * 0.04)))


def draw_tk_zones(canvas: tk.Canvas, project: dict[str, Any], zoom: float) -> None:
    settings = project["settings"]
    if not settings.get("showZones", True):
        return
    c = settings["cellSize"] * zoom
    for zone in project.get("zones", []):
        if not zone.get("visible", True):
            continue
        x = zone["x"] * c
        y = zone["y"] * c
        w = zone["width"] * c
        h = zone["height"] * c
        color = zone.get("color") or settings.get("selectionColor", SELECT)
        canvas.create_rectangle(x, y, x + w, y + h, outline=color, width=max(1, int(c * 0.08)), dash=(6, 4))
        canvas.create_text(x + max(4, c * 0.25), y + max(8, c * 0.35), text=str(zone.get("name", "Zone")), anchor="w", fill=color, font=("Segoe UI", max(7, int(c * 0.42)), "bold"))


def draw_tk_markers(canvas: tk.Canvas, project: dict[str, Any], zoom: float) -> None:
    settings = project["settings"]
    c = settings["cellSize"] * zoom
    color = settings.get("selectionColor", SELECT)
    for marker in project.get("markers", []):
        x = marker["x"] * c
        y = marker["y"] * c
        r = max(5, c * 0.22)
        canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
        canvas.create_line(x - r * 1.4, y, x + r * 1.4, y, fill=color, width=2)
        canvas.create_line(x, y - r * 1.4, x, y + r * 1.4, fill=color, width=2)
        canvas.create_text(x + r * 1.6, y, text=str(marker.get("name", "Marker")), anchor="w", fill=color, font=("Segoe UI", max(7, int(c * 0.38)), "bold"))


def draw_tk_measure_overlay(canvas: tk.Canvas, settings: dict[str, Any], points: list[tuple[float, float]], preview: tuple[float, float] | None, zoom: float) -> None:
    live_points = list(points)
    if preview is not None and (not live_points or math.hypot(live_points[-1][0] - preview[0], live_points[-1][1] - preview[1]) > 0.000001):
        live_points.append(preview)
    if not live_points:
        return
    c = settings["cellSize"] * zoom
    color = settings.get("selectionColor", SELECT)
    px_points = [(x * c, y * c) for x, y in live_points]
    if len(px_points) >= 2:
        canvas.create_line(flatten_points(px_points), fill=color, width=max(2, int(c * 0.08)), dash=(5, 3))
    if len(px_points) >= 3:
        canvas.create_polygon(flatten_points(px_points), outline=color, fill="", width=max(1, int(c * 0.04)), dash=(3, 3))
    for index, (x, y) in enumerate(px_points, start=1):
        r = max(4, c * 0.14)
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="#17384a")
        canvas.create_text(x + r * 1.5, y - r * 1.5, text=str(index), fill="#17384a", font=("Segoe UI", max(7, int(c * 0.34)), "bold"))


def nice_ruler_cells(value: float) -> float:
    value = max(1.0, value)
    magnitude = 10 ** math.floor(math.log10(value))
    for step in (1, 2, 5, 10):
        candidate = step * magnitude
        if candidate >= value:
            return candidate
    return 10 * magnitude


def draw_tk_ruler_overlay(canvas: tk.Canvas, project: dict[str, Any], zoom: float, mouse_grid: tuple[float, float] | None, measure_points: list[tuple[float, float]]) -> None:
    settings = project["settings"]
    if not settings.get("showRuler", True):
        return
    c = settings["cellSize"] * zoom
    view_left = canvas.canvasx(0)
    view_bottom = canvas.canvasy(max(1, canvas.winfo_height()))
    pad = 10
    bar_cells = nice_ruler_cells(120 / max(1, c))
    bar_px = bar_cells * c
    x = view_left + pad
    y = view_bottom - 34
    bg = soften_color(settings.get("floorColor", WHITE), 0.1)
    ink = settings.get("gridColor", BLUE)
    text = f"{format_measure_value(bar_cells)} cells / {real_distance_label(bar_cells, settings)}"
    if mouse_grid:
        text += f" | {mouse_grid[0]:.2f},{mouse_grid[1]:.2f}"
    if len(measure_points) >= 2:
        text += " | " + measurement_summary(measure_points, settings).replace("measure | ", "")
    text_width = max(bar_px, 120, len(text) * 7)
    canvas.create_rectangle(x - 6, y - 18, x + text_width + 16, y + 12, fill=bg, outline=ink)
    canvas.create_line(x, y, x + bar_px, y, fill=ink, width=3)
    canvas.create_line(x, y - 5, x, y + 5, fill=ink, width=2)
    canvas.create_line(x + bar_px, y - 5, x + bar_px, y + 5, fill=ink, width=2)
    canvas.create_text(x, y - 12, text=text, anchor="w", fill=ink, font=("Segoe UI", 9, "bold"))


def draw_tk_bounds(canvas: tk.Canvas, settings: dict[str, Any], box: tuple[float, float, float, float], zoom: float, dash: tuple[int, int] = (6, 4)) -> None:
    x, y, w, h = box
    c = settings["cellSize"] * zoom
    canvas.create_rectangle(x * c - 4, y * c - 4, (x + w) * c + 4, (y + h) * c + 4, outline=settings.get("selectionColor", SELECT), width=2, dash=dash)


def draw_tk_selection(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], zoom: float, show_handles: bool) -> None:
    draw_tk_bounds(canvas, settings, bounds(obj), zoom)
    if not show_handles:
        return
    c = settings["cellSize"] * zoom
    size = HANDLE_PIXEL_SIZE
    for name, hx, hy in selection_handles(obj):
        px, py = hx * c, hy * c
        if name == "rotate":
            canvas.create_line(obj["x"] * c, obj["y"] * c, px, py, fill=settings.get("selectionColor", SELECT), width=2, dash=(3, 2))
            canvas.create_oval(px - size / 2, py - size / 2, px + size / 2, py + size / 2, fill=settings.get("selectionColor", SELECT), outline="#17384a")
        elif name.startswith("insert:"):
            half = size / 2
            canvas.create_polygon(px, py - half, px + half, py, px, py + half, px - half, py, fill=settings.get("selectionColor", SELECT), outline="#17384a")
            canvas.create_text(px, py, text="+", fill="#17384a", font=("Segoe UI", max(6, int(size)), "bold"))
        else:
            canvas.create_rectangle(px - size / 2, py - size / 2, px + size / 2, py + size / 2, fill=settings.get("selectionColor", SELECT), outline="#17384a")


def draw_tk_object(canvas: tk.Canvas, project: dict[str, Any], settings: dict[str, Any], obj: dict[str, Any], zoom: float) -> None:
    if obj["type"] in {"room", "corridor", "round", "cave"}:
        draw_tk_rectlike(canvas, settings, obj, zoom)
    elif obj["type"] == "diagonal_corridor":
        draw_tk_diagonal_corridor(canvas, settings, obj, zoom)
    elif obj["type"] == "symbol":
        c = settings["cellSize"] * zoom
        if is_custom_symbol(project, obj["kind"]):
            draw_tk_custom_symbol(canvas, project, obj, c, settings)
        else:
            draw_tk_builtin_symbol_rotated(canvas, project, obj, c, settings)
        draw_tk_rotation_indicator(canvas, obj, c, symbol_ink(settings, obj))
    elif obj["type"] == "text":
        c = settings["cellSize"] * zoom
        draw_tk_text(canvas, settings, obj, c)
    elif obj["type"] == "shape":
        draw_tk_shape(canvas, settings, obj, zoom)
    elif obj["type"] == "legend":
        draw_tk_legend_object(canvas, project, obj, zoom)


def draw_tk_shape(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], zoom: float, dash: tuple[int, int] | None = None) -> None:
    c = settings["cellSize"] * zoom
    opacity = shape_opacity(obj)
    ink = blend_color(obj.get("strokeColor") or settings["gridColor"], settings.get("backgroundColor", WHITE), opacity)
    fill = obj.get("fillColor") or ""
    if fill:
        fill = blend_color(fill, settings.get("backgroundColor", WHITE), opacity)
    width = max(1, int(float(obj.get("lineWidth", 0.12)) * c))
    options = {"outline": ink, "width": width}
    dash = dash or tk_shape_dash(obj)
    if dash:
        options["dash"] = dash
    kind = obj.get("kind")
    if kind == "line":
        line_options: dict[str, Any] = {"fill": ink, "width": width, "capstyle": "round", "smooth": bool(obj.get("curve", False))}
        if dash:
            line_options["dash"] = dash
        arrow = tk_arrow_value(obj)
        if arrow:
            line_options["arrow"] = arrow
            line_options["arrowshape"] = (max(8, width * 5), max(10, width * 6), max(3, width * 2))
        start = (obj["x"] * c, obj["y"] * c)
        end = (obj["x2"] * c, obj["y2"] * c)
        if obj.get("curve", False):
            control = curved_line_control(start, end)
            canvas.create_line(flatten_points([start, control, end]), **line_options)
        else:
            canvas.create_line(start[0], start[1], end[0], end[1], **line_options)
        return
    x, y = obj["x"] * c, obj["y"] * c
    w, h = obj["width"] * c, obj["height"] * c
    if kind == "circle":
        canvas.create_oval(x, y, x + w, y + h, fill=fill, **options)
    elif kind == "polygon":
        points = shape_polygon_points(obj, c)
        if obj.get("_open") or len(points) < 3:
            if len(points) >= 2:
                canvas.create_line(flatten_points(points), fill=ink, width=width, dash=dash, smooth=bool(obj.get("curve", False)))
            if points:
                fx, fy = points[0]
                radius = max(4, width + 3)
                canvas.create_oval(fx - radius, fy - radius, fx + radius, fy + radius, outline=ink, width=max(1, width), dash=dash)
            return
        if obj.get("curve", False):
            options["smooth"] = True
        canvas.create_polygon(flatten_points(points), fill=fill, **options)
    else:
        canvas.create_rectangle(x, y, x + w, y + h, fill=fill, **options)


def draw_tk_rotation_indicator(canvas: tk.Canvas, obj: dict[str, Any], cell: float, ink: str) -> None:
    rotation = float(obj.get("rotation", 0)) % 360
    if not rotation:
        return
    size = float(obj.get("size", 1)) * cell * 0.45
    angle = math.radians(rotation - 90)
    x, y = obj["x"] * cell, obj["y"] * cell
    canvas.create_line(x, y, x + math.cos(angle) * size, y + math.sin(angle) * size, fill=ink, width=max(1, int(cell * 0.08)), arrow="last")


def draw_tk_text(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], cell: float) -> None:
    align = obj.get("align", "center")
    anchor = {"left": "nw", "center": "n", "right": "ne"}.get(align, "n")
    x = obj["x"] * cell
    y = obj["y"] * cell
    width = obj.get("width", 0) * cell if obj.get("width", 0) else 0
    font = (obj.get("font") or settings.get("defaultTextFont", "Arial"), max(7, int(obj.get("size", 1) * cell)), "bold")
    fill = obj.get("color") or settings.get("textColor", settings["gridColor"])
    if obj.get("textRole") == "note" or not obj.get("export", True):
        fill = soften_color(fill, 0.25)
        canvas.create_rectangle(x - 3, y - 3, x + max(width, cell * 4), y + cell * 2.2, fill=soften_color(settings["floorColor"], 0.15), outline=fill, dash=(3, 2))
        anchor = "nw"
    options = {"text": obj.get("text", ""), "anchor": anchor, "fill": fill, "font": font, "justify": align if align in {"left", "center", "right"} else "center"}
    if width:
        options["width"] = width
    rotation = float(obj.get("rotation", 0)) % 360
    if rotation:
        options["angle"] = -rotation
    canvas.create_text(x, y, **options)


def styled_custom_symbol_image(image, obj: dict[str, Any], settings: dict[str, Any]):
    if Image is None or ImageDraw is None:
        return image
    padding = max(2, int(max(image.width, image.height) * 0.14))
    side_w = image.width + padding * 2
    side_h = image.height + padding * 2
    result = Image.new("RGBA", (side_w, side_h), (0, 0, 0, 0))
    left = padding
    top = padding
    if obj.get("shadow"):
        shadow = image_shadow(image, 0.35)
        offset = max(1, int(max(image.width, image.height) * 0.08))
        result.alpha_composite(shadow, (left + offset, top + offset))
    if obj.get("outline"):
        draw = ImageDraw.Draw(result)
        draw.rectangle((left - 1, top - 1, left + image.width + 1, top + image.height + 1), outline=symbol_outline_color(settings, obj), width=max(1, int(max(image.width, image.height) * 0.05)))
    result.alpha_composite(image_with_opacity(image, symbol_opacity(obj)), (left, top))
    return result


def draw_tk_custom_symbol(canvas: tk.Canvas, project: dict[str, Any], obj: dict[str, Any], cell: float, settings: dict[str, Any]) -> None:
    image = load_custom_symbol_image(project, obj["kind"], max(8, int(obj.get("size", 1) * cell)), float(obj.get("rotation", 0)), str(obj.get("variant", "")))
    x = obj["x"] * cell
    y = obj["y"] * cell
    if image is None:
        label = symbol_label(project, obj["kind"])[:2].upper()
        ink = symbol_ink(settings, obj)
        if obj.get("shadow"):
            canvas.create_rectangle(x - cell * 0.45 + cell * 0.08, y - cell * 0.45 + cell * 0.08, x + cell * 0.45 + cell * 0.08, y + cell * 0.45 + cell * 0.08, fill="#000000", outline="", stipple="gray50")
        if obj.get("outline"):
            canvas.create_rectangle(x - cell * 0.5, y - cell * 0.5, x + cell * 0.5, y + cell * 0.5, fill="", outline=symbol_outline_color(settings, obj), width=max(1, int(cell * 0.08)))
        canvas.create_rectangle(x - cell * 0.45, y - cell * 0.45, x + cell * 0.45, y + cell * 0.45, fill=settings["floorColor"], outline=ink, width=2)
        canvas.create_text(x, y, text=label, fill=ink, font=("Arial", max(8, int(cell * 0.6)), "bold"))
        return
    try:
        from PIL import ImageTk
    except ImportError:
        return
    image = styled_custom_symbol_image(image, obj, settings)
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(x, y, image=photo)
    refs = getattr(canvas, "_image_refs", [])
    refs.append(photo)
    canvas._image_refs = refs


def draw_tk_builtin_symbol_rotated(canvas: tk.Canvas, project: dict[str, Any], obj: dict[str, Any], cell: float, settings: dict[str, Any]) -> None:
    if Image is None or ImageDraw is None:
        x, y, size = obj["x"] * cell, obj["y"] * cell, obj.get("size", 1) * cell
        if obj.get("shadow"):
            draw_tk_symbol(canvas, effective_symbol_kind(project, obj), x + cell * 0.08, y + cell * 0.08, size, symbol_shadow_color(settings, obj), settings["floorColor"])
        if obj.get("outline"):
            draw_tk_symbol(canvas, effective_symbol_kind(project, obj), x, y, size * 1.12, symbol_outline_color(settings, obj), settings["floorColor"])
        draw_tk_symbol(canvas, effective_symbol_kind(project, obj), x, y, size, symbol_ink(settings, obj), settings["floorColor"])
        return
    size_px = max(8, int(obj.get("size", 1) * cell))
    side = max(16, int(size_px * 2.7))
    image = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = side / 2
    kind = effective_symbol_kind(project, obj)
    scale = max(1, int(cell / settings["cellSize"]))
    if obj.get("shadow"):
        offset = max(1, int(size_px * 0.08))
        draw_pillow_symbol(draw, kind, center + offset, center + offset, size_px, symbol_shadow_color(settings, obj), settings["floorColor"], scale)
    if obj.get("outline"):
        draw_pillow_symbol(draw, kind, center, center, size_px * 1.12, symbol_outline_color(settings, obj), settings["floorColor"], scale)
    draw_pillow_symbol(draw, kind, center, center, size_px, symbol_ink(settings, obj), settings["floorColor"], scale)
    image = image.rotate(-float(obj.get("rotation", 0)), resample=Image.Resampling.BICUBIC, expand=True)
    image = image_with_opacity(image, symbol_opacity(obj))
    try:
        from PIL import ImageTk
    except ImportError:
        return
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(obj["x"] * cell, obj["y"] * cell, image=photo)
    refs = getattr(canvas, "_image_refs", [])
    refs.append(photo)
    canvas._image_refs = refs


def draw_tk_legend_object(canvas: tk.Canvas, project: dict[str, Any], obj: dict[str, Any], zoom: float) -> None:
    settings = project["settings"]
    c = settings["cellSize"] * zoom
    x, y = obj["x"] * c, obj["y"] * c
    width, height = obj["width"] * c, obj["height"] * c
    ink = settings.get("legendColor", settings["gridColor"])
    canvas.create_rectangle(x, y, x + width, y + height, fill=settings["floorColor"], outline=ink, width=2)
    title_size = max(10, int(c * obj.get("scale", 1.0) * 1.1))
    canvas.create_text(x + c * 0.65, y + c * 0.8, text="LEGEND", anchor="w", fill=ink, font=("Arial", title_size, "bold"))
    entries = legend_entries(project, obj)
    columns = max(1, int(obj.get("columns", 4)))
    entry_w = max(c * 4, (width - c) / columns)
    entry_h = c * 1.15 * obj.get("scale", 1.0)
    for index, (kind, label) in enumerate(entries):
        col = index % columns
        row = index // columns
        ex = x + c * 0.65 + col * entry_w
        ey = y + c * 1.8 + row * entry_h
        if ey > y + height - c * 0.4:
            break
        if kind == "cell":
            canvas.create_rectangle(ex, ey - c * 0.35, ex + c * 0.7, ey + c * 0.35, fill=settings["floorColor"], outline=ink)
        elif kind == "manual":
            canvas.create_text(ex + c * 0.2, ey, text="•", anchor="w", fill=ink, font=("Arial", max(7, int(c * 0.7)), "bold"))
        elif is_custom_symbol(project, kind):
            draw_tk_custom_symbol(canvas, project, {"kind": kind, "x": (ex + c * 0.35) / c, "y": ey / c, "size": 0.75, "rotation": 0}, c, settings)
        else:
            draw_tk_symbol(canvas, kind, ex + c * 0.35, ey, c * 0.7, ink, settings["floorColor"])
        canvas.create_text(ex + c * 1.1, ey, text=label, anchor="w", fill=ink, font=("Arial", max(7, int(c * 0.55 * obj.get("scale", 1.0))), "bold"))


def draw_tk_floor_objects(canvas: tk.Canvas, settings: dict[str, Any], objects: list[dict[str, Any]], zoom: float) -> None:
    if not objects:
        return
    for obj in objects:
        draw_tk_floor_outline(canvas, settings, obj, zoom)
    for obj in objects:
        draw_tk_floor_fill(canvas, settings, obj, zoom)
    for obj in objects:
        draw_tk_floor_grid(canvas, settings, obj, zoom)


def draw_tk_floor_outline(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], zoom: float) -> None:
    c = settings["cellSize"] * zoom
    ink = settings["gridColor"]
    wall = max(1.0, c * max(0.02, coerce_float(obj.get("wallThickness"), 0.16)) / 2)
    obj_type = obj.get("type")
    if obj_type == "diagonal_corridor":
        x1, y1 = obj["x"] * c, obj["y"] * c
        x2, y2 = obj["x2"] * c, obj["y2"] * c
        thickness = max(3, int(obj.get("width", 1) * c))
        outline = thickness + max(2, int(c * max(0.02, coerce_float(obj.get("wallThickness"), 0.16))))
        canvas.create_polygon(flatten_points(corridor_polygon_points(x1, y1, x2, y2, outline)), fill=ink, outline="")
        return
    x, y = obj["x"] * c, obj["y"] * c
    w, h = obj["width"] * c, obj["height"] * c
    if obj_type == "round":
        canvas.create_oval(x - wall, y - wall, x + w + wall, y + h + wall, fill=ink, outline="")
    elif obj_type == "cave":
        points = cave_points(obj["x"], obj["y"], obj["width"], obj["height"], obj.get("seed", 1), c)
        canvas.create_line(flatten_points(points + [points[0]]), fill=ink, width=max(2, int(wall * 2)), smooth=True)
    else:
        canvas.create_rectangle(x - wall, y - wall, x + w + wall, y + h + wall, fill=ink, outline="")


def draw_tk_floor_fill(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], zoom: float) -> None:
    c = settings["cellSize"] * zoom
    floor = settings["floorColor"]
    obj_type = obj.get("type")
    if obj_type == "diagonal_corridor":
        canvas.create_polygon(flatten_points(floor_polygon_points(obj, c)), fill=floor, outline="")
        return
    x, y = obj["x"] * c, obj["y"] * c
    w, h = obj["width"] * c, obj["height"] * c
    if obj_type == "round":
        canvas.create_oval(x, y, x + w, y + h, fill=floor, outline="")
    elif obj_type == "cave":
        canvas.create_polygon(flatten_points(floor_polygon_points(obj, c)), fill=floor, outline="", smooth=True)
    else:
        canvas.create_rectangle(x, y, x + w, y + h, fill=floor, outline="")


def draw_tk_floor_grid(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], zoom: float) -> None:
    c = settings["cellSize"] * zoom
    for gx1, gy1, gx2, gy2 in orthogonal_grid_segments(floor_polygon_points(obj, c), c):
        canvas.create_line(gx1, gy1, gx2, gy2, fill=settings["gridColor"])


def draw_tk_rectlike(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], zoom: float, stipple: str = "") -> None:
    c = settings["cellSize"] * zoom
    x, y, w, h = obj["x"] * c, obj["y"] * c, obj["width"] * c, obj["height"] * c
    obj_type = obj.get("type", obj.get("kind"))
    if obj_type == "round":
        canvas.create_oval(x, y, x + w, y + h, fill=settings["floorColor"], outline=settings["gridColor"], width=2, stipple=stipple)
    elif obj_type == "cave":
        points = cave_points(obj["x"], obj["y"], obj["width"], obj["height"], obj.get("seed", 1), c)
        canvas.create_polygon(points, fill=settings["floorColor"], outline=settings["gridColor"], width=2, smooth=True, stipple=stipple)
    else:
        canvas.create_rectangle(x, y, x + w, y + h, fill=settings["floorColor"], outline=settings["gridColor"], stipple=stipple)
    for gx in range(int(obj["width"]) + 1):
        canvas.create_line(x + gx * c, y, x + gx * c, y + h, fill=settings["gridColor"])
    for gy in range(int(obj["height"]) + 1):
        canvas.create_line(x, y + gy * c, x + w, y + gy * c, fill=settings["gridColor"])


def draw_tk_diagonal_corridor(canvas: tk.Canvas, settings: dict[str, Any], obj: dict[str, Any], zoom: float) -> None:
    c = settings["cellSize"] * zoom
    x1, y1 = obj["x"] * c, obj["y"] * c
    x2, y2 = obj["x2"] * c, obj["y2"] * c
    thickness = max(3, int(obj.get("width", 1) * c))
    outline = thickness + max(2, int(c * max(0.02, coerce_float(obj.get("wallThickness"), 0.16))))
    outline_polygon = corridor_polygon_points(x1, y1, x2, y2, outline)
    floor_polygon = corridor_polygon_points(x1, y1, x2, y2, thickness)
    canvas.create_polygon(flatten_points(outline_polygon), fill=settings["gridColor"], outline="")
    canvas.create_polygon(flatten_points(floor_polygon), fill=settings["floorColor"], outline="")
    for gx1, gy1, gx2, gy2 in orthogonal_grid_segments(floor_polygon, c):
        canvas.create_line(gx1, gy1, gx2, gy2, fill=settings["gridColor"])


def draw_tk_symbol(canvas: tk.Canvas, kind: str, x: float, y: float, size: float, ink: str, floor: str) -> None:
    kind = normalize_symbol_kind(kind)
    s = size
    w = max(1, int(s * 0.12))
    if kind in DOOR_SYMBOLS:
        draw_tk_door(canvas, kind, x, y, s, ink, floor, w)
    elif kind in HAZARD_SYMBOLS:
        canvas.create_rectangle(x - s * 0.45, y - s * 0.45, x + s * 0.45, y + s * 0.45, outline=ink, width=w)
        if kind == "covered_pit":
            canvas.create_line(x - s * 0.32, y - s * 0.32, x + s * 0.32, y + s * 0.32, fill=ink, width=w)
            canvas.create_line(x + s * 0.32, y - s * 0.32, x - s * 0.32, y + s * 0.32, fill=ink, width=w)
        elif kind == "open_pit":
            canvas.create_rectangle(x - s * 0.25, y - s * 0.25, x + s * 0.25, y + s * 0.25, fill=ink, outline=ink)
        else:
            letters = {"trap": "T", "trap_ceiling": "C", "trap_floor": "F", "secret_trap_door": "S"}
            label = letters.get(kind, symbol_icon(kind).strip()[:2])
            canvas.create_text(x, y, text=label, fill=ink, font=("Arial", max(8, int(s * (0.62 if len(label) > 1 else 0.75))), "bold"))
    elif kind in {"stairs", "stair_slide_trap", "natural_stairs"}:
        for i in range(7):
            offset = i * s * 0.14
            canvas.create_line(x - s * 0.48 + offset, y - s * 0.42, x - s * 0.26 + offset, y + s * 0.42, fill=ink, width=w)
        if kind == "stair_slide_trap":
            canvas.create_line(x - s * 0.48, y + s * 0.45, x + s * 0.48, y + s * 0.45, fill=ink, width=w)
        if kind == "natural_stairs":
            canvas.create_arc(x - s * 0.5, y - s * 0.45, x + s * 0.5, y + s * 0.4, start=0, extent=180, outline=ink, width=w)
    elif kind == "spiral_stairs":
        for radius in (0.15, 0.3, 0.45):
            canvas.create_oval(x - s * radius, y - s * radius, x + s * radius, y + s * radius, outline=ink, width=w)
        canvas.create_line(x, y, x + s * 0.45, y, fill=ink, width=w)
    elif kind == "ladder":
        canvas.create_line(x - s * 0.25, y - s * 0.45, x - s * 0.25, y + s * 0.45, fill=ink, width=w)
        canvas.create_line(x + s * 0.25, y - s * 0.45, x + s * 0.25, y + s * 0.45, fill=ink, width=w)
        for i in range(5):
            yy = y - s * 0.35 + i * s * 0.18
            canvas.create_line(x - s * 0.25, yy, x + s * 0.25, yy, fill=ink, width=w)
    elif kind == "slide":
        canvas.create_line(x - s * 0.45, y, x + s * 0.35, y, fill=ink, width=w)
        canvas.create_line(x + s * 0.18, y - s * 0.18, x + s * 0.38, y, fill=ink, width=w)
        canvas.create_line(x + s * 0.18, y + s * 0.18, x + s * 0.38, y, fill=ink, width=w)
    elif kind in {"pillar", "rock_column"}:
        canvas.create_oval(x - s * 0.3, y - s * 0.3, x + s * 0.3, y + s * 0.3, fill=ink, outline=ink)
        if kind == "rock_column":
            canvas.create_text(x, y, text="×", fill=floor, font=("Arial", max(7, int(s * 0.7)), "bold"))
    elif kind == "statue":
        canvas.create_oval(x - s * 0.45, y - s * 0.45, x + s * 0.45, y + s * 0.45, outline=ink, width=w)
        canvas.create_text(x, y, text="*", fill=ink, font=("Arial", max(8, int(s)), "bold"))
    elif kind in {"fountain", "well"}:
        canvas.create_oval(x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42, outline=ink, width=w)
        canvas.create_oval(x - s * 0.18, y - s * 0.18, x + s * 0.18, y + s * 0.18, outline=ink, width=w)
        if kind == "fountain":
            canvas.create_arc(x - s * 0.25, y - s * 0.35, x + s * 0.25, y + s * 0.15, start=200, extent=140, outline=ink, width=w)
    elif kind in {"pool", "pool_lake", "stream", "curtain", "submerged_path"}:
        for i in range(3):
            yy = y - s * 0.25 + i * s * 0.25
            canvas.create_line(x - s * 0.42, yy, x - s * 0.15, yy + s * 0.08, x + s * 0.15, yy - s * 0.08, x + s * 0.42, yy, fill=ink, smooth=True, width=w)
    elif kind in {"dais", "teleporter"}:
        canvas.create_rectangle(x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42, outline=ink, width=w)
        canvas.create_rectangle(x - s * 0.25, y - s * 0.25, x + s * 0.25, y + s * 0.25, outline=ink, width=w)
        if kind == "teleporter":
            for i in range(9):
                px = x - s * 0.25 + (i % 3) * s * 0.25
                py = y - s * 0.25 + (i // 3) * s * 0.25
                canvas.create_rectangle(px, py, px + s * 0.08, py + s * 0.08, fill=ink, outline=ink)
    elif kind == "altar":
        canvas.create_rectangle(x - s * 0.2, y - s * 0.48, x + s * 0.2, y + s * 0.48, outline=ink, width=w)
        canvas.create_rectangle(x - s * 0.07, y - s * 0.22, x + s * 0.07, y - s * 0.08, fill=ink, outline=ink)
        canvas.create_rectangle(x - s * 0.07, y + s * 0.12, x + s * 0.07, y + s * 0.26, fill=ink, outline=ink)
    elif kind == "fireplace":
        canvas.create_rectangle(x - s * 0.38, y - s * 0.4, x + s * 0.38, y + s * 0.15, outline=ink, width=w)
        canvas.create_arc(x - s * 0.25, y - s * 0.15, x + s * 0.25, y + s * 0.45, start=0, extent=180, outline=ink, width=w)
    elif kind == "table_chest":
        canvas.create_rectangle(x - s * 0.45, y - s * 0.2, x - s * 0.05, y + s * 0.2, outline=ink, width=w)
        canvas.create_rectangle(x + s * 0.08, y - s * 0.18, x + s * 0.42, y + s * 0.18, outline=ink, width=w)
        canvas.create_line(x + s * 0.08, y, x + s * 0.42, y, fill=ink, width=w)
    elif kind == "bed":
        canvas.create_rectangle(x - s * 0.42, y - s * 0.25, x + s * 0.42, y + s * 0.25, outline=ink, width=w)
        canvas.create_line(x - s * 0.18, y - s * 0.25, x - s * 0.18, y + s * 0.25, fill=ink, width=w)
    elif kind in {"railing", "illusory_wall", "rock_wall", "subterranean_passage"}:
        if kind == "railing":
            for i in range(5):
                canvas.create_oval(x - s * 0.45 + i * s * 0.22, y - s * 0.06, x - s * 0.37 + i * s * 0.22, y + s * 0.06, fill=ink, outline=ink)
        elif kind == "illusory_wall":
            for i in range(4):
                canvas.create_line(x - s * 0.45 + i * s * 0.24, y, x - s * 0.32 + i * s * 0.24, y, fill=ink, width=w)
        elif kind == "subterranean_passage":
            canvas.create_rectangle(x - s * 0.45, y - s * 0.28, x + s * 0.45, y + s * 0.28, fill=ink, outline=ink, stipple="gray50")
        else:
            for i in range(5):
                yy = y - s * 0.3 + i * s * 0.15
                canvas.create_line(x - s * 0.45, yy, x + s * 0.45, yy, fill=ink, width=w)
    elif kind in {"stalactite", "stalagmite"}:
        if kind == "stalactite":
            points = (x - s * 0.35, y - s * 0.35, x + s * 0.35, y - s * 0.35, x, y + s * 0.35)
        else:
            points = (x - s * 0.35, y + s * 0.35, x + s * 0.35, y + s * 0.35, x, y - s * 0.35)
        canvas.create_polygon(points, outline=ink, fill=floor, width=w)
    elif kind in {"rubble", "depression"}:
        for i in range(9):
            angle = i * math.tau / 9
            radius = s * (0.15 + 0.3 * ((i % 3) / 2))
            canvas.create_oval(x + math.cos(angle) * radius - s * 0.05, y + math.sin(angle) * radius - s * 0.05, x + math.cos(angle) * radius + s * 0.05, y + math.sin(angle) * radius + s * 0.05, outline=ink, fill=ink if kind == "rubble" else floor)
    elif kind in {"crevasse", "sinkhole", "elevated_ledge", "natural_chimney"}:
        if kind == "sinkhole":
            for radius in (0.42, 0.27, 0.12):
                canvas.create_oval(x - s * radius, y - s * radius, x + s * radius, y + s * radius, outline=ink, width=w)
        elif kind == "natural_chimney":
            for i in range(8):
                angle = i * math.tau / 8
                canvas.create_line(x, y, x + math.cos(angle) * s * 0.42, y + math.sin(angle) * s * 0.42, fill=ink, width=w)
        elif kind == "elevated_ledge":
            canvas.create_line(x - s * 0.45, y - s * 0.1, x - s * 0.2, y + s * 0.25, x + s * 0.1, y + s * 0.1, x + s * 0.45, y + s * 0.3, fill=ink, width=w)
            canvas.create_line(x - s * 0.45, y - s * 0.25, x + s * 0.45, y - s * 0.05, fill=ink, width=w)
        else:
            canvas.create_line(x - s * 0.4, y - s * 0.4, x - s * 0.1, y - s * 0.1, x - s * 0.25, y + s * 0.2, x + s * 0.15, y, x + s * 0.4, y + s * 0.35, fill=ink, width=w)
    else:
        label = symbol_icon(kind).strip()[:2]
        canvas.create_oval(x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42, outline=ink, width=max(1, int(w * 0.8)))
        canvas.create_text(x, y, text=label, fill=ink, font=("Arial", max(8, int(s * (0.62 if len(label) > 1 else 0.76))), "bold"))


DOOR_SYMBOLS = {
    "door",
    "double_door",
    "secret_door",
    "one_way_door",
    "false_door",
    "locked_door",
    "archway",
    "concealed_door",
    "barred_door",
    "portcullis",
    "one_way_secret_door",
    "window",
    "arrow_slit",
    "open_door",
    "revolving_door",
    "archway_door",
    "magic_sealed_door",
    "cursed_door",
    "directional_portcullis",
    "broken_door",
    "heavy_stone_door",
    "illusion_passage",
    "revolving_wall",
    "collapse_barrier",
    "barricade",
    "force_barrier",
}

HAZARD_SYMBOLS = {
    "covered_pit",
    "open_pit",
    "trap",
    "trap_ceiling",
    "trap_floor",
    "secret_trap_door",
    "spear_trap",
    "arrow_trap",
    "blade_trap",
    "pendulum_blade",
    "fire_jet",
    "poison_gas_jet",
    "pressure_plate",
    "tripwire",
    "falling_block",
    "rolling_boulder",
    "trap_rune",
    "alarm_glyph",
    "teleport_trap",
    "collapse_hazard",
    "slippery_floor",
    "deep_chasm",
    "lava_field",
    "acid_pool",
}

def draw_tk_door(canvas: tk.Canvas, kind: str, x: float, y: float, s: float, ink: str, floor: str, w: int) -> None:
    canvas.create_rectangle(x - s * 0.48, y - s * 0.2, x + s * 0.48, y + s * 0.2, fill=floor, outline=ink, width=w)
    canvas.create_line(x - s * 0.48, y, x + s * 0.48, y, fill=ink, width=w)
    if kind == "door":
        canvas.create_rectangle(x - s * 0.16, y - s * 0.09, x + s * 0.16, y + s * 0.09, fill=floor, outline=ink, width=w)
    elif kind == "double_door":
        canvas.create_rectangle(x - s * 0.34, y - s * 0.09, x - s * 0.05, y + s * 0.09, fill=floor, outline=ink, width=w)
        canvas.create_rectangle(x + s * 0.05, y - s * 0.09, x + s * 0.34, y + s * 0.09, fill=floor, outline=ink, width=w)
    elif kind == "secret_door":
        canvas.create_text(x, y, text="S", fill=ink, font=("Arial", max(7, int(s * 0.55)), "bold"))
    elif kind == "one_way_door":
        canvas.create_polygon(x - s * 0.12, y - s * 0.02, x + s * 0.12, y - s * 0.02, x, y + s * 0.18, fill=ink, outline=ink)
    elif kind == "false_door":
        canvas.create_arc(x - s * 0.22, y - s * 0.05, x + s * 0.22, y + s * 0.25, start=0, extent=180, outline=ink, width=w)
    elif kind == "locked_door":
        canvas.create_rectangle(x - s * 0.13, y - s * 0.1, x + s * 0.13, y + s * 0.1, outline=ink, width=w)
        canvas.create_oval(x - s * 0.04, y - s * 0.04, x + s * 0.04, y + s * 0.04, fill=ink, outline=ink)
    elif kind in {"archway", "archway_door"}:
        canvas.create_line(x - s * 0.2, y - s * 0.12, x + s * 0.2, y - s * 0.12, fill=ink, width=w)
        canvas.create_line(x, y - s * 0.12, x, y + s * 0.16, fill=ink, width=w)
    elif kind == "concealed_door":
        canvas.create_text(x, y, text="C", fill=ink, font=("Arial", max(7, int(s * 0.55)), "bold"))
    elif kind == "barred_door":
        for offset in (-0.16, 0, 0.16):
            canvas.create_rectangle(x + s * offset - s * 0.04, y - s * 0.12, x + s * offset + s * 0.04, y + s * 0.12, fill=ink, outline=ink)
    elif kind == "portcullis":
        for offset in (-0.18, 0, 0.18):
            canvas.create_oval(x + s * offset - s * 0.035, y - s * 0.035, x + s * offset + s * 0.035, y + s * 0.035, fill=ink, outline=ink)
    elif kind == "one_way_secret_door":
        canvas.create_text(x - s * 0.12, y, text="S", fill=ink, font=("Arial", max(7, int(s * 0.45)), "bold"))
        canvas.create_polygon(x + s * 0.02, y - s * 0.04, x + s * 0.22, y - s * 0.04, x + s * 0.12, y + s * 0.14, fill=ink, outline=ink)
    elif kind == "window":
        canvas.create_rectangle(x - s * 0.25, y - s * 0.05, x + s * 0.25, y + s * 0.05, fill=ink, outline=ink)
    elif kind == "arrow_slit":
        canvas.create_polygon(x - s * 0.25, y - s * 0.1, x - s * 0.05, y + s * 0.1, x - s * 0.28, y + s * 0.1, fill=ink, outline=ink)
        canvas.create_polygon(x + s * 0.25, y - s * 0.1, x + s * 0.05, y + s * 0.1, x + s * 0.28, y + s * 0.1, fill=ink, outline=ink)
    elif kind == "open_door":
        canvas.create_line(x - s * 0.05, y, x + s * 0.25, y - s * 0.28, fill=ink, width=w)
    elif kind == "revolving_door":
        canvas.create_arc(x - s * 0.24, y - s * 0.24, x + s * 0.24, y + s * 0.24, start=20, extent=280, outline=ink, width=w)
        canvas.create_line(x, y, x + s * 0.22, y, fill=ink, width=w)
    else:
        label = symbol_icon(kind).strip()[:2]
        canvas.create_text(x, y, text=label, fill=ink, font=("Arial", max(7, int(s * 0.52)), "bold"))


def draw_tk_legend(canvas: tk.Canvas, project: dict[str, Any], zoom: float) -> None:
    settings = project["settings"]
    c = settings["cellSize"] * zoom
    x, y = c * 2, settings["height"] * c + c
    width, height = settings["width"] * c - c * 4, c * 5
    canvas.create_rectangle(x, y, x + width, y + height, fill=settings["floorColor"], outline=settings["gridColor"], width=2)
    canvas.create_text(x + c * 1.2, y + c * 1.55, text="LEGEND", anchor="w", fill=settings["gridColor"], font=("Arial", max(12, int(c * 1.4)), "bold"))
    used = []
    for obj in project["objects"]:
        if obj.get("type") == "symbol" and obj.get("kind") not in used:
            used.append(obj["kind"])
    entries = [("cell", cell_scale_label(settings))] + [(kind, SYMBOL_LABELS[kind]) for kind in used if kind in SYMBOL_LABELS]
    for index, (kind, label) in enumerate(entries[:12]):
        col, row = index % 4, index // 4
        ex, ey = x + c * 14 + col * c * 13, y + c * 1.35 + row * c * 1.55
        if kind == "cell":
            canvas.create_rectangle(ex, ey - c * 0.5, ex + c, ey + c * 0.5, fill=settings["floorColor"], outline=settings["gridColor"])
        else:
            draw_tk_symbol(canvas, kind, ex + c * 0.5, ey, c * 0.9, settings["gridColor"], settings["floorColor"])
        canvas.create_text(ex + c * 1.6, ey, text=label, anchor="w", fill=settings["gridColor"], font=("Arial", max(7, int(c * 0.78)), "bold"))


def render_pillow(draw, project: dict[str, Any], scale: int, selected_id: str | None, draft: Draft | None, include_legend: bool | None = None) -> None:
    settings = project["settings"]
    if project_layer_visible(project, "background") and settings.get("exportGrid", True):
        draw_pillow_grid(draw, settings, scale)
    renderable_objects = []
    for obj in project["objects"]:
        if not should_render_object(project, obj, for_export=True):
            continue
        if obj.get("type") == "legend" and include_legend is False:
            continue
        renderable_objects.append(obj)
    draw_pillow_floor_objects(draw, settings, [obj for obj in renderable_objects if obj.get("type") in FLOOR_TYPES], scale)
    for obj in renderable_objects:
        if obj.get("type") in FLOOR_TYPES:
            continue
        draw_pillow_object(draw, project, settings, obj, scale)


def draw_pillow_grid(draw, settings: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    width = settings["width"] * cell
    height = settings["height"] * cell
    if settings.get("showSubGrid", True):
        step = normalize_snap_step(settings.get("snapStep", 1.0))
        if step < 1:
            sub = cell * step
            color = soften_color(settings["backgroundColor"], 0.35)
            for index in range(int(settings["width"] / step) + 2):
                x = index * sub
                draw.line((x, 0, x, height), fill=color, width=max(1, scale))
            for index in range(int(settings["height"] / step) + 2):
                y = index * sub
                draw.line((0, y, width, y), fill=color, width=max(1, scale))
    if settings.get("showMainGrid", True):
        color = soften_color(settings["backgroundColor"], 0.55)
        for index in range(settings["width"] + 1):
            x = index * cell
            draw.line((x, 0, x, height), fill=color, width=max(1, scale))
        for index in range(settings["height"] + 1):
            y = index * cell
            draw.line((0, y, width, y), fill=color, width=max(1, scale))
    if settings.get("showCoordinates", False):
        draw_pillow_coordinates(draw, settings, scale)


def draw_pillow_coordinates(draw, settings: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    width = settings["width"] * cell
    height = settings["height"] * cell
    ink = settings.get("gridColor", BLUE)
    font = get_font(max(7, int(cell * 0.38)))
    for column in range(settings["width"]):
        x = column * cell + cell / 2
        label = grid_column_label(column + 1)
        draw.text((x, max(6, cell * 0.28)), label, fill=ink, font=font, anchor="mm")
        draw.text((x, height - max(6, cell * 0.28)), label, fill=ink, font=font, anchor="mm")
    for row in range(settings["height"]):
        y = row * cell + cell / 2
        label = str(row + 1)
        draw.text((max(8, cell * 0.32), y), label, fill=ink, font=font, anchor="mm")
        draw.text((width - max(8, cell * 0.32), y), label, fill=ink, font=font, anchor="mm")


def draw_pillow_floor_objects(draw, settings: dict[str, Any], objects: list[dict[str, Any]], scale: int) -> None:
    if not objects:
        return
    for obj in objects:
        draw_pillow_floor_outline(draw, settings, obj, scale)
    for obj in objects:
        draw_pillow_floor_fill(draw, settings, obj, scale)
    for obj in objects:
        draw_pillow_floor_grid(draw, settings, obj, scale)


def draw_pillow_floor_outline(draw, settings: dict[str, Any], obj: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    ink = settings["gridColor"]
    wall = max(1, int(cell * max(0.02, coerce_float(obj.get("wallThickness"), 0.16)) / 2))
    obj_type = obj.get("type")
    if obj_type == "diagonal_corridor":
        x1, y1 = obj["x"] * cell, obj["y"] * cell
        x2, y2 = obj["x2"] * cell, obj["y2"] * cell
        thickness = max(3, int(obj.get("width", 1) * cell))
        outline = thickness + max(2, int(cell * max(0.02, coerce_float(obj.get("wallThickness"), 0.16))))
        draw.polygon(corridor_polygon_points(x1, y1, x2, y2, outline), fill=ink)
        return
    x, y = obj["x"] * cell, obj["y"] * cell
    w, h = obj["width"] * cell, obj["height"] * cell
    if obj_type == "round":
        draw.ellipse((x - wall, y - wall, x + w + wall, y + h + wall), fill=ink)
    elif obj_type == "cave":
        points = floor_polygon_points(obj, cell)
        draw.line(points + [points[0]], fill=ink, width=max(1, wall * 2), joint="curve")
    else:
        draw.rectangle((x - wall, y - wall, x + w + wall, y + h + wall), fill=ink)


def draw_pillow_floor_fill(draw, settings: dict[str, Any], obj: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    floor = settings["floorColor"]
    obj_type = obj.get("type")
    if obj_type == "diagonal_corridor":
        draw.polygon(floor_polygon_points(obj, cell), fill=floor)
        return
    x, y = obj["x"] * cell, obj["y"] * cell
    w, h = obj["width"] * cell, obj["height"] * cell
    if obj_type == "round":
        draw.ellipse((x, y, x + w, y + h), fill=floor)
    elif obj_type == "cave":
        draw.polygon(floor_polygon_points(obj, cell), fill=floor)
    else:
        draw.rectangle((x, y, x + w, y + h), fill=floor)


def draw_pillow_floor_grid(draw, settings: dict[str, Any], obj: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    for gx1, gy1, gx2, gy2 in orthogonal_grid_segments(floor_polygon_points(obj, cell), cell):
        draw.line((gx1, gy1, gx2, gy2), fill=settings["gridColor"], width=max(1, scale))


def draw_pillow_object(draw, project: dict[str, Any], settings: dict[str, Any], obj: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    ink, floor = settings["gridColor"], settings["floorColor"]
    if obj["type"] in {"room", "corridor", "round", "cave"}:
        x, y, w, h = obj["x"] * cell, obj["y"] * cell, obj["width"] * cell, obj["height"] * cell
        if obj["type"] == "round":
            draw.ellipse((x, y, x + w, y + h), fill=floor, outline=ink, width=max(1, scale * 2))
        elif obj["type"] == "cave":
            points = cave_points(obj["x"], obj["y"], obj["width"], obj["height"], obj.get("seed", 1), cell)
            draw.polygon(points, fill=floor)
            draw.line(points + [points[0]], fill=ink, width=max(1, scale * 2))
        else:
            draw.rectangle((x, y, x + w, y + h), fill=floor, outline=ink, width=max(1, scale))
        for gx in range(int(obj["width"]) + 1):
            draw.line((x + gx * cell, y, x + gx * cell, y + h), fill=ink, width=max(1, scale))
        for gy in range(int(obj["height"]) + 1):
            draw.line((x, y + gy * cell, x + w, y + gy * cell), fill=ink, width=max(1, scale))
    elif obj["type"] == "diagonal_corridor":
        draw_pillow_diagonal_corridor(draw, settings, obj, scale)
    elif obj["type"] == "symbol":
        if is_custom_symbol(project, obj["kind"]):
            draw_pillow_custom_symbol(draw, project, obj, cell, settings)
        else:
            draw_pillow_symbol_object(draw, project, obj, cell, settings, scale)
        draw_pillow_rotation_indicator(draw, obj, cell, symbol_ink(settings, obj), scale)
    elif obj["type"] == "text":
        draw_pillow_text(draw, settings, obj, cell)
    elif obj["type"] == "shape":
        draw_pillow_shape(draw, settings, obj, scale)
    elif obj["type"] == "legend":
        draw_pillow_legend_object(draw, project, obj, scale)


def draw_pillow_styled_line(draw, points: list[tuple[float, float]], fill: str, width: int, style: str, closed: bool = False) -> None:
    if len(points) < 2:
        return
    segments = list(zip(points, points[1:]))
    if closed:
        segments.append((points[-1], points[0]))
    if style == "solid":
        line_points = points + ([points[0]] if closed else [])
        draw.line(line_points, fill=fill, width=width, joint="curve")
        return
    dash_length = max(width, 2) if style == "dot" else max(width * 4, 4)
    gap_length = max(width * 3, 4) if style == "dot" else max(width * 2, 3)
    for start, end in segments:
        sx, sy = start
        ex, ey = end
        length = math.hypot(ex - sx, ey - sy)
        if length <= 0:
            continue
        ux, uy = (ex - sx) / length, (ey - sy) / length
        distance = 0.0
        while distance < length:
            current = min(dash_length, length - distance)
            x1, y1 = sx + ux * distance, sy + uy * distance
            x2, y2 = sx + ux * (distance + current), sy + uy * (distance + current)
            if style == "dot":
                radius = max(1, width / 2)
                draw.ellipse((x1 - radius, y1 - radius, x1 + radius, y1 + radius), fill=fill)
            else:
                draw.line((x1, y1, x2, y2), fill=fill, width=width)
            distance += dash_length + gap_length


def draw_pillow_arrowhead(draw, tail: tuple[float, float], tip: tuple[float, float], fill: str, width: int) -> None:
    size = max(width * 4, 8)
    draw.polygon(svg_arrowhead_points(tail, tip, size), fill=fill)


def draw_pillow_shape(draw, settings: dict[str, Any], obj: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    opacity = shape_opacity(obj)
    ink = blend_color(obj.get("strokeColor") or settings["gridColor"], settings.get("backgroundColor", WHITE), opacity)
    fill = obj.get("fillColor") or None
    if fill:
        fill = blend_color(fill, settings.get("backgroundColor", WHITE), opacity)
    width = max(1, int(float(obj.get("lineWidth", 0.12)) * cell))
    style = shape_line_style(obj)
    kind = obj.get("kind")
    if kind == "line":
        start = (obj["x"] * cell, obj["y"] * cell)
        end = (obj["x2"] * cell, obj["y2"] * cell)
        points = quadratic_curve_points(start, curved_line_control(start, end), end) if obj.get("curve", False) else [start, end]
        draw_pillow_styled_line(draw, points, ink, width, style)
        arrow = shape_arrow_style(obj)
        if arrow in {"start", "both"}:
            draw_pillow_arrowhead(draw, end, start, ink, width)
        if arrow in {"end", "both"}:
            draw_pillow_arrowhead(draw, start, end, ink, width)
        return
    x, y = obj["x"] * cell, obj["y"] * cell
    w, h = obj["width"] * cell, obj["height"] * cell
    if kind == "circle":
        draw.ellipse((x, y, x + w, y + h), fill=fill, outline=ink, width=width)
    elif kind == "polygon":
        points = shape_polygon_points(obj, cell)
        draw.polygon(points, fill=fill)
        draw_pillow_styled_line(draw, points, ink, width, style, closed=True)
    else:
        draw.rectangle((x, y, x + w, y + h), fill=fill, outline=ink, width=width)


def draw_pillow_rotation_indicator(draw, obj: dict[str, Any], cell: float, ink: str, scale: int) -> None:
    rotation = float(obj.get("rotation", 0)) % 360
    if not rotation:
        return
    size = float(obj.get("size", 1)) * cell * 0.45
    angle = math.radians(rotation - 90)
    x, y = obj["x"] * cell, obj["y"] * cell
    x2, y2 = x + math.cos(angle) * size, y + math.sin(angle) * size
    draw.line((x, y, x2, y2), fill=ink, width=max(1, scale * 2))
    head = max(3, scale * 4)
    draw.ellipse((x2 - head, y2 - head, x2 + head, y2 + head), fill=ink)


def draw_pillow_symbol_rotated(draw, kind: str, x: float, y: float, s: float, ink: str, floor: str, scale: int, rotation: float) -> None:
    if abs(rotation % 360) < 0.01:
        draw_pillow_symbol(draw, kind, x, y, s, ink, floor, scale)
        return
    side = max(8, int(s * 2.4))
    temp = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp)
    draw_pillow_symbol(temp_draw, kind, side / 2, side / 2, s, ink, floor, scale)
    rotated = temp.rotate(-rotation, resample=Image.Resampling.BICUBIC, expand=True)
    paste_image_onto_draw(draw, rotated, x, y)


def draw_pillow_symbol_object(draw, project: dict[str, Any], obj: dict[str, Any], cell: float, settings: dict[str, Any], scale: int) -> None:
    x = obj["x"] * cell
    y = obj["y"] * cell
    size = obj.get("size", 1) * cell
    kind = effective_symbol_kind(project, obj)
    if getattr(draw, "_target_image", None) is None:
        if obj.get("shadow"):
            offset = max(1, int(size * 0.08))
            draw_pillow_symbol(draw, kind, x + offset, y + offset, size, symbol_shadow_color(settings, obj), settings["floorColor"], scale)
        if obj.get("outline"):
            draw_pillow_symbol(draw, kind, x, y, size * 1.12, symbol_outline_color(settings, obj), settings["floorColor"], scale)
        ink = blend_color(symbol_ink(settings, obj), settings.get("backgroundColor", WHITE), symbol_opacity(obj))
        draw_pillow_symbol(draw, kind, x, y, size, ink, settings["floorColor"], scale)
        return
    side = max(16, int(size * 2.7))
    temp = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp)
    center = side / 2
    if obj.get("shadow"):
        offset = max(1, int(size * 0.08))
        draw_pillow_symbol(temp_draw, kind, center + offset, center + offset, size, symbol_shadow_color(settings, obj), settings["floorColor"], scale)
    if obj.get("outline"):
        draw_pillow_symbol(temp_draw, kind, center, center, size * 1.12, symbol_outline_color(settings, obj), settings["floorColor"], scale)
    draw_pillow_symbol(temp_draw, kind, center, center, size, symbol_ink(settings, obj), settings["floorColor"], scale)
    rotation = float(obj.get("rotation", 0))
    if abs(rotation % 360) >= 0.01:
        temp = temp.rotate(-rotation, resample=Image.Resampling.BICUBIC, expand=True)
    temp = image_with_opacity(temp, symbol_opacity(obj))
    paste_image_onto_draw(draw, temp, x, y)


def draw_pillow_custom_symbol(draw, project: dict[str, Any], obj: dict[str, Any], cell: float, settings: dict[str, Any]) -> None:
    image = load_custom_symbol_image(project, obj["kind"], max(8, int(obj.get("size", 1) * cell)), float(obj.get("rotation", 0)), str(obj.get("variant", "")))
    x = obj["x"] * cell
    y = obj["y"] * cell
    if image is None:
        label = symbol_label(project, obj["kind"])[:2].upper()
        ink = symbol_ink(settings, obj)
        if obj.get("shadow"):
            offset = cell * 0.08
            draw.rectangle((x - cell * 0.45 + offset, y - cell * 0.45 + offset, x + cell * 0.45 + offset, y + cell * 0.45 + offset), fill=blend_color("#000000", settings.get("backgroundColor", WHITE), 0.35))
        if obj.get("outline"):
            draw.rectangle((x - cell * 0.5, y - cell * 0.5, x + cell * 0.5, y + cell * 0.5), outline=symbol_outline_color(settings, obj), width=max(1, int(cell * 0.08)))
        draw.rectangle((x - cell * 0.45, y - cell * 0.45, x + cell * 0.45, y + cell * 0.45), fill=settings["floorColor"], outline=ink, width=max(1, int(cell * 0.08)))
        draw.text((x, y), label, fill=ink, font=get_font(max(8, int(cell * 0.6))), anchor="mm")
        return
    image = styled_custom_symbol_image(image, obj, settings)
    paste_image_onto_draw(draw, image, x, y)


def draw_pillow_text(draw, settings: dict[str, Any], obj: dict[str, Any], cell: float) -> None:
    font = get_font(max(8, int(obj.get("size", 1) * cell)))
    fill = obj.get("color") or settings.get("textColor", settings["gridColor"])
    x, y = obj["x"] * cell, obj["y"] * cell
    width = obj.get("width", 0) * cell if obj.get("width", 0) else 0
    text = str(obj.get("text", ""))
    rotation = float(obj.get("rotation", 0)) % 360
    if rotation and getattr(draw, "_target_image", None) is not None:
        lines = wrap_text_for_draw(text, font, width) if width else text.splitlines() or [text]
        line_height = max(8, int(obj.get("size", 1) * cell * 1.15))
        text_width = max(1, int(max(text_measure(draw, line, font) for line in lines)))
        text_height = max(1, line_height * len(lines))
        temp = Image.new("RGBA", (text_width + 12, text_height + 12), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        for index, line in enumerate(lines):
            temp_draw.text((6, 6 + index * line_height), line, fill=fill, font=font, anchor="la")
        rotated = temp.rotate(-rotation, resample=Image.Resampling.BICUBIC, expand=True)
        paste_image_onto_draw(draw, rotated, x, y + text_height / 2)
        return
    if width:
        lines = wrap_text_for_draw(text, font, width)
        line_height = max(8, int(obj.get("size", 1) * cell * 1.15))
        for index, line in enumerate(lines):
            line_x = aligned_text_x(draw, line, font, x, width, obj.get("align", "center"))
            draw.text((line_x, y + index * line_height), line, fill=fill, font=font, anchor="la")
    else:
        anchor = {"left": "la", "center": "ma", "right": "ra"}.get(obj.get("align", "center"), "ma")
        draw.text((x, y), text, fill=fill, font=font, anchor=anchor)


def draw_pillow_legend_object(draw, project: dict[str, Any], obj: dict[str, Any], scale: int) -> None:
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    x, y = obj["x"] * cell, obj["y"] * cell
    width, height = obj["width"] * cell, obj["height"] * cell
    ink, floor = settings.get("legendColor", settings["gridColor"]), settings["floorColor"]
    draw.rectangle((x, y, x + width, y + height), fill=floor, outline=ink, width=max(1, scale * 2))
    draw.text((x + cell * 0.65, y + cell * 0.8), "LEGEND", fill=ink, font=get_font(max(12, int(cell * obj.get("scale", 1.0) * 1.1))), anchor="lm")
    entries = legend_entries(project, obj)
    columns = max(1, int(obj.get("columns", 4)))
    entry_w = max(cell * 4, (width - cell) / columns)
    entry_h = cell * 1.15 * obj.get("scale", 1.0)
    for index, (kind, label) in enumerate(entries):
        col = index % columns
        row = index // columns
        ex = x + cell * 0.65 + col * entry_w
        ey = y + cell * 1.8 + row * entry_h
        if ey > y + height - cell * 0.4:
            break
        if kind == "cell":
            draw.rectangle((ex, ey - cell * 0.35, ex + cell * 0.7, ey + cell * 0.35), fill=floor, outline=ink, width=max(1, scale))
        elif kind == "manual":
            draw.text((ex + cell * 0.2, ey), "•", fill=ink, font=get_font(max(8, int(cell * 0.7))), anchor="lm")
        elif is_custom_symbol(project, kind):
            draw_pillow_custom_symbol(draw, project, {"kind": kind, "x": (ex + cell * 0.35) / cell, "y": ey / cell, "size": 0.75, "rotation": 0}, cell, settings)
        else:
            draw_pillow_symbol(draw, kind, ex + cell * 0.35, ey, cell * 0.7, ink, floor, scale)
        draw.text((ex + cell * 1.1, ey), label, fill=ink, font=get_font(max(7, int(cell * 0.55 * obj.get("scale", 1.0)))), anchor="lm")


def draw_pillow_diagonal_corridor(draw, settings: dict[str, Any], obj: dict[str, Any], scale: int) -> None:
    cell = settings["cellSize"] * scale
    x1, y1 = obj["x"] * cell, obj["y"] * cell
    x2, y2 = obj["x2"] * cell, obj["y2"] * cell
    thickness = max(3, int(obj.get("width", 1) * cell))
    outline = thickness + max(2, int(cell * max(0.02, coerce_float(obj.get("wallThickness"), 0.16))))
    outline_polygon = corridor_polygon_points(x1, y1, x2, y2, outline)
    floor_polygon = corridor_polygon_points(x1, y1, x2, y2, thickness)
    draw.polygon(outline_polygon, fill=settings["gridColor"])
    draw.polygon(floor_polygon, fill=settings["floorColor"])
    for gx1, gy1, gx2, gy2 in orthogonal_grid_segments(floor_polygon, cell):
        draw.line((gx1, gy1, gx2, gy2), fill=settings["gridColor"], width=max(1, scale))


def draw_pillow_symbol(draw, kind: str, x: float, y: float, s: float, ink: str, floor: str, scale: int) -> None:
    kind = normalize_symbol_kind(kind)
    width = max(1, scale * 2)
    if kind in DOOR_SYMBOLS:
        draw_pillow_door(draw, kind, x, y, s, ink, floor, width)
    elif kind in HAZARD_SYMBOLS:
        draw.rectangle((x - s * 0.45, y - s * 0.45, x + s * 0.45, y + s * 0.45), outline=ink, width=width)
        if kind == "covered_pit":
            draw.line((x - s * 0.32, y - s * 0.32, x + s * 0.32, y + s * 0.32), fill=ink, width=width)
            draw.line((x + s * 0.32, y - s * 0.32, x - s * 0.32, y + s * 0.32), fill=ink, width=width)
        elif kind == "open_pit":
            draw.rectangle((x - s * 0.25, y - s * 0.25, x + s * 0.25, y + s * 0.25), fill=ink)
        else:
            letters = {"trap": "T", "trap_ceiling": "C", "trap_floor": "F", "secret_trap_door": "S"}
            label = letters.get(kind, symbol_icon(kind).strip()[:2])
            draw.text((x, y), label, fill=ink, font=get_font(max(8, int(s * (0.62 if len(label) > 1 else 0.75)))), anchor="mm")
    elif kind in {"stairs", "stair_slide_trap", "natural_stairs"}:
        for i in range(7):
            draw.line((x - s * 0.55 + i * s * 0.16, y - s * 0.45, x - s * 0.3 + i * s * 0.16, y + s * 0.45), fill=ink, width=width)
        if kind == "stair_slide_trap":
            draw.line((x - s * 0.48, y + s * 0.45, x + s * 0.48, y + s * 0.45), fill=ink, width=width)
        if kind == "natural_stairs":
            draw.arc((x - s * 0.5, y - s * 0.45, x + s * 0.5, y + s * 0.4), 0, 180, fill=ink, width=width)
    elif kind == "spiral_stairs":
        for radius in (0.15, 0.3, 0.45):
            draw.ellipse((x - s * radius, y - s * radius, x + s * radius, y + s * radius), outline=ink, width=width)
        draw.line((x, y, x + s * 0.45, y), fill=ink, width=width)
    elif kind == "ladder":
        draw.line((x - s * 0.25, y - s * 0.45, x - s * 0.25, y + s * 0.45), fill=ink, width=width)
        draw.line((x + s * 0.25, y - s * 0.45, x + s * 0.25, y + s * 0.45), fill=ink, width=width)
        for i in range(5):
            yy = y - s * 0.35 + i * s * 0.18
            draw.line((x - s * 0.25, yy, x + s * 0.25, yy), fill=ink, width=width)
    elif kind == "slide":
        draw.line((x - s * 0.45, y, x + s * 0.35, y), fill=ink, width=width)
        draw.line((x + s * 0.18, y - s * 0.18, x + s * 0.38, y, x + s * 0.18, y + s * 0.18), fill=ink, width=width)
    elif kind in {"pillar", "rock_column"}:
        draw.ellipse((x - s * 0.3, y - s * 0.3, x + s * 0.3, y + s * 0.3), fill=ink)
    elif kind == "statue":
        draw.ellipse((x - s * 0.45, y - s * 0.45, x + s * 0.45, y + s * 0.45), outline=ink, width=width)
        draw.text((x, y), "*", fill=ink, font=get_font(max(8, int(s))), anchor="mm")
    elif kind in {"fountain", "well"}:
        draw.ellipse((x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42), outline=ink, width=width)
        draw.ellipse((x - s * 0.18, y - s * 0.18, x + s * 0.18, y + s * 0.18), outline=ink, width=width)
    elif kind in {"pool", "pool_lake", "stream", "curtain", "submerged_path"}:
        for i in range(3):
            yy = y - s * 0.25 + i * s * 0.25
            draw.line((x - s * 0.42, yy, x - s * 0.15, yy + s * 0.08, x + s * 0.15, yy - s * 0.08, x + s * 0.42, yy), fill=ink, width=width)
    elif kind in {"dais", "teleporter"}:
        draw.rectangle((x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42), outline=ink, width=width)
        draw.rectangle((x - s * 0.25, y - s * 0.25, x + s * 0.25, y + s * 0.25), outline=ink, width=width)
        if kind == "teleporter":
            for i in range(9):
                px = x - s * 0.25 + (i % 3) * s * 0.25
                py = y - s * 0.25 + (i // 3) * s * 0.25
                draw.rectangle((px, py, px + s * 0.08, py + s * 0.08), fill=ink)
    elif kind == "altar":
        draw.rectangle((x - s * 0.2, y - s * 0.48, x + s * 0.2, y + s * 0.48), outline=ink, width=width)
        draw.rectangle((x - s * 0.07, y - s * 0.22, x + s * 0.07, y - s * 0.08), fill=ink)
        draw.rectangle((x - s * 0.07, y + s * 0.12, x + s * 0.07, y + s * 0.26), fill=ink)
    elif kind == "fireplace":
        draw.rectangle((x - s * 0.38, y - s * 0.4, x + s * 0.38, y + s * 0.15), outline=ink, width=width)
        draw.arc((x - s * 0.25, y - s * 0.15, x + s * 0.25, y + s * 0.45), 0, 180, fill=ink, width=width)
    elif kind == "table_chest":
        draw.rectangle((x - s * 0.45, y - s * 0.2, x - s * 0.05, y + s * 0.2), outline=ink, width=width)
        draw.rectangle((x + s * 0.08, y - s * 0.18, x + s * 0.42, y + s * 0.18), outline=ink, width=width)
        draw.line((x + s * 0.08, y, x + s * 0.42, y), fill=ink, width=width)
    elif kind == "bed":
        draw.rectangle((x - s * 0.42, y - s * 0.25, x + s * 0.42, y + s * 0.25), outline=ink, width=width)
        draw.line((x - s * 0.18, y - s * 0.25, x - s * 0.18, y + s * 0.25), fill=ink, width=width)
    elif kind in {"railing", "illusory_wall", "rock_wall", "subterranean_passage"}:
        if kind == "railing":
            for i in range(5):
                draw.ellipse((x - s * 0.45 + i * s * 0.22, y - s * 0.06, x - s * 0.37 + i * s * 0.22, y + s * 0.06), fill=ink)
        elif kind == "illusory_wall":
            for i in range(4):
                draw.line((x - s * 0.45 + i * s * 0.24, y, x - s * 0.32 + i * s * 0.24, y), fill=ink, width=width)
        elif kind == "subterranean_passage":
            draw.rectangle((x - s * 0.45, y - s * 0.28, x + s * 0.45, y + s * 0.28), fill=ink)
        else:
            for i in range(5):
                yy = y - s * 0.3 + i * s * 0.15
                draw.line((x - s * 0.45, yy, x + s * 0.45, yy), fill=ink, width=width)
    elif kind in {"stalactite", "stalagmite"}:
        points = (
            [(x - s * 0.35, y - s * 0.35), (x + s * 0.35, y - s * 0.35), (x, y + s * 0.35)]
            if kind == "stalactite"
            else [(x - s * 0.35, y + s * 0.35), (x + s * 0.35, y + s * 0.35), (x, y - s * 0.35)]
        )
        draw.polygon(points, fill=floor, outline=ink)
    elif kind in {"rubble", "depression"}:
        for i in range(9):
            angle = i * math.tau / 9
            radius = s * (0.15 + 0.3 * ((i % 3) / 2))
            px, py = x + math.cos(angle) * radius, y + math.sin(angle) * radius
            draw.ellipse((px - s * 0.05, py - s * 0.05, px + s * 0.05, py + s * 0.05), outline=ink, fill=ink if kind == "rubble" else floor)
    elif kind in {"crevasse", "sinkhole", "elevated_ledge", "natural_chimney"}:
        if kind == "sinkhole":
            for radius in (0.42, 0.27, 0.12):
                draw.ellipse((x - s * radius, y - s * radius, x + s * radius, y + s * radius), outline=ink, width=width)
        elif kind == "natural_chimney":
            for i in range(8):
                angle = i * math.tau / 8
                draw.line((x, y, x + math.cos(angle) * s * 0.42, y + math.sin(angle) * s * 0.42), fill=ink, width=width)
        elif kind == "elevated_ledge":
            draw.line((x - s * 0.45, y - s * 0.1, x - s * 0.2, y + s * 0.25, x + s * 0.1, y + s * 0.1, x + s * 0.45, y + s * 0.3), fill=ink, width=width)
            draw.line((x - s * 0.45, y - s * 0.25, x + s * 0.45, y - s * 0.05), fill=ink, width=width)
        else:
            draw.line((x - s * 0.4, y - s * 0.4, x - s * 0.1, y - s * 0.1, x - s * 0.25, y + s * 0.2, x + s * 0.15, y, x + s * 0.4, y + s * 0.35), fill=ink, width=width)
    else:
        label = symbol_icon(kind).strip()[:2]
        draw.ellipse((x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42), outline=ink, width=max(1, width))
        draw.text((x, y), label, fill=ink, font=get_font(max(8, int(s * (0.62 if len(label) > 1 else 0.76)))), anchor="mm")


def draw_pillow_door(draw, kind: str, x: float, y: float, s: float, ink: str, floor: str, width: int) -> None:
    draw.rectangle((x - s * 0.48, y - s * 0.2, x + s * 0.48, y + s * 0.2), fill=floor, outline=ink, width=width)
    draw.line((x - s * 0.48, y, x + s * 0.48, y), fill=ink, width=width)
    if kind == "door":
        draw.rectangle((x - s * 0.16, y - s * 0.09, x + s * 0.16, y + s * 0.09), fill=floor, outline=ink, width=width)
    elif kind == "double_door":
        draw.rectangle((x - s * 0.34, y - s * 0.09, x - s * 0.05, y + s * 0.09), fill=floor, outline=ink, width=width)
        draw.rectangle((x + s * 0.05, y - s * 0.09, x + s * 0.34, y + s * 0.09), fill=floor, outline=ink, width=width)
    elif kind == "secret_door":
        draw.text((x, y), "S", fill=ink, font=get_font(max(7, int(s * 0.55))), anchor="mm")
    elif kind == "one_way_door":
        draw.polygon([(x - s * 0.12, y - s * 0.02), (x + s * 0.12, y - s * 0.02), (x, y + s * 0.18)], fill=ink)
    elif kind == "false_door":
        draw.arc((x - s * 0.22, y - s * 0.05, x + s * 0.22, y + s * 0.25), 0, 180, fill=ink, width=width)
    elif kind == "locked_door":
        draw.rectangle((x - s * 0.13, y - s * 0.1, x + s * 0.13, y + s * 0.1), outline=ink, width=width)
        draw.ellipse((x - s * 0.04, y - s * 0.04, x + s * 0.04, y + s * 0.04), fill=ink)
    elif kind in {"archway", "archway_door"}:
        draw.line((x - s * 0.2, y - s * 0.12, x + s * 0.2, y - s * 0.12), fill=ink, width=width)
        draw.line((x, y - s * 0.12, x, y + s * 0.16), fill=ink, width=width)
    elif kind == "concealed_door":
        draw.text((x, y), "C", fill=ink, font=get_font(max(7, int(s * 0.55))), anchor="mm")
    elif kind == "barred_door":
        for offset in (-0.16, 0, 0.16):
            draw.rectangle((x + s * offset - s * 0.04, y - s * 0.12, x + s * offset + s * 0.04, y + s * 0.12), fill=ink)
    elif kind == "portcullis":
        for offset in (-0.18, 0, 0.18):
            draw.ellipse((x + s * offset - s * 0.035, y - s * 0.035, x + s * offset + s * 0.035, y + s * 0.035), fill=ink)
    elif kind == "one_way_secret_door":
        draw.text((x - s * 0.12, y), "S", fill=ink, font=get_font(max(7, int(s * 0.45))), anchor="mm")
        draw.polygon([(x + s * 0.02, y - s * 0.04), (x + s * 0.22, y - s * 0.04), (x + s * 0.12, y + s * 0.14)], fill=ink)
    elif kind == "window":
        draw.rectangle((x - s * 0.25, y - s * 0.05, x + s * 0.25, y + s * 0.05), fill=ink)
    elif kind == "arrow_slit":
        draw.polygon([(x - s * 0.25, y - s * 0.1), (x - s * 0.05, y + s * 0.1), (x - s * 0.28, y + s * 0.1)], fill=ink)
        draw.polygon([(x + s * 0.25, y - s * 0.1), (x + s * 0.05, y + s * 0.1), (x + s * 0.28, y + s * 0.1)], fill=ink)
    elif kind == "open_door":
        draw.line((x - s * 0.05, y, x + s * 0.25, y - s * 0.28), fill=ink, width=width)
    elif kind == "revolving_door":
        draw.arc((x - s * 0.24, y - s * 0.24, x + s * 0.24, y + s * 0.24), 20, 300, fill=ink, width=width)
        draw.line((x, y, x + s * 0.22, y), fill=ink, width=width)
    else:
        label = symbol_icon(kind).strip()[:2]
        draw.text((x, y), label, fill=ink, font=get_font(max(7, int(s * 0.52))), anchor="mm")


def draw_pillow_legend(draw, project: dict[str, Any], scale: int) -> None:
    settings = project["settings"]
    cell = settings["cellSize"] * scale
    x, y = cell * 2, settings["height"] * cell + cell
    width, height = settings["width"] * cell - cell * 4, cell * 5
    ink, floor = settings["gridColor"], settings["floorColor"]
    draw.rectangle((x, y, x + width, y + height), fill=floor, outline=ink, width=max(1, scale * 2))
    draw.text((x + cell * 1.2, y + cell * 1.45), "LEGEND", fill=ink, font=get_font(max(12, int(cell * 1.35))), anchor="lm")
    used = []
    for obj in project["objects"]:
        if obj.get("type") == "symbol" and obj.get("kind") not in used:
            used.append(obj["kind"])
    entries = [("cell", cell_scale_label(settings))] + [(kind, SYMBOL_LABELS[kind]) for kind in used if kind in SYMBOL_LABELS]
    for index, (kind, label) in enumerate(entries[:12]):
        col, row = index % 4, index // 4
        ex, ey = x + cell * 14 + col * cell * 13, y + cell * 1.35 + row * cell * 1.55
        if kind == "cell":
            draw.rectangle((ex, ey - cell * 0.5, ex + cell, ey + cell * 0.5), fill=floor, outline=ink, width=max(1, scale))
        else:
            draw_pillow_symbol(draw, kind, ex + cell * 0.5, ey, cell * 0.9, ink, floor, scale)
        draw.text((ex + cell * 1.6, ey), label, fill=ink, font=get_font(max(7, int(cell * 0.72))), anchor="lm")


def cave_points(x: float, y: float, width: float, height: float, seed: int, cell: float) -> list[tuple[float, float]]:
    rng = random.Random(seed)
    cx, cy = x + width / 2, y + height / 2
    points = []
    for i in range(24):
        angle = i / 24 * math.tau
        wobble = 0.84 + rng.random() * 0.32
        points.append(((cx + math.cos(angle) * width / 2 * wobble) * cell, (cy + math.sin(angle) * height / 2 * wobble) * cell))
    return points


def get_font(size: int):
    if ImageFont is None:
        return None
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def safe_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "-" for char in value.strip().lower())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned or "osr-map"


if __name__ == "__main__":
    app = OSRMapMaker()
    app.mainloop()
