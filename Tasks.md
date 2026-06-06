# OSR Map Maker: Neue GUI- und Funktionsvorschlaege

Diese Liste baut auf dem aktuellen Stand der App auf. Viele Punkte aus dem alten Plan sind bereits umgesetzt; die folgenden Aufgaben sind als neue, offene Roadmap gedacht.

## Leitlinien

- [ ] Bedienung schneller machen: haeufige Aktionen sollen ohne Dialogsuche erreichbar sein.
- [ ] Panels kontextsensitiver machen: nur relevante Felder zeigen, aber Detailbearbeitung nicht verstecken.
- [ ] Kartenarbeit fehlertoleranter machen: mehr Vorschau, Validierung und Wiederherstellung.
- [ ] Export- und VTT-Workflows reproduzierbarer machen: Profile, Pruefungen und klare Zielsysteme.
- [ ] Das grosse `osr_map_maker.py` schrittweise in kleinere Module aufteilen, ohne laufende Features zu brechen.

## GUI-Verbesserungen

### Hauptlayout und Navigation

- [x] Rechtes Inspector-Panel resizable machen und Breite pro Projekt oder global speichern.
- [x] Inspector-Tabs in sinnvolle Gruppen trennen: `Build`, `Inspect`, `Campaign`, `Export`, `Project`.
- [x] Optionalen kompakten Modus fuer kleine Bildschirme einfuehren, bei dem Symbolbrowser und Inspector einklappbar sind.
- [x] Eine Command-Palette einbauen, z. B. fuer Werkzeuge, Exportprofile, Kartenwechsel, Symbolsuche und Einstellungen.
- [x] Aktuelle Karte/Etage als Breadcrumb oder gut sichtbaren Titel oberhalb der Arbeitsflaeche anzeigen.
- [x] Minimap einklappbar machen und mit Zoom-Rechteck, sichtbarem Ausschnitt und Layer-Filter ausstatten.
- [x] Statusleiste erweitern um aktuelles Werkzeug, Rasterposition, Auswahlanzahl, Zoomwert und Speicherstatus.
- [x] Globale Suche anbieten, die Objekte, Raeume, Symbole, Marker, Zonen und Karten findet.

### Werkzeugleiste

- [x] Werkzeugleiste frei andockbar machen: oben, links oder schwebend auf der Karte.
- [x] Aktives Werkzeug staerker hervorheben und den zuletzt genutzten Submodus direkt sichtbar machen.
- [x] Werkzeuggruppen einklappbar machen, damit Basiswerkzeuge, Formen, Marker und Messwerkzeuge nicht konkurrieren.
- [x] Kleine Dropdowns fuer Werkzeugvarianten einbauen, z. B. Tuerart, Linienart, Raumform oder Symbolgroesse.
- [x] Doppelklick auf ein Werkzeug als "Werkzeugoptionen" verwenden.
- [x] Tooltips um Shortcut, letzte Nutzung und wichtigsten Modus ergaenzen.
- [x] Werkzeugleiste per Tastatur fokussierbar machen.

### Canvas und direkte Bearbeitung

- [x] Hover-Highlight fuer das Objekt unter dem Mauszeiger anzeigen, bevor geklickt wird.
- [x] Auswahlgriffe visuell nach Typ unterscheiden: Skalieren, Rotieren, Punktbearbeitung, Link-Endpunkte.
- [x] Snap-Vorschau anzeigen, z. B. Rasterpunkt, Objektkante oder Mittelpunkt.
- [x] Smart Guides fuer Ausrichtung an Objektkanten, Mittelpunkten und gleichen Abstaenden einbauen.
- [x] Beim Ziehen numerische Live-Masse direkt am Objekt anzeigen.
- [x] Fit-to-map, Fit-to-selection und 100-Prozent-Zoom als Buttons und Shortcuts anbieten.
- [x] Canvas-Hintergrund fuer Player-/GM-Vorschau schnell umschaltbar machen.
- [x] Fokusmodus fuer grosse Karten anbieten: nur aktive Ebene oder aktive Zone hervorheben.
- [x] Sichtbare Arbeitsbereichsgrenzen und Exportbereiche deutlicher markieren.
- [x] Optionales Pixel-/Druckraster fuer hochaufloesende Exporte anzeigen.

