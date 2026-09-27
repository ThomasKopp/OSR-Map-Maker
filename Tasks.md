# UI-Verbesserungsvorschlaege fuer OSR Map Maker

## Ergänzungen: Bedienbarkeit, GUI-Übersicht und Funktionalität – 2026-09-13

Grundlage: Abgleich der bestehenden Aufgaben mit `README.md`, `UI_SPEC.md`
und den GUI-Abläufen in `osr_map_maker.py`. Die folgenden Punkte sind offene
Vorschläge, keine bestätigten GUI-Fehler und keine Umsetzungsnachweise. Eine
interaktive GUI-Abnahme gehört zur späteren Umsetzung. Bereits vorhandene
Funktionen werden gezielt erweitert; die bisherigen Aufgaben bleiben erhalten.

Prioritäten: P1 = Schutz der Arbeitsergebnisse, P2 = verlässliche tägliche
Nutzung, P3 = Komfort und Funktionsausbau. Aufwand: S = lokal begrenzt,
M = mehrere Abläufe, L = strukturelle Änderung. Neue Aufgaben laufen als
TASK-13 bis TASK-27 weiter; alle bleiben bis zur Umsetzung und Abnahme offen.

### Bedienbarkeit: präziser auswählen, navigieren und bearbeiten

- [x] **TASK-13: Überlappende Objekte gezielt auswählen.** P2 · Aufwand: M.
  Die bestehende Auswahl um eine Aktion „Objekt unter Maus auswählen“ im
  Kontextmenü ergänzen. Treffer mit Typ, Name, Layer und Sperrstatus auflisten;
  beim Überfahren eines Eintrags das zugehörige Objekt vorübergehend umranden.
  Gesperrte Objekte dürfen inspiziert, aber nicht nebenbei entsperrt werden.
  **Akzeptanz:** Bei Raum, Symbol und Text an derselben Position lässt sich
  jedes Objekt mit der Maus eindeutig auswählen, ohne die anderen zu verschieben.
  Ausgeblendete Objekte werden nicht versehentlich als sichtbare Treffer angeboten.
  **Umgesetzt und geprüft am 2026-09-13:** Das Canvas-Kontextmenü enthält
  „Select object here“ mit allen sichtbaren Treffern in Vordergrundreihenfolge,
  Typ, Layer und Sperrhinweis. Gesperrte Objekte lassen sich dort ausschließlich
  zur Inspektion auswählen; normale Mausauswahl und Verschieben überspringen sie.
  `tests/test_task_13_14.py` prüft Überlappung, Reihenfolge, ausgeblendete
  Kandidatenlogik und die Inspektionsauswahl.

- [x] **TASK-14: Ursache blockierter Bearbeitung direkt erklären.** P2 · Aufwand: M.
  Bestehende Fehlerhinweise um eine kontextbezogene Erklärung für nicht mögliche
  Auswahl-, Zeichen- und Verschiebeaktionen erweitern: etwa gesperrtes Objekt,
  gesperrter Layer oder ungeeigneter Arbeitsmodus. Passende sichtbare Aktionen
  wie „Layer anzeigen“ oder „Zum Zeichnen wechseln“ anbieten. Entsperren bleibt
  eine ausdrückliche Nutzeraktion; Hinweise nach erfolgreicher Korrektur entfernen.
  **Akzeptanz:** Ein Platzierungsversuch auf einem gesperrten Layer nennt dessen
  Namen und bietet einen passenden Lösungsweg. Wiederholte Versuche erzeugen
  keine Folge identischer modaler Dialoge.
  **Umgesetzt und geprüft am 2026-09-13:** Zeichen- und Einfügeaktionen prüfen
  den aktiven Layer vor der Änderung. Der Status und ein nichtmodaler Hinweis
  nennen den gesperrten Layer; „Show layer“ öffnet dessen Verwaltung. Gesperrte
  Objekte lassen sich inspizieren, aber nicht über den Inspector ändern,
  verschieben, löschen oder in einen gesperrten Layer verschieben. Die
  Fehlermeldung ist nichtmodal und blockiert daher keine weiteren Eingaben.

- [x] **TASK-15: Scrollen in verschachtelten Panels eindeutig zuordnen.**
  P2 · Aufwand: M. Nacharbeit zur vorhandenen Panel- und Zoom-Bedienung:
  Das Mausrad soll zuerst die Liste beziehungsweise das Panel unter dem Zeiger
  bewegen. Erst an dessen Rand darf der umgebende Inspector weiterscrollen.
  Beim Wechsel zwischen schwebenden Panels, Dialogen und Canvas dürfen keine
  globalen Mausradbindungen hängen bleiben oder fremde Bindungen entfernen.
  **Akzeptanz:** Durch eine lange Symbol- oder Eigenschaftenliste scrollen,
  ein schwebendes Panel öffnen und schließen und anschließend auf dem Canvas
  zoomen: Jeder Schritt wirkt ausschließlich auf den erwarteten Bereich.
  **Umgesetzt und geprüft am 2026-09-13:** Eine einzige geroutete Mausradbindung
  prüft den sichtbaren Inspector unter dem Zeiger und scrollt nur diesen. Die
  bisherigen temporären globalen Bindungen und ihr `unbind_all()` sind entfernt;
  Canvas-Zoom und fremde Bindungen werden nicht überschrieben. Der gezielte Test
  prüft die Zuordnung eines Mausradereignisses zum einzigen passenden Panel.

- [x] **TASK-16: Numerische Eingaben mit Einheiten und relativen Werten erweitern.**
  P2 · Aufwand: M. Die vorhandene Feldvalidierung um eindeutige Einheiten für
  Position, Größe, Winkel und Deckkraft ergänzen. Dezimalkomma und Dezimalpunkt
  unterstützen. Für passende Felder eine explizite Auswahl „Absolut/Relativ“
  anbieten, damit etwa mehrere Objekte um zwei Rasterzellen wachsen können,
  ohne ihre unterschiedlichen Ausgangsgrößen zu verlieren.
  **Akzeptanz:** „1,5“ und „1.5“ ergeben denselben Wert. Eine relative Änderung
  wirkt nur auf das gewählte Feld; ungültige Werte verändern nichts. Eine
  Mehrfachänderung lässt sich mit einem Undo vollständig zurücknehmen.
  **Umgesetzt und geprüft am 2026-09-13:** Alle Inspector-Zahlenfelder
  akzeptieren Dezimalkomma und Dezimalpunkt. Für gemeinsame Mehrfachfelder
  Position, Größe, Symbolgröße und Drehung zeigt der Inspector „Absolute“ oder
  „Relative“; die Feldbeschriftung nennt Zellen beziehungsweise Grad. Relative
  Änderungen werden als ein gemeinsamer Verlaufsschritt geschrieben und wahren
  die individuellen Ausgangswerte. Tests prüfen beide Dezimalschreibweisen und
  eine Größenänderung zweier unterschiedlich großer Räume.

- [x] **TASK-17: Navigation mit Zurück-/Vorwärts-Verlauf ergänzen.**
  P3 · Aufwand: M. Zusätzlich zu gespeicherten Ansichten und Sprungmarken die
  zuletzt besuchten Karten und Ausschnitte als Navigationsverlauf anbieten.
  Sichtbare Zurück-/Vorwärts-Buttons führen nach Suchtreffern, Etagenlinks und
  Markersprüngen zum vorherigen Arbeitsort samt Zoom zurück. Normales Panning
  soll den Verlauf nicht mit jedem Mausereignis füllen.
  **Akzeptanz:** Nach einem Sprung über zwei Etagenlinks ist die ursprüngliche
  Ansicht wieder erreichbar. Gelöschte Ziele werden übersprungen; reine
  Navigation erzeugt weder Bearbeitungs-Undo-Schritte noch ungespeicherte Änderungen.
  **Umgesetzt und geprüft am 2026-09-13:** Die Command Bar enthält aktive
  Zurück-/Vorwärts-Buttons. Der Verlauf speichert Karte, Zoom und Ausschnitt
  vor Kartenwechseln, Suchtreffern, Markern und Etagenlinks. Gelöschte Karten
  werden beim Wiederherstellen übersprungen. Kartenwechsel und der Verlauf
  schreiben keine Dokumentänderung und keinen Undo-Schritt mehr. Die Tests
  prüfen den Rück-/Vorwärtsstapel sowie das Überspringen fehlender Ziele.

### GUI-Übersicht: Inhalte leichter finden und Zustände verstehen

- [x] **TASK-18: Eigenschaften nach Relevanz filtern und Favoriten anheften.**
  P2 · Aufwand: M. Die vorhandenen Abschnitte Position, Größe, Darstellung,
  Inhalt, Verknüpfungen und Export um eine Feldsuche und „Basis/Alle“ ergänzen.
  Häufig verwendete Felder lassen sich pro Objekttyp oben anheften. Suchfilter,
  ausgeblendete Abschnitte und Rückkehr zur vollständigen Ansicht bleiben
  erkennbar; vorhandene Mischwerte und Reset-Aktionen weiter unterstützen.
  **Akzeptanz:** Bei einem Raum sind Name, Nummer und Größe ohne lange Suche
  erreichbar. „GM“ findet die passenden Notizfelder. Ein Wechsel zur
  Mehrfachauswahl zeigt ausschließlich unterstützte gemeinsame Bearbeitungen.
  **Umgesetzt und geprüft am 2026-09-13:** Der Inspector hat eine Feldsuche,
  „Basic/All“ und pro Objekttyp anheftbare Felder (★). Basic zeigt die täglichen
  Eigenschaften; die Suche durchsucht immer den vollständigen Feldbestand,
  sodass „GM“ die GM-Notizen findet. Angeheftete Felder bleiben in Basic sichtbar.
  Die vorhandene Mehrfachauswahl bleibt auf gemeinsame Felder begrenzt. Tests
  prüfen Basisansicht, angeheftete Felder und die GM-Suche.

