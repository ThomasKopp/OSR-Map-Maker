# UI-Verbesserungsvorschlaege fuer OSR Map Maker

Orientierung: Paint.NET wirkt stark, weil die Arbeitsflaeche im Zentrum bleibt,
Werkzeuge schnell erreichbar sind, Ebenen und Verlauf als eigene Arbeitsfenster
sichtbar sind und haeufige Aktionen ohne langes Suchen funktionieren. OSR Map
Maker sollte diese Prinzipien auf Kartenbau, Symbole, Layer, Kampagnennotizen
und Export/VTT-Workflows uebertragen.

## Leitprinzipien

- [x] Canvas-first: Die Karte bleibt immer der visuelle Mittelpunkt. Panels und
      Werkzeugleisten unterstuetzen die Arbeit, sie dominieren sie nicht.
- [x] Sofort lernbar: Die wichtigsten Aktionen sollen durch Icon, Tooltip,
      Shortcut und Statuszeile verstaendlich sein, ohne lange Hilfetexte im UI.
- [x] Schnelle Wege fuer haeufige Aufgaben: Zeichnen, Auswaehlen, Layer wechseln,
      Symbol platzieren, Undo/Redo, Zoom und Export brauchen direkte Kontrollen.
- [x] Paint.NET-aehnliche Fensterlogik: Tools, Layers, History, Colors/Style,
      Symbols und Navigator koennen gedockt, schwebend, geschlossen und wieder
      eingeblendet werden.
- [x] Ruhige Windows-Desktop-Aesthetik: klare Linien, neutrale Flaechen,
      konsistente Abstaende, Segoe-UI-Typografie, deutliche aktive Zustaende.
- [x] Weniger Registerkarten-Tiefe: Haefig genutzte Panels sollten direkt
      sichtbar sein; seltene Spezialfunktionen duerfen in Dialoge oder
      aufklappbare Bereiche wandern.

## Hohe Prioritaet

- [x] Top-Leiste zu einer kompakten Command Bar umbauen.
      Nur globale Kernaktionen sichtbar halten: Neu, Oeffnen/Laden, Speichern,
      Undo, Redo, Zoom/Fit, Suche/Command Palette, Export. Detailoptionen wie
      Exportformat, Exportskalierung und Toolbar-Dock in passende Panels oder
      Menues verschieben, damit die Leiste ruhiger wird.

- [x] Werkzeugleiste staerker wie Paint.NET strukturieren.
      Eine feste Icon-Matrix fuer Zeichenwerkzeuge nutzen, mit klarer aktiver
      Markierung, 24-32 px Zielgroesse, einheitlichem Raster, Tooltip inklusive
      Shortcut und kurzem Modus-Hinweis. Unicode-Symbole schrittweise durch
      konsistente PNG/Icon-Assets ersetzen.

- [x] Kontextuelle Werkzeugoptionen als eigene Optionsleiste einfuehren.
      Direkt unter der Top-Leiste oder am oberen Canvas-Rand sollten nur die
      Optionen des aktiven Werkzeugs erscheinen, z. B. Snap-Schritt, Linienbreite,
      Symbolgroesse, Textgroesse, Fuelle/Farbe, Pfeilenden oder Zufallsvariante.
      Dadurch muessen Nutzer fuer einfache Werkzeuganpassungen nicht in den
      rechten Inspector wechseln.

- [x] Rechte Seitenleiste in dockbare Einzelpanels aufteilen.
      Statt alle Inhalte in verschachtelten Inspector-Tabs zu verstecken, sollten
      die wichtigsten Panels separat sichtbar sein: Layers, History, Symbols,
      Properties/Selection, Navigator und Export. Jedes Panel bekommt eine kleine
      Titelleiste mit Schliessen, Andocken, Abdocken und optionalem Einklappen.

- [x] Layers-Panel paint.net-aehnlich ueberarbeiten.
      Jede Ebene als Zeile mit kleinem Layer-Thumbnail, Name, Sichtbarkeit,
      Lock-Status, Opacity und Objektanzahl darstellen. Aktive Ebene blau
      hervorheben, Drag-and-drop-Reihenfolge beibehalten, plus/minus/duplizieren/
      nach oben/nach unten als Icon-Leiste am unteren Panelrand anbieten.