### Inspector und Objektbearbeitung

- [x] Selection-Panel in Abschnitte gliedern: Position, Groesse, Darstellung, Inhalt, Links, Export.
- [x] Boolean-Felder als Checkboxen anzeigen statt als Texteingabe, z. B. `export`, `shadow`, `outline`, `playerVisible`.
- [x] Zahlenfelder mit Steppern, Min/Max und Einheit versehen.
- [x] Rotation, Deckkraft, Linienbreite und Skalierung zusaetzlich als Slider anbieten.
- [x] Farbfelder als klickbare Swatches anzeigen und zuletzt genutzte Farben direkt anbieten.
- [x] Multi-Selection-Inspector fuer gemeinsame Eigenschaften einfuehren, z. B. Ebene, Farbe, Deckkraft, Exportflag.
- [x] Konfliktanzeige fuer gemischte Werte in Mehrfachauswahl anzeigen.
- [x] Text-, Raum- und GM-Notizfelder als groessere Editor-Dialoge mit Markdown-Vorschau oeffnen.
- [x] Fehlerhafte Eingaben direkt am Feld markieren statt nur in der Statuszeile zu melden.
- [x] Undo-Gruppierung fuer fortlaufende Inspector-Aenderungen einfuehren, damit ein Slider nicht hunderte History-Eintraege erzeugt.

### Symbolbrowser

- [x] Symbole per Drag-and-drop aus dem Browser auf die Karte ziehen.
- [x] Symbolbrowser als Grid/List-Ansicht umschaltbar machen.
- [x] Symbolsuche um Filterchips fuer Gruppe, Tags, Favoriten, Custom und zuletzt genutzt erweitern.
- [x] Preview-Popover mit Varianten, Tags, Legendenname und Standardgroesse anzeigen.
- [x] Favoriten und zuletzt genutzte Symbole getrennt darstellen.
- [x] Symbolgruppen per Drag-and-drop sortierbar machen.
- [x] Custom-Symbolverwaltung mit Umbenennen, Tag-Bearbeitung, Variantenloeschen und Dateipfad-Reparatur ergaenzen.
- [x] Warnsymbol anzeigen, wenn eine Custom-Symbol-Datei fehlt oder nicht geladen werden kann.
- [x] Symbol-Set-Import mit Vorschau und Konfliktloesung anbieten.

### Ebenen, Objekte und Navigator

- [x] Layers-Panel als Tabelle mit Sichtbarkeit, Lock, Export-Opacity und Anzahl Objekte darstellen.
- [x] Ebenen per Drag-and-drop sortieren und Objekt-Z-Reihenfolge sichtbar machen.
- [x] Objekte als Baum anzeigen, inklusive Gruppen, Karten, Zonen und Ebenen.
- [x] Objektliste um Mehrfachauswahl, Kontextmenue und Batch-Aktionen erweitern.
- [x] Navigator nach Typen gruppieren: Ansichten, Marker, Zonen, Exportrahmen, Floor-Links.
- [x] Navigator-Elemente umbenennen und farblich markieren koennen.
- [x] Doppelklick-Aktionen konsistent machen: Jump, Auswahl und optional Zoom-to-fit.

### Dialoge und Feedback

- [x] Exportdialog mit groesserer, zoombarer Vorschau und Warnungen zu Aufloesung, Dateigroesse und transparentem Hintergrund erweitern.
- [x] Batch-Exportdialog mit Dateinamen-Vorschau und Zielordner-Pruefung bauen.
- [x] Projektvalidierung als Dialog mit kopierbarer Liste, Schweregrad und "zum Objekt springen" anzeigen.
- [x] Autosave-Wiederherstellung mit Vorher/Nachher-Metadaten und Dateipfad anzeigen.
- [x] Einheitliche Dialogbuttons verwenden: `Abbrechen`, `Anwenden`, `Speichern`, `Exportieren`.
- [x] Toast- oder Inline-Meldungen fuer erfolgreiche Aktionen anzeigen, damit modale Dialoge seltener noetig sind.

