# GUI-Smoke-Abnahme

Dieser kurze Ablauf ergänzt die automatisierten Modell-, Speicher- und
Render-Tests. Er wird auf einem Windows-Desktop mit Tk ausgeführt und bei einer
UI-Änderung zusammen mit Datum und Ergebnis in `Tasks.md` oder dem zugehörigen
Änderungsnachweis festgehalten.

## Vorbereitung

1. `python osr_map_maker.py` starten.
2. Über **File > Open** `examples/vtt-export.osrmap.json` öffnen.
3. Einen neuen, leeren Ordner für die Probeausgaben wählen.

## Ablauf und erwartetes Ergebnis

| Schritt | Aktion | Erwartung |
| --- | --- | --- |
| Öffnen | Beispielkarte öffnen und zwischen Karte/Objektliste wechseln | Karte, Ebenen und Objekte erscheinen ohne Dialogfehler. |
| Zeichnen | Rechteck-Werkzeug wählen und einen kleinen Raum einzeichnen | Ein neues Objekt erscheint auf Karte und in der Objektliste. |
| Undo/Redo | Einmal **Undo**, einmal **Redo** ausführen | Der Raum verschwindet und erscheint wieder; die Beschriftungen/Schaltflächen für Verlauf ändern sich passend. |
| Speichern | **Save As** in den Probeordner, danach schließen und dieselbe Datei erneut öffnen | Der neue Raum bleibt erhalten; es erscheint keine Wiederherstellungs- oder Konfliktmeldung. |
| PNG | **Export > Image**, PNG wählen und exportieren | Die Datei existiert, lässt sich öffnen und zeigt die Karte einschließlich des neuen Raums. |
| PDF | **Export > Image**, PDF wählen und exportieren | Die PDF-Datei existiert und zeigt die Karte auf mindestens einer Seite. |

Bei einem Fehler bitte die erzeugte Projekt-/Exportdatei, den sichtbaren
Dialogtext und – bei einem Renderproblem – die Bilder aus `artifacts/visual/`
beilegen. Die Referenzbilder werden ausschließlich nach Sichtprüfung mit
`python scripts/regenerate_visual_references.py` aktualisiert.
