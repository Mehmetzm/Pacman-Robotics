# damt_vision
>der Name ist ein wenig irreführend

Dieses Projekt beinhaltet alle Nodes, die für die Steuerung eines Emaros Roboters für das Anwendungsbeispiel Pacman benötigt wird

---

## Features
- kamerabasierte Erkennung von Linien auf dem Boden
- Verfolgung der Linien und erkennung von Kreuzungen/Abbiegungen
- manuelle Steuerung des Roboters, z.b mit Controller
- mehr oder weniger intelligente autonome Wegfindung im Spiel
- Objekterkennung der im Spiel vorkommenden Entities

---

## Projektstruktur
- `damt_vision/` → enthält alle Haupt-Dateien 
  - `cam_encoder` → ist für die Initalisierung, Erfassung, Komprimierung und Veröffentlichung der Kamerbilder zuständig
  - `cam_decoder` → abboniert und enpackt die Bilder, folgt den Linien, Erkennt Kreuzungen und regelt das Fahrverhalten
  - `cam_combined`→ kombinierte Version der beiden Kameraklassen
  - `controllhub`→ regelt die Kommunikation zwischen Peripherie und Fahrsteuerung
  - `pac_logik`→ berechnet Fahr-Entscheidungen entspechend der Situation im Spiel 
- `Messungen/` → ein paar Messungen in Bezug auf Rechenaufwand der Nodes
- `Deprecated/` → alte/alternative Versionen, die nicht genutzt oder weiterentwickelt wurden
  - `object_detector`→ frühe Version eine Objekterkennung für Geister, Items etc.
- der Rest entspricht den Standard-Ros2 Dateien

---

## Voraussetzungen
- Ros2 installation und eine Pythonumgebung  
- An Hardware, werden beide Kameras, die Motoren, und ein geeigneter ArUco Marker benötigt
- an Emaros packages wird nur 'emaros_controll motor_controll' benötigt
- an damt packages wird für pac_logik die [damt_game_msg](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_game_msg) benötigt
- optional kann noch 'emaros_xbox_bt xbox_publisher' für die Controllersteuerung und 'emaros_status_information emaros_status_information' für die CPU-Auslastung aktiviert werden

---

## Installation & Nutzung
1. Repository in den **src/**-Ordner des ros-workspaces kopieren
2. builden und sourcen
3. 'emaros_controll motor_controll' + 'damt_vision cam_combined' oder 'emaros_controll motor_controll' + 'damt_vision decoder' + 'damt_vision encoder' starten
4. zur Funktion wird eine dunkle Map mit hellen Linien benötigt, dafür kann [damt_map](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_map/-/tree/main?ref_type=heads) genutzt werden
5. die Fahrsteuerung fährt vollautomatisch und wenn keine Befehle vorhanden, zufällig durch die Map
#### Hinweise:
 - die Lichtverhältniss haben größen einluss auf die Linienerkennung
 - die Kameras haben einen ca. 10cm großen toten Winken. D.h der Roboter sieht nichts, was sich näher als das vor ihm befindet und keine höhe hat
 - die Steuerung der Motoren ist nicht geeicht und kann sich von Roboter zu Roboter und von Richtung zu Richtung unterscheiden
 - die Motoren sind etwas träge
   - bei niedrigen Geschwindigkeiten braucht der Motor etwas, bis diese erreicht wird
   - bei hohen Geschwindigkeiten braucht der Motor etwas um anzuhalten
 - zum Debugen und Anzeigen des gesteamten Bildes kann der decoder lokal auf einem Rechner mit Bildschirm laufen, falls Tools wie 'rqt_image_view' nicht funktionieren
   - daher auch die Aufteilung zwischen 'encoder' und 'decoder', sollte das jedoch nicht benötigt werden, sollte aufgrund von Performance die kombinierte Klasse genutzt werden
 - die Linienverfolgung ist so programmiert, dass diese Steuerbefehle nur an Kreuzungen anwendet, um fehlerhafte Zustände zu vermeiden

## Projektstatus:
Ziel war, die kamerabasierte Linienverfolgung und Zustandserkennung zu nutzen, um darauf basierend das Spiel Pacman auf zu programmieren
### Erfolge
- die Linienverfolgung funktioniert, wenn die Lichtverhältnisse stimmen, und der Versatz nicht zu hoch ist
- die Kreuzungserkennung und Traversierung funktioniert relativ stabil
- sollte der Roboter vom Pfad abkommen/in fehlerhafte Zustände kommen, Pendelt er sich nach einiger Zeit wieder ein
- Entscheidungen werden kurzsichtig, aber für die jeweilige Kreuzung optimal, getroffen
- die Steuerung mittels XBox-Controller funktioniert, weitere Tasten, Steuergeräte und Befehle können relativ einfach hinzugefügt werden
- die Map-Traversierung ist von Pacman abgekapselt und kann für jede kreuzungsbasierte Anwendung genutzt werden

### Probleme
- der größte Störfaktor sind die Lichtverhältnisse.
  - die Kamera passen sich den Lichtverhältnissen an, dadurch kann nicht immer ein ausreichend großer Kontrast zwischen Map und Linien hergestellt werden
- die Wegfindung, wenn vom Pfad abgekommen sollte noch erweitert/verbessert werden
- die Steuerung der Motoren ist für hohe Präzision sehr umständlich geworden und könnte optimiert/vereinfacht werden
  - die gilt auch für die Geschwindigkeiten, da das Abbiegen relativ langam ist
- die Entscheidungen der Logik ist zwar relativ gut, kann jedoch verbessert werden
- Objekterkennung hat zwar funktioniert, jedoch sind die damit einhergehenden Probleme so groß, dass eine weiterentwicklung sich nicht lohnt
  - Objekte, die zu hell sind, blenden sich in den Linien ein und werden nicht erkannt
  - Objekte, die zu dunkel sind, unterbrechen die Linie sodass die Linienverfolgung/Zustandserkennung gestörrt wird
  - Unhandlichkeit in der Anwendung, da schon weit entfernte Objekte erkannt, aber keine Informationen daraus geschlossen werden kann
- alle Nodes zusammen, beanspruchen eine bemerkbare Menge an Ressourcen
## Fazit
Das Projekt wurde erfolgreich beendet, alle Funktionalitäten wurden umgesetzt und Pacman läuft ohne größere Fehler. Es gibt zwar noch genügend Anhaltspunkte, die optimiert werden könnten, aber für Pacman als Anwendungsbeispiel ist es gut genug.

Aufgrund der Modularität dieser Package, kann man je nach Anwendung relativ leicht, die gewünschte Funktionalität extrahieren 