### Accessibility und Lokalisierung

- [x] Alle Buttons und Panels per Tastatur erreichbar machen.
- [x] Fokusrahmen, Tab-Reihenfolge und Screenreader-Labels pruefen.
- [x] Mindestgroessen fuer Buttons und Eingabefelder definieren.
- [x] Farbige Statusanzeigen immer mit Text oder Icon kombinieren.

## Funktionsverbesserungen

### Zeichen- und Bearbeitungsworkflow

- [x] Copy/Paste ueber Karten und Projekte hinweg unterstuetzen, inklusive Custom-Symbol-Referenzen.
- [x] Paste-at-cursor einfuehren, damit eingefuegte Objekte direkt an der Mausposition erscheinen.
- [x] Duplizieren mit wiederholbarem Offset anbieten.
- [x] Nudge per Pfeiltasten und schnelles Nudge per Shift/Ctrl ergaenzen.
- [x] Gruppen transformieren: skalieren, drehen, spiegeln und proportional anpassen.
- [x] Mehrfachauswahl als wiederverwendbare Vorlage speichern koennen.
- [x] Raum- und Korridorkanten automatisch verschmelzen, wenn sie exakt aneinanderliegen.
- [x] Ueberlappende Flaechen optional bereinigen, damit interne Linien sauber verschwinden.
- [x] Boolean-Operationen fuer Raumformen pruefen: Vereinen, Subtrahieren, Schnittmenge.
- [x] Freihand-Zeichenmodus fuer Hoehlen, Wasser und Markierungen anbieten.
- [x] Pinselwerkzeug fuer Wandstil, Bodenmarkierung oder schwieriges Gelaende einfuehren.
- [x] Polygonpunkt-Bearbeitung mit Punktliste im Inspector synchronisieren.
- [x] Objektrotation um frei waehlbaren Pivot ergaenzen.

### Kartenstruktur

- [x] Karten-Templates fuer Dungeon, Stadt, Overland, Hexmap und leere Skizze anbieten.
- [x] Projektweite Einstellungen von kartenbezogenen Einstellungen deutlicher trennen.
- [x] Karten/Etagen in Ordner oder Kapitel gruppieren.
- [x] Floor-Link-Uebersicht bauen, die fehlende oder kaputte Links markiert.
- [x] Etagenvergleich einbauen: darunterliegende Etage als halbtransparentes Overlay anzeigen.
- [x] Kartenmassstab pro Karte und optional pro Zone speichern.
- [x] Zonenhierarchie ermoeglichen, z. B. Dungeon > Tempelbezirk > Krypta.
- [x] Exportrahmen mit Seitenformaten koppeln, z. B. A4, Letter, Foundry Scene, Roll20 Page.

### Raum- und Kampagnenarbeit

- [x] Raumformular mit Vorlagen fuer typische OSR-Raeume erweitern.
- [x] Markdown-Vorschau fuer Raumtexte, Handouts und GM-Notizen anbieten.
- [x] Raumstatus visuell auf der Karte codieren, optional nur im GM-Modus.
- [x] Automatische Raumnummerierung mit Praefix, Suffix und Zonenbereich verbessern.
- [x] Raumlisten-Ansicht mit Sortierung nach Nummer, Zone, Status, Gefahr und Spieler-Sichtbarkeit bauen.
- [x] Encounter-/Loot-Tabellen aus Markdown oder CSV importieren.
- [x] Zufallsinhalte mit Seed speichern, damit Ergebnisse nachvollziehbar bleiben.
- [x] Beziehungen zwischen Raeumen speichern: Fraktion, Hinweis, Schluessel, Quest, Geheimtuer.
- [x] Handout-Export separat erzeugen, ohne GM-Notizen und versteckte Informationen.
- [x] GM-Booklet mit Templates fuer Kurzform, Volltext und Session-Prep anbieten.
- [x] Kampagnenbericht mit offenen TODOs, fehlenden Raumnummern und ungenutzten Symbolnotizen erweitern.

