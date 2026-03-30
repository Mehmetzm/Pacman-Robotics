import sys, os, rclpy, settings
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
from pylon_camera_aruco import Pac_Coords

# nicht optimale Lösung um die Daten an den emaros Roboter zu schicken
ros_ws_path = os.path.expanduser("~/ros2_ws/install/damt_game/lib/python3.12/site-packages")
if ros_ws_path not in sys.path:
    sys.path.append(ros_ws_path)
from damt_game_msgs.msg import GameData, IntPoint
import gamestate


class Packman_Map(Node):
    def __init__(self):
        super().__init__('pacman_map')
        self.map_pub = self.create_publisher(Int16MultiArray,'/game_map', 1)
        self.data_pub = self.create_publisher(GameData,'/game_data', 1)
        self.create_timer(5.0, self.update_map)
        self.create_timer(0.2, self.update_data)
        self.get_logger().info(f"Map size: {settings.NUM_ROWS}, {settings.NUM_COLS}")

    def update_map(self):
        msg = Int16MultiArray()
        msg.data = [ord(cell) for row in settings.MAP for cell in row]
        self.map_pub.publish(msg)

    def update_data(self):
        msg = GameData() 
        msg.ghost_positions = []
        for ghost in gamestate.ghosts:
            pt = IntPoint()
            pt.x = round(ghost.rect.centerx) // settings.TILE_WIDTH
            pt.y = round(ghost.rect.centery) // settings.TILE_HEIGHT
            msg.ghost_positions.append(pt)
        pac_pt = IntPoint()
        pac_pt.x = Pac_Coords.x_proj // settings.TILE_WIDTH
        pac_pt.y = Pac_Coords.y_proj // settings.TILE_HEIGHT
        msg.pacman = [pac_pt]
        msg.points = [IntPoint(x=p[0]// settings.TILE_WIDTH, y=p[1]// settings.TILE_HEIGHT) for p in gamestate.score_system.export_pellets()]
        msg.super_points = [IntPoint(x=sp[0]// settings.TILE_WIDTH, y=sp[1]// settings.TILE_HEIGHT) for sp in gamestate.score_system.export_superpellets()]
        msg.cherries = [IntPoint(x=ch[0]// settings.TILE_WIDTH, y=ch[1]// settings.TILE_HEIGHT) for ch in gamestate.score_system.export_cherry()]
        self.data_pub.publish(msg)

def main(args=None):
    node = Packman_Map()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()