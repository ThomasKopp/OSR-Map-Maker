# Programmdokumentation: OSR Map Maker

Stand: 2026-06-27

Status: Gegen Schema-Version 10, die aktuelle Tk-Oberflaeche und die vorhandene
Testsuite geprueft. Die Bedienung aus Nutzersicht steht im `README.md`; diese
Datei richtet sich an Entwicklung, Wartung und spaetere Modularisierung.

## 1. Zweck und Zielgruppe

### 1.1 Zweck

OSR Map Maker ist eine lokale Python/Tkinter-Desktop-Anwendung zum Erstellen,
Annotieren, Verwalten und Exportieren von Old-School-Rollenspielkarten.
Technisch verbindet die App Kartenzeichnung, Kampagnennotizen, Symbolverwaltung,
mehrere Renderpfade, VTT-Export und Projektpersistenz in einem Projektformat.

### 1.2 Zielgruppen

- Entwickler, die Fehler beheben oder neue Funktionen einbauen.
- Maintainer, die Projektdateien, Schema-Migrationen und Exporte stabil halten.
- Tester, die kritische Workflows und Performance-Risiken absichern.
- Dokumentationsautoren, die Nutzerhandbuch und technische Dokumentation
  synchron halten.

### 1.3 Abgrenzung

- `README.md`: Benutzerhandbuch, Installation, Workflows und Shortcuts.
- `docs/architecture.md`: Kurzer Architekturueberblick.
- `UI_SPEC.md`: UI- und Designvorgaben.
- `DOKUMENTATION.md`: Technische Programmdokumentation, Struktur,
  Datenfluesse, Wartungsregeln und Erweiterungspunkte.

## 2. Quellen der Analyse

| Quelle | Rolle |
| --- | --- |
| `osr_map_maker.py` | Zentrales Hauptmodul mit Datenmodell, Tk-App, Rendering, Export und Services |
| `app.py` | Schlanker Einstiegspunkt fuer `OSRMapMaker` |
| `constants.py` | Import-Fassade fuer Konstanten |
| `models.py` | Import-Fassade fuer Modell-, Validierungs- und Geometriehelfer |
| `project_services.py` | Import-Fassade fuer Projekt-, VTT-, Reporting- und Servicefunktionen |
| `renderers.py`, `render_tk.py`, `render_pillow.py` | Import-Fassaden fuer Renderfunktionen |
| `storage.py` | Kleine Persistenz-Fassade fuer Laden, Speichern und Autosave |
| `symbols.py` | Import-Fassade fuer Symbolgruppen und Symbolrendering |
| `tests/` | Regressionen, Modelltests und Performance-Smoke-Tests |
| `README.md` | Nutzerfunktionen und vorhandene Featurebeschreibung |
| `docs/architecture.md` | Architektur- und Performance-Notizen |
| `UI_SPEC.md` | UI-Zielbild und Layoutregeln |

## 3. Architekturueberblick

### 3.1 Aktueller Architekturzustand

Das Projekt ist funktional breit, aber technisch noch monolithisch. Das Modul
`osr_map_maker.py` enthaelt weiterhin den groessten Teil der Implementierung:
Konstanten, Projektmodell, Validierung, Tkinter-UI, Canvas-Interaktion,
Geometrie, Rendering, Exporte, Generatoren, Symbolverwaltung, Autosave und
Performance-Caches.

Die kleineren Module sind derzeit stabile Import-Fassaden. Sie schaffen bereits
Modulgrenzen fuer spaetere Extraktion, enthalten aber kaum eigene Logik.

### 3.2 Hohe Systemebene

```text
Start
  app.py oder osr_map_maker.py
    -> OSRMapMaker()
      -> Projektmodell erzeugen oder laden
      -> Tkinter-Menues, Command Bar, Panels und Canvas aufbauen
      -> Nutzerinteraktion verarbeitet Projektzustand
      -> Rendering zeichnet aktuellen Projektzustand
      -> Speichern/Autosave/Export schreiben abgeleitete Dateien
```

### 3.3 Zentrale Verantwortlichkeiten