- [x] History-Panel prominenter machen.
      Der Undo-Verlauf sollte nicht tief im Project-Tab versteckt sein. Ein
      sichtbares History-Panel wie bei Paint.NET zeigt die letzten Aktionen mit
      kleinem Icon, aktuellem Undo-Ziel und getrenntem Redo-Bereich. Unten:
      Undo/Redo-Buttons als Icons, optional "Zu Zustand springen" als spaetere
      Erweiterung.

- [x] Map-/Floor-Wechsel als Thumbnail-Tabs gestalten.
      Paint.NET nutzt Bild-Tabs mit Live-Thumbnails. OSR Map Maker kann oben ueber
      dem Canvas kleine Tabs fuer Karten/Floors anzeigen: Mini-Vorschau, Name,
      Dirty-Indikator, Kontextmenue fuer Umbenennen/Duplizieren/Loeschen. Der
      aktuelle Kombobox-Wechsel waere dann nur noch eine Zusatznavigation.

- [x] Canvas-Rahmung verbessern.
      Den Arbeitsbereich neutraler gestalten: hellgrauer App-Hintergrund,
      zentrierte Kartenflaeche mit subtiler Kante/Schatten, klare Map Bounds,
      dezente Scrollbars und weniger dominante blaue Hintergrundflaeche. Das
      hilft, die Karte wie ein Dokument auf einer Arbeitsflaeche zu lesen.

- [x] Statusleiste ausbauen.
      Neben Meldungen auch aktive Koordinate, Grid-Zelle, Zoom, aktives Werkzeug,
      aktive Ebene, Auswahlanzahl, Snap-Status, Speicherstatus/Autosave und
      Validierungswarnungen anzeigen. Kritische Warnungen farblich rechts buendeln.

- [x] Sprache vereinheitlichen.
      Aktuell mischen UI-Texte Englisch und Deutsch, z. B. "Recover" neben
      "Abbrechen" oder deutsche Tooltip-Fragmente. Eine Sprachstrategie festlegen:
      entweder voll Englisch oder voll Deutsch, mit Begriffstabelle fuer Tool,
      Layer, Export, Map, Room, Symbol, History.

## Mittlere Prioritaet

- [x] Properties-Panel fuer Auswahl fokussieren.
      Bei einer Auswahl sollte sofort ein kompaktes Eigenschaften-Panel sichtbar
      werden: Typ, Position, Groesse, Rotation, Layer, Farbe, Sichtbarkeit,
      Export/Player-visible. Mehrfachauswahl zeigt Batch-Aktionen wie Align,
      Distribute, Group, Lock und Layer wechseln.

- [x] Symbolbrowser visuell staerken.
      Die Symbolgruppen als Icon-Tabs oder Segmented Control anzeigen, darunter
      Suche, Filter und Raster/List-Umschalter. Symbolkacheln sollten echte
      Vorschauen, Favorit, zuletzt genutzt, Custom/Missing-Indikator und
      Drag-to-canvas unterstuetzen. Aktionen wie PNG/SVG/Set/Repair in ein
      kleines Menue auslagern, damit das Raster ruhiger bleibt.

- [x] Farb- und Stilpanel nach Paint.NET-Vorbild anbieten.
      Ein dockbares Colors/Style-Panel mit Primaer-/Sekundaerfarbe, aktuellen
      Swatches, gespeicherten Paletten, Hintergrund/Floor/Grid/Text/Selection und
      Style Templates. Farbbuttons sollten Farbflaechen zeigen, nicht nur Text.

- [x] Minimap als Navigator-Panel behandeln.
      Die Minimap sollte denselben Panel-Stil wie Layers/History bekommen:
      Titelleiste, Pin/Dock, Layer-Filter, Viewport-Rechteck, Klick-zum-Springen
      und optional transparenter Floating-Modus.

- [x] View- und Workspace-Presets einfuehren.
      Paint.NET bleibt uebersichtlich, weil Bildbearbeitung im Vordergrund steht.
      OSR Map Maker hat mehr Domaenen. Sinnvolle Workspaces waeren "Drawing",
      "Symbols", "Campaign", "Export/VTT" und "Print". Jeder Workspace schaltet
      passende Panels ein und blendet Nebensachen aus.

- [x] Menues neu sortieren.
      Eine klarere Desktop-Struktur verwenden: File, Edit, View, Map, Layer,
      Tools, Export, Help. Layer-Aktionen gehoeren in Layer, Export/VTT-Aktionen
      in Export, Kartenstruktur in Map. So wird die Menueleiste erwartbarer.

