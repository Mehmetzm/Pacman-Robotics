#!/usr/bin/env python3
import rclpy, heapq, sys, os, copy
from rclpy.node import Node
from std_msgs.msg import String, Int16MultiArray
ros_ws_path = os.path.expanduser("~/ros2_ws/install/damt_game/lib/python3.12/site-packages")
if ros_ws_path not in sys.path:
    sys.path.append(ros_ws_path) # vor Ort testen #findet er nicht
from damt_game_msgs.msg import GameData
from collections import deque

#vec_to_direction [current_heading][abolute_Richtungsvektor] --> relative_direction
vec_to_rel = {
    "up":    {(1,0): "geradeaus", (0,-1): "links",  (0, 1): "rechts", (-1,0): "umkehren"},
    "down":  {( 1,0): "geradeaus", (0, 1): "links", (0,-1): "rechts",  (-1,0): "umkehren"},
    "left":  {( 0,-1): "geradeaus", (-1,0): "rechts", (1,0): "links",  (0, 1): "umkehren"},
    "right": {( 0, 1): "geradeaus", (1,0): "rechts",  (-1,0): "links", (0,-1): "umkehren"}
            }

direction_map = {
    (1, 0): "up",
    (-1, 0): "down",
    (0, 1): "right",
    (0, -1): "left",
}

#direction_to_vec[current_heading][relative_direction] --> Richtungsvektor
direction_to_vec = {
    "up": {"geradeaus": (-1, 0), "links":(0, -1), "rechts":(0, 1), "umkehren":(1, 0),},
    "down": {"geradeaus": (1, 0), "rechts": (0, 1), "links": (0, -1), "umkehren": (-1, 0),},
    "left": {"geradeaus": (0, -1), "links": (-1, 0), "rechts": (1, 0), "umkehren": (0, 1),},
    "right": {"geradeaus": (0, 1), "links": (1, 0), "rechts":(-1, 0), "umkehren": (0, -1),}
}