- [x] **TASK-19: Viele Karten in einer durchsuchbaren Projektübersicht verwalten.**
  P2 · Aufwand: M. Die vorhandenen Thumbnail-Tabs und Kartenordner um eine
  kompakte Übersicht mit Suche, Ordnerbaum und Sortierung ergänzen. Aktive
  Karte, gleichnamige Karten und Ordnerzugehörigkeit deutlich unterscheiden;
  Tabs bleiben für den schnellen Wechsel nutzbar.
  **Akzeptanz:** In einem Projekt mit 30 Karten lässt sich eine Karte nach
  Name oder Ordner finden und öffnen, ohne alle Tabs durchzuscrollen. Umbenennen
  und Verschieben erhalten bestehende Etagen- und Objektverknüpfungen.
  **Umgesetzt und geprüft am 2026-09-13:** Das Maps-Panel bietet Suche nach
  Kartenname, Ordner oder Kapitel, Sortierung nach Ordner/Name oder Name und
  eine gruppierte Ordneransicht. Die gefilterten Thumbnail-Treffer bleiben direkt
  anklickbar; die Auswahl zeigt weiterhin den eindeutigen Karten-ID-Suffix.
  Die bestehende Änderung von Namen/Ordnern bleibt Metadatenarbeit und erhält
  damit Etagen- und Objektverknüpfungen. Ein Test prüft Suche über Name, Ordner
  und Kapitel sowie die erwartete Sortierung.

- [x] **TASK-20: Persönliche Anordnung vor automatischen Panelwechseln schützen.**
  P2 · Aufwand: M. Die vorhandene Workspace-Automatik um „Panel angeheftet“
  und „Layout vorübergehend fixieren“ erweitern. Automatische Kontextwechsel
  dürfen angeheftete Panels nicht verdrängen. Manuell versteckte Panels nur
  gemäß einer sichtbaren, änderbaren Einstellung wieder öffnen; temporäre
  Änderungen nicht ungefragt als neues Workspace-Preset speichern.
  **Akzeptanz:** Ein angeheftetes History-Panel bleibt beim Wechsel zwischen
  Zeichnen, Symbolen und Auswahl sichtbar. Nach Aufheben der Fixierung arbeitet
  die Automatik wieder; ein Layout-Reset bleibt jederzeit erreichbar.
  **Umgesetzt und geprüft am 2026-09-13:** Jedes rechte Dock-Panel hat eine
  sichtbare Pin/Unpin-Aktion. Angeheftete Panels werden durch Workspace- und
  Werkzeugwechsel nicht versteckt. Manuelles Schließen wird als eigener Zustand
  gespeichert und von automatischen Kontextöffnungen respektiert; nach Unpin
  greift die Workspace-Automatik wieder. Die bestehende Layout-Wiederherstellung
  bleibt unverändert verfügbar. Der Test prüft den Erhalt des History-Panels
  beim Workspace-Wechsel sowie den Schutz einer manuellen Ausblendung.

- [x] **TASK-21: Sichtbarkeit und Exportteilnahme gemeinsam erklären.**
  P2 · Aufwand: M. Die bestehenden Layer-, Objekt- und Spieleroptionen durch
  eine lesbare Zusammenfassung im Inspector ergänzen: „Im Editor sichtbar“,
  „Im GM-Export enthalten“ und „Im Spielerexport enthalten“. Bei Ausschluss den
  wirksamen Grund nennen und zum zuständigen Feld führen. Die Zusammenfassung
  aus denselben Regeln wie die Vorschau und Exporte ableiten (Anschluss an TASK-06).
  **Akzeptanz:** Für eine Geheimtür, eine GM-Notiz und ein Objekt auf einem
  ausgeblendeten Layer ist nachvollziehbar, in welcher Ausgabe sie erscheinen.
  Änderungen aktualisieren Erklärung und Vorschau konsistent.
  **Umgesetzt und geprüft am 2026-09-13:** Der Selection-Inspector zeigt für
  ein einzelnes Objekt Editor, GM-Export und Spielerexport samt Einschluss- oder
  Ausschlussgrund. Die Zusammenfassung nutzt dieselben Layer-, Legenden-, Text-,
  Raum- und Geheimnisregeln wie `should_render_object()`; „Show export controls“
  führt direkt zu den zuständigen Eigenschaften. Die Logik wird mit verborgenem
  Layer, nicht exportiertem Text und Spieler-Ausschluss getestet.

- [x] **TASK-22: Kleine Fenster und Monitorwechsel mit klarer Überlaufregel behandeln.**
  P2 · Aufwand: M. Nacharbeit zum vorhandenen Kompaktmodus und DPI-Konzept:
  Wenn der Platz nicht reicht, seltene Leistenaktionen in ein beschriftetes
  „Weitere“-Menü verlagern. Primäre Aktionen und aktives Werkzeug sichtbar
  halten; Dialoginhalte bei Bedarf scrollen, ihre Abschlussbuttons erreichbar
  halten. Schwebende Panels nach Monitorwechsel in den sichtbaren Bereich holen.
  **Akzeptanz:** Bei 1050 × 720 Fenstergröße sowie 100, 150 und 200 Prozent
  Skalierung sind Speichern, Exportieren, Übernehmen und Abbrechen erreichbar.
  Abgezogene Zweitmonitore hinterlassen keine unerreichbaren Dialoge oder Panels.
  **Umgesetzt und geprüft am 2026-09-13:** Unter 1180 px Breite bleiben Save
  und Export sichtbar; New, Load, Undo/Redo, Zoom, Suche, Navigation und die
  Command-Palette wandern in das beschriftete „More“-Menü. Bei Größen- oder
  Monitorwechseln werden schwebende Werkzeug-/Navigator-Panels sowie offene
  Dialoge zurück in den sichtbaren Bereich verschoben. Bereits vorhandene
  scrollbare Inspector- und persistente Dialoglayouts halten ihre Inhalte und
  Abschlussaktionen zugänglich. Der Test prüft die feste Überlaufgrenze bei
  der Mindestfensterbreite 1050 px.

### Funktionalität: größere Projekte und wiederkehrende Abläufe unterstützen

- [x] **TASK-23: Globale Suche auf Inhalte aller Karten ausweiten.**
  P2 · Aufwand: M. Die bestehende Suche führt Karten bereits als Ziele auf;
  Objekt-, Raum-, Marker- und Zoneninhalte werden in `global_search_items()`
  aus dem aktiven Projektkontext gesammelt. Einen sichtbaren Suchbereich
  „Aktuelle Karte/Ganzes Projekt“ und Filter nach Treffertyp ergänzen. Ergebnisse
  mit Kartenname und Ordner anzeigen; erst beim Öffnen zur Zielkarte wechseln.
  **Akzeptanz:** Gleichnamige Räume auf zwei verschiedenen Karten sind eindeutig
  unterscheidbar. Ein Treffer auf einer inaktiven Karte öffnet und markiert das
  richtige Objekt. Die Suche selbst verändert keine Kartendaten; spielergerichtete
  Ansichten dürfen keine GM-Notizen über Treffertexte offenlegen.
  **Umgesetzt und geprüft am 2026-09-13:** Die globale Suche kann zwischen
  „Current map“ und „Whole project“ umschalten und nach Map, Object, Room,
  Marker, Zone oder Symbol filtern. Projektweite Treffer enthalten Karten- und
  Ordner-/Kapitelkontext; ihr Öffnen wechselt erst dann zur Zielkarte und markiert
  das Objekt beziehungsweise den Ausschnitt. In der Spieleransicht werden
  `gmNotes` nicht in die Suchtexte aufgenommen. Der Test prüft gleichnamige
  Räume auf zwei Karten, Karten-/Ordnerkontext und den Ausschluss einer GM-Notiz.

- [x] **TASK-24: Wiederverwendbare Werkzeugvorgaben speichern.**
  P3 · Aufwand: M. Zusätzlich zu Kartenstilen, Symbolfavoriten und Auswahlvorlagen
  benannte Vorgaben für Werkzeugparameter anbieten, etwa „Schmaler Gang“,
  „Naturhöhle“ oder „Raumbeschriftung“. Größe, Linien-/Füllstil und relevante
  Werkzeugoptionen speichern; vor Anwendung die enthaltenen Werte zeigen.
  Vorgaben lassen sich duplizieren, umbenennen und löschen.
  **Akzeptanz:** Eine gespeicherte Gangvorgabe ist nach einem Neustart verfügbar
  und auf einer anderen Karte nutzbar. Ihre Anwendung verändert vorhandene
  Objekte erst nach einer gesonderten, ausdrücklich gewählten Aktion.
  **Umgesetzt und geprüft am 2026-09-13:** Das Tool-Options-Menü speichert
  benannte Vorgaben für das aktive Werkzeug. Der Manager zeigt Werkzeug und alle
  enthaltenen Werte vor dem Anwenden und kann Vorgaben anwenden, duplizieren,
  umbenennen oder löschen. Gespeichert werden passende Fang-, Symbol-, Shape-,
  Text- und Bodenparameter im Projekt, daher stehen sie nach Speichern und
  Wiederöffnen auch auf anderen Karten zur Verfügung. Die Anwendung ändert nur
  die Vorgaben für künftige Platzierungen, keine vorhandenen Objekte; ein Test
  prüft Persistenz, Wiederanwendung und unveränderte Bestandsgeometrie.