- [x] Context Menus konsequenter nutzen.
      Rechtsklick auf Canvas, Auswahl, Layer, History, Symbol, Map-Tab und
      Navigator-Eintrag sollte direkte, kontextpassende Aktionen bieten. Dadurch
      muessen weniger Buttons dauerhaft sichtbar bleiben.

- [x] Zoom-Bedienung praezisieren.
      Neben Slider und Fit-Buttons ein Zoom-Dropdown mit 25/50/75/100/150/200 %,
      Fit Map, Fit Selection und Fit Width. Der aktuelle Prozentwert sollte auch
      in der Statusleiste klickbar sein.

- [x] Auswahl- und Handle-Design modernisieren.
      Selektionsrahmen, Resize-Handles, Polygonpunkte, Rotationsgriff und Hover
      sollten einheitlich blau, gut kontrastiert und bei hohem Zoom nicht zu gross
      wirken. Multi-Selection bekommt eine eigene Rahmenfarbe oder leichte
      Binnenmarkierungen.

- [x] Live-Preview fuer Stil, Export und Generatoren staerken.
      Paint.NET lebt von direktem Feedback. Style Templates, Exportprofile,
      VTT-Audience, Random Dungeon und Effekte sollten eine kleine Vorschau mit
      Apply/Cancel oder Vorher/Nachher-Diff bekommen, bevor sie committen.

- [x] Notifications und Toasts standardisieren.
      Toasts unten rechts im Canvas zeigen, mit einheitlichen Farben fuer Info,
      Erfolg, Warnung und Fehler. Lange Fehler bleiben im Dialog oder in einem
      Validation-Panel, kurze Statusmeldungen gehoeren in die Statusleiste.

- [x] Panel-Layout speichern und zuruecksetzen.
      Nutzer sollten das Layout nach Wunsch arrangieren koennen. Einstellungen:
      Dockposition, Panelgroesse, Sichtbarkeit, Workspace, Toolbarposition.
      Zusaetzlich ein Befehl "Reset Window Layout".

## Niedrigere Prioritaet / Feinschliff

- [x] App-Theme definieren.
      Ein konsistentes helles Theme mit neutralen Flaechen, dezenter
      System-Akzentfarbe und gutem Kontrast. Spaeter optional Dark Theme. Wichtig:
      keine zu stark blau dominierte UI, weil die Karte selbst visuell sprechen
      soll.

- [x] High-DPI und Skalierung pruefen.
      Buttons, Icons, Canvas-Handles, Panelbreiten und Schriftgroessen auf 100 %,
      125 %, 150 % und kleinen Laptop-Displays pruefen. Mindestgroessen fuer
      Iconbuttons und Scrollbereiche festlegen.

- [x] Empty States fuer leere Panels gestalten.
      Leere History, keine Auswahl, keine Suchtreffer, fehlende Custom Symbols
      und leere Navigator-Listen sollten knapp, ruhig und handlungsorientiert
      aussehen. Keine langen Erklaertexte im Arbeitsbereich.

- [x] Dirty-/Autosave-Zustaende sichtbar machen.
      Im Fenstertitel, Map-Thumbnail-Tab und Statusbar anzeigen, ob ungespeicherte
      Aenderungen oder ein aktueller Autosave existieren. Nach Autosave kurze
      Statusmeldung statt stoerendem Dialog.

- [x] Dialoge vereinheitlichen.
      Export, Shortcuts, Autosave Recovery, Project Settings, Asset Library und
      Validation sollten dieselbe Button-Reihenfolge, Padding, Titelstruktur und
      Fehlermeldungslogik nutzen.

- [x] Tastaturbedienung sichtbarer machen.
      Tooltips, Menues und Command Palette zeigen Shortcuts. In Panels klare
      Fokusrahmen, Enter/Space-Aktivierung und Pfeilnavigation beibehalten.

- [x] Icons fuer globale Aktionen einfuehren.
      Speichern, Oeffnen, Export, Undo, Redo, Suche, Zoom, Fit, Lock, Sichtbarkeit,
      Layer hoch/runter und Loeschen sollten vertraute Symbole erhalten. Text nur
      dort nutzen, wo die Aktion sonst nicht eindeutig ist.

- [x] Performance als Designmerkmal behandeln.
      Paint.NET betont Geschwindigkeit. OSR Map Maker sollte UI-Aktionen sofort
      rueckmelden: Canvas-Redraw inkrementell halten, lange Exporte/Generatoren
      mit Progress anzeigen, Panels nicht beim Tippen sichtbar ruckeln lassen.

