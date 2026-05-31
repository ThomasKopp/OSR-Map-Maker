# OSR Map Maker

Python-Desktop-App zum Erstellen, Speichern, Laden und Exportieren von OSR-/Dungeon-Karten im Blueprint-Stil.

## Start

```powershell
python osr_map_maker.py
```

Die App nutzt Tkinter fuer die Oberflaeche und Pillow fuer den Export als PNG, JPEG und WebP.

Falls Pillow fehlt:

```powershell
python -m pip install pillow
```

SVG-Importe werden angezeigt, wenn `cairosvg` installiert ist; ohne diese optionale Bibliothek bleiben sie als gespeicherte Symboldefinition mit Fallback-Darstellung nutzbar.

## Bedienung

- Neue Projekte starten mit einer Karte und einer verschiebbaren Legende als eigenem Objekt.
- Die gesamte linke Seite ist ein zweistufiges Werkzeugpanel.
- Oben stehen Basiswerkzeuge und uebergeordnete Symbolgruppen; beim Klick auf eine Gruppe oeffnet sich darunter der Bereich mit den passenden Untersymbolen.
- Der Werkzeugname erscheint beim Hover.
- Raeume, Korridore, Rundraeume und Hoehlen per Ziehen erstellen.
- Einfache grafische Formen wie Rechtecke, Kreise und Linien per Ziehen erstellen; Polygone entstehen Punkt fuer Punkt und werden geschlossen, indem wieder auf den ersten Punkt geklickt wird.
- Beim Korridor-Werkzeug erzeugt horizontales oder vertikales Ziehen einen geraden Rasterkorridor; schraeges Ziehen erzeugt einen diagonalen Korridor.
- Symbole, Text und Nummern per Klick platzieren. Das aktuelle Werkzeug bleibt aktiv, das zuletzt platzierte Element bleibt ausgewaehlt.
- Mit `Select` Objekte anklicken, verschieben, im rechten Panel bearbeiten oder mit `Delete` loeschen.
- Im `Select`-Werkzeug mit `Shift` mehrere Objekte anklicken oder auf leerer Flaeche einen Auswahlrahmen ziehen.
- Ausgewaehlte Raeume, Korridore, Rundraeume und Hoehlen haben Resize-Handles; diagonale Korridore haben Endpunkt-Handles.
- Ausgewaehlte Formen lassen sich verschieben und bearbeiten; Linien haben Endpunkt-Handles, Rechtecke, Kreise und Polygone Resize-Handles.
- Neue Formen haben eigene Standardwerte fuer Strichdicke und Linienfarbe; pro Form lassen sich Strichdicke, Linienfarbe und optionale Fuellfarbe separat bearbeiten.
- Ausgewaehlte Symbole haben Skalierungs- und Rotations-Handles. Die Drehung wird gespeichert und gerendert.
- Mehrere ausgewaehlte Objekte koennen im rechten Panel gruppiert oder entgruppiert werden.
- Der rechte Bereich hat Tabs fuer Karte, Ebenen und Auswahl; Ebenen koennen sichtbar/unsichtbar oder gesperrt sein, und ausgewaehlte Objekte koennen in eine andere Ebene verschoben werden.
- Projekte koennen mehrere Karten/Etagen enthalten; im Karten-Tab lassen sich Etagen anlegen, duplizieren, umbenennen, loeschen und wechseln.
- Treppen-, Portal- oder Markersymbole koennen im `Nav`-Tab mit einer Zielkarte verknuepft und direkt verfolgt werden.
- Der `Objects`-Tab bietet Suche, Typ-/Ebenenfilter und direkte Auswahl; ein Doppelklick springt zum Objekt.
- Der `Nav`-Tab speichert Ansichten, Sprungmarken und benannte Zonen; Zonen koennen aus der Auswahl oder dem aktuellen Sichtfenster erzeugt werden.
- Stilvorlagen fuer Blueprint, Schwarz/weiss-Druck, Pergament und dunkles VTT stehen im Karten-Tab; eigene Farben fuer Hintergrund, Boden, Linien, Text, Auswahl und Legende werden gespeichert.
- Optional koennen Koordinaten am Kartenrand, benannte Zonen und ein Lineal-Overlay eingeblendet werden.
- Links im Symbolpanel gibt es Suche nach Namen und Tags, Favoritenfilter, Favoriten-Toggle, eigene Gruppen, PNG-/SVG-Importe, Varianten und Symbolset-Import/Export. Beim Hover erscheint eine groessere Symbolvorschau.
- Die eingebauten Symbolgruppen decken Tueren/Barrieren, Fallen/Gefahren, Magie/Mysterien, Natur, Dungeon-Objekte, Gameplay-Marker sowie Stadt-/Overland-Symbole ab.
- Symbole lassen sich per Handle skalieren und rotieren; Groessen-Presets, Zufallsvarianten, eigene Farbe, Deckkraft, Schatten und Outline koennen pro Symbol gesetzt werden.
- Textobjekte koennen Schriftart, Groesse, Farbe, Ausrichtung und Textboxbreite speichern. `Note` erzeugt nicht exportierbare Notiztexte.
- Nummern nutzen den Startwert und optionalen Bereichscode aus dem Karten-Tab, sodass getrennte Nummernkreise moeglich sind.
- Die Legende wird automatisch aus verwendetem Kartenmassstab und nach Gruppen sortierten Symbolen erzeugt, kann verschoben/resized werden und unterstuetzt Spaltenzahl, Skalierung, manuelle Eintraege und eigene Legendennamen.
- Der Karten-Tab enthaelt prozedurale Aktionen fuer Zufallsraeume, Korridore, bestaetigbare Verbindungsvorschlaege, Cave-Roughening, parametrisierte Dungeon-Generierung, Stichwort-Dungeons, natuerliche Hoehlen, automatische Tueren, Wandstile und Patrouillenrouten.
- Der `Campaign`-Tab enthaelt das Raumformular, automatische Raumnummerierung, Nummernluecken-Erkennung, Begegnungstabellen, Zufallsinhalte und den GM-Booklet-Export.
- Raeume speichern Kampagnendaten: Nummer, Name, Status, Beschreibung, Inhalt, Gegner, Schaetze, Loot-Tabelle, Fallen, Vorlesetext, Geruechte, Hinweise, Geheimnisse, Spielerhandout, GM-Notizen und Sichtbarkeit fuer Spieler.
- Symbole koennen ebenfalls Geruechte, Hinweise, Geheimnisse, Handout-Text und GM-Notizen speichern.
- Der Raumreport exportiert Inhaltsverzeichnis, Symbollegende, Begegnungstabellen, Raumtexte, verknuepfte Symbolnotizen und fehlende Custom-Symbol-Dateien als Markdown.
- Nummern werden beim Platzieren mit dem darunterliegenden Raum verknuepft, wenn ein Raum getroffen wird.
- VTT-Optionen unterstuetzen gridless Export sowie Foundry- und Roll20-Presets. `Player Export` blendet nicht exportierbare Notizen und GM-only Raeume aus; `GM Export` zeigt alles Sichtbare.
- Snap-to-grid, Snap-Schritt, Haupt-/Unterraster und optionales Ausrichten an Objektkanten stehen im rechten Panel.
- Das `Measure`-Werkzeug misst Segmentdistanz, Weglaenge und Flaeche in Rasterzellen und im eingestellten Realweltmassstab.
- Mittlere oder rechte Maustaste verschiebt die Karte in jedem Werkzeug.
- Mit dem Mausrad oder den Pfeiltasten hoch/runter zoomen.
- Projekte koennen als `.osrmap.json` gespeichert und geladen werden.
- Projektdateien verwenden `schemaVersion`; alte Symbolnamen wie `secret`, `pit` und `column` werden beim Laden migriert.
- Export unterstuetzt PNG, JPEG, WebP, PDF und SVG mit 1x bis 4x Skalierung, Vorschau, Qualitaet, transparentem PNG/WebP-Hintergrund, Legendenschalter, Grid-Schalter, Karten-/Seiten-/Auswahlbereich sowie Druckrand und Titelbereich.
