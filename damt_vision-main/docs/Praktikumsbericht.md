# Praktikumsdokumentation
Im Rahmen des Hardware-Programmierpraktikums SoSe-2025, zur Entwicklung von EMAROs Robotern, dient dieser Bericht als Zusammenfassung und Auswertung der Ergebnisse.
Die Gruppe bestand ursprünglich aus den vier Mitgliedern Mehmet Zaid Murat, Tony La, Daniel Deutsch und Ahmet Celik.
Aufgrund anderer Verpflichtungen konnte Daniel Deutsch jedoch leider nicht mehr am Praktikum teilnehmen.

Das Praktikumsthema war es, entweder mittels Hardwarebausteinen einen eigenen Prozessor zu bauen oder die Funktionalität der EMAROs-Roboter zu erweitern.
Als Gruppe hatten wir uns entschieden, ein Anwendungsbeispiel für den Roboter zu programmieren, da wir das als unterhaltsamsten empfanden.
Keiner der Gruppenmitglieder hatte vorherige Erfahrungen in Bezug zu den Robotern oder ROS2 im Allgemeinen.

## Einleitung
Das Praktikum bestand aus zwei Teilen: der Prä-Blockphase, in der man pro Woche mindestens 8 Stunden am Projekt arbeiten sollte, und der Blockphase, in der man pro Tag mindestens 6 Stunden am Projekt arbeiten sollte.
Die Prä-Blockphase ging in etwa 10 Wochen lang, während die Blockphase 2 Wochen dauerte.
Bevor das Praktikum begann, sollten wir uns für das Thema unseres Projektes entschieden haben.

### Projektübersicht
Als Anwendungsbeispiel hatten wir uns letztendlich für das Videospiel Pacman entschieden, wobei ein Roboter Pacman simulieren sollte und, wenn möglich, weitere Roboter die Geister.
Nach Rücksprache mit den Praktikumsleitern hatten wir eine ungefähre Ahnung, welche Möglichkeiten der Roboter bietet und welche Limitationen es gab.

So stellten wir uns die Frage, welche der Sensoren sich am besten zur Umsetzung der Fahrlogik für das Spiel eignen würden und ob eine Kombination sinnvoll wäre.

Für die Umsetzung interessant waren:
- die Bodensensoren und LEDs, um Farbwerte vom Boden messen zu können,
- die zwei Frontkameras zur Bildverarbeitung,
- und die Motoren, um den Roboter zu steuern.

Die Pläne haben sich im Laufe des Praktikums mehrere Male geändert.
Zu Beginn war unser Plan, die Bodensensoren zu nutzen, um einer schwarzen Linie auf einem hellen Untergrund folgen zu können – das sollte unsere bodenbasierte Linienverfolgung werden.

Zusätzlich dazu sollte die Kamera genutzt werden, um Kreuzungen zu erkennen und darauf basierend Entscheidungen zu treffen.
So wollten wir am Ende eine hybride Herangehensweise implementieren, um die Wegfindung vor Fehlern abzusichern.

Aus den aufgenommenen Kamerabildern sollte zusätzlich zur Linienerkennung auch die Objekterkennung genutzt werden, um so Items, Gegner und sonstige Informationen zu gewinnen.

Das Spielfeld sollte ein mit Klebestreifen vorgefertigtes Gitter werden und die Geister andere, auf denselben Grundfunktionen basierende EMAROs-Roboter.

Bei den Items hatten wir uns noch nicht entschieden, ob diese analog auf dem Boden liegen oder digital projiziert werden sollten.

## Ablauf
Im Ablaufsplan hatten wir uns überlegt, die erste Phase zu nutzen, um uns mit der Umgebung und dem Roboter vertraut zu machen und grundlegende Funktionen wie die Wegfindung zu implementieren.  
Während wir uns dann in der zweiten Phase mithilfe der grundlegenden Funktionalitäten dem eigentlichen Spiel widmen würden.  

### Pre-Blockphase
Ziel dieser Phase war das Einrichten aller benötigten Werkzeuge, darunter die Roboter, GitLab und ROS2 auf unseren Rechnern, sowie das Vertrautmachen mit diesen Werkzeugen.  
Unsere Gruppe hatte minimale bis gar keine Erfahrung mit Git, wodurch sich das Einrichten der GitLab-Repositories als schwieriger herausgestellt hat als erwartet.