### Prozedurale Werkzeuge

- [x] Generatoren mit Seed-Feld, Vorschau und "erneut wuerfeln"-Button versehen.
- [x] Generatoren sollen bestehende Auswahl/Zonen respektieren und optional nur dort arbeiten.
- [x] Diff-Vorschau fuer Generatorergebnisse anzeigen, bevor Objekte uebernommen werden.
- [x] Dungeon-Generator um Themenprofile erweitern: Krypta, Mine, Festung, Kanalisation, Zaubererlabor.
- [x] Natural-Cave-Generator mit Wasser, Engstellen, Hoehenstufen und Sackgassenoptionen ausbauen.
- [x] Automatische Tuerplatzierung mit Mindestabstand und Tuerwahrscheinlichkeit pro Wandtyp verbessern.
- [x] Automatische Lichtquellen fuer VTT aus Raumtyp, Symbolen und Wandtyp ableiten.
- [x] Patrouillenrouten mit Wegpunkten, Timing und Begegnungstabelle verbinden.
- [x] "Map cleanup" als Werkzeug anbieten: kleine Artefakte entfernen, Kanten runden, Rasterausrichtung pruefen.

### Export und VTT

- [x] Exportprofile im Projekt und optional global speichern.
- [x] Exportprofile duplizieren, loeschen und als Standard markieren.
- [x] Export vor dem Speichern validieren: leere Auswahl, fehlender Frame, riesige Aufloesung, fehlende Assets.
- [x] Dateinamen-Templates anbieten, z. B. `{project}_{map}_{audience}_{profile}`.
- [x] Batch-Export mit mehreren Karten/Etagen kombinieren.
- [x] Player-Export als Vorschau im Canvas anzeigen.
- [x] Foundry-Export um Walls, Doors, Lights, Notes und Scene-Metadaten erweitern.
- [x] Roll20-Export um Page-Groesse, Grid, Dynamic-Lighting-Hinweise und Layer-Zuordnung verbessern.
- [x] Fantasy-Grounds-Exportprofil pruefen und dokumentieren.
- [x] SVG-Export mit CSS-Klassen, Titel/Description und stabilen IDs fuer Nachbearbeitung erweitern.
- [x] PDF-Export mit Seitenumbruch fuer grosse Karten und Kartenatlas-Modus ausbauen.
- [x] WebP/JPEG-Export mit sichtbarer Qualitaetszahl neben dem Slider anzeigen.

### Speichern, Laden und Sicherheit

- [x] Autosave-Versionen mit Zeitstempel statt nur einer Datei aufbewahren.
- [x] Projektdateien optional komprimiert speichern, wenn viele Custom-Symbole eingebettet werden.
- [x] Beim Laden fehlende Custom-Symbole reparieren: Ordner suchen, Pfad ersetzen, Symbol aus Projekt entfernen.
- [x] Projektvalidierung als eigener Menuepunkt mit Reparaturvorschlaegen anbieten.
- [x] Backups vor groesseren Migrationsschritten automatisch anlegen.
- [x] Speichern unter neuem Namen als klare Aktion in Menue und Toolbar anbieten.
- [x] Zuletzt geoeffnete Projekte im File-Menue anzeigen.
- [x] Crash-Recovery mit Projektname, letzter Aenderung und Objektanzahl anzeigen.

### Tastatur und Produktivitaet

- [x] Shortcut-Editor um Konfliktwarnungen und Reset-auf-Standard erweitern.
- [x] Shortcut-Presets fuer Zeichenmodus, VTT-Workflow und Laptop ohne Maus anbieten.
- [x] Wiederholbare letzte Aktion einfuehren, z. B. "noch eine Tuer dieses Typs".
- [x] Quick-actions per Kontextmenue und Command-Palette angleichen.
- [x] Objektaktionen per `/` oder `Ctrl+K` suchbar machen.
- [x] Temporare Werkzeuge per gehaltenem Shortcut einfuehren, z. B. Space fuer Pan.