- [x] Review- und Validation-Hinweise visuell trennen.
      Nicht jede Warnung muss modal sein. Ein kleines Warning-Symbol in der
      Statusleiste kann ein Validation-Panel oeffnen, in dem Probleme nach Asset,
      Layer, Export und Campaign gruppiert sind.

## Konkrete erste Umsetzungsschritte

- [x] Eine kleine UI-Spezifikation anlegen: Farben, Abstaende, Buttonhoehen,
      Icongroessen, Panel-Titelleisten, aktive Zustaende, Fokusrahmen.
- [x] Den rechten Inspector testweise in drei sichtbare Dock-Panels umbauen:
      Symbols, Layers, Properties. History als viertes optionales Panel.
- [x] Map-Thumbnail-Tabs ueber dem Canvas prototypisieren.
- [x] Werkzeugoptionen aus Toolbar/Map-Tab in eine kontextuelle Optionsleiste
      verschieben.
- [x] Layers- und History-Panel optisch an Paint.NET annaehern.
- [x] Statusleiste erweitern und die Top-Leiste vereinfachen.
- [x] Danach Usability-Runde: Ein Nutzer soll in unter 60 Sekunden Raum,
      Korridor, Tuer, Nummer, Layerwechsel, Undo und Export finden koennen.

## Referenzpunkte aus Paint.NET

- Paint.NET beschreibt seine UI als schnell lernbar und intuitiv.
- Die Bild-/Dokumentnavigation nutzt Tabs mit Live-Thumbnails statt nur Text.
- Layers und History sind zentrale, sichtbare Arbeitsfenster.
- History ist nicht nur Undo/Redo, sondern ein nachvollziehbarer Verlauf.
- Werkzeuge bleiben einfach erreichbar, waehrend fortgeschrittene Funktionen in
      Menues, Panels und Dialogen liegen.
- Performance und unmittelbares Feedback sind Teil der Produktwirkung.

Referenz: https://paint.net/ und https://paint.net/features.html

## Performance- und Effizienzvorschlaege

Ziel: Die App soll auch bei grossen Karten, vielen Symbolen, Underlays,
mehreren Floors und Exportvorschauen fluessig bleiben. Die folgenden Punkte
basieren auf einer Code-Sichtung von `osr_map_maker.py`, besonders den Pfaden
`redraw`, `render_tk`, Hit-Testing, Snapping, Autosave und Export.

## Performance: Hohe Prioritaet

- [x] `redraw()` in Canvas-Redraw und Panel-Refresh aufteilen.
      Aktuell loescht `redraw()` den ganzen Canvas, rendert neu und aktualisiert
      danach Selection-Panel, Objektliste, Navigator, Toolbar, Status und
      Minimap. Bei Drag, Hover und Measure sollten nur Canvas/Overlay neu
      gezeichnet werden; Objektliste, Navigator und Inspector reichen bei
      Auswahlwechsel, Projektstruktur-Aenderungen oder Mouse-Release.

- [x] Redraws aus Mausbewegungen zusammenfassen und begrenzen.
      `on_motion` und `on_drag` rufen haeufig direkt `redraw()` auf. Eine
      `schedule_redraw(reason)`-Methode mit `after_idle` oder einem 16-ms-Timer
      kann doppelte Redraws pro Event-Flut verwerfen und die UI auf ca. 60 FPS
      begrenzen. Fuer Live-Drag reicht oft ein schneller Overlay-Redraw.

- [x] Canvas in Tags/Layer zerlegen statt immer `canvas.delete("all")`.
      Sinnvolle Tags waeren `background`, `grid`, `underlays`, `floor`,
      `objects`, `selection`, `hover`, `draft`, `guides` und `minimap`.
      Unveraenderte Tags koennen stehen bleiben; beim Verschieben einer Auswahl
      muessen nur betroffene Objekte und Overlays aktualisiert werden.

- [x] Grid, Hintergrund und Workspace-Bounds cachen.
      `draw_tk_grid` erzeugt bei jedem Redraw alle Grid-Linien neu. Fuer grosse
      Karten und Subgrid ist das teuer. Eine Tk-PhotoImage- oder Canvas-Tag-Cache
      pro `settings`/Zoom/Viewport wuerde Dragging und Hover deutlich
      beschleunigen. Alternativ nur Grid-Linien im sichtbaren Viewport zeichnen.

