# Line-Follower
Projekt zur bodensensorbasierten Linienverfolgung für die Emaros-Roboter

## Inhalt / Features:
- greift auf die Boden- Sensoren/LEDs des Emaros-Roboters zu und wertet die Sensordaten aus, um dunkle Linien zu unterscheiden
- berechnet aufgrund des Versatzes der Linie zwischen den Sensoren die Korrektur aus, die gefahren werden muss, um der Linie zu folgen
- erkennt mittels äußerer Sensoren, ob es sich um eine Abbiegung/Kreuzung handelt
- im Falle des Abbiegens folgt die Node nicht mehr der Linie, sondern dreht sich unabhängig davon um 90°

## Projektstruktur:
- beinhaltet wie jedes Ros2 C++-Paket, die Standarddateien(package.xml, CMakeList, etc.)
- der Source-Ordner, welche die C++ Datei line_follower.cpp enthält, welche wiederum alle beschriebene Funktionalitäten umsetzt
- zusätzlich gibt es noch den Messdaten-Ordner, welcher mehrere TXT-Dateien enthält. Diese beinhalten bei verschiedenen Versuchen ermittelte Messdaten
und eine kleine C++-Datei, welche zum Auswerten der gemessenen Daten genutzt wurde
- der deprecated-Ordner enthält eine zweite Node, welcher die Funktionalität hat die Fahrbefehle aus line_follower und dem [damt_vision](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_drive) Projekt zu verrechnen, um eine hybride Steuerung zu ermöglichen

## Kurzanleitung:
die Node sollte ohne weitere Probleme, auf einer ros2 Installation, gebuildet und ausgeführt werden können
### Vorraussetzung:
- eine ros2 Installation, eine C++ Umgebung und die in der CmakeList angegebenen dependencies
- das Projekt greift an Hardware, auf alle Bodensensoren, alle Boden-LEDs und den Motor zu
- an Standard Emaros-Nodes werden floor_sensors_node und motor_control benötigt
### Nutzung:
- beim starten der Nodes, ist zu beachten, dass die line_follower erst gestartet werden sollte, wenn alle dependencies voll funktionsfähig laufen,
sonst kann es dazu kommen, dass die line_follower Node, falsche Sensordaten interpretiert und in einen falschen Zustand gerät
- damit die Node die Linie erkennen kann, wird ein heller Boden mit einer dunklen Linie benötigt
- die Breite der Linie sollte max. 2-3 cm entsprechen, bei breiteren Linien müsste der Code entsprechend angepasst werden
- gestartet wird die Node nach dem Build mit dem Befehl: ros2 run damt_drive line_follower
### Bearbeitung:
- sowohl die C++ Datei, als auch einige Messdaten enthalten Kommentare, welche die Ansätze benennen oder die interpretation der Werte vereinfachen
- sollte jemand das Projekt weiter fortführen, sind einige sachen zu beachten:
  1. die "Zuweisung" der vorhandenen Sensoren sollte angepasst werden
     - aktuell sind die inneren zwei für die Linienverfolgung, und die äußeren für die Kreuzungsenkennung zuständig
  2. die Helligkeit der LEDs und die Empfindlichkeit der Sensoren muss je nach Umgebungangepasst werden 
  3. der PID-Regler setzt mehrere Ansätze um, um das Übersteuern zu verhindern
     - welche für die geplante Anwendung nicht benötigt werden sollten der Einfachheit halber entfernt werden
  4. die Linienverfolgung besteht aus zwei Teilen:
     - der einfachen Verfolgung
     - die Erkennung von Abbiegungen
  - ähnlich wie in Punkt 2. sollte die Erkennung, wenn nicht benötigt, entfernt werden
## Projektstatus:
Ziel war, die Linienverfolgung und Zustandserkennung zu nutzen, um darauf basierend das Spiel Pacman auf zu programmieren
### Erfolge
- die Linienverfolgung funktioniert so weit, dass der Roboter mit nur 2 Sensoren einer Linie folgen kann, ohne diese zu verlieren
### Probleme
- die Zustandserkennung erwies sich als nicht zuverlässig
- sobald der Roboter etwas von der Linie versetzt fuhr, interpretierte er die Linie als Kreuzung
- Umgekehrt bestand das selbe Problem. Sobald der Roboter versetzt von der Linie an einer Kreuzung ankam, interpretiert er diese als keine oder als falsche Art von Kreuzung
### Fazit
- aufgrund der limitierten Möglichkeiten das Problem sicher zu beheben haben wir uns entschieden diesen Ansatz einzustellen
- stattdessen haben wir den Kammera basierten Ansatz von [damt_vision](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_drive) genutzt.