| Bereich | Hauptort | Verantwortung |
| --- | --- | --- |
| App-Start | `app.py`, `osr_map_maker.py` | Tk-App erzeugen und Mainloop starten |
| Projektmodell | `create_project`, `validate_project`, `validate_object` | Defaultstruktur, Schema, Migration und Normalisierung |
| UI | `OSRMapMaker` | Fenster, Menues, Panels, Dialoge, Events, Status |
| Canvas-Interaktion | `OSRMapMaker` | Zeichnen, Auswahl, Drag, Zoom, Pan, Handles, Snapping |
| Rendering | `render_tk`, `render_pillow`, `save_svg` | Anzeige und Exportausgabe |
| Persistenz | `read_project_file`, `write_project_data`, `storage.py` | JSON, komprimierte Projekte, Autosave |
| Export | `open_export_dialog`, `render_image`, VTT-Funktionen | Bild-, PDF-, SVG- und JSON-Exporte |
| Tests | `tests/test_core.py`, `tests/test_performance.py` | Modell-, Export-, Cache- und Performance-Absicherung |

## 4. Repository- und Modulstruktur

### 4.1 Wichtige Dateien

| Datei | Beschreibung | Dokumentationsbedarf |
| --- | --- | --- |
| `osr_map_maker.py` | Hauptimplementierung | Funktionsgruppen und Wartungsregeln detaillieren |
| `app.py` | Alternativer Einstiegspunkt | Kurz dokumentieren |
| `storage.py` | Laden/Speichern-Fassade | Projektdateien und Autosave erklaeren |
| `models.py` | Modell-Fassade | Oeffentliche Modellfunktionen auflisten |
| `renderers.py` | Renderer-Fassade | Renderpfade und Abhaengigkeiten erklaeren |
| `project_services.py` | Service-Fassade | Reports, VTT und raeumliche Suche einordnen |
| `constants.py` | Konstanten-Fassade | Wertebereiche und Defaults referenzieren |
| `symbols.py` | Symbol-Fassade | Symbolgruppen, Custom Symbols und Renderrollen beschreiben |
| `tests/` | Test-Suite | Teststrategie und wichtige Testfaelle dokumentieren |
| `examples/` | Beispielprojekte | Als manuelle Pruefflaeche auffuehren |
| `scripts/quality.ps1` | Lokale Qualitaetspipeline | Entwicklungsworkflow dokumentieren |

### 4.2 Aktuelle Facade-Grenzen

| Facade | Verifizierte Exporte |
| --- | --- |
| `models.py` | Factories, Bounds, Validierung, Karten-/VTT-Modellhelfer |
| `renderers.py` | Canvasgroesse, Tk/Pillow, SVG, PDF-Seiten und Static-Layer-Cache |
| `project_services.py` | Spatial Index, Reports, Review, VTT-Daten und Dateinamen |
| `constants.py` | Schema, Defaults, Layer, Mapmodi, Exportframes und Symbole |
| `symbols.py` | Symbolkatalog, Normalisierung und Tk/Pillow-Symbolrenderer |
| `storage.py` | Validiertes Laden sowie Speichern/Autosave ueber Projektdateien |

Die Facades importieren Implementierungen aus `osr_map_maker.py`; sie sind
stabile Importoberflaechen, keine unabhaengigen Subsysteme.

## 5. Datenmodell und Projektformat

### 5.1 Projektdateien

Unterstuetzte Formate:

- `.osrmap.json`: lesbare JSON-Projektdatei.
- `.osrmapz`: komprimiertes Projektarchiv mit `project.json`.

Zentrale Funktionen:

- `read_project_file(path)`: Projektdatei lesen.
- `write_project_data(path, project)`: Projektdatei schreiben.
- `compressed_project_path(path)`: Zielpfad fuer komprimierte Varianten.
- `backup_project_before_migration(path, schema_version)`: Backup vor Migration.

### 5.2 Root-Struktur

Die Projektwurzel enthaelt unter anderem:

- `schemaVersion`
- `meta`
- `settings`
- `layers`
- `objects`
- `maps`
- `campaign`
- `zones`
- `markers`
- `views`
- `exportFrames`
- `exportProfiles`
- `customSymbols`
- `customSymbolGroups`
- `symbolFavorites`
- `assetLibrary`
- `reviewComments`
- `changeLog`
- `snapshots`