- [x] **TASK-25: Underlays anhand zweier Referenzpunkte kalibrieren.**
  P3 · Aufwand: M. Die vorhandene Größen- und Rasterausrichtung um einen
  geführten Ablauf erweitern: zwei Punkte auf dem Bild markieren, bekannte
  Entfernung und Einheit eingeben, resultierenden Maßstab vorab anzeigen.
  Optional die Referenzlinie am Kartenraster ausrichten. Originalbild behalten;
  Kalibrierung als rückgängig machbare Transformation speichern.
  **Akzeptanz:** Eine eingescannte Karte mit bekannter Referenzstrecke kann
  ohne manuelles Ausprobieren skaliert werden. Eine Kontrollmessung entspricht
  der Eingabe innerhalb der angezeigten Rundung; Abbrechen erhält den alten Stand.
  **Umgesetzt und geprüft am 2026-09-13:** Map → „Calibrate Underlay“ bietet
  einen geführten Zwei-Punkt-Ablauf mit normierten Bildkoordinaten, bekannter
  Strecke in Zellen, Vorschau des resultierenden Maßstabs und optionaler
  Ausrichtung an der nächsten Rasterachse. Die Berechnung hält den ersten
  Referenzpunkt fest; erst „Apply“ schreibt die als Undo-Schritt gespeicherte
  Transformation. Cancel verändert die bestehende Referenz nicht. Der Test
  prüft Maßstab, Ankerpunkt und die unveränderte Quelle.

- [x] **TASK-26: Export als wiederholbaren Auftrag anbieten.**
  P2 · Aufwand: M. Auf Exportprofilen und dem geprüften Batch-Plan (TASK-04/05)
  aufbauen: Kartenwahl, Profile, Ausschnitte und Dateinamensschema als benannten
  Auftrag speichern. Vor jedem Lauf den konkreten Plan neu erzeugen. Fehlende
  Karten, gelöschte Rahmen, Zielkonflikte und Abweichungen vom Profil sichtbar
  machen; nach Abschluss Ausgabeordner und Ergebnisdateien direkt öffnen lassen.
  **Akzeptanz:** Ein Auftrag exportiert drei gewählte Karten jeweils für GM
  und Spieler mit sechs eindeutigen Zielen. Nach Änderung einer Karte nutzt
  der nächste Lauf deren aktuellen Stand; alte Konfliktfreigaben gelten nicht
  automatisch für neu hinzugekommene Dateien. Abbruch und Einzelfehler bleiben
  im Ergebnis nachvollziehbar. TASK-08 bleibt eine separate VTT-Live-Abnahme.
  **Umgesetzt und geprüft am 2026-09-13:** Batch Export kann die Zielmap-Auswahl
  (aktive Karte oder alle Karten), Zielordner, Konfliktregel und die enthaltenen
  GM-/Spieler-/Gridless-Profile als benannten Auftrag speichern und erneut laden.
  Jeder Lauf erzeugt vor dem Export einen aktuellen Konflikt- und Zielplan aus
  dem momentanen Projektstand; Fingerprints machen nachträgliche Zieländerungen
  sichtbar, Abbruch und Einzelfehler bleiben in der Ergebnisliste. Der Auftrag
  wird mit dem Projekt gespeichert. Tests prüfen seine Validierung und erhaltene
  Profile; die Batch-Tests decken eindeutige Ziele, Konflikte und Abbruch ab.

- [x] **TASK-27: Fehlende Assets gesammelt neu zuordnen.**
  P2 · Aufwand: M. Die vorhandene Symbolreparatur und Einbettung um eine
  gemeinsame Zuordnung für Symbole und Underlays erweitern. Nach Auswahl eines
  Ersatzordners Kandidaten mit Vorschau, Dateityp und betroffenen Verwendungen
  auflisten. Mehrdeutige Dateinamen ausdrücklich zur Auswahl stellen; erst nach
  Übernahme Pfade ändern. Anschließend optional das Einbetten anbieten.
  **Akzeptanz:** Ein Projekt mit verschobenem Assetordner lässt sich in einem
  Ablauf reparieren. Zwei gleichnamige Bilddateien werden nicht still vertauscht;
  nicht gefundene Dateien bleiben sichtbar. Abbrechen verändert keine Referenzen,
  und Speichern/Wiederöffnen erhält die übernommenen Zuordnungen.
  **Umgesetzt und geprüft am 2026-09-13:** Die Projektprüfung öffnet „Repair
  assets“ für fehlende Custom-Symbole und Underlays gemeinsam. Nach Auswahl
  eines Ordners zeigt jede Referenz Typ, bisherigen Pfad und alle passenden
  Kandidaten; doppelte Dateinamen bleiben ausdrücklich zur Auswahl, Einzeltreffer
  werden nur vorausgewählt. „Apply selected“ schreibt ausschließlich die
  ausgewählten Pfade als einen Undo-Schritt; nicht gefundene Referenzen bleiben
  sichtbar. Tests prüfen sowohl die unterlassene automatische Mehrdeutigkeits-
  zuordnung als auch die gemeinsame explizite Reparatur von Symbol und Underlay.

### Empfohlene Umsetzung und Abnahme

Zuerst TASK-13 bis TASK-16 sowie TASK-21 für sichere tägliche Bedienung angehen.
Danach TASK-18 bis TASK-20, TASK-22 und TASK-23 für Übersicht in größeren
Projekten; anschließend TASK-26/27 für wiederkehrende Dateiabläufe. TASK-17,
TASK-24 und TASK-25 als Komfortausbau einplanen. Bestehende offene Abnahmen
TASK-08 und TASK-10 bleiben unabhängig davon offen.

Jeden Punkt mit seinem konkreten Akzeptanzszenario abnehmen und Datum sowie
Nachweis ergänzen. Datenändernde Funktionen auf Undo/Redo und Speichern/
Wiederöffnen prüfen; für Auswahl, Navigation und Layout eine tatsächliche
GUI-Prüfung durchführen. Für die Gesamtabnahme dieselbe Beispielkarte mit
überlappenden Objekten, gesperrten Layern, GM-Inhalten und mehreren Etagen nutzen.
Ältere Erledigungsmarkierungen ersetzen diese neue Abnahme nicht.

## Neuer Verbesserungsbacklog – 2026-09-06

Grundlage: Sichtung des aktuellen Quellcodes, der Architektur, des Handbuchs
und der vorhandenen Tests. Keine interaktive GUI-Abnahme durchgeführt.
Die bisherigen Aufgaben und ihre Erledigungsmarkierungen bleiben erhalten.
Die folgenden offenen Aufgaben ergänzen sie; wo ein bereits behandeltes Thema
noch konkrete Lücken zeigt, ist dies ausdrücklich als Nacharbeit benannt.

Prioritäten: P1 = Schutz der Arbeitsergebnisse, P2 = verlässliche tägliche
Nutzung, P3 = Ausbau und einfachere Weiterentwicklung. Aufwand relativ:
S = lokal begrenzt, M = mehrere Abläufe, L = strukturelle Änderung.

### P1 – Speichern, Wiederherstellen und Export absichern

- [x] **TASK-01: Projektdateien und Autosaves atomar speichern.** Aufwand: M.
  `write_project_data()` öffnet die Zieldatei direkt zum Schreiben;
  `run_autosave()` schreibt ebenfalls direkt in die Wiederherstellungsdatei.
  Ein abgebrochener Schreibvorgang kann dadurch eine vorhandene Datei beschädigen.
  Zuerst eine temporäre Datei im Zielverzeichnis vollständig schreiben und
  schließen, anschließend das Ziel atomar ersetzen. Dieselbe Speicherlogik für
  JSON, komprimierte Projekte und Autosaves verwenden. Speicherfehler sichtbar
  behandeln; Dirty-State und Wiederherstellungsstände erst nach Erfolg ändern.
  **Akzeptanz:** Simulierte Schreib- und Ersetzungsfehler lassen das bisherige
  Projekt unverändert und ladbar. Die Oberfläche meldet keinen Speichererfolg;
  ungespeicherte Änderungen bleiben erkennbar. Beide Dateiformate sind getestet.
  **Umgesetzt und geprüft am 2026-09-06:** Gemeinsame atomare Schreibfunktion
  mit temporärer Datei, Flush, `fsync`, Schließen und `os.replace`; kompakter
  Autosave nutzt denselben Pfad. Speicherfehler liefern keinen Erfolg zurück,
  verhindern das Schließen nach fehlgeschlagenem Speichern und erhalten den
  bisherigen Speicherstatus sowie Recovery-Dateien. Fehlertests für partielle
  Schreibvorgänge, Flush, Ersetzen und Autosave-Versionen stehen in
  `tests/test_storage_recovery.py` (`AtomicStorageTests`).

