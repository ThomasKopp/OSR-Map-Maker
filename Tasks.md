# UI-Verbesserungsvorschlaege fuer OSR Map Maker

Orientierung: Paint.NET wirkt stark, weil die Arbeitsflaeche im Zentrum bleibt,
Werkzeuge schnell erreichbar sind, Ebenen und Verlauf als eigene Arbeitsfenster
sichtbar sind und haeufige Aktionen ohne langes Suchen funktionieren. OSR Map
Maker sollte diese Prinzipien auf Kartenbau, Symbole, Layer, Kampagnennotizen
und Export/VTT-Workflows uebertragen.

## Leitprinzipien

- [ ] Canvas-first: Die Karte bleibt immer der visuelle Mittelpunkt. Panels und
      Werkzeugleisten unterstuetzen die Arbeit, sie dominieren sie nicht.
- [ ] Sofort lernbar: Die wichtigsten Aktionen sollen durch Icon, Tooltip,
      Shortcut und Statuszeile verstaendlich sein, ohne lange Hilfetexte im UI.
- [ ] Schnelle Wege fuer haeufige Aufgaben: Zeichnen, Auswaehlen, Layer wechseln,
      Symbol platzieren, Undo/Redo, Zoom und Export brauchen direkte Kontrollen.
- [ ] Paint.NET-aehnliche Fensterlogik: Tools, Layers, History, Colors/Style,
      Symbols und Navigator koennen gedockt, schwebend, geschlossen und wieder
      eingeblendet werden.
- [ ] Ruhige Windows-Desktop-Aesthetik: klare Linien, neutrale Flaechen,
      konsistente Abstaende, Segoe-UI-Typografie, deutliche aktive Zustaende.
- [ ] Weniger Registerkarten-Tiefe: Haefig genutzte Panels sollten direkt
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

- [ ] App-Theme definieren.
      Ein konsistentes helles Theme mit neutralen Flaechen, dezenter
      System-Akzentfarbe und gutem Kontrast. Spaeter optional Dark Theme. Wichtig:
      keine zu stark blau dominierte UI, weil die Karte selbst visuell sprechen
      soll.

- [ ] High-DPI und Skalierung pruefen.
      Buttons, Icons, Canvas-Handles, Panelbreiten und Schriftgroessen auf 100 %,
      125 %, 150 % und kleinen Laptop-Displays pruefen. Mindestgroessen fuer
      Iconbuttons und Scrollbereiche festlegen.

- [ ] Empty States fuer leere Panels gestalten.
      Leere History, keine Auswahl, keine Suchtreffer, fehlende Custom Symbols
      und leere Navigator-Listen sollten knapp, ruhig und handlungsorientiert
      aussehen. Keine langen Erklaertexte im Arbeitsbereich.

- [ ] Dirty-/Autosave-Zustaende sichtbar machen.
      Im Fenstertitel, Map-Thumbnail-Tab und Statusbar anzeigen, ob ungespeicherte
      Aenderungen oder ein aktueller Autosave existieren. Nach Autosave kurze
      Statusmeldung statt stoerendem Dialog.

- [ ] Dialoge vereinheitlichen.
      Export, Shortcuts, Autosave Recovery, Project Settings, Asset Library und
      Validation sollten dieselbe Button-Reihenfolge, Padding, Titelstruktur und
      Fehlermeldungslogik nutzen.

- [ ] Tastaturbedienung sichtbarer machen.
      Tooltips, Menues und Command Palette zeigen Shortcuts. In Panels klare
      Fokusrahmen, Enter/Space-Aktivierung und Pfeilnavigation beibehalten.

- [ ] Icons fuer globale Aktionen einfuehren.
      Speichern, Oeffnen, Export, Undo, Redo, Suche, Zoom, Fit, Lock, Sichtbarkeit,
      Layer hoch/runter und Loeschen sollten vertraute Symbole erhalten. Text nur
      dort nutzen, wo die Aktion sonst nicht eindeutig ist.

- [ ] Performance als Designmerkmal behandeln.
      Paint.NET betont Geschwindigkeit. OSR Map Maker sollte UI-Aktionen sofort
      rueckmelden: Canvas-Redraw inkrementell halten, lange Exporte/Generatoren
      mit Progress anzeigen, Panels nicht beim Tippen sichtbar ruckeln lassen.

- [ ] Review- und Validation-Hinweise visuell trennen.
      Nicht jede Warnung muss modal sein. Ein kleines Warning-Symbol in der
      Statusleiste kann ein Validation-Panel oeffnen, in dem Probleme nach Asset,
      Layer, Export und Campaign gruppiert sind.

## Konkrete erste Umsetzungsschritte

- [ ] Eine kleine UI-Spezifikation anlegen: Farben, Abstaende, Buttonhoehen,
      Icongroessen, Panel-Titelleisten, aktive Zustaende, Fokusrahmen.
- [x] Den rechten Inspector testweise in drei sichtbare Dock-Panels umbauen:
      Symbols, Layers, Properties. History als viertes optionales Panel.
- [ ] Map-Thumbnail-Tabs ueber dem Canvas prototypisieren.
- [x] Werkzeugoptionen aus Toolbar/Map-Tab in eine kontextuelle Optionsleiste
      verschieben.
- [ ] Layers- und History-Panel optisch an Paint.NET annaehern.
- [ ] Statusleiste erweitern und die Top-Leiste vereinfachen.
- [ ] Danach Usability-Runde: Ein Nutzer soll in unter 60 Sekunden Raum,
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