| Feld | Typ/Default | Validierung und Wirkung |
| --- | --- | --- |
| `schemaVersion` | Integer, aktuell `10` | `validate_project`; Migration und Kompatibilitaet |
| `meta` | Objekt | Titel, Autor, Zeitstempel fuer Fenster, Reports und Dateinamen |
| `settings` | Objekt | `validate_settings`; Karte, Grid, Stil, UI, Tools und Exportdefaults |
| `layers` | Liste | `validate_layers`; Sichtbarkeit, Lock, Opacity und Reihenfolge |
| `objects` | Liste | `validate_object_list`; aktive Map-Objekte fuer UI und Rendering |
| `maps` / `activeMapId` | Liste / String | Persistente Maps und Auswahl der aktiven Map |
| `campaign` | Objekt | `validate_campaign`; Raumdaten, Tabellen und Generatorverlauf |
| `zones`, `markers`, `views` | Listen | Navigator-, Fokus- und Sprungziele |
| `exportFrames`, `exportProfiles` | Listen | Validierte Exportausschnitte und wiederverwendbare Optionen |
| `customSymbols`, `customSymbolGroups` | Objekt / Liste | Assetquellen, Varianten, Tags und Browsergruppen |
| `symbolFavorites` | Liste | Favoritenfilter des Symbolbrowsers |
| `assetLibrary`, `symbolPackManifests` | Listen | Asset- und Paketmetadaten |
| `reviewComments`, `changeLog`, `snapshots` | Listen | Review, Audit und Vergleiche |
| `underlays`, `printLayouts`, `sessionState` | Listen / Objekt | Referenzbilder, Druck und GM/Player-Sitzung |

### 5.3 Karten und aktive Map

Das Projekt speichert mehrere Maps/Floors in `maps`. Die aktive Karte wird in
die Root-Felder gespiegelt, damit viele bestehende Funktionen weiter mit
`project["objects"]`, `project["settings"]`, `project["layers"]` und
`project["campaign"]` arbeiten koennen. Vor Map-Wechsel, Snapshot, Speichern
und Export schreibt `sync_active_map_storage()` diese Root-Sicht in den aktiven
Map-Datensatz zurueck.

Wichtige Funktionen:

- `create_map_record(...)`
- `validate_map_record(...)`
- `validate_maps(...)`
- `OSRMapMaker.active_map_record()`
- `OSRMapMaker.sync_active_map_storage()`
- `OSRMapMaker.load_map_record(record)`

### 5.4 Objekttypen

Wichtige Objektfamilien:

- Floor-Objekte: `room`, `room_polygon`, `corridor`, `diagonal_corridor`,
  `cave_corridor`, `round`, `cave`.
- Zeichenobjekte: Rechteck, Kreis, Polygon, Linie, Freehand, Brush.
- Textobjekte: Text, Nummer, Note.
- Symbolobjekte: Built-in und Custom Symbols mit Varianten.
- Spezialobjekte: Legende, Marker, Zonen, Export Frames.

| Familie | Typen | Wichtige Felder |
| --- | --- | --- |
| Floor | `room`, `room_polygon`, `corridor`, `diagonal_corridor`, `cave_corridor`, `round`, `cave` | Geometrie, `layer`, Rotation, Wandstil, Raumstatus, Kampagnenfelder, `playerVisible` |
| Shape | `shape` mit `rect`, `circle`, `polygon`, `line`, `freehand`, `brush` | Punkte/Bounds, Stroke, Fill, Opacity, Linie, Pfeile, Rotation |
| Text | `text` mit Rollen `text`, `number`, `note` | Text, Position, Font, Groesse, Farbe, Exportflag, Nummernmuster |
| Symbol | `symbol` | `kind`, Position, Groesse/Preset, Variante, Farbe, Opacity, Shadow, Outline, Linkziele |
| Legend | `legend` | Position, Groesse, Spalten und Scale |

`validate_object` normalisiert fehlende Werte und lehnt unbekannte Typen ab.
Neue Objektfelder muessen in Factory, Validator, Selection-UI und allen
betroffenen Renderpfaden gleichzeitig ergaenzt werden.

### 5.5 Validierung und Migration

Validierung ist zentralisiert und sollte bei jedem neuen persistenten Feld
angepasst werden.

Wichtige Funktionen:

- `validate_project(value)`
- `validate_settings(value)`
- `validate_object(obj, index)`
- `validate_layers(value)`
- `validate_campaign(value, objects)`
- `validate_export_profiles(value)`
- `validate_export_frames(value)`
- `validate_custom_symbols(value)`
- `project_validation_warnings(project)`

Wartungsregel: Neue Felder brauchen Default, Validator, Migration/Normalisierung,
Tests und Dokumentation.

## 6. Laufzeit- und Datenfluesse

### 6.1 App-Start