- [x] **TASK-02: Wiederherstellung projektbezogen und fehlertolerant machen.**
  Aufwand: M. `check_autosave_recovery()` verwendet aktuell den ersten Kandidaten
  und beendet den Versuch bei einem Lesefehler. `clear_autosave()` räumt die
  Kandidaten im verwendeten Wiederherstellungsverzeichnis auf.
  Autosaves mit stabiler Projekt- und Sitzungskennung organisieren. Verfügbare
  Stände mit Projektname, Zeitpunkt und Lesbarkeitsstatus anbieten; bei einem
  beschädigten neuesten Stand einen älteren gültigen Stand auswählbar machen.
  Bereinigung nur auf das zugehörige Projekt beziehungsweise die Sitzung anwenden.
  **Akzeptanz:** Bei zwei Projekten und einem beschädigten neuesten Autosave ist
  der ältere gültige Stand wiederherstellbar. Speichern oder Verwerfen eines
  Projekts entfernt keine Wiederherstellungsstände des anderen.
  **Umgesetzt und geprüft am 2026-09-06:** Persistente `meta.projectId`, eigene
  Verzeichnisse je Sitzung und Bereinigung ausschließlich der eigenen Sitzung.
  Der Recovery-Dialog zeigt alle Stände mit Zeitpunkt und Lesbarkeit und wählt
  den neuesten lesbaren Stand vor. Alte Autosaves bleiben auffindbar. Verwerfen
  löscht nur den ausgewählten Stand; Wiederherstellen behält die Quelle und
  öffnet eine neue ungespeicherte Sitzung. Isolation, beschädigter neuester Stand,
  Projektwechsel sowie echte Tk-Dialogaktionen sind in
  `tests/test_storage_recovery.py` (`RecoveryIsolationTests`,
  `RecoveryDialogTests`) geprüft. Zusätzlich vollständigen App-Ablauf von
  Bearbeitung über Autosave und JSON-Speichern bis Recovery und ZIP-Speichern
  erfolgreich ausgeführt; Dokumentation aktualisiert.

- [x] **TASK-03: Externe Änderungen vor dem Überschreiben erkennen.** Aufwand: M.
  `write_project_file()` schreibt ohne Abgleich mit dem zuletzt geladenen
  Dateistand. Beim Laden und erfolgreichen Speichern einen Dateifingerabdruck
  merken und unmittelbar vor dem nächsten Speichern vergleichen. Bei Änderungen
  durch eine zweite App-Instanz oder Dateisynchronisierung die Optionen
  „Als Kopie speichern“, „Neu laden“ und „Bewusst überschreiben“ anbieten.
  **Akzeptanz:** Eine zwischenzeitlich extern geänderte oder entfernte Datei wird
  nicht still überschrieben. Abbrechen erhält die lokale Bearbeitung; Neuladen
  schützt noch ungespeicherte Änderungen durch eine klare Entscheidung.
  **Umgesetzt und geprüft am 2026-09-09:** SHA-256 des tatsächlich geladenen
  beziehungsweise geschriebenen Dateiinhalts, Konfliktdialog mit Kopie,
  Neuladen, bewusstem Überschreiben und Abbrechen sowie erneuter Abgleich vor
  dem atomaren Ersetzen. Entfernte Dateien werden ebenfalls erkannt;
  Neuladen kann lokale Änderungen zuerst als Kopie sichern. Regressionen und
  Tk-Dialogprüfung in `tests/test_save_conflicts_batch.py` (`SaveConflictTests`).

- [x] **TASK-04: Batch-Export mit überprüfbarem Ergebnisplan ausführen.** Aufwand: M.
  `batch_export()` weist auf vorhandene Dateien hin, überschreibt sie beim Start
  jedoch direkt. Vorher alle Zielpfade auf Kollisionen untereinander und mit
  vorhandenen Dateien prüfen. Überschreiben, Überspringen oder automatische
  Umbenennung auswählbar machen. Einzeldateien zunächst temporär erzeugen und
  am Ende Erfolge, übersprungene Dateien und Fehler mit Dateinamen auflisten.
  **Akzeptanz:** Zwei Karten mit demselben bereinigten Dateinamen verlieren kein
  Exportergebnis. Ein Fehler nach dem ersten Export hinterlässt keine halbfertige
  Zieldatei und zeigt die bereits erfolgreich erzeugten Dateien korrekt an.
  **Umgesetzt und geprüft am 2026-09-09:** Vorschau mit konkreten Dateipfaden,
  expliziter Behandlung vorhandener Dateien und eindeutigen Namen innerhalb
  des Batches. Atomare Einzeldateien werden gegen den vorgemerkten Dateistand
  geprüft. Fehler einzelner Exporte verhindern die übrigen Ausgaben nicht;
  die Ergebnisliste bleibt sichtbar. Projekt-/Kartenkontext bleibt erhalten.
  Regressionen und Tk-Dialogprüfung in `tests/test_save_conflicts_batch.py`
  (`BatchExportTests`). Status zusätzlich in `plan.md` dokumentiert.

### P2 – Verlässliche Vorschau und flüssige Arbeitsabläufe

- [x] **TASK-05: Lange Aufgaben tatsächlich unterbrechbar ausführen.** Aufwand: L.
  Nacharbeit zu den abgehakten Performance- und Fortschrittsaufgaben:
  `run_autosave()` serialisiert und schreibt weiterhin synchron;
  die Schleife in `batch_export()` rendert ebenfalls im GUI-Callback.
  Auf einem konsistenten Projektsnapshot arbeiten und geeignete Rechen- und
  Dateioperationen aus dem Tk-Hauptthread auslagern. Fortschritt über eine Queue
  und `after()` anzeigen; ausschließlich der Hauptthread greift auf Tk zu.
  Abbruch zwischen Arbeitsschritten und eine eindeutige Behandlung veralteter
  Vorschauergebnisse vorsehen. TASK-01 und TASK-04 berücksichtigen.
  **Akzeptanz:** Während eines großen Batch-Exports zeichnet sich das Fenster
  weiter neu; ein sichtbarer Abbrechen-Button reagiert zwischen Exportdateien.
  Ein alter Autosave-Job markiert neuere Bearbeitungen nicht als gesichert.
  Schließen während eines laufenden Jobs hinterlässt keine beschädigte Datei.
  **Umgesetzt und geprüft am 2026-09-12:** Autosaves und Batch-Exporte arbeiten
  auf einem im Hauptthread erzeugten Snapshot. Worker greifen nie auf Tk zu;
  Fortschritt, Ergebnis und Fehler laufen über Queue und `after()`. Der
  Abbrechen-Button beendet den Batch zwischen atomaren Einzeldateien. Beim
  Schließen werden Jobs erst beendet/abgebrochen und anschließend die eigenen
  Recovery-Dateien bereinigt. Veraltete Autosave-Ergebnisse dürfen eine neuere
  Revision nicht als gesichert markieren. Tests: `tests/test_backlog_completion.py`
  sowie Speicher-/Batch-Regressionen.

- [x] **TASK-06: Spielersicht über alle Exportwege konsistent prüfen.** Aufwand: M.
  Player-Filter und einzelne Tests für Handouts sowie versteckte Raumnummern
  bestehen bereits. Eine gemeinsame Testkarte mit GM-Notizen, Geheimtüren,
  versteckten Räumen, Nummern, Layern, Underlays und Sitzungszuständen ergänzen.
  Für Vorschau, Rasterbild, SVG, Handout und VTT-Paket ausdrücklich festlegen,
  welche Informationen sichtbar sein dürfen. VTT-Daten für die Spielleitung
  dabei von tatsächlich spielerlesbaren Daten unterscheiden.
  **Akzeptanz:** Jeder Exportweg besitzt einen Test für die festgelegte
  Zielgruppe. Spielerdateien enthalten keine GM-Texte in sichtbarer Darstellung
  oder auslesbaren Metadaten. Die Vorschau entspricht dem gewählten Exportprofil.
  **Umgesetzt und geprüft am 2026-09-12:** Gemeinsame Player-Filter gelten für
  Rastervorschau, SVG, Handout sowie Foundry-, Roll20- und Fantasy-Grounds-Daten.
  Versteckte Objekte, Geheimtüren und GM-Laufzeitdaten (Nebel, Sitzung,
  Begegnungsstarts) fehlen im Player-Paket. Die Referenztests prüfen sichtbaren
  SVG-Inhalt, gleiches Rasterbild mit/ohne ausgeblendete Objekte und auslesbare
  VTT-/Handout-Daten.