- [x] Sichtbarkeits- und Layerdaten pro Renderdurchlauf vorberechnen.
      `should_render_object` ruft pro Objekt `project_layer_visible` auf, das
      wiederum die Layerliste durchsucht. Im Player-Preview-Fall wird zudem
      `hidden_player_room_ids` pro Objekt neu berechnet. Ein Render-Kontext mit
      `visible_layer_ids`, `layer_opacity_by_id` und `hidden_player_room_ids`
      macht diese Pruefungen O(1) statt wiederholt O(n).

- [x] Spatial Index mit Dirty-Version statt JSON-Signatur invalidieren.
      `current_spatial_index()` berechnet ueber `spatial_index_signature()` eine
      JSON-Signatur aller Objekt-Bounds und Layerzustaende. Das passiert im
      Select-Modus beim Hover/Hit-Test und kann bei vielen Objekten teurer sein
      als der eigentliche Index. Besser: `project_revision` und
      `spatial_index_revision` fuehren und nur bei Objekt-/Layer-Aenderungen neu
      bauen.

- [x] Objekt-Bounds und Objekt-Lookups cachen.
      Viele Pfade scannen `project["objects"]` oder berechnen `bounds(obj)`
      wiederholt: Auswahl, Hit-Test, Minimap, `canvas_size`, Export-Frame,
      Snapping und Objektliste. Ein invalidierbarer Cache fuer `object_by_id`,
      `bounds_by_id`, `selected_objects` und optional `objects_by_layer` wuerde
      viele lineare Suchlaeufe entfernen.

- [x] Objekt-Snapping vorberechnen.
      `object_alignment_guides` wird bei Object-Snap aus allen Objekten neu
      erzeugt. Beim Start eines Drags koennen X-/Y-Guides fuer alle nicht
      bewegten Objekte einmal gebaut und danach wiederverwendet werden. Fuer
      sehr grosse Karten sollten Guides nach Achsenwerten oder Buckets
      abfragbar sein, statt jede Bewegung alle Guides zu pruefen.

## Performance: Mittlere Prioritaet

- [x] Underlay-Bilder und transformierte PhotoImages cachen.
      `draw_tk_underlays` laedt, resized, rotiert und konvertiert Underlays beim
      Redraw. Cache-Schluessel: Underlay-ID oder Pfad/Embedded-Hash, Zoom,
      Groesse, Rotation und Opacity. Dasselbe lohnt sich fuer Pillow-Export,
      besonders bei grossen eingebetteten Bildern.

- [x] Symbol-Rendering fuer Tk cachen.
      Custom Symbols werden zwar als PIL-Bilder geladen gecacht, aber
      Styling/Opacity/Outline/Shadow und `ImageTk.PhotoImage` entstehen beim
      Canvas-Redraw erneut. Rotierte Built-in-Symbole werden ebenfalls per
      Pillow neu gerendert. Ein Symbol-PhotoImage-Cache pro
      Kind/Groesse/Rotation/Farbe/Opacity/Style wuerde Karten mit vielen
      Symbolen spuerbar entlasten.

- [x] Floor-Geometrie und Grid-Segmente cachen.
      `floor_polygon_points`, `floor_grid_segments`, Cave-Punkte, Rotation und
      interne Bodenraster werden beim Rendern mehrfach berechnet. Pro Objekt-ID,
      Objekt-Revision, Cellsize/Zoom und relevanten Style-Optionen cachen. Das
      ist besonders fuer Caves, Rounds, rotierte Raeume und Cave-Corridors
      nuetzlich.

- [x] `canvas_size` cachen.
      `canvas_size(project, scale, include_legend)` laeuft ueber alle Objekte
      und wird waehrend Redraw, Minimap, Zoom, Export und Fit-Funktionen mehrfach
      aufgerufen. Ein Cache pro Project-Revision, Scale und Legend-Flag reicht
      aus; bei Objektbewegung oder Settings-Aenderung wird er invalidiert.

- [x] Minimap-Redraw entkoppeln und drosseln.
      `redraw()` ruft immer `redraw_minimap()` auf, und die Minimap iteriert
      wieder ueber alle Objekte. Die Minimap sollte bei Drag/Hover nur gedrosselt
      aktualisiert werden, z. B. alle 100-200 ms, und bei reinem Viewport-Scroll
      nur das Viewport-Rechteck neu zeichnen.

- [x] Exportvorschau mit Cache und niedriger Preview-Aufloesung rendern.
      Der Exportdialog rendert nach Optionsaenderungen ein komplettes Bild und
      skaliert es danach. Fuer Vorschauen reicht eine reduzierte Render-Skala
      oder ein gecachter Preview-Render pro Optionshash/Project-Revision.
      Lange Preview-Render sollten abbrechbar sein oder in einem Worker laufen.