1. Einstieg ueber `app.py` oder direkt `osr_map_maker.py`.
2. `OSRMapMaker()` erzeugt Defaultprojekt und Tk-Status.
3. UI wird ueber `_build_menu()`, `_build_ui()` und Panel-Builder aufgebaut.
4. Events und Shortcuts werden gebunden.
5. Autosave-Recovery und Recent Projects werden vorbereitet.

### 6.2 Projekt laden

1. Datei auswaehlen.
2. `read_project_file()` liest JSON oder `.osrmapz`.
3. `validate_project()` normalisiert und migriert Daten.
4. Aktive Map wird geladen.
5. UI-Variablen, Panels, Canvas und Status werden synchronisiert.

### 6.3 Objekt zeichnen

1. Aktives Werkzeug wird in `self.tool` gesetzt.
2. Canvas-Events wandeln Mauspositionen in Gridkoordinaten um.
3. Snap-, Layer- und Tool-Defaults werden angewendet.
4. Objekt wird erzeugt, validiert und in `project["objects"]` eingefuegt.
5. History, Dirty-State, Autosave und Redraw werden aktualisiert.

### 6.4 Auswahl bearbeiten

1. Hit-Test nutzt Bounds und optional Spatial Index.
2. Auswahl wird in `selected_ids` und `selected_id` gepflegt.
3. Inspector/Selection-Panel zeigt gemeinsame oder objektbezogene Felder.
4. Aenderungen laufen ueber Snapshot/History und Redraw.

### 6.5 Export

1. Exportdialog oder Quick Export erzeugt Exportoptionen.
2. `export_project_for_scope(...)` erstellt eine abgeleitete Projektansicht.
3. Je nach Format wird Pillow, SVG, PDF oder JSON genutzt.
4. Dateiname entsteht ueber Exportprofil und Filename Template.

## 7. UI-Architektur

### 7.1 Hauptklasse `OSRMapMaker`

`OSRMapMaker` erbt von `tk.Tk` und ist zentrale Koordinationsklasse fuer:

- Projektzustand und aktive Map.
- Tk-Variablen und UI-Synchronisierung.
- Menues, Command Bar, Toolbar, Panels und Dialoge.
- Canvas-Events, Zeichnen, Auswahl und Shortcuts.
- History, Dirty-State, Autosave und Recovery.
- Exportdialoge und Reports.

Methodengruppen in [`osr_map_maker.py`](osr_map_maker.py):

| Gruppe | Zentrale Methoden |
| --- | --- |
| Aufbau | `_build_menu`, `_build_ui`, `_build_toolbar`, `create_dock_panel` |
| Kontext-UI | `rebuild_contextual_tool_options`, `update_selection_panel`, `refresh_status_fields` |
| Workspaces/Layout | `apply_workspace_preset`, `apply_compact_mode`, `apply_window_layout` |
| Canvas | `on_press`, `on_drag`, `on_release`, `on_motion`, `on_context_menu` |
| History/Projekt | `commit_history`, `undo`, `redo`, `sync_vars`, `project_snapshot` |
| Persistenz | `save_project`, `load_project_path`, `run_autosave`, `check_autosave_recovery` |
| Export | `open_export_dialog`, `render_image`, `export_project_for_scope`, `batch_export` |

### 7.2 Hauptbereiche der Oberflaeche

- Command Bar: globale Aktionen wie New, Load, Save, Undo, Redo, Search,
  Command Palette und Export.
- Tool Options: kontextuelle Optionen fuer aktives Werkzeug.
- Canvas: Zeichnung, Auswahl, Guides, Overlays, Grid und Vorschauen.
- Dock Panels: Symbols, Colors/Style, Layers, Selection, History, Navigator,
  Export, Objects, Map, Rooms.
- Status Bar: Koordinate, Zelle, Zoom, Werkzeug, Layer, Auswahl, Snap,
  Speicherstatus und Validierung.

Dock-Panels sind gestapelte Frames im rechten Inspector. Ihre Hoehe wird pro
Panel gespeichert und an der Unterkante gezogen. Compact Mode ersetzt den
Inspector durch direkte Buttons fuer Layers, Selection, Symbols, Navigator und
Export. Die UI-Terminologie ist Englisch; deutsche Begriffe existieren nur als
Suchaliase fuer Symbole.

### 7.3 Workspaces

Aktuelle Workspaces:

- `Drawing`
- `Symbols`
- `Campaign`
- `Export/VTT`
- `Print`

Wichtige Funktionen:

- `normalize_workspace_preset(value)`
- `workspace_panel_visibility(preset_name)`
- `default_window_layout_settings(preset_name)`
- `OSRMapMaker.apply_workspace_preset(name)`