- [x] **TASK-07: Visuelle Regressionen zwischen Renderern erkennen.** Aufwand: M.
  Die Tests enthalten Export-Smoke-Tests und Prüfungen einzelner Zeichenpfade.
  Zusätzlich kleine Referenzkarten für gedrehte Räume, verbundene Böden,
  transparente Symbole, Text, Hexraster und beschnittene Underlays anlegen.
  Tk-Vorschau, Pillow-Ausgabe und gerastertes SVG anhand derselben Szenen prüfen.
  Unterschiede durch Schrift-Rendering mit dokumentierter Toleranz behandeln.
  **Akzeptanz:** Ein absichtlich verschobenes Symbol oder eine fehlende Wand
  fällt im Bildvergleich auf. Fehlgeschlagene Prüfungen liefern Referenz-,
  Ergebnis- und Differenzbild; Referenzaktualisierungen werden bewusst geprüft.
  **Umgesetzt und geprüft am 2026-09-12:** Die versionierte Referenzszene deckt
  Rotation, Bodenverbindung, Transparenz, Text und Raster ab. Pillow, eine echte
  Tk-Canvas (per Ghostscript gerastert) und CairoSVG (wenn `.[svg]` installiert
  ist) vergleichen dieselbe Szene; die 16-stufige Anti-Aliasing-Toleranz ist
  dokumentiert. Ein absichtlich verschobenes Symbol erzeugt nachweislich
  Referenz-, Ergebnis- und Differenzbild. Die Regeneration erfolgt ausschließlich
  über `scripts/regenerate_visual_references.py` nach Sichtprüfung.

- [ ] **TASK-08: VTT-Exporte anhand echter Importabläufe abnehmen.** Aufwand: M.
  `docs/architecture.md` beschreibt Foundry- und Roll20-JSON sowie die
  Fantasy-Grounds-Bild-XML;
  vorhandene Tests prüfen unter anderem Wände, Türen und Lichter als Daten.
  Pro Zielplattform den konkreten Importweg, unterstützte Versionen und nötige
  Zusatzwerkzeuge dokumentieren. Eine kleine exportierte Referenzszene samt
  Importanleitung bereitstellen und ihre Übernahme in der Zielanwendung prüfen.
  Versionsabhängige Anforderungen bei Umsetzung anhand offizieller Quellen
  verifizieren; erforderliche Konverter in der Exportoberfläche benennen.
  **Akzeptanz:** Rastermaßstab, Ursprung, Wände, Türen und Lichtquellen stimmen
  nach dem dokumentierten Import überein. Nicht übertragbare Eigenschaften
  erscheinen vor dem Export als konkrete Einschränkungen.
  **Vorbereitet am 2026-09-12, Live-Abnahme ausstehend:**
  `docs/vtt-import.md`, die reproduzierbaren Dateien unter
  `examples/vtt-reference/` und Contract-Tests dokumentieren bzw. prüfen
  Plattformweg, Referenzwerte und Grenzen. Die tatsächliche Übernahme muss noch
  in Foundry, Roll20 und Fantasy Grounds mit den dort verfügbaren Versionen
  protokolliert werden; ohne diese drei Live-Nachweise bleibt der Punkt offen.
  **Korrigiert am 2026-09-13:** Der Fantasy-Grounds-Export ist nun die native
  Bild-Sidecar-XML mit `root`, `grid`, `gridsize` und `occluders`; die frühere
  JSON-Referenz wurde entfernt. Die Live-Abnahme prüft dort Raster und LOS;
  Pins, schaltbare Türen und Lichter werden ausdrücklich manuell ergänzt.

- [x] **TASK-09: Große Projekte vor Laden und Rendern auf Ressourcenbedarf prüfen.**
  Aufwand: M. `read_project_file()` liest den JSON-Inhalt beziehungsweise den
  entpackten Archivinhalt vollständig in den Speicher. Vorab Dateigröße und
  deklarierte entpackte Größe prüfen; zusätzlich beim Lesen eine Größenbegrenzung
  durchsetzen. Vor hochauflösenden Exporten Pixelzahl und groben Speicherbedarf
  anzeigen und eine kleinere Skalierung oder gekachelte Ausgabe anbieten.
  Grenzwerte konfigurierbar machen und als Schutz vor Überlastung erklären.
  **Akzeptanz:** Ein übergroßes Archiv wird kontrolliert abgelehnt, ohne das
  geöffnete Projekt zu ersetzen. Eine extrem große Exportfläche führt zu einer
  verständlichen Auswahl statt zu einem unkontrollierten Speicherfehler.
  **Umgesetzt und geprüft am 2026-09-12:** `storage.py` begrenzt Datei- und
  deklarierte/gelesene entpackte Archivgröße vor dem JSON-Laden. Rasterexporte
  berechnen Pixelzahl und Mindest-RAM; der Dialog bietet verkleinerte Skalierung
  oder einen nummerierten Kachelsatz. Grenzen sind über
  `OSR_MAP_MAX_FILE_MIB`, `OSR_MAP_MAX_EXPANDED_MIB` und
  `OSR_MAP_MAX_EXPORT_MP` konfigurierbar. Grenzfalltests decken ZIP-Abweisung,
  verständliche Fehlermeldung und Kachelabmessungen ab.

### P3 – Installation und Weiterentwicklung vereinfachen

- [ ] **TASK-10: Reproduzierbare Installation und Windows-Paket anbieten.** Aufwand: L.
  Das Handbuch setzt Python und manuell installierte Zusatzpakete voraus;
  eine zentrale Paketdefinition fehlt im gesichteten Dateibestand.
  Eine `pyproject.toml` mit unterstützter Python-Version, Laufzeitabhängigkeiten
  und optionalen Export-/Entwicklungspaketen ergänzen. Einen reproduzierbaren
  Build für eine portable Windows-Ausgabe erstellen. In „Über/Diagnose“ Version
  und verfügbare Exportfähigkeiten anzeigen.
  **Akzeptanz:** Auf einem frischen Windows-Testsystem ohne Python lassen sich
  eine Beispielkarte öffnen, Änderungen speichern und PNG/PDF exportieren.
  Fehlende optionale SVG-Unterstützung wird mit einer verständlichen Erklärung
  angezeigt. Der Paketbuild ist aus dem Repository wiederholbar.
  **Vorbereitet am 2026-09-12, Frischsystem-Abnahme ausstehend:**
  `pyproject.toml`, `scripts/setup-dev.ps1`, `scripts/build-portable.ps1` sowie
  Über/Diagnose sind umgesetzt; das Paket lässt sich lokal ohne Netzabhängigkeit
  als Editable-Install importieren. Der reproduzierbare PyInstaller-Build wurde
  lokal erfolgreich erzeugt (`OSRMapMaker.exe`, 34.8 MB); der Runner funktioniert
  auch ohne vorhandenes Benutzerprofil. Die EXE muss noch auf einem Windows-
  System ohne Python mit Öffnen, Speichern sowie PNG-/PDF-Export geprüft werden.
  Diese Abnahme lässt sich nicht durch den vorhandenen Python-Checkout ersetzen;
  der Punkt bleibt daher offen.

- [x] **TASK-11: Modulaufteilung durch echte Implementierungstrennung abschließen.**
  Aufwand: L. Laut `docs/architecture.md` sind die kleinen Module überwiegend
  Importfassaden; `osr_map_maker.py` umfasst derzeit rund 30.800 Zeilen.
  Zuerst Speicherlogik und Validierung, danach Geometrie und Renderer auslagern.
  Abhängigkeiten vom Datenmodell zur Oberfläche vermeiden und bestehende
  Importpfade während der Umstellung kompatibel halten. Kleine, einzeln prüfbare
  Schritte statt einer vollständigen Neuschreibung planen.
  **Akzeptanz:** Speicher- und Modelltests importieren die extrahierten Module
  direkt, ohne die Hauptanwendung laden zu müssen. Es entstehen keine zyklischen
  Imports; bestehende Projektdateien und die bisherige Testsuite funktionieren.
  **Umgesetzt und geprüft am 2026-09-12:** Die produktiven, Tk-freien Module
  `storage.py`, `validation.py`, `geometry.py` und `rendering.py` enthalten
  Speicher-/Ressourcenschutz, Dokumentstrukturprüfung, Geometrie und den
  Bildvergleich; die bisherigen Importfassaden bleiben kompatibel. Der
  Modulgrenztest importiert sie direkt, und die vollständige Suite (212 Tests,
  1 erwarteter Skip) besteht ohne zyklische Importe.

- [x] **TASK-12: Qualitätsprüfung und Backlog-Abnahme nachvollziehbar machen.**
  Aufwand: M. `scripts/quality.ps1` überspringt Ruff und Mypy, wenn sie fehlen;
  die bisherigen Backlog-Abschnitte sind durchgehend als erledigt markiert.
  Eine automatisierte Windows-Prüfung mit festgelegter Toolinstallation und
  sichtbar getrennten Prüfergebnissen ergänzen. Einen GUI-Smoke-Ablauf für
  Öffnen, Zeichnen, Undo/Redo, Speichern, Wiederöffnen und Export aufnehmen.
  Bei künftigen Aufgaben den Test oder die manuelle Abnahme samt Datum vermerken;
  ältere Häkchen zunächst als bisherigen Projektstatus erhalten.
  **Akzeptanz:** Fehlende Pflichtwerkzeuge lassen die automatisierte Prüfung
  scheitern. Ein Testlauf veröffentlicht seine Ergebnisse und bei visuellen
  Fehlern die Prüfbilder. Neue Aufgaben gelten erst mit Abnahmenachweis als fertig.
  **Umgesetzt und geprüft am 2026-09-12:** `scripts/setup-dev.ps1` installiert
  die festgelegten Entwicklungswerkzeuge aus `pyproject.toml`; `quality.ps1`
  veröffentlicht den JUnit-Bericht unter `artifacts/quality/pytest.xml` und
  scheitert bei fehlendem Ruff oder Mypy. Der dokumentierte GUI-Smoke-Ablauf
  umfasst Öffnen, Zeichnen, Undo/Redo, Speichern, Wiederöffnen sowie PNG-/PDF-
  Export. Visuelle Abweichungen speichern Referenz-, Ergebnis- und
  Differenzbilder in `artifacts/visual/`; neue Häkchen tragen diesen Nachweis.

