# damt_map

Dieses Projekt beinhaltet alle Nodes/Skripts, die für das Game Pacman zuständig sind

---

## Features
- Darstellung des Spielfelds
- Umsetzung der meisten Pacman Features
  - Items, Geister, Punktesystem, Gameloop etc.
- tracken des ArUco-Markers (als Pacman) 

---

## Projektstruktur
die Struktur weicht etwas von der gewöhnlichen Ros2-Norm ab.
Das Projekt ist zwar als ros2-package Strukturiert, gestartet wird es allerdings wie ein normales Pythonskript. Es ist aber auch möglich das Spiel als Ros-Node zu starten, was wir allerdings nicht empfehlen würden
- `damt_game/` → enthält alle Pacman relevanten Klassen 
  - `images/` → enthält die für das Spiel genutzte PNGs
  - `sounds/` → enthält die für das Spiel genutzten Sounds
  - `gamestate`→ enthält globale Spielzustände
  - `ghost`→ implementiert den Geist und Pacman
  - `main`→ steuert+initialisiert Gameloop, startet zudem alle weiteren Skripte als Threads 
  - `map_node`→ eine Ros-Node, wird über main als Thread gestartet. Kommuniziert über Ros-Topics mit Pacman
  - `pylon_camera_aruco`→ wird über main als Thread gestartet. Greift auf Kamera zu und erkennt ArUco-Marker
  - `renderer`→ stellt die Map dar
  - `score`→ implementiert verschiedene Items und das Punktesystem
  - `settings`→ definniert Einstellungen und Konstanten    
- der Rest entspricht den Standard-Ros2 Dateien

---

## Voraussetzungen
- Ros2 installation, eine Pythonumgebung mit Extrapaketen Pypylon, CV2 und Pygame   
- An Hardware, wird unabhängig vom Roboter ein extra Rechner mit Kamera und Beamer benötigt.
- an damt packages wird für map_node die damt_game_msg benötigt

---

## Installation & Nutzung
1. Repository in einen von Ros2 zugreifbaren Pfad kopieren
2. die damt_game_msg builden und sourcen
3. Anwendung über python3 main.py starten
5. Pacman, bzw den ArUco-Marker auf die Map und in Sichtfeld der Kamera legen
#### Hinweise:
 - Häufigste fehlerursachen werden Pfadfehler sein
   - main.py: achte darauf, dass Pygame korrekt installiert ist
   - map_node: achte darauf, dass die Node die Ros2-Umgebung findet und die damt_game_msg-installation
   - pylon_camera_aruco: achte darauf, dass Pypylon und CV2 korrekt installiert sind und auf die Kamera zugreifen können
 - das Spielfenster kann mit 'ESC' geschlossen werden, die Threads könnten allerdings zusätzlich maßnamen benötigen
 - es ist darauf zu achten, dass das Spielfeld und der Sichtbereich der Kamera sich überdecken
 
## Projektstatus:
Ziel war, zusätzliche Hardware zu nutzen, um damit eine digitale Pacman-Umgebung für den Emaros zu erstellen
### Erfolge
- das Spiel ist voll funktionsfähig und setzt die meisten Grundfeatures des Originals um  
- ein Emaros-Roboter mit entsprechendem Marker kann getrackt werden und dessen Position wird im Spiel verrechnet
- das Spiel publisht erfolgreich Informationen über Ros-Topics, zudem können die Topics einfach um weitere Informationen erweitert werden  

### Probleme/ToDos
- der Tracker hat Probleme den Roboter konstant zu erkennen
  - da die Map als schwarzer Hintergrund mit weißen Linien Projeziert wird, wird der ArUco-Tracker gestörrt
- Geister werden, wenn sie frightened sind,teilweise als Aruco Marker erkannt(pylon_camera_aruco wandelt das Bild in Graustufen um, was die Geister wie Aruco Marker aussehen lässt)  
- das Spiel kann noch verbessert/erweitert werden, zusätzliche Level, gezieltes Geistverhalten, mehr Items etc.
- das gesamte Spiel könnte Threadsicher gemacht werden, wobei das kein Problem darstellt
- das Spiel könnte noch dynamischer designed werden, um neue Maps zu unterstützen 

## Fazit
Das Projekt wurde erfolgreich beendet, alle geplanten Funktionalitäten wurden umgesetzt das Spiel läuft ohne Fehler, einzig für das Tracking-Problem müsste man sich eine Lösung überlegen