### 7.4 Events und Shortcuts

Wichtige Themen:

- Mausklick, Drag, Release, Motion.
- Zoom per Wheel und Tasten im Bereich von 25 bis 400 Prozent.
- Pan per mittlerer Maustaste und Space; Rechtsklick oeffnet Kontextmenues.
- Konfigurierbare Shortcuts aus `DEFAULT_SHORTCUTS`.
- Command Palette und globale Suche.

| Event/Aktion | Methode | Zustand und Nebenwirkung |
| --- | --- | --- |
| Canvas Press/Drag/Release | `on_press`, `on_drag`, `on_release` | Draft oder Auswahlbewegung; Snap, History und Redraw |
| Mouse Motion | `on_motion` | Hover, Koordinate, Smart Guides und Status ohne Panel-Neuaufbau |
| Rechtsklick | `on_context_menu` | Kontextmenue fuer leeren Canvas, Auswahl oder Polygonpunkt |
| Mausrad | `on_mousewheel_zoom` | Zoom um Cursorposition |
| Space Press/Release | `start_space_pan`, `end_space_pan` | Temporaerer Pan; in Textfeldern deaktiviert |
| Pfeiltasten | `handle_arrow_key` | Auswahl verschieben oder Zoom; Eingabefelder sind ausgenommen |
| Tool Enter/Space | `activate_tool_from_keyboard` | Aktiviert fokussiertes Werkzeug |
| Workspace | `apply_workspace_preset` | Panels, Minimap, Toolbar, Farbe und Fokusziel wechseln |
| Command Palette | `open_command_palette` | Filtert Befehle; Up/Down waehlt, Enter fuehrt aus |

Projektweite Shortcuts laufen ueber `guarded_shortcut` und duerfen nicht
ausloesen, wenn Entry, Text, Listbox, Treeview, Combobox oder Spinbox fokussiert
ist. Die Defaultbelegung liegt in `DEFAULT_SHORTCUTS`.

## 8. Fachliche Funktionsbereiche

### 8.1 Zeichnen und Editieren

- Raum-, Korridor-, Hoehlen- und Polygonwerkzeuge.
- Zeichenformen, Linien, Freehand und Brush.
- Text, Nummern, Notes.
- Handles, Rotation, Resize, Polygonpunkte.
- Snapping, Guides, Align, Distribute, Group/Ungroup.

### 8.2 Symbole und Custom Assets

- Eingebaute Symbolgruppen und Labels.
- Custom Symbols aus PNG/SVG.
- Varianten, Tags, Aliase, Favoriten, Recent Symbols.
- Symbolsets importieren/exportieren.
- Einbetten externer Symboldaten fuer portable Projekte.

### 8.3 Layer, Maps und Navigation

- Layer mit Sichtbarkeit, Lock, Export-Opacity und Static Cache.
- Mehrere Maps/Floors mit Templates und Thumbnail-Tabs.
- Navigator fuer Views, Marker, Zones, Export Frames und Floor Links.

### 8.4 Kampagne und Raeume

- Strukturierte Raumdaten.
- Raumstatus, Player Visibility, GM-only Felder.
- Encounter- und Loot-Tabellen.
- Reports, GM Booklet und Handouts.

### 8.5 Generatoren

- Random Rooms.
- Random Corridors.
- Dungeon-Generator.
- Keyword Dungeon.
- Natural Caves.
- Auto Doors, Auto Walls, Patrol Routes und Cleanup.

| Gruppe | Eingaben | Ergebnis/Commit |
| --- | --- | --- |
| Random Rooms/Corridors | Anzahl, Scope, Seed | Fuegt validierte Floor-Objekte hinzu und erzeugt einen History-Eintrag |
| Dungeon/Keyword Dungeon | Theme oder Keywords, Seed, Scope | Erzeugt Raum-/Korridorstruktur mit Vorschau bzw. Zusammenfassung |
| Natural Caves | Seed, Scope | Erzeugt unregelmaessige Cave-Geometrie |
| Auto Doors/Walls | vorhandene Floor-Kanten | Analysiert Geometrie und fuegt Symbole bzw. Wandstile hinzu |
| Patrol Routes/Suggest Links | Raeume und Zonen | Erzeugt Navigation oder Vorschlaege, ohne Exportdaten direkt zu schreiben |
| Cleanup/Roughen/Check Walls | aktuelle Map oder Auswahl | Veraendert bzw. validiert bestehende Geometrie |

