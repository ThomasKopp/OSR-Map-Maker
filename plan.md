# OSR Map Maker: Verbesserungs- und Erweiterungsplan

## 1. Ausgangspunkt

Der aktuelle OSR Map Maker ist eine Python-Desktop-App mit Tkinter-Oberflaeche und Pillow-Export. Vorhanden sind:

- Leere Startkarte mit einstellbarer Groesse.
- Zeichenwerkzeuge fuer Raeume, Korridore, diagonale Korridore, Rundraeume und Hoehlen.
- Zweistufiges linkes Symbolpanel mit uebergeordneten Symbolgruppen und Untersymbolen.
- Auswahl, Verschieben, Loeschen und Bearbeitung im rechten Panel.
- Maus-Pan, Mausrad-Zoom und Pfeil-hoch/runter-Zoom.
- Speichern/Laden als JSON.
- Export als PNG, JPEG und WebP.

Dieser Plan beschreibt sinnvolle Verbesserungen und Funktionserweiterungen fuer die naechsten Iterationen.

## 2. Hohe Prioritaet

### 2.1 Stabileres Undo/Redo

- Alle Aenderungen als Commands modellieren.
- Undo/Redo fuer Objektbearbeitung, Verschieben, Groessenaenderung, Farben, Karteneinstellungen und Laden/Speichern konsistent machen.
- Mehrfaches versehentliches History-Pushing beim Bearbeiten verhindern.

### 2.2 Bessere Auswahl und Bearbeitung

- Resize-Handles fuer Raeume, Korridore und Formen.
- Endpunkt-Handles fuer diagonale Korridore.
- Rotations-Handle fuer Symbole.
- Multi-Select per Shift-Klick.
- Auswahlrahmen fuer mehrere Objekte.
- Gruppieren und Entgruppieren.

### 2.3 Snap- und Rasteroptionen

- Snap-to-grid ein- und ausschaltbar machen.
- Snap-Schritt waehlbar: ganze Zelle, halbe Zelle, Viertelzelle.
- Sichtbares Haupt- und Unterraster.
- Optionales Ausrichten an Objektkanten.

### 2.4 Projektformat versionieren

- `schemaVersion` sauber migrieren.
- Projektvalidierung beim Laden erweitern.
- Fehlende Felder automatisch ergaenzen.
- Altdaten fuer alte Symbolnamen wie `secret`, `pit`, `column` in neue Namen migrieren.

### 2.5 Exportdialog ausbauen

- Export-Vorschau.
- Qualitaetsregler fuer JPEG/WebP.
- Transparenter Hintergrund fuer PNG/WebP.
- Option: Legende exportieren ja/nein.
- Option: Nur Kartenbereich, gesamte Seite oder Auswahl exportieren.
- Option: Druckrand und Titelbereich.

## 3. Mittlere Prioritaet

### 3.1 Ebenen

- Ebenen fuer Hintergrund, Raeume, Korridore, Symbole, Text, Legende und Notizen.
- Ebenen sichtbar/unsichtbar schalten.
- Ebenen sperren.
- Objekt in Ebene verschieben.
- Export nur sichtbarer Ebenen.

### 3.2 Stilvorlagen

- Blueprint-Stil als Standard.
- Schwarz/weiss-Druckstil.
- Pergamentstil.
- Dunkler VTT-Stil.
- Eigene Farben fuer Hintergrund, Boden, Linien, Text, Auswahl und Legende speichern.

### 3.3 Symbolverbesserungen

- Symbole skalieren und rotieren.
- Symbolfavoriten.
- Symbolsuche im linken Panel.
- Eigene Symbolgruppen anlegen.
- Eigene Symbole als SVG oder PNG importieren.
- Symbolvorschau mit grossem Preview beim Hover.

### 3.4 Textwerkzeuge

- Schriftart, Groesse, Farbe und Ausrichtung einstellbar.
- Textboxen mit Zeilenumbruch.
- Automatische Raumnummerierung mit Startwert.
- Nummernkreis fuer verschiedene Dungeonbereiche.
- Notiztext, der nicht exportiert wird.

