# OSR Map Maker: Verbesserungs- und Erweiterungsplan

## Aktueller Umsetzungsstand – 2026-09-09

Dieser Abschnitt dokumentiert den Stand der neuen Aufgaben aus `Tasks.md`.
`[x]` bedeutet umgesetzt und geprüft; `[ ]` bedeutet weiterhin offen.
Die ursprüngliche Funktionsübersicht in den Abschnitten 1–7 bleibt erhalten.

- [x] **TASK-01 – Atomisches Speichern** (2026-09-06): JSON, komprimierte
  Projekte und Autosaves werden über eine temporäre Datei, Flush, `fsync` und
  atomisches Ersetzen gespeichert. Fehler erhalten die bisherige Datei,
  ungespeicherte Änderungen und Wiederherstellungsstände.
- [x] **TASK-02 – Projektbezogene Wiederherstellung** (2026-09-06): Stabile
  Projektkennung, getrennte Sitzungsverzeichnisse, Auswahl älterer lesbarer
  Autosaves und gezieltes Verwerfen einzelner Stände. Andere Projekte und
  Sitzungen bleiben bei der Bereinigung erhalten.
- [x] **TASK-03 – Externe Dateiänderungen erkennen** (2026-09-09): Fingerabdruck
  des tatsächlich geladenen beziehungsweise gespeicherten Dateiinhalts.
  Konfliktdialog mit Kopie, Neuladen, bewusstem Überschreiben und Abbrechen;
  Neuladen erfordert eine Entscheidung über lokale Änderungen. Erneute Prüfung
  unmittelbar vor dem Ersetzen schützt auch vor Änderungen während des Schreibens.
- [x] **TASK-04 – Batch-Export mit Ergebnisplan** (2026-09-09): Sichtbare
  Zielpfade mit Umbenennen, Überspringen oder Überschreiben vorhandener Dateien;
  interne Namenskollisionen bekommen eindeutige Suffixe. Atomare Einzeldateien,
  Schutz vor Änderungen nach der Vorschau und eine dauerhafte Ergebnisliste
  mit Erfolgen, übersprungenen Dateien und Fehlern. Aktives Projekt und aktive
  Karte bleiben nach dem Export erhalten.
- [x] **TASK-05 – Lange Aufgaben unterbrechbar ausführen** (2026-09-12):
  Snapshot-Worker für Autosave/Batch, Queue- und `after()`-Rückmeldung,
  Cancel zwischen atomaren Dateien sowie sicherer Close-Pfad. Veraltete
  Autosave-Ergebnisse können keine neue Revision als gespeichert markieren.
- [x] **TASK-06 – Spielersicht über alle Exportwege konsistent prüfen**
  (2026-09-12): Raster-/SVG-/Handout- und VTT-Export verwenden denselben
  Player-Filter; versteckte Inhalte und GM-Laufzeitdaten fehlen aus Playerdaten.
- [ ] **TASK-07 – Visuelle Regressionen zwischen Renderern erkennen.**
- [ ] **TASK-08 – VTT-Exporte anhand echter Importabläufe abnehmen.**
- [x] **TASK-09 – Ressourcenbedarf vor Laden und Rendern prüfen** (2026-09-12):
  konfigurierte Datei-/Archivgrenzen und Raster-Schätzung mit Skalierungs- oder
  Kachelentscheidung vor der Speicherallokation.
- [ ] **TASK-10 – Reproduzierbare Installation und Windows-Paket anbieten.**
- [ ] **TASK-11 – Implementierungen in eigenständige Module aufteilen.**
- [ ] **TASK-12 – Automatisierte Qualitätsprüfung und Abnahme ausbauen.**

Prüfnachweise: `tests/test_storage_recovery.py` für TASK-01/02 und
`tests/test_save_conflicts_batch.py` für TASK-03/04. Die Tests umfassen
Schreibfehler, externe Änderungen, getrennte Sitzungen, beschädigte Autosaves,
Namenskollisionen, Teilerfolge sowie Aktionen in echten Tk-Dialogen.
Gesamtprüfung über `scripts/quality.ps1`; die vorhandenen Tests bleiben erhalten.

## 1. Ausgangspunkt

Der aktuelle OSR Map Maker ist eine Python-Desktop-App mit Tkinter-Oberflaeche und Pillow-Export. Vorhanden sind:

- Leere Startkarte mit einstellbarer Groesse.
- Zeichenwerkzeuge fuer Raeume, Korridore, diagonale Korridore, Rundraeume und Hoehlen.
- Schwebende Basiswerkzeugleiste auf der Karte und Symbolbrowser im rechten Panel mit uebergeordneten Symbolgruppen und Untersymbolen.
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
- Symbolsuche im rechten `Symbols`-Tab.
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

Als nächster Schritt folgt **TASK-05** aus `Tasks.md`: Autosave und längere
Exporte auf konsistenten Snapshots ausführen, geeignete Arbeit aus dem
Tk-Hauptthread auslagern und einen reagierenden Fortschritts-/Abbruchablauf
ergänzen. Die atomaren Schreibpfade und der überprüfbare Batch-Plan stehen
dafür bereit. TASK-05 ist noch nicht umgesetzt.