Empfohlene Reihenfolge: TASK-01 und TASK-02 zuerst, anschließend TASK-03 und
TASK-04. Danach TASK-05 bis TASK-09; TASK-12 begleitet deren Umsetzung.
Paketierung und Modultrennung in kleinen eigenständigen Schritten einplanen.

## Aktueller UI/UX-Umsetzungsplan: Werkzeuge immer griffbereit

Stand: 2026-06-26

Ziel: OSR Map Maker so umbauen, dass Nutzerinnen und Nutzer im jeweiligen
Arbeitskontext sofort die passenden Werkzeuge, Optionen und Rueckmeldungen
sehen. Die Karte bleibt im Zentrum; Panels, Toolbar, Optionen und Command
Palette sollen sich an der aktuellen Aufgabe orientieren: Zeichnen, Symbole
platzieren, Auswahl bearbeiten, Kampagneninformationen pflegen oder exportieren.

### Ausgangslage aus der Code-Sichtung

- Es gibt bereits Workspaces in `WORKSPACE_PRESETS`, dockbare Panels in
  `WORKSPACE_PANEL_TITLES`, eine globale Command Bar, eine kontextuelle
  Tool-Options-Bar, Toolbar, Minimap/Navigator, Command Palette und Statusleiste.
- Die vorhandene UI ist funktional breit, aber einige Werkzeuge sind noch auf
  mehrere Orte verteilt: Toolbar, Optionsleiste, rechte/freie Panels,
  Menues, Kontextmenues und Dialoge konkurrieren miteinander.
- Dock-Panels sind technisch als eigene Fenster umgesetzt. Das ist flexibel,
  kann aber im Standardlayout mehr Suchaufwand erzeugen als ein klarer
  Arbeitsbereich mit sichtbarer Seitenleiste.
- Der beste naechste Schritt ist deshalb kein kompletter Neustart, sondern eine
  kontextbewusste Neuordnung der bestehenden Bausteine.

### Leitprinzipien

- Canvas zuerst: Die Karte ist immer der Hauptarbeitsbereich.
- Kontext statt Vollstaendigkeit: Sichtbar sind zuerst die Aktionen, die zur
  aktuellen Aufgabe, Auswahl und zum aktiven Werkzeug passen.
- Ein Werkzeug, ein Ort: Jede haeufige Aktion hat einen bevorzugten UI-Ort;
  Menues und Command Palette bleiben schnelle Zweitwege.
- Keine versteckten Voraussetzungen: Wenn ein Werkzeug Layer, Snap, Farbe,
  Groesse, Exportziel oder Auswahl braucht, steht die Option direkt daneben.
- Ruhig und kompakt: Panels zeigen klare Arbeitsgruppen, keine tiefen
  Verschachtelungen und keine langen Hilfetexte im Hauptfenster.

## Phase 1: Standardlayout und Werkzeugzugriff klaeren

- [x] Default-Workspace "Drawing" neu anordnen.
      Links eine kompakte Werkzeugleiste, Mitte Canvas, rechts eine sichtbare
      Arbeitsleiste mit `Layers`, `Selection` und `History`. `Navigator` bleibt
      als Minimap oder kleines Panel verfuegbar. Ziel: Raum, Korridor, Tuer,
      Nummer, Layerwechsel und Undo sind ohne Fensterjagd erreichbar.

- [x] Toolbar zu einer echten Aufgabenleiste verdichten.
      In `_build_toolbar()` die Toolgruppen visuell staerker trennen:
      Auswahl, Raeume/Korridore, Formen/Linien, Text/Notizen, Messen, letzte
      Werkzeuge. Die aktive Gruppe und das aktive Werkzeug muessen auf einen
      Blick sichtbar sein. Labels kurz halten, Tooltips mit Shortcut anzeigen.

- [x] Tool-Options-Bar priorisieren.
      In `rebuild_contextual_tool_options()` zuerst die wirklich relevanten
      Optionen des aktiven Werkzeugs zeigen. Immer sichtbar: aktiver Layer,
      Snap, wichtigste Groesse/Farbe/Variante. Weniger wichtige Optionen in ein
      kleines "More"-Menue auslagern.

- [x] Command Bar entlasten.
      Oben nur globale Aktionen lassen: New, Load, Save, Undo, Redo, Zoom/Fit,
      Search/Command, Export. Details wie Exportvarianten, Spezialansichten und
      Layoutoptionen in passende Panels oder Menues verschieben.

### Akzeptanzkriterien Phase 1

- [x] Ein neuer Nutzer kann in unter 60 Sekunden einen Raum, einen Korridor,
      eine Tuer, eine Raumnummer und einen Layerwechsel finden.
- [x] Das aktive Werkzeug ist in Toolbar, Optionsleiste und Statusleiste
      konsistent sichtbar.
- [x] Keine Standardansicht startet mit vielen frei schwebenden Fenstern, die
      den Canvas verdecken.

## Phase 2: Kontextuelle Panels und Auswahlfluss

- [x] Unterpanels individuell in der Hoehe anpassbar machen.
      Jedes sichtbare Panel besitzt an seiner Unterkante einen Ziehgriff; die
      eingestellte Hoehe bleibt beim Ein-/Ausklappen und nach Neustarts erhalten.
- [x] Selection-Panel als Arbeitszentrale fuer markierte Objekte ausbauen.
      Bei Auswahl automatisch `Selection` sichtbar machen und dort zuerst
      haeufige Aktionen anbieten: Layer wechseln, Lock, Hide/Show, Duplicate,
      Delete, Align, Group, Player-visible, Export. Detailfelder bleiben darunter
      in Sektionen.

- [x] Layers-Panel naeher an den Kartenbau bringen.
      Jede Layer-Zeile soll Sichtbarkeit, Lock, Name, Opacity und Objektanzahl
      direkt zeigen. Haeufige Aktionen kommen als Icon-Leiste an den Panelrand:
      Neu, Duplizieren, Loeschen, Hoch/Runter, Alle sperren/entsperren.

- [x] History-Panel als Sicherheitsnetz nutzbar machen.
      Der Verlauf soll direkt zeigen, was rueckgaengig gemacht wird. Undo/Redo
      bleiben global in der Command Bar, aber das Panel erklaert die letzten
      Schritte mit kurzer Beschreibung und aktuellem Zustand.

- [x] Symbol-Workflow fokussieren.
      Beim Symbolwerkzeug automatisch den `Symbols`-Workspace oder das
      Symbolpanel sichtbar machen. Symbolsuche, Favoriten, zuletzt genutzt und
      Groesse/Variante muessen direkt neben dem Platzieren erreichbar sein.

- [x] Kontextmenues vervollstaendigen.
      Rechtsklick auf Canvas, Auswahl, Layer, Symbol und Map-Tab soll jeweils
      die naechstliegenden Aktionen anbieten. Ziel: weniger dauerhafte Buttons,
      aber schnellere lokale Bedienung.

### Akzeptanzkriterien Phase 2

- [x] Nach Auswahl eines Objekts sind Bearbeiten, Layerwechsel und Sichtbarkeit
      ohne Menues erreichbar.
- [x] Beim Wechsel auf ein Symbolwerkzeug sind Symbolbrowser und Symboloptionen
      sichtbar oder mit einem Klick erreichbar.
- [x] Rechtsklicks fuehlen sich kontextpassend an und duplizieren nicht einfach
      nur die Hauptmenues.

## Phase 3: Workspace-Automatik und progressive Komplexitaet

- [x] Workspace-Wechsel smarter machen.
      `apply_workspace_preset()` soll nicht nur Panels ein-/ausblenden, sondern
      auch den jeweils besten Fokus setzen: Drawing -> Toolbar/Selection,
      Symbols -> Symbolsuche, Campaign -> Rooms/Navigator, Export/VTT -> Export.

- [x] Erste optionale Auto-Switch-Regeln einfuehren.
      Umgesetzt: Auswahl blendet `Selection` ein, Symbolwerkzeuge blenden
      `Symbols` ein, Shape-Werkzeuge blenden `Colors/Style` ein. Die Automatik
      ist ueber `View > Auto Context Panels` abschaltbar. Offen fuer spaeter:
      Exportframe-Auswahl -> `Export`, Room-Objekte -> `Rooms`/`Selection`.

- [x] Kompaktmodus als echte Arbeitsansicht gestalten.
      `compactMode` soll Panels nicht nur verstecken, sondern eine kleine
      wiederherstellbare Panel-Leiste anzeigen: Layers, Selection, Symbols,
      Navigator, Export. So bleibt der Canvas gross, ohne dass Werkzeuge
      verschwinden.

- [x] Layout-Reset und Layout-Speichern klarer machen.
      View-Menue und Command Palette sollen eindeutige Aktionen enthalten:
      "Reset to Drawing Layout", "Save Current Layout", "Restore Saved Layout".
      Status/Toast bestaetigen ohne stoerende Dialoge.

### Akzeptanzkriterien Phase 3