- [x] Autosave UI-schonender machen.
      `run_autosave()` prueft Dirty-State ueber einen kompletten kanonischen
      JSON-Vergleich und schreibt dann zwei pretty-printed JSON-Dateien. Besser:
      Autosave nur bei geaenderter `project_revision`, Snapshot auf dem UI-Thread
      erzeugen, Datei-I/O in einen Worker auslagern und fuer Autosave kompaktes
      JSON ohne `indent=2` nutzen.

- [x] Undo/Redo von Vollprojekt-Snapshots auf gezielte Diffs pruefen.
      Viele Aktionen rufen `project_snapshot()` vor und nach der Aenderung auf;
      das serialisiert das gesamte Projekt per JSON. Fuer grosse Projekte waeren
      Command-Diffs oder objektbezogene Vorher/Nachher-Snapshots deutlich
      sparsamer. Als Zwischenschritt: nur betroffene Map/Objekte snapshotten.

- [x] Static-Layer-Cache auf die Tk-Vorschau erweitern.
      Fuer Pillow-Export existiert bereits ein Static-Layer-Cache. Derselbe
      Ansatz waere fuer die interaktive Tk-Canvas sinnvoll: statische Layer als
      Bitmap oder unveraenderte Canvas-Tags halten und nur dynamische Layer,
      Auswahl und Overlays neu zeichnen.

## Performance: Niedrigere Prioritaet / Messbarkeit

- [x] Performance-Benchmarks fuer echte UI-Szenarien ergaenzen.
      Bestehende Tests decken grosse Bounds, viele Symbole, Spatial Index und
      Static-Layer-Cache ab. Ergaenzen: Redraw einer 5.000-Objekt-Karte, Drag mit
      100 selektierten Objekten, Player-Preview, Object-Snap, Minimap und
      Autosave eines Projekts mit eingebetteten Symbolen.

- [x] Kleine Profiling-Helfer einbauen.
      Ein optionaler Dev-Modus kann Zeiten fuer `redraw`, `render_tk`,
      `draw_tk_grid`, `draw_tk_floor_objects`, `draw_tk_object`,
      `redraw_minimap`, `project_snapshot` und `render_image` in der Statuszeile
      oder Konsole ausgeben. So werden Performance-Regressions schnell sichtbar.

- [x] Layer- und Objektlisten nur bei Daten-Aenderung neu fuellen.
      `refresh_object_list` baut Labels und Gruppen neu auf und nutzt dabei
      `object_label`, das wiederum `index(obj)` und Layernamen berechnet. Die
      Liste sollte nur bei Objekt-/Filter-/Auswahl-Aenderung refreshen, nicht bei
      jedem Canvas-Redraw.

- [x] Projektdateien fuer grosse Assets standardmaessig komprimiert anbieten.
      Bei vielen eingebetteten Symbolen und Underlays sind `.osrmapz`-Dateien
      effizienter. Die App kann frueher und deutlicher empfehlen, komprimiert zu
      speichern, und Autosave-Versionen bei sehr grossen Projekten optional
      seltener schreiben.

- [x] Hilfsfunktionen fuer Layer-Zugriff vereinheitlichen.
      `layer_state`, `layer_name`, `layer_id_from_name`,
      `project_layer_visible` und `project_layer_opacity` suchen jeweils linear.
      Zentrale Layer-Indizes vermeiden Duplikate und beschleunigen Render,
      Inspector, Object List und Export.

## Empfohlene Reihenfolge

- [x] Zuerst messen: Profiling-Helfer und Benchmarks fuer Redraw, Drag,
      Player-Preview, Snapping und Autosave anlegen.
- [x] Danach Redraw entkoppeln: Canvas-only-Redraw, `schedule_redraw` und
      Panel-Refresh nur bei echten Daten-/Auswahl-Aenderungen.
- [x] Anschliessend Index- und Kontext-Caches: `object_by_id`, `bounds_by_id`,
      Layer-Maps, Render-Kontext, Spatial-Index-Revision.
- [x] Danach Bild-/Geometrie-Caches: Grid, Underlays, Symbole, Floor-Geometrie,
      Static-Layer fuer Tk.
- [x] Zum Schluss Export/Autosave/Undo optimieren, weil diese Pfade weniger
      haeufig sind, aber bei grossen Projekten stark blockieren koennen.