### 3.5 Legende

- Legende automatisch aus verwendeten Symbolen erzeugen.
- Legende frei verschieben.
- Spaltenzahl und Groesse einstellen.
- Manuelle Legendeneintraege.
- Legende als eigenes Objekt behandeln.

## 4. Niedrige Prioritaet / Spaetere Erweiterungen

### 4.1 Prozedurale Hilfen

- Zufallsraeume erzeugen.
- Zufallskorridore und Verbindungsvorschlaege.
- Hoehlenraender verrauschen.
- Dungeon-Generator mit Raeumen, Korridoren und Tueren.
- Automatische Wand- und Tuerplatzierung.

### 4.2 VTT- und Publishing-Export

- Export mit transparentem Hintergrund fuer VTTs.
- Gridless Export.
- Foundry-/Roll20-kompatible Rastergroesse.
- PDF-Export fuer Druck.
- SVG-Export fuer verlustfreie Nachbearbeitung.

### 4.3 Kampagnenfunktionen

- Raumlisten mit Beschreibung, Inhalt, Gegnern und Schaetzen.
- Raumnummern mit Notizen verknuepfen.
- GM-Notizen getrennt von Spielerkarte.
- Spieler- und Spielleiter-Export.

## 5. UX-Verbesserungen

- Statuszeile mit Mausposition in Rasterkoordinaten.
- Mini-Map fuer grosse Karten.
- Bessere Cursor je nach Werkzeug.
- Tooltips mit kurzer Beschreibung und Tastaturkuerzel.
- Konfigurierbare Shortcuts.
- Kontextmenue per Rechtsklick.
- Schnellaktionen: Duplizieren, Nach vorne, Nach hinten, Sperren.
- Visuelle Fehlermeldungen statt nur Dialogboxen.

## 6. Technische Verbesserungen

### 6.1 Code-Struktur

Aktuell liegt viel Logik in `osr_map_maker.py`. Sinnvolle Aufteilung:

- `models.py`: Projektmodell, Objekte, Validierung, Migrationen.
- `render_tk.py`: Tkinter-Rendering.
- `render_pillow.py`: Export-Rendering.
- `symbols.py`: Symboldefinitionen und Zeichenroutinen.
- `commands.py`: Undo-/Redo-Commands.
- `app.py`: Hauptfenster und UI.
- `storage.py`: Speichern, Laden, Autosave.

### 6.2 Tests

- Unit-Tests fuer Projektvalidierung und Migration.
- Tests fuer Objekt-Bounds und Hit-Detection.
- Tests fuer Undo/Redo.
- Export-Smoke-Tests fuer PNG, JPEG und WebP.
- Symbol-Abdeckungstest: jedes Symbol muss in Tk und Pillow renderbar sein.

### 6.3 Performance

- Redraw nur fuer sichtbaren Kartenausschnitt pruefen.
- Caching fuer statische Objekte.
- Groessere Karten mit vielen Symbolen testen.
- Optional: Tile-basierter Canvas-Renderer.

## 7. Empfohlene Reihenfolge

1. Projektformat validieren und Migrationen einbauen.
2. Undo/Redo konsistent ueber Commands loesen.
3. Auswahl, Resize-Handles und diagonale Korridor-Endpunkte verbessern.
4. Exportdialog mit Vorschau und Optionen bauen.
5. Ebenen einfuehren.
6. Legende als bearbeitbares Objekt umsetzen.
7. Symbolsuche, Favoriten und eigene Symbole ergaenzen.
8. PDF/SVG/VTT-Export ergaenzen.

## 8. Konkrete naechste Aufgabe

Als naechster kleiner, wertvoller Schritt empfiehlt sich:

- Endpunkt-Handles fuer diagonale Korridore implementieren.
- Resize-Handles fuer Raeume und Korridore implementieren.
- Danach Undo/Redo fuer diese Bearbeitungen sauber absichern.

Das verbessert die direkte Zeichenarbeit deutlich, ohne die gesamte Architektur sofort umzubauen.