- [x] Ein Workspace-Wechsel bringt den Tastaturfokus an eine sinnvolle Stelle.
- [x] Auto-Switching hilft beim ersten Arbeiten, laesst sich aber deaktivieren.
- [x] Kompaktmodus bleibt produktiv und macht keine Kernwerkzeuge unsichtbar.

## Phase 4: Visuelle Klarheit und Bedienbarkeit

- [x] UI-Sprache vereinheitlichen.
      Entweder konsequent Englisch beibehalten oder eine deutsche Lokalisierung
      planen. Kurzfristig: gleiche Begriffe fuer Tool, Layer, Map, Export,
      Selection, History, Symbol verwenden.

- [x] Icon- und Buttonsystem konsolidieren.
      `GLOBAL_ACTION_ICONS` und Toolicons konsistent einsetzen. Haefige Aktionen
      bekommen Icon + Tooltip; Textbuttons bleiben fuer Dialog- und
      Sonderaktionen.

- [x] Fokus, Tastatur und DPI pruefen.
      Toolbar, Command Palette, Panels, Symbolbrowser und Selection-Felder
      muessen per Tastatur bedienbar bleiben. Buttontexte duerfen bei 125 und
      150 Prozent Skalierung nicht abgeschnitten werden.

- [x] Statusleiste als Live-Kontext nutzen.
      `refresh_status_fields()` und `update_status()` sollen immer Werkzeug,
      Layer, Koordinate, Auswahl, Snap, Zoom, Speicherstatus und Warnungen
      zeigen. Klickbare Bereiche fuer Zoom, Validation und Autosave pruefen.

- [x] Leere Zustaende verbessern.
      Panels wie `Selection`, `Symbols`, `History`, `Objects` und `Export`
      brauchen kurze, handlungsorientierte Empty States mit der jeweils
      naheliegenden Aktion, aber ohne lange Erklaertexte.

### Akzeptanzkriterien Phase 4

- [x] Die Standardansicht wirkt ruhig, nicht wie eine Sammlung offener Dialoge.
- [x] Keine Buttonlabels laufen bei groesserer Skalierung aus ihren Containern.
- [x] Die Statusleiste beantwortet jederzeit: Was mache ich gerade, wo bin ich,
      worauf wirkt die naechste Aktion?

## Phase 5: Test- und Review-Runde

- [x] Mini-Usability-Szenarien manuell testen.
      Szenario 1: Neue Karte -> Raum -> Korridor -> Tuer -> Nummer -> Undo.
      Szenario 2: Symbol suchen -> platzieren -> Groesse/Farbe aendern.
      Szenario 3: Objekt auswaehlen -> Layer wechseln -> Player-visible setzen.
      Szenario 4: Export/VTT-Profil waehlen -> Player-Export starten.

- [x] Layout-Regressionen pruefen.
      Startlayout, Workspace-Wechsel, Layout speichern/laden, Reset, Kompaktmodus,
      Minimap-Dock und Panel-Sichtbarkeit testen.

- [x] Technische Checks ausfuehren.
      Nach UI-Codeaenderungen mindestens `python -m py_compile osr_map_maker.py`
      und die vorhandenen Core-Tests ausfuehren. Bei groesseren Aenderungen
      `.\scripts\quality.ps1` verwenden, sofern die lokalen Tools verfuegbar sind.

- [x] Dokumentation aktualisieren.
      `README.md`, `UI_SPEC.md` und dieses `Tasks.md` nach der Umsetzung anpassen,
      damit Workspaces, Panels, Toolbar und Shortcuts nicht auseinanderlaufen.

### Empfohlene Umsetzungsreihenfolge

1. Standardlayout und Toolbar/Optionsleiste verbessern.
2. Selection, Layers, History und Symbols als wichtigste Arbeits-Panels
   kontextbewusst nach vorne holen.
3. Workspace-Fokus, Auto-Switching und Kompaktmodus ergaenzen.
4. Visuelle Konsistenz, Tastaturbedienung und DPI-Details polieren.
5. Vier manuelle Nutzerszenarien plus technische Checks abschliessen.

## Programmdokumentation: Erstellungsplan

Stand: 2026-06-22

Ziel: Eine Programmdokumentation erstellen, die Entwicklern und zukuenftigen
Maintainerinnen erklaert, wie OSR Map Maker aufgebaut ist, welche Datenfluesse
es gibt, wo zentrale Funktionen liegen und wie Aenderungen sicher umgesetzt und
getestet werden.

### Ergebnisartefakte

- [x] Grundstruktur in `DOKUMENTATION.md` anlegen.
- [x] Bestehende Quellen auswerten: `README.md`, `docs/architecture.md`,
      `UI_SPEC.md`, Tests und zentrale Python-Module.
- [x] Detailinhalte pro Kapitel ausarbeiten und mit Code-Referenzen versehen.
- [x] Datenmodell-Kapitel mit Schemafeldern, Objektarten und Migrationen
      vervollstaendigen.
- [x] UI-Kapitel mit Menues, Workspaces, Panels, Canvas-Events und Dialogen
      vervollstaendigen.
- [x] Rendering- und Export-Kapitel mit Tk-, Pillow-, SVG-, PDF- und
      VTT-Pfaden vervollstaendigen.
- [x] Entwicklungs- und Test-Kapitel mit Qualitaetsbefehlen, Testabdeckung und
      bekannten Risiken vervollstaendigen.
- [x] Dokumentation gegen die App pruefen und veraltete oder spekulative
      Aussagen entfernen.

### Vorgehen

1. Bestandsaufnahme
   - [x] Repository-Dateien, vorhandene Dokumente und Tests sichten.
   - [x] Hauptmodul `osr_map_maker.py` nach Funktionsgruppen analysieren.
   - [x] Facade-Module (`models.py`, `renderers.py`, `project_services.py`,
         `constants.py`, `symbols.py`, `storage.py`) einordnen.

2. Dokumentationsstruktur
   - [x] Zielgruppe, Zweck und Abgrenzung definieren.
   - [x] Architekturueberblick und Modulkarte anlegen.
   - [x] Kapitel fuer Datenmodell, UI, Rendering, Export, Persistenz,
         Performance, Tests und Wartung vorbereiten.

3. Inhaltliche Ausarbeitung
   - [x] Pro Kapitel die wichtigsten Funktionen, Klassen und Datenstrukturen
         mit relativen Dateipfaden dokumentieren.
   - [x] Wiederkehrende Datenfluesse beschreiben: App-Start, Projekt laden,
         Objekt zeichnen, Auswahl bearbeiten, Autosave, Export.
   - [x] Risiken und Wartungsregeln dokumentieren, besonders fuer neue
         persistente Felder, Exportprofile, Symboltypen und UI-Aenderungen.

4. Qualitaetssicherung
   - [x] Markdown-Struktur und interne Links pruefen.
   - [x] Terminologie vereinheitlichen.
   - [x] `git diff --check -- DOKUMENTATION.md Tasks.md` ausfuehren.
   - [x] Optional nach inhaltlichen Code-Aenderungen `.\scripts\quality.ps1`
         ausfuehren.

### Erste Analyseergebnisse

- `osr_map_maker.py` ist weiterhin das zentrale Modul und enthaelt Tk-App,
      Datenmodell-Helfer, Validierung, UI-Events, Rendering, Export und
      Generatorlogik.
- Die kleineren Python-Dateien sind stabile Import-Fassaden fuer eine
      schrittweise Modularisierung, keine vollstaendig getrennten
      Implementierungsmodule.
- Projekte werden als JSON (`.osrmap.json`) oder komprimiert (`.osrmapz`)
      gespeichert und beim Laden validiert/migriert.
- Die wichtigsten technischen Achsen fuer die Dokumentation sind:
      Datenmodell/Schema, Tkinter-UI, Canvas-Interaktion, Rendering,
      Export/VTT, Symbolverwaltung, Autosave/Recovery, Performance-Caches und
      Tests.

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

## Neue GUI-Vorschlaege zur einfacheren Bedienung

Stand: 2026-08-05

Ziel: Neue und gelegentliche Nutzer sollen die wichtigsten Arbeitsablaeufe
allein ueber sichtbare GUI-Elemente verstehen und sicher ausfuehren koennen.
Die Vorschlaege in diesem Abschnitt betreffen bewusst keine Tastenkombinationen
und keine Steuerung ueber Tasten.

### Hohe Prioritaet: Einstieg und Orientierung

- [x] Startbereich fuer neue und bestehende Projekte einfuehren.
      Beim Programmstart grosse, klar beschriftete Kacheln fuer "Neue Karte",
      "Projekt oeffnen" und die zuletzt verwendeten Projekte zeigen. Fuer neue
      Karten kleine visuelle Vorlagen wie Dungeon, Hoehle, Gebaeude und leere
      Karte mit Format- und Rastervorschau anbieten.

- [x] Gefuehrten Erste-Schritte-Modus anbieten.
      Eine freiwillige, jederzeit schliessbare Tour markiert nacheinander
      Werkzeugleiste, Canvas, Layer und Export. Jeder Schritt enthaelt genau eine
      sichtbare Aktion und eine kleine Beispielgrafik statt langer Hilfetexte.

- [x] Aktuellen Arbeitsmodus deutlich am Canvas anzeigen.
      Modi wie Player Preview, Export Frame, Messen oder Generatorvorschau
      erhalten ein farblich ruhiges Banner am oberen Canvas-Rand. Das Banner
      erklaert den Modus kurz und enthaelt einen gut sichtbaren Button zum
      Beenden oder Uebernehmen.