Generatoren lesen `generatorScope` (`Map`, `Selection`, `Active zone`) und
schreiben Seed/Zusammenfassung in `campaign.generatorHistory`. Mutierende
Aktionen verwenden `project_snapshot` und `commit_history`; Abbruch vor Apply
darf keinen History-Eintrag erzeugen.

## 9. Rendering und Export

### 9.1 Renderpfade

| Pfad | Zweck |
| --- | --- |
| `render_tk` | Anzeige im Canvas |
| `render_pillow` | Rasterexport und PDF-Ausgabe |
| `save_svg` | Vektor-Ausgabe mit Objektgruppen und Metadaten |
| `render_static_layer_image` | Cache fuer unveraenderte Layer |

### 9.2 Gemeinsame Renderkonzepte

- Canvasgroesse aus Projektbounds und Zellgroesse.
- Layer-Sichtbarkeit und Export-Opacity.
- Audience-Filter fuer GM/Player.
- Grid, Hexgrid, Koordinaten, Zonen, Underlays und Legende.
- Built-in Symbols und Custom Symbols.
- Textumbruch, Rotation, Opacity und Styling.

### 9.3 Exportformate

- PNG
- JPEG
- WebP
- PDF
- SVG
- Foundry Scene JSON
- Roll20 Page JSON
- Fantasy Grounds JSON

### 9.4 Exportprofile und Scopes

Scopes:

- Map
- Page
- Selection
- Frame

Wichtige Funktionen:

- `export_project_for_frame(project, frame_id)`
- `OSRMapMaker.export_project_for_scope(...)`
- `OSRMapMaker.render_image(...)`
- `default_batch_export_jobs(...)`
- `batch_export_targets(...)`
- `export_filename_from_template(...)`

| Option | Standard | Wirkung |
| --- | --- | --- |
| `format` | Profilabhaengig, meist PNG | Waehlt Pillow-Raster, PDF oder SVG |
| `scale` | `1` oder Profilwert | Pixeldichte relativ zur Canvas-Zellgroesse |
| `scope` | Map/Page | Vollkarte, Auswahl oder benannter Frame |
| `audience` | GM | Filtert `playerVisible`, GM-Notizen und verdeckte Inhalte |
| `export_grid` | `True` | Zeichnet Haupt-/Subgrid entsprechend Settings |
| `legend` | Profilwert | Nimmt die Kartenlegende auf |
| `jpeg_quality`, `webp_quality` | validierte Profilwerte | Kompressionsqualitaet verlustbehafteter Formate |
| `frame_id` | leer | Begrenzt Ausgabe auf `exportFrames` |
| Dateinamensvorlage | `{project}_{map}_{audience}_{profile}` | Wird durch `export_filename_from_template` aufgeloest |

`open_export_dialog` rendert eine gedrosselte Vorschau. `render_image` erstellt
die Pillow-Ausgabe, `save_svg` den Vektorpfad und `save_export_image` schreibt
Raster/PDF. `export_scene_json` nutzt je nach Ziel `foundry_scene_data`,
`roll20_page_data` oder `fantasy_grounds_data`. Batch-Export erzeugt Jobs ueber
`default_batch_export_jobs` und `batch_export_targets`.

## 10. Persistenz, Autosave und Recovery

### 10.1 Projektpersistenz

Wichtige Speicherpfade:

- Projektdatei nach Nutzerwahl.
- App-State-Verzeichnis aus `app_state_dir()`.
- Recent Projects.
- Gespeichertes Window Layout (`preferred_window_layout.json`).
- Autosave-Dateien und Autosave-Versionen.
- Migration-Backups in `.osr_map_backups`.

### 10.2 Autosave

Autosave nutzt Projektrevisionen, speichert kompakte Projektdateien und prueft
beim Start, ob ein neuerer Autosave vorhanden ist.

Wichtige Funktionen:

- `autosave_path()`
- `autosave_versions_dir()`
- `autosave_candidates(...)`
- `prune_autosave_versions(...)`
- `autosave_recovery_metadata(...)`
- `OSRMapMaker.schedule_autosave()`
- `OSRMapMaker.run_autosave()`
- `OSRMapMaker.check_autosave_recovery()`

## 11. Performance

### 11.1 Aktuelle Mechanismen

- Redraw-Scheduling und Zusammenfassen haeufiger Canvas-Updates.
- Getrennte Canvas- und Interaction-Overlays.
- Minimap-Redraw-Throttling.
- Spatial Index fuer Hit Detection.
- Cache fuer Canvasgroessen, Floor-Geometrie, Underlays, Tk-Symbole und
  statische Layer.