class PackmanLogik(Node):
    def __init__(self):
        super().__init__('pacman_AI')

        #subs und pubs
        self.logik_pub = self.create_publisher(String, '/logik', 1)
        self.game_sub = self.create_subscription(GameData,'/game_data', self.think, 1)
        self.map_sub = self.create_subscription(Int16MultiArray,'/game_map', self.map_update, 1)

        #############   params  #############
        #map
        self.rows = 26 #nicht dynamisch, map node könnte zusaätzlich die Dim übergeben
        self.cols = 48
        self.seg_len = 8 #segmente sind min 8 felder lang, absolut nicht dynamisch, und müsste für jede map angepasst werden
        self.map =  None
        self.heatmap = None
        self.TILE_WIDTH = 1920 // self.cols
        self.TILE_HEIGHT = 1080 // self.rows

        #Ghosts
        self.ghost_tiles = None
        self.last_ghost_tiles = None
        self.heading_ghosts = None

        #Pacman
        self.pac_tile = (0,0)
        self.last_pac_tile = (0,0)
        self.heading_pac = "up"
        self.supermode = False
        self.supermode_duration = 30

        #Items
        self.point_tiles = None
        self.super_point_tiles = None
        self.cherry_tiles = None

        self.next_move = "geradeaus"

    def map_update(self, msg):
        data = msg.data
        if len(data) != self.rows * self.cols:
            self.get_logger().info(f"Error: Map dim stimmen nicht. Erwartet sind 26 rows, 48 collums. Tätsächliche Länge ist: {len(data)}")
            return
        old_map = copy.deepcopy(self.map)
        self.map = [[chr(data[r*self.cols + c]) for c in range(self.cols)] for r in range(self.rows)]
        if old_map != self.map:
            self.get_logger().info(f"neue map erhalten")

    def think(self, msg):
        if not self.map:
            return
        ghosts = [(p.y, p.x) for p in msg.ghost_positions]
        pacman = [(p.y, p.x) for p in msg.pacman]
        points = [(p.y, p.x) for p in msg.points]
        super_points = [(p.y, p.x) for p in msg.super_points]
        cherries = [(p.y, p.x) for p in msg.cherries]

        if not self.ghost_tiles:#initialisierung
            self.ghost_tiles = ghosts.copy()
            self.last_ghost_tiles = [None] * len(ghosts)
            self.heading_ghosts = [None] * len(ghosts)
        else:
            for i, pos in enumerate(self.ghost_tiles):
                if self.last_ghost_tiles[i] != self.ghost_tiles[i]:
                    self.last_ghost_tiles[i] = pos
            self.ghost_tiles = ghosts.copy()

            for i, pos in enumerate(self.ghost_tiles):
                heading_temp = self.get_heading(self.last_ghost_tiles[i], self.ghost_tiles[i])
                if heading_temp:
                    self.heading_ghosts[i] = heading_temp

        self.last_pac_tile = self.pac_tile
        self.pac_tile = self.snap_to_path(pacman[0])
        self.point_tiles = points.copy()
        self.super_point_tiles = super_points.copy()
        self.cherry_tiles = cherries.copy()

        if self.pac_tile == self.super_point_tiles:
            self.supermode = True
            self.timer = self.create_timer(0.1, self.timer_callback)
            self.timer_start = self.get_clock().now()
            self.timer_dauer = rclpy.duration.Duration(seconds=self.supermode_duration)

        heading_temp = self.get_heading(self.last_pac_tile, self.pac_tile)
        if heading_temp:
            self.heading_pac = heading_temp

        #self.get_logger().info(f"pacman absolute-Richtung ist: {self.heading_pac} an pos: {self.pac_tile}")
        self.generate_heatmap()
        if not self.heatmap:
            return

        path, _, u = self.get_segment(self.pac_tile, self.heading_pac) #Pfad bis zum nächsten Tile, an dem eine Entscheidung getroffen werden kann
        if path is None:
            return
        abs_vec, next_path = self.a_stern(path.pop())
        path.extend(next_path)

        self.get_logger().info(f"Path ist: {path}")#debug
        if path:
            self.last_move = self.next_move
            self.next_move = vec_to_rel[self.heading_pac][abs_vec]

        if self.next_move != self.last_move:    
            self.logik_pub.publish(String(data=self.next_move))
        self.get_logger().info(f"heading: ({self.heading_pac}) || pos: ({self.pac_tile}) || next Move: ({self.next_move})")#debug
        self.print_heatmap() #debug bei zu schnellen Publishraten von damt_game/map_node kann es schwierig werden, die karte zu lesen

        self.heatmap = None #resette heatmap, um sicherzugehen, dass nicht auf alten daten gearbetet wird

    # generiere die Heatmap, funktioniert nur wenn alle nötigen Daten vorhanden sind
    def generate_heatmap(self):
        if not self.map:
            self.get_logger().info(f"ERROR, Spielmap fehlt, oder ist fehlerhaft")
            return
        if not self.pac_tile or not self.heading_pac:
            self.get_logger().info(f"ERROR, pacman konnte nicht lokalisiert werden")
            return
        for i, _ in enumerate(self.ghost_tiles):
            if self.ghost_tiles[i] == None or self.heading_ghosts[i] == None:
                self.get_logger().info(f"ERROR, Geist {i} konnte nicht lokalisiert werden")
                return
        self.heatmap = copy.deepcopy(self.map)
        #Wände und noch nicht eingesammelte Punkte
        for r in range(self.rows):
            for c in range(self.cols):
                if self.map[r][c] == "W":
                    self.heatmap[r][c] = 9999
                elif self.map[r][c] == ".":
                    if (r, c) in self.point_tiles:
                        self.heatmap[r][c] = 1
                    else:
                        self.heatmap[r][c] = 5
                else: 
                    self.get_logger().info(f"ERROR map konnte nicht entschlüsselt werden, unbekanntes Zeichen: {self.map[r][c]} an pos {r},{c}")

        #Cherrys
        for (y, x) in self.cherry_tiles:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.heatmap[y][x] -= 10

        #Superpunkte
        for (y, x) in self.super_point_tiles:
            if 0 <= y < self.rows and 0 <= x < self.cols:
                self.heatmap[y][x] -= 30
        if self.supermode:
            basecost = -65
        else:
            basecost = 65
        danger_range = (self.seg_len * 3)//2
        #Geister, hohe Kosten in Laufrichtung, mittlere Kosten gegen Laufrichtung, kosten über mehrere Abschnitte
        for i,(gy, gx) in enumerate(self.ghost_tiles):
            dy, dx = direction_to_vec[self.heading_ghosts[i]]["geradeaus"]
            self.trace_ghost_path(gy, gx, dy, dx, 1, danger_range, basecost, forward=True) #in Laufrichtung
            self.trace_ghost_path(gy - dy, gx - dx, -dy, -dx, 1, 5, basecost, forward=False) #gegen Laufrichtung

    
    #hilfsfunktion um mit DFS die Geistpfade zu berechnen
    def trace_ghost_path(self, y, x, dy, dx, depth, danger_range, basecost, forward):
        if depth > danger_range or not self.is_path((y, x)):#abbruchbedingung
            return
        if not self.is_path((y,x)):
            self.get_logger().info(f"ERROR, Rekursion an pos {y,x} mit tiefe {depth} läuft gegen eine Wand")
            return

        if forward: #in Laufrichtung
            cost = basecost - (depth * 5)
        else:  #gegen Laufrichtung
            cost = (basecost // 10) - depth

        if cost > 0: #könnte negativ werden, wenn danger_range erhöht wird, ohne basecost anzupassen
            self.heatmap[y][x] += cost
        else:
            self.get_logger().info(f"ERROR, heatmap-kosten an pos {y,x} sind {cost}")
            
        if self.is_intersection((y, x)): #bei Kreuzung in alle Richtungen außer zurück
            for ndy, ndx in [(-1,0),(1,0),(0,-1),(0,1)]:
                if (ndy, ndx) == (-dy, -dx):
                    continue
                if self.is_path((y + ndy, x + ndx)): #nur wenn da auch ein Pfad ist
                    self.trace_ghost_path(y + ndy, x + ndx, ndy, ndx, depth+1, danger_range, basecost, forward)
        else:
            if self.is_path((y + dy, x + dx)):
                self.trace_ghost_path(y + dy, x + dx, dy, dx, depth+1, danger_range, basecost, forward)


    #debug
    def print_heatmap(self):
        print()
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                if self.pac_tile[0] == r and self.pac_tile[1] == c:
                    row.append("  P ")
                else:
                    val = self.heatmap[r][c]
                    if val == 9999:
                        row.append("   #")
                    else:
                        row.append(f"{val:4}")
            print("".join(row))
        print()


    # True wenn Kreuzung bzw. Knotengrad != 2, also Kreuzug; zusätzlich: wenn Abbiegung(Knotengrad = 2)
    def is_intersection(self, pos):
        if self.is_path(pos):
            y, x = pos
            grad = 0
            tiles = []
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                if self.is_path((y+dy, x+dx)):
                    tiles.append((dy, dx))
                    grad += 1
            if grad == 2:
                last_y, last_x = tiles[0]
                next_y, next_x = tiles[1]
                if abs(last_y) == abs(next_y) and abs(last_x) == abs(next_x): #kann nicht auf Sackgassen prüfen
                    return False, grad #Fall normaler Gang, da selbe Richtungsvektoren
                else:
                    return True, grad #Fall Abbiegung, da unterschiedlicher Richtungsvektoren
            else:
                return True, grad #Fall Kreuzung, da Knotengrad != 2
        return None, None #Fall ist kein Pfad, sollte am besten Fehler werfen wenn nicht behandelt

    # gibt alle Tiles in Laufrichtung bis zum nächsten Abschnitt aus
    def get_segment(self, pos, heading):
        if not self.is_path(pos):
            return None, None, None
        dy, dx = direction_to_vec[heading]["geradeaus"]
        y, x = pos
        segment = [pos]
        segment_cost = self.heatmap[y][x]
        while True:
            next_pos = (y + dy, x + dx)
            is_intersection, grad = self.is_intersection(next_pos)
            if is_intersection:#Kreuzung, oder Abbiegung. Ab hier kann pacman wieder Entscheidungen treffen
                segment.append(next_pos)
                segment_cost += self.heatmap[next_pos[0]][next_pos[1]]
                break 
            elif is_intersection is None and grad is None:
                return None, None, None
            segment.append(next_pos)
            segment_cost += self.heatmap[next_pos[0]][next_pos[1]]
            y, x = next_pos
        return segment, segment_cost, grad

    #überprüfung, ob feld Pfad oder Wand ist
    def is_path(self, pos):
        y, x = pos
        return (0 <= y < self.rows and 0 <= x < self.cols and self.map[y][x] != "W")
    
    #Beitensuche nach dem nähsten Pfad, da Roboter nicht immer genau auf Linie
    def snap_to_path(self, pos):
        if self.is_path(pos):
                return pos
        visited = set()
        queue = deque()
        queue.append(pos)
        visited.add(pos)
        while queue:
            current = queue.popleft()
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                neighbor = (current[0] + dy, current[1] + dx)
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                if self.is_path(neighbor):
                    return neighbor
                queue.append(neighbor)
        return pos
    
    #die Absolute Laufrichtung emitteln
    def get_heading(self, last_pos, current_pos):
        dy = current_pos[0] - last_pos[0]
        dx = current_pos[1] - last_pos[1]

        #nicht optimal, da pacman durch lag springen kann
        if dy <= -1 and dx == 0:
            return "up"
        elif dy >= 1 and dx == 0:
            return "down"
        elif dy == 0 and dx <= -1:
            return "left"
        elif dy == 0 and dx >= 1:
            return "right"
        elif dy == 0 and dx == 0:
            return None
        else:
            pass
            #self.get_logger().info(f"Laufrichtung konnte nicht ermittelt werden last_pos={last_pos}, current_pos={current_pos}")

        #debug, große toleranz mit lag/springen
        if dy <= -1 and dy < -abs(dx):
            return "up"
        elif dy >= 1 and dy > abs(dx):
            return "down"
        elif dx <= -1 and dx < -abs(dy):
            return "left"
        elif dx >= 1 and dx > abs(dy):
            return "right"
        elif dy == dx:
            return None
        else:
            self.get_logger().info(f"Laufrichtung konnte nicht ermittelt werden last_pos={last_pos}, current_pos={current_pos}")
    
    def a_stern(self, start): #das hat nichts mehr viel mit a* zu tun aber es war mal ein A*-Algorithmus
        best_heading = None
        best_cost = float("inf")
        best_path = []

        #koordinaten der Items, um Wegfindung noch weiter Steuern zu können
        point_set = set(self.point_tiles)
        super_set = set(self.super_point_tiles)
        cherry_set = set(self.cherry_tiles)

        for heading in [(-1,0),(1,0),(0,-1),(0,1)]: #es muss nur die nächste Richtung berechnet werden, dafür ist nur der "Wert" der nächsten Kreuzung wichtig
            segment, seg_cost, grad = self.get_segment(start, direction_map[heading]) #alle möglichen Richtungen bekommen
            if segment is None:
                continue
            
            #übernächste Kreuzung bewerten
            for new_heading in [(-1,0),(1,0),(0,-1),(0,1)]:
                if new_heading[0]  == -heading[0] and new_heading[1]  == -heading[1]: #ignoriere die Rückrichtung
                    continue
                new_segment, new_cost, _ = self.get_segment(start, direction_map[new_heading]) #alle möglichen Richtungen überprüfen
                if new_segment is None:
                    continue
                seg_cost += new_cost #addiere die übernächsten Segmente als Kosten auf die nächste Kreuzung, um die Gefahr der nächsten Kreuzung zu bewerten

            #bewertung der Gefahr der Nächsten Kreuzung: erst den Mittelwert bestimmen, dann mit Gefahrenbewertung multiplizieren
            if grad == 1: #Sackgassen nicht vorhanden, aber theoretisch am gefährlichsten
                seg_cost *= 4
            elif grad == 2: #Abbiegung, gefährlicher und weniger Kosten, da nicht so viele benachbarte Pfade. D.h fixxkosten müssen addiert werden
                seg_cost = (seg_cost / (grad-1)) * 1.5 # 50% teurer
            elif grad == 3: #T-kreuzung, mittelgefährlich
                seg_cost = (seg_cost / (grad-1)) * 1.2 # 20% teurer
            elif grad == 4: #normale Kreuzung, zu bevorzugen
                seg_cost = (seg_cost / (grad-1)) * 1

            #weitere Einstellmöglichkeiten für die Wegfindung 
            for _, (y, x) in enumerate(segment):
                if (y, x) not in point_set:
                    seg_cost *= 1.1  # 10% teurer weil nichts wichtiges eingesammelt
                else:
                    pass
                if (y, x) not in super_set:
                    pass
                else:
                    seg_cost *= 0.7 # 30% Rabatt, da gutes Item eingesammelt
                if (y, x) not in cherry_set:
                    pass
                else:
                    seg_cost *= 0.9 # 10% Rabatt

            if seg_cost < best_cost: #Speichere die "beste" Richtung ab
                best_heading = heading
                best_cost = seg_cost
                best_path = segment

        return best_heading, best_path

    def timer_callback(self):
        if self.get_clock().now() - self.timer_start >= self.timer_dauer:
            self.timer.cancel()

    

def main(args=None):
    rclpy.init(args=args)
    node = PackmanLogik()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