Diese Schwierigkeiten haben sich durch das ganze Praktikum gezogen, mit untreffenden Projektnamen, vergessenen git pull/push requests und mehreren fälschlich erstellten Repositories. 
Darunter sind z.b.:

- [Lehre/Hardwarepraktikum/2025/EMAROs/Roboter-Anwendung/Pacman](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/pacman)
- [EMAROs/Pacman](https://gitlabti.informatik.uni-osnabrueck.de/emaros/pacman)

Diese konnten wir im Nachhinein auch nicht mehr löschen.  

Das Vertrautmachen mit dem Roboter und ROS2 ging schneller als ursprünglich geplant.
Dadurch konnten wir recht früh mit der Implementierung der Linienverfolgung beginnen.
Diese verlief jedoch nicht wie vorgesehen: Da wir vermuteten, dass die kamerabasierte Fahrweise aufwendiger zu implementieren sei, planten wir von Anfang an mehr Zeit dafür ein als für die bodensensorbasierte Fahrweise.

Wir hatten uns in zwei Zweiergruppen aufgeteilt, um jeweils einen Linienverfolgungsansatz zu implementieren.  
- Das kamerabasierte Verfahren konnte bereits nach wenigen Wochen grob einer Linie folgen.  
- Das bodensensorbasierte Verfahren folgte der Linie zwar präziser, verlor sie aber auch sehr schnell.  

Selbst mit PID-Reglern konnte die Verfolgung nicht vollständig kontrolliert werden. Die ersten großen Schwierigkeiten traten jedoch beim Abbiegen auf:  
- Das Schwenken führte bei den Bodensensoren häufig zu Fehlinterpretationen der Klebestreifen, wodurch der Roboter in unerwartete Richtungen fuhr.
- Der Kamera gelang das Abbiegen durch die Tiefenwahrnehmung grundsätzlich besser, allerdings verfolgte der Roboter die Linie nur und nahm eher Kurven als Abbiegungen.

Da sich die Bodensensormethode bis zur Blockphase nicht ausreichend verbessern ließ, entschieden wir uns, ausschließlich die kamerabasierte Fahrlogik weiterzuentwickeln und die andere Methode einzustellen.

### Blockphase

Zu Beginn der Blockphase entschieden wir uns zudem dafür, dass das Spielfeld nicht länger mit Klebestreifen dargestellt, sondern mithilfe von *pygame* auf den Boden projiziert werden sollte.  
Dasselbe galt für die Items und Geister des Spiels – analog sollte nur noch Pacman als EMAROs-Roboter agieren.  

#### Woche 1

Das erste Wochenziel war es, das Fahrverhalten, die Objekterkennung und einen Map-Prototypen zu vervollständigen.  
Bezüglich des Fahrverhaltens hingen wir, aufgrund der an den Bodensensoren verlorenen Zeit, hinter dem Zeitplan.  
Daher wurde die Gruppe noch weiter aufgeteilt, und jeder sollte sich alleine um ein Ziel kümmern.  

Im Laufe der Woche entschieden wir uns trotz einiger Erfolge, die kamerabasierte Objekterkennung einzustellen, da Probleme mit den projizierten Objekten auftraten:  
- helle Objekte verschmolzen mit den Linien und wurden größtenteils nicht erkannt,  
- dunkle Objekte wurden als Rand interpretiert und störten die Linienverfolgung.  

Das größte Problem war allerdings, wie wir die in der Tiefe wahrgenommenen Objekte in die flache, zweidimensionale Karte mappen sollten.  
- Wenn die Kamera ein Objekt aus größerer Entfernung erkannte, musste irgendwie festgestellt werden, wo sich dieses auf der Map befindet.  
- Wenn die Kamera in der Sichtweite limitiert wurde, wurden Objekte zu spät erkannt, sodass die Wahrnehmung nur noch zur Registrierung eingesammelter Objekte diente.  

Dies hätte zu einer zufälligen Wegfindung des Pacmans geführt.  
Da wir keine vielversprechenden Lösungsansätze hatten und es deutlich einfachere und sicherere Methoden zum Tracken der Positionen gab, entschieden wir uns auch hier für eine digitale Umsetzung.  

Auch in Bezug auf die Linienverfolgung traten erhebliche Probleme auf, was dazu führte, dass sich deren Vervollständigung bis zum Ende der ersten Woche zog.  
- Mit der Kamera gelang das Abbiegen und Erkennen der Kreuzungen grundsätzlich,  
- allerdings kam es oft zu Abweichungen, da die Drehungen selten exakt 90 Grad betrugen, wodurch der Roboter vom Weg abkam oder die folgenden Kreuzungen falsch interpretierte.  
- Außerdem verlief der gesamte Abbiegevorgang sehr langsam, was problematisch für die Flucht vor den Geistern gewesen wäre.  

Generell nahm das Feinjustieren der einzelnen Parameter sehr viel Zeit in Anspruch.  

Was in der ersten Woche reibungslos lief, war das Spiel selbst: Da es mit *pygame* programmiert wurde, konnten Fehler schnell behoben werden.  

#### Woche 2

Das zweite Wochenziel war es, das Spiel zu beenden, eine Kommunikation zwischen Spiel und Pacman herzustellen und eine sinnvolle Entscheidungsfindung für Pacman zu implementieren.  
Da wir bereits hinter dem Zeitplan lagen und weitere unerwartete Aufgaben hinzukamen, mussten wir in der zweiten Woche mehr Zeit in die Implementierung von Features als in das Feinjustieren und Fixen von Fehlern investieren.  

Zusätzlich zu den bestehenden Funktionen haben wir eine Schnittstelle für die Steuerung erstellt, über die man die Topics von Steuergeräten abonnieren und die Tasten zu Befehlen für den Roboter mappen kann.  
Außerdem wurde eine Klasse geschrieben, die mit den vom Spiel übermittelten Daten Entscheidungen bezüglich der Wegfindung treffen sollte.  

Da wir die Daten nicht geordnet übermitteln konnten, entschieden wir uns, eine ROS-Message zu definieren, in der wir die Daten ordnen und benennen konnten.  
Wir entschieden uns dazu, die Daten so klein wie möglich zu verpacken, da die Übertragung abhängig von der Internetverbindung war.  

Die Internetverbindung stellte während des gesamten Praktikums eine Problemquelle dar, da die SSH-Verbindung zum Roboter immer wieder abbrach und dadurch unnötig Zeit verloren ging.  

---

### Technische Umsetzung

Weitere technische Details stehen in den Repositories der jeweiligen Packages.  
Im Folgenden finden sich grobe Erklärungen zur Umsetzung der Ideen der Hauptklassen.

#### Sensorbasierte Verfolgung

Um die Linienverfolgung zu realisieren, haben wir die Lichtstärke der LEDs auf das Maximum gesetzt, um so die wahrgenommene Differenz zwischen Boden und Linie zu maximieren.  
Anschließend wurden die durch die vier Sensoren gemessenen RGBC-Werte ausgewertet und in Helligkeit umgerechnet.  

Da die Linienverfolgung an sich präzise funktionierte, aber das Abbiegen zu Fehlern führte, entschieden wir uns, die äußeren Sensoren ausschließlich zur Erkennung der Kreuzungen zu nutzen.  
Dies führte jedoch dazu, dass die Linienverfolgung mit nur noch zwei Sensoren instabil wurde.  

Zudem spielte die Breite und die Textur der Linie eine Rolle für die Messwerte der Sensoren.  
Dies führte zu weiterer Instabilität, und da wir keine sichere Lösung für dieses Problem fanden, entschieden wir uns, diesen Ansatz einzustellen.  

#### Kamerabasierte Verfolgung

Um die kamerabasierte Linienverfolgung zu realisieren, werden beide Kameras des Roboters aktiviert und ein Bild in Full HD mit 10 FPS aufgenommen.  
Generell haben wir verschiedene Konfigurationen getestet. Dabei stellte sich heraus, dass das Aufnehmen der Bilder die rechenaufwendigste Aufgabe für den Roboter ist, gefolgt von der Komprimierung, um Speicherplatz zu sparen.  

Zum Debuggen war dieser Ansatz für uns unumgänglich. Gegen Ende sind wir jedoch auf eine Version umgestiegen, die das Aufnehmen und Verarbeiten der Bilder innerhalb derselben Node erledigt.  
Dies ist effizienter, da keine Bilder mehr publiziert und somit auch nicht mehr ver- und entpackt werden müssen. Dadurch konnten wir die FPS auf 10 erhöhen, ohne dass die CPU voll ausgelastet ist.  

Die Verarbeitung der Bilder erfolgt in mehreren Schritten:

1. Das Bild wird in drei benötigte Bildausschnitte zerschnitten, um unnötige Berechnung zu vermeiden.  
2. Die Bilder werden von drei Farbkanälen auf Graustufen reduziert.  
3. Die Bilder werden verwaschen, um Rauscheffekte zu reduzieren.  
4. Die Bilder werden mit einem Threshold in schwarz und weiß eingeteilt (helle Linie bleibt weiß, alles andere wird schwarz).  
5. Um die weißen Stellen werden Konturen gezeichnet.  

Über diese Konturen kann bestimmt werden, wie der Roboter fahren muss:  
- Die Konturen aus dem Hauptbildausschnitt werden genutzt, um den Fehler für die Linienverfolgung zu berechnen.  
- Die Konturen aus den beiden anderen Bildausschnitten dienen dazu, Abbiegungen nach rechts oder links zu erkennen.  

Das Fahrverhalten selbst ist als Zustandsmaschine umgesetzt, mit zwei Hauptzuständen:  
- **Fahren:** konstante Geschwindigkeit geradeaus, nur kleine Korrekturen.  
- **Abbiegen:** Roboter bleibt stehen und führt eine Drehung aus.  

Die Übergänge werden durch die Bildinformationen gesteuert. Zusätzliche Zustände und Übergänge dienen dazu, Probleme zu vermeiden, z. B.:  
- Beim Übergang von *Fahren* zu *Abbiegen* fährt der Roboter zuerst ein Stück nach vorne. Damit wird sichergestellt, dass er tatsächlich auf der Kreuzung steht und nicht zu früh abbiegt.  
- Ein *Idle*-Zustand verhindert unerwünschte Bewegungen während asynchroner Operationen, ohne die Node komplett zu blockieren.  

Der Übergang ins Abbiegen wird durch zwei Booleans (`rechts`, `links`) gesteuert.  
Beispiele:  
- Sind beide true und der Hauptausschnitt zeigt noch eine Linie → Kreuzung mit vier Wegen.  
- Ist keine Linie mehr sichtbar → T-Kreuzung.  

Die Entscheidungsfindung an Kreuzungen folgt immer demselben Prinzip:  
1. Zuerst wird geprüft, ob ein manueller Befehl vom Spieler vorhanden ist (höchste Priorität).  
2. Danach, ob die Logik-Node einen Befehl publiziert hat.  
3. Wenn beides nicht zutrifft, wird die Richtung zufällig gewählt.  

So kann die Node vollautomatisch und unbegrenzt eine Map traversieren.

#### Pacman Main

Die Main besteht aus drei Hauptteilen:  
- die `main` selbst, welche den Gameloop steuert,  
- die `map_node`, welche als ROS-Node Informationen an den Roboter weitergibt,  
- und das Pylon-Skript, welches den ArUco-Marker trackt.  

Diese Aufteilung war ursprünglich nicht geplant, sondern ist eher zufällig entstanden.  
Da wir nicht wussten, wie wir `pygame` als ROS-Node implementieren könnten, haben wir zunächst versucht, eine ROS-Node einfach als Python-Skript zu starten.  
Nachdem das funktionierte, haben wir die Node als Thread über ein anderes Skript gestartet.  
Dieser Ansatz war letztlich einfacher umzusetzen, als `pygame` direkt mit den sich überschneidenden Loop-Mechanismen in eine ROS-Node einzubinden.  

Anfangs gab es einige kleinere Probleme zwischen den Skripten, die sich aber ohne große Schwierigkeiten beheben ließen.  
Ein größeres Problem war die Übertragung der Spieldaten an den Roboter:  
Hätten wir alles über ein Topic geschickt, wären alle Koordinaten gemischt in einem langen Array verpackt gewesen.  
Da die Anzahl der Koordinaten variabel ist, wäre es unmöglich gewesen, diese zuverlässig zu entpacken – insbesondere, um z. B. zwischen Map-Koordinaten und Geist-Koordinaten zu unterscheiden.  

Daher haben wir uns entschieden, eine eigene ROS-Message zu definieren.  
Da das Repository allerdings als Python-Package aufgebaut ist und Messages in einem C++-Package definiert werden müssen, haben wir extra ein eigenes Package für die Message erstellt.  

---

#### Pacman Logik

Die erste Idee war, einen A\*-Algorithmus zu implementieren, der den günstigsten Weg zwischen zwei Punkten findet.  
Diese Idee stellte sich jedoch als wenig vielversprechend heraus, da es nicht trivial war, den Zielpunkt zu bestimmen.  

Anfangs haben wir alle Spielpunkte, die Pacman einsammeln kann, als mögliche Zielpunkte verwendet.  
Das führte dazu, dass Pacman stumpf alle Punkte nacheinander abarbeitete: zuerst (1,1), dann (1,2) usw.  
Ein weiteres Problem war, dass der A\*-Algorithmus immer zwingend einen Weg findet.  
Wenn das Ziel also in jeder Richtung von einem Geist blockiert war, wählte er trotzdem den „günstigsten“ Weg – direkt durch den Geist.  

Darum entschieden wir uns, dass A\* nicht der beste Ansatz war. Stattdessen haben wir einige Vereinfachungen genutzt:  

1. Alle übermittelten Daten (Positionen, Richtungsvektoren etc.) werden entpackt und ausgewertet.  
2. Mit diesen Daten wird eine Heatmap generiert, um doppelte Berechnungen zu vermeiden.  
3. Nur an der jeweils kommenden Kreuzung wird eine Entscheidung getroffen, da Pacman ohnehin nur dort handeln kann.  
4. Die Entscheidung basiert auf der Bewertung aller möglichen Richtungen bis zur nächsten Kreuzung.  
5. Die Bewertung ist die Summe aus Pfadkosten, den von dort erreichbaren Kreuzungen und einigen Justierungsfaktoren.  
6. Zu diesen Faktoren gehören z. B. die Anzahl erreichbarer Punkte oder die Art der Kreuzung.  

So wird vermieden, dass Berechnungen über die gesamte Map nötig sind, und die Spiellogik bleibt trotzdem sinnvoll.  

---

## Ergebnisse

Das Projektziel – ein Pacman-Spiel mit autonomer, kamerabasierter Linienverfolgung auf dem EMAROs-Roboter – wurde erreicht.  
- Die Linienverfolgung und die Kreuzungserkennung funktionieren stabil und zuverlässig.  
- Die Entscheidungsfindung des Roboters erfolgt jeweils lokal an Kreuzungen und ist für diesen Kontext optimal.  
- Die Pacman-Spiellogik wurde erfolgreich umgesetzt und orientiert sich stark am Originalspiel.  

Es zeigte sich jedoch, dass äußere Faktoren wie Lichtverhältnisse sowie Hardwareeigenschaften (z. B. Motoren) einen erheblichen Einfluss auf Genauigkeit und Zuverlässigkeit haben.  

Zusammenfassend ist die Anwendung vollständig und funktionsfähig, allerdings gibt es noch einige Stellen, die optimiert werden könnten.

### Fazit

Im Verlauf des Praktikums habe wir nicht nur technische Erfahrungen gesammelt, sondern auch einiges über die Arbeitsweise in Projekten gelernt, vor allem in Bezug auf paralleles Arbeiten und gute Planung.
Besonders deutlich wurde das, da dadurch viele unserer Probleme verhindert werden könnten.
Da wir die Aufgaben allerdings unterschätzt oder unerwartete Schwierigkeiten nicht einkalkuliert hatten, 
mussten wir später improvisieren und mehr Zeit in das Beheben von Fehlern investieren, anstatt Details gezielt zu verbessern.

Außerdem habe wir gelernt, wie wichtig eine klare Kommunikation und Abstimmung im Team ist. 
Nur wenn jeder weiß, woran gearbeitet wird bzw. jeder eine eigene Aufgabe hat, lassen sich Überschneidungen oder Missverständnisse vermeiden und effizient Arbeiten.

Auf technischer Ebene konnte wir alle gleichermaßen unsere Kenntnisse im Umgang mit ROS, Robotik, Bildverarbeitung und Git stark erweitern. 
Gleichzeitig haben wir gemerkt, dass äußere unvorhersehbare Faktoren wie Hardwaregrenzen oder Internetverbindungen die Umsetzung stark beeinflussen können und man keine andere Wahl hat, als flexibel darauf zu reagieren.

Insgesamt war das Praktikum sehr lehrreich und unterhaltsam und ist jedem Robotikinteressierten zu empfehlen.