- `PerformanceProfiler` fuer Laufzeitmessungen.

### 11.2 Wartungsregeln

- Bei Drag/Mouse-Move keine unnoetigen Panel-Rebuilds ausloesen.
- Cache-Schluessel muessen alle renderrelevanten Felder enthalten.
- Neue Renderoptionen muessen Tk-, Pillow- und SVG/PDF-Pfade pruefen.
- Performance-Tests erweitern, wenn Datenmengen oder Renderpfade wachsen.

## 12. Tests und Qualitaetssicherung

### 12.1 Tests

| Datei | Abdeckung |
| --- | --- |
| `tests/test_core.py` | Validierung, Einstellungen, Projektdateien, Modelle, Exporthelfer |
| `tests/test_performance.py` | Caches, Spatial Index, Render-Smoke-Tests, Redraw/Minimap-Scheduling |

### 12.2 Qualitaetsskript

`scripts/quality.ps1` fuehrt aus:

```powershell
python -m py_compile osr_map_maker.py models.py constants.py renderers.py project_services.py
python -m pytest -q
ruff check .
mypy --ignore-missing-imports osr_map_maker.py models.py constants.py renderers.py project_services.py
```

`ruff` und `mypy` laufen nur, wenn die Tools installiert sind.

### 12.3 Mindestpruefung fuer Aenderungen

- Dokumentation: `git diff --check -- DOKUMENTATION.md Tasks.md`.
- Modell-/Serviceaenderung: relevante Unit-Tests plus `python -m pytest -q`.
- UI-Aenderung: manuelle App-Pruefung mit Beispielprojekten.
- Render-/Exportaenderung: mindestens PNG/PDF/SVG oder betroffener VTT-JSON-Pfad
  mit Beispielprojekt pruefen.

### 12.4 UI- und Layout-Regressionen

| Szenario | Erwartung |
| --- | --- |
| Raum, Korridor, Tuer, Nummer, Undo | Werkzeuge erreichbar; letzter Schritt verschwindet aus Projekt und erscheint in Redo |
| Symbol suchen, platzieren, gestalten | Symbols-Workspace fokussiert Suche; Preset und Farbe landen am Objekt |
| Auswahl, Layer, Player Visibility | Selection-Panel und Batchmethoden schreiben validierte Werte mit History |
| Exportprofil und Player Export | Audience/Profile bleiben gesetzt; Exportdialog startet |
| Workspace-Matrix | Sichtbarkeit entspricht `WORKSPACE_PRESETS`; Fokusziel ist bedienbar |
| Layout Save/Restore/Reset | Inspectorbreite, Panels, Toolbar, Minimap und Compact Mode werden reproduziert |

Tk-Tests koennen auf Systemen ohne Display uebersprungen werden. Modell-,
Persistenz-, Render- und Performance-Tests muessen dort weiterhin laufen.

## 13. Erweiterungspunkte und Wartungsregeln

### 13.1 Neues persistentes Feld

1. Default in `default_settings()` oder passender Factory ergaenzen.
2. Validator/Migration anpassen.
3. Speichern/Laden mit Altprojekt testen.
4. UI-Synchronisierung pruefen.
5. Export- und Player/GM-Auswirkungen pruefen.
6. Tests und Dokumentation aktualisieren.

### 13.2 Neues Werkzeug

1. Tool-Konstante und `BASIC_TOOLS`/Gruppen ergaenzen.
2. Shortcut und Toolbeschreibung definieren.
3. Toolbar, Tool Options und Cursor pruefen.
4. Canvas-Events fuer Press/Drag/Release anpassen.
5. Objektfactory und Validator ergaenzen.
6. Tk/Pillow/SVG-Rendering ergaenzen.
7. Tests und README/Dokumentation aktualisieren.

### 13.3 Neuer Symboltyp

1. Symbolgruppe und Label definieren.
2. Built-in-Rendering fuer Tk/Pillow/SVG ergaenzen.
3. VTT-Rolle und Legendeneinordnung pruefen.
4. Such-, Alias- und Variantenverhalten pruefen.
5. Export und Symbolset-Kompatibilitaet testen.

### 13.4 Neuer Export