## Funktionserweiterungen

### Neue Kartentypen und Inhalte

- [x] Hexmap-Modus mit Hexraster, Terrain-Symbolen und Koordinaten einfuehren.
- [x] Stadtplan-Modus mit Strassen, Gebaeuden, Bezirken und POI-Markern pruefen.
- [x] Overland-Modus mit Hoehenlinien, Wegen, Flusssystemen und Landmarken ergaenzen.
- [x] Isometrische oder Seitenansicht-Symbole als optionale Symbolsets vorbereiten.
- [x] Kartenunterlage als Bild importieren und abpausen koennen.
- [x] Rasterausrichtung fuer importierte Bildunterlagen anbieten.
- [x] Procedural texture fills fuer Stein, Erde, Wasser, Holz und Lava ergaenzen.

### Asset- und Symbolsystem

- [x] Symbolpacks mit Manifest, Lizenzhinweis und Preview-Bild definieren.
- [x] Custom-Symbole optional ins Projekt einbetten, damit Dateien portabel bleiben.
- [x] Farbvarianten fuer Built-in-Symbole als Palette speichern.
- [x] Symbol-Aliase erlauben, z. B. `secret door` findet `one_way_secret_door`.
- [x] Symbol-Metadaten um VTT-Rolle erweitern: Door, Wall, Light, Hazard, Spawn, Note.
- [x] Automatische Legendenkategorien pro Projekt editierbar machen.
- [x] Kleine Asset-Bibliothek fuer Papiertexturen, Kartenstempel und Rahmen anbieten.

### Kollaboration und Review

- [x] Projektkommentare als nicht exportierbare Review-Notizen einfuehren.
- [x] Aenderungslog im Projekt speichern: Autor, Zeit, Kurzbeschreibung.
- [x] Zwei Projektdateien vergleichen und Unterschiede als Liste ausgeben.
- [x] Review-Export erzeugen, der neue/geaenderte Objekte seit einem Snapshot markiert.
- [x] Snapshot-Bookmarks fuer wichtige Versionen innerhalb eines Projekts anbieten.

### Druck und Publishing

- [x] Drucklayout-Editor fuer Titel, Legende, Massstab, Copyright und Seitenzahlen bauen.
- [x] Kartenatlas-Modus fuer mehrere Exportrahmen in einer PDF-Datei ergaenzen.
- [x] One-page-dungeon-Layout mit Karte plus Raumliste anbieten.
- [x] Spielerhandouts als separates PDF mit freigegebenen Texten und Bildern exportieren.
- [x] Print-Proof-Ansicht mit Beschnitt, Rand und DPI-Warnung anzeigen.

### Spieltisch- und VTT-Hilfen

- [x] Fog-of-war-Masken aus Raeumen, Tueren und Sichtblockern ableiten.
- [x] Sichtlinien-Test fuer VTT-Walls im Canvas anzeigen.
- [x] Lichtreichweiten und Dunkelheitszonen visuell simulieren.
- [x] Encounter-Startpunkte mit Token-Anzahl und Fraktion verbinden.
- [x] Zufallstabellen direkt aus Raum oder Zone wuerfeln und Ergebnis speichern.
- [x] Session-Modus pruefen: Player-View, GM-View und schnelle Statusupdates.

## Technische Verbesserungen

### Architektur

- [x] Datenmodell, Validierung und Migrationen vollstaendig aus `osr_map_maker.py` nach `models.py` ziehen.
- [x] Tk-Rendering, Pillow-Rendering und SVG-Export klar trennen.
- [x] UI-Aufbau in Komponenten aufteilen: Toolbar, Inspector, Symbolbrowser, Navigator, Exportdialog.
- [x] Commands fuer Undo/Redo vereinheitlichen und History-Transaktionen unterstuetzen.
- [x] Projektoperationen als testbare Services kapseln.
- [x] Konstanten, Defaultwerte und Symboldefinitionen in eigene Module verschieben.