- [x] Platzierungsvorschau fuer alle Zeichen- und Symbolwerkzeuge vereinheitlichen.
      Vor dem Klick zeigt eine halbtransparente Vorschau Position, Ausrichtung,
      Groesse und Snap-Ergebnis. Unzulaessige Positionen werden direkt am
      Mauszeiger erklaert, statt erst nach dem Platzierungsversuch.

- [x] Kontextleiste direkt an der Auswahl ergaenzen.
      Nach dem Markieren erscheint nahe der Auswahl eine kleine, nicht
      verdeckende Leiste fuer die haeufigsten Mausaktionen: Duplizieren, Layer
      wechseln, Sperren, Sichtbarkeit und Loeschen. Seltene Eigenschaften
      bleiben im Selection-Panel.

- [x] Leere Canvas-Ansicht handlungsorientiert gestalten.
      Eine neue Karte zeigt in der Mitte drei dezente Startaktionen: Raum
      zeichnen, Vorlage waehlen und Projekt importieren. Nach dem ersten Objekt
      verschwindet dieser Hinweis dauerhaft fuer die aktuelle Karte.

### Hohe Prioritaet: Fehler vermeiden und rueckmeldbar machen

- [x] Formulare direkt am betroffenen Feld validieren.
      Ungueltige Werte erhalten eine kurze Meldung unter dem Eingabefeld und
      eine erkennbare Markierung. Der Bestaetigen-Button bleibt deaktiviert und
      erklaert bei Beruehrung mit der Maus, welche Angaben noch fehlen.

- [x] Destruktive Dialoge mit konkreter Auswirkung formulieren.
      Vor Loeschen, Ersetzen oder Zuruecksetzen Namen, Anzahl und gegebenenfalls
      eine Miniatur der betroffenen Karten, Layer oder Objekte zeigen. Der
      Hauptbutton nennt die Aktion eindeutig, zum Beispiel "Layer mit 24
      Objekten loeschen" statt nur "OK".

- [x] Rueckgaengig machbare Aktionen als Toast mit Aktionsbutton bestaetigen.
      Nach Loeschen, Verschieben oder groesseren Batch-Aenderungen kurz anzeigen,
      was passiert ist, und direkt im Toast "Rueckgaengig" anbieten. Der Toast
      darf den Canvas nicht verdecken und schliesst sich automatisch.

- [x] Speichern-beim-Schliessen-Dialog differenzieren.
      Bei mehreren geaenderten Karten jede betroffene Karte mit Name und
      Aenderungsstatus auflisten. Sichtbare Buttons fuer "Alle speichern",
      "Ohne Speichern schliessen" und "Abbrechen" vermeiden unklare
      Ja/Nein-Abfragen.

- [x] Fehlerdialoge um passende Loesungsaktionen erweitern.
      Bei fehlenden Assets, ungueltigen Exportpfaden oder gesperrten Layern
      direkt Buttons wie "Asset suchen", "Anderen Ordner waehlen" oder "Layer
      entsperren" anbieten. Technische Details bleiben in einem aufklappbaren
      Bereich.

### Mittlere Prioritaet: Panels, Listen und Eigenschaften

- [x] Aktive Filter als sichtbare Chips darstellen.
      Objekt-, Symbol- und Assetlisten zeigen oberhalb der Treffer jeden aktiven
      Filter als einzeln entfernbaren Chip sowie "Alle Filter entfernen". Die
      Trefferzahl wird daneben sofort aktualisiert.

- [x] Mehrfachauswahl mit eindeutigen Mischzustaenden anzeigen.
      Wenn ausgewaehlte Objekte unterschiedliche Farben, Layer oder
      Sichtbarkeiten besitzen, zeigt das Properties-Panel "Mehrere Werte" statt
      einen scheinbar gueltigen Einzelwert. Aenderungen wirken erst nach einer
      bewussten Auswahl in diesem Feld auf alle Objekte.

- [x] Geaenderte Eigenschaften sichtbar kennzeichnen und einzeln zuruecksetzen.
      Vom Standard abweichende Werte erhalten einen kleinen Marker und einen
      Reset-Button direkt am Feld. Eine Vorschau zeigt vor dem Zuruecksetzen,
      welcher Standardwert wiederhergestellt wird.

- [x] Drag-and-drop in Layern und Objektlisten praezisieren.
      Beim Ziehen eine klare Einfuegelinie, das Ziel-Layer und die Zahl der
      bewegten Objekte anzeigen. Lange Listen scrollen am Rand automatisch;
      gesperrte oder ungueltige Ziele werden sichtbar deaktiviert und begruendet.

- [x] Lange Panels mit festen Abschnittstiteln und Scrollhinweisen versehen.
      Wichtige Kopfaktionen bleiben beim Scrollen sichtbar. Ein dezenter Verlauf
      am oberen oder unteren Rand macht erkennbar, dass weitere Inhalte ausserhalb
      des sichtbaren Bereichs liegen.

- [x] Panel- und Dialoggroessen pro Arbeitsbereich merken.
      Wiederkehrende Fenster oeffnen an ihrer letzten sinnvollen Position und
      Groesse, werden aber automatisch in den sichtbaren Bildschirmbereich
      zurueckgeholt. So muessen Nutzer ihre Arbeitsumgebung nicht wiederholt
      neu ordnen.

### Mittlere Prioritaet: Sichtbarkeit und Mausbedienung

- [x] Klickflaechen fuer kleine Icons vergroessern.
      Sichtbarkeit, Sperren, Favoriten, Panel-Schliessen und Layer-Reihenfolge
      erhalten eine ausreichend grosse unsichtbare Trefferflaeche mit klarem
      Hover-Zustand. Dicht nebeneinanderliegende Aktionen brauchen Abstand, um
      Fehlklicks zu vermeiden.

- [x] Interaktive Elemente konsequent durch Hover-Zustaende kenntlich machen.
      Klickbare Statusfelder, Miniaturen, Canvas-Handles, Tabs und Paneltitel
      reagieren mit derselben Akzentfarbe und bei Bedarf einem kurzen Tooltip.
      Reine Informationen duerfen nicht wie Buttons aussehen.

- [x] Farben nie als einziges Zustandssignal verwenden.
      Warnungen, aktive Werkzeuge, gesperrte Layer und Sichtbarkeitszustaende
      zusaetzlich durch Icon, Kontur oder Text kennzeichnen. Farbkontraste fuer
      normale, Hover-, aktive und deaktivierte Zustaende pruefen.

- [x] Ueberlagerungen automatisch vom Arbeitsbereich fernhalten.
      Tooltips, Symbolvorschauen, Kontextleisten und Toasts sollen sich so
      positionieren, dass Auswahl, Mauszeiger und wichtige Canvas-Handles
      sichtbar bleiben. Bei wenig Platz wechseln sie selbststaendig die Seite.

### Niedrigere Prioritaet: Komfort und Feinschliff

- [x] Fortschrittsanzeige fuer laengere Aktionen vereinheitlichen.
      Export, Laden grosser Projekte, Asset-Import und Generatoren zeigen einen
      gemeinsamen Fortschrittsdialog mit aktuellem Teilschritt, Prozentwert und
      sichtbarem Abbrechen-Button. Die restliche Oberflaeche zeigt klar, ob sie
      waehrenddessen weiter bedienbar ist.

- [x] Vorher/Nachher-Vergleich per sichtbarem Umschalter anbieten.
      Bei Stil-, Generator- und Exportvorschauen einen beschrifteten Schieber
      oder zwei nebeneinanderliegende Ansichten verwenden. Uebernehmen und
      Verwerfen bleiben dauerhaft am unteren Dialogrand sichtbar.

- [x] Zoom- und Navigatorbedienung um direkte Mausaktionen ergaenzen.
      Im Navigator sichtbare Buttons fuer Hineinzoomen, Herauszoomen, Ganze
      Karte und Auswahl einpassen anbieten. Das Viewport-Rechteck bekommt
      erkennbare Griff- und Hover-Zustaende fuer Verschieben und Skalieren.

- [x] Konsistente visuelle Hierarchie fuer Primaer- und Nebenaktionen festlegen.
      Pro Dialog oder Panel nur eine primaere Aktion farblich hervorheben.
      Sekundaeraktionen neutral, gefaehrliche Aktionen separat und deaktivierte
      Aktionen eindeutig, aber weiterhin lesbar darstellen.

### Akzeptanzkriterien fuer den neuen GUI-Backlog

- [x] Eine neue Nutzerin kann ohne Tastaturhinweise ein Projekt anlegen, einen
      Raum platzieren, dessen Eigenschaften aendern und einen Export starten.
- [x] Jeder Sondermodus ist am Canvas erkennbar und besitzt einen sichtbaren Weg
      zum Beenden, Uebernehmen oder Abbrechen.
- [x] Fehler werden moeglichst am Entstehungsort erklaert und bieten eine direkt
      anklickbare Loesung an.
- [x] Alle wichtigen Mausziele zeigen Hover-Feedback und bleiben auch bei 150
      Prozent Skalierung gut treffbar.
- [x] Keine der neuen Hilfen, Hinweise oder Rueckmeldungen verdeckt dauerhaft
      die Karte oder zwingt erfahrene Nutzer durch eine Tour.
