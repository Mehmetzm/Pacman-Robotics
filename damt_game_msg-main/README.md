# Game Message
dient zur Übertragung der Spieldaten

## Inhalt / Features:
- der Zweck dieses Ros-Pakets ist es eine Message du definieren, weche die Datenübertragung vereinfachen soll

## Projektstruktur:
- **msg/** beinhaltet die msg-Dateien
- der Rest sind Ros2 Standarddateien
- dieses Ros2 package hat für sich ganommen keinen Nutzen, wird allerdings von [damt_map](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_map) und [damt_vision](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_vision) benötigt
- da es nicht möglich war, die msg in dem python package von [damt_map](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_map) zu builden, wurde diese C++ package erstellt

## Kurzanleitung:
- kopiere diese package in den **src/** Ordner des Ros-work-spaces
- da diese msg sowohl von publisher als auch von subscriber benötigt wird, muss die package auf beiden Rechnern vorhanden sein
  - d.h dem Rechner, welches das Spiel simuliert, und dem Roboter
- bevor die msg von ros2 erkannt wird, muss diese erst mit colcon build --symlink-install und source install/setup.bash gebaut werden
  - es kommt dabei schnell zu Pfad-/ bzw. Build-fehlern. Stelle sicher, dass die Ordnerstruktur richtig ist
- um Bandbreite zu sparen wird ein Array aus 16-Bit Integern definiert, sollte das nicht notwendig sein, kann man auch die ros2 standard Floatpoint-array verwenden
  - dazu muss nur die GameData.msg angepasst werden