### Tests

- [x] Tests fuer GUI-unabhaengige Inspector-Validierung schreiben.
- [x] Tests fuer Exportprofile, Batch-Export und Dateinamen-Templates erweitern.
- [x] Tests fuer Autosave-Versionierung und Wiederherstellung ergaenzen.
- [x] Tests fuer VTT-Export mit Walls, Doors, Lights und Player-Sichtbarkeit ausbauen.
- [x] Regressionstests fuer Copy/Paste, Gruppentransform und Multi-Selection einfuehren.
- [x] Snapshot-Tests fuer SVG-Ausgabe mit stabilen IDs pruefen.

### Performance

- [x] Canvas-Redraw auf sichtbaren Ausschnitt begrenzen.
- [x] Statische Layer als Cache rendern und nur bei Aenderung neu zeichnen.
- [x] Symbolbilder und Custom-SVG-Rasterungen mit Groesse, Rotation und Variante cachen.
- [x] Objekt-Hit-Detection mit raeumlichem Index beschleunigen.
- [x] Grosse Projekte mit 10.000+ Objekten als Performance-Szenario testen.
- [x] Exportvorschau entkoppeln oder debouncen, damit Dialoge fluessig bleiben.

### Qualitaet und Wartbarkeit

- [x] Typisierung mit `mypy` oder `pyright` schrittweise pruefen.
- [x] Linting/Formatting als Skript oder Make-Task dokumentieren.
- [x] README mit aktueller Featureliste, Screenshots und typischen Workflows aktualisieren.
- [x] Architekturentscheidung fuer Projektformat und Exportformat dokumentieren.
- [x] Beispielprojekte fuer Dungeon, Stadt, Hexmap und VTT-Export anlegen.

## Priorisierte naechste Umsetzung

1. [x] Inspector verbessern: Boolean-Felder, Slider, Farbswatches und bessere Feldvalidierung.
2. [x] Command-Palette plus globale Suche fuer Werkzeuge, Objekte, Karten und Exportprofile bauen.
3. [x] Exportdialog aufwerten: groessere Vorschau, Validierung, Dateinamen-Templates und Profilverwaltung.
4. [x] Symbolbrowser modernisieren: Drag-and-drop, Filterchips, Variantenverwaltung und fehlende Assets reparieren.
5. [x] Canvas-Bearbeitung verbessern: Hover-Highlight, Smart Guides, Snap-Vorschau und Live-Masse.
6. [x] Autosave-Versionierung und zuletzt geoeffnete Projekte einfuehren.
7. [ ] Batch-Export ueber mehrere Karten/Etagen inklusive Player-/GM-/Gridless-Ausgaben erweitern.
8. [x] Code modularisieren, beginnend mit Inspector, Exportdialog und Symbolbrowser.

## Kleine, schnell umsetzbare Wins

- [x] Zoomwert als Prozentzahl neben dem Slider anzeigen.
- [x] Buttons fuer `Fit map`, `Fit selection` und `100%` ergaenzen.
- [x] Export-Qualitaet als Zahl neben JPEG-/WebP-Slidern anzeigen.
- [x] `Save As` und `Recent Projects` ins File-Menue aufnehmen.
- [x] Im Selection-Panel `export` und `playerVisible` als Checkboxen anzeigen.
- [x] Fehlende Custom-Symbole in Symbolbrowser und Statuszeile deutlicher markieren.
- [x] Objektliste mit `Select all visible` und `Invert selection` erweitern.
- [x] Aktives Werkzeug in der Statusleiste inklusive Shortcut anzeigen.
- [x] Drag-to-pan mit Space-Taste als temporaeres Werkzeug einbauen.
- [x] Projektvalidierung als Menuepunkt `Tools > Validate Project` anbieten.