1. Exportoptionen und Profilverhalten definieren.
2. Gemeinsame Exportscopes wiederverwenden.
3. Dateinamen und Batch-Verhalten pruefen.
4. Player/GM-Filter und Layer-Opacity pruefen.
5. Tests und Beispielprojekt ergaenzen.

## 14. Fehlerbehandlung und Validierung

Wichtige Fehlerquellen:

- Beschaedigte oder alte Projektdateien.
- Fehlende Custom-Symbol-Dateien.
- Ungueltige Objektgeometrie.
- Nicht installierte optionale Abhaengigkeiten wie Pillow oder CairoSVG.
- Zu grosse Exporte oder sehr grosse eingebettete Assets.
- Inkonsistente Links zwischen Maps/Floors.

| Fehlerklasse | Nutzerreaktion | Technischer Pfad |
| --- | --- | --- |
| Datei nicht lesbar/ungueltig | Modaler Fehler; Projekt bleibt unveraendert | `read_project_file`, `validate_project`, `show_error` |
| Fehlendes Custom Asset | Validation-Warnung und Repair-Aktion im Symbolmenue | `missing_custom_symbol_files`, `repair_current_custom_symbol_path` |
| Ungueltige Eingabe | Feldstatus oder kurze Statusmeldung; kein Commit | Feldvalidatoren und `change_selection_field` |
| Fehlende optionale Library | Exportdialog nennt Pillow/CairoSVG-Abhaengigkeit | Export- und Asset-Ladepfade |
| Inkonsistenter Link | Validation-Warnung; Ziel kann im Dialog korrigiert werden | `project_validation_warnings` |
| Neuerer Autosave | Recovery-Dialog mit Projektvergleich | `check_autosave_recovery`, `ask_autosave_recovery` |
| Schema-Migration | Normalisierung und optionales Backup | `validate_project`, `backup_project_before_migration` |

Lange oder entscheidungspflichtige Fehler sind modal. Kurze Erfolge und
Warnungen erscheinen als Toast/Status; sammelbare Probleme gehoeren in Project
Validation. Fehlerpfade duerfen Projekt und History nicht teilweise mutieren.

## 15. Bekannte technische Risiken

- `osr_map_maker.py` ist sehr gross; Aenderungen koennen mehrere Bereiche
  unbeabsichtigt betreffen.
- Root-Map-Spiegelung und `maps`-Liste muessen synchron bleiben.
- Renderinglogik ist ueber mehrere Ausgabeformate verteilt.
- Neue persistente Felder koennen alte Projekte brechen, wenn Defaults oder
  Validatoren fehlen.
- UI-Events und Redraw-Scheduling sind eng gekoppelt.
- Custom Assets koennen externe Dateipfade oder eingebettete Daten verwenden;
  beide Varianten muessen getestet werden.

## 16. Dokumentationsstatus nach Kapiteln

| Kapitel | Status | Verifizierte Quelle |
| --- | --- | --- |
| Zweck, Architektur, Module | Vollstaendig | Einstiegspunkte und Facade-Module |
| Datenmodell und Migration | Vollstaendig | Schema 10, Factory- und Validatorfunktionen |
| Laufzeitfluesse | Vollstaendig | Projekt-, Canvas-, History- und Exportmethoden |
| UI-Architektur | Vollstaendig | Menues, Workspaces, Dock-Panels, Events und Dialoge |
| Fachfunktionen | Vollstaendig | Tools, Symbole, Layer, Maps, Campaign und Generatoren |
| Rendering und Export | Vollstaendig | Tk, Pillow, SVG, PDF und drei VTT-Ziele |
| Persistenz und Autosave | Vollstaendig | JSON/ZIP, App-State, Recovery und Backups |
| Performance | Vollstaendig | Caches, Revisionen, Scheduler und Profiler |
| Tests und Wartung | Vollstaendig | Core-/Performance-Suite und `scripts/quality.ps1` |

## 17. Dokumentationspflege

- UI-Aenderungen muessen mit `README.md` und `UI_SPEC.md` abgeglichen werden.
- Persistente Felder erfordern eine Aktualisierung der Feldmatrix und
  Schema-/Migrationstests.
- Neue Renderer oder Exporte erfordern Eintraege in Kapitel 9 und mindestens
  einen Test oder verifizierten Beispiel-Export.
- Neue Facade-Exporte muessen in deren `__all__` und in Kapitel 4 nachvollziehbar
  bleiben.
- Vor Abschluss: Markdown-Links pruefen und
  `git diff --check -- README.md UI_SPEC.md DOKUMENTATION.md Tasks.md` ausfuehren.
