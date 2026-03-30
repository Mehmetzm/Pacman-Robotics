import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Joy

class CommandPublisher(Node):
    def __init__(self):
        super().__init__('command_publisher')
        self.cmd_pub = self.create_publisher(String, '/controll', 1)
        self.xbox_sub = self.create_subscription(Joy, '/joy', self.controller_callback, 1)
        #beliebige controller adden
        self.commands = ["geradeaus", "links", "rechts", "umkehren"]

    #Beim verändern der xbox Steuerun müssen die Tasten neu gemappt werden
    def controller_callback(self, msg):
        # Steuerkreuz: links:[6]->-1.0, oben:[7]->-1.0, rechts:[6]->1.0, unten:[7]->1.0
        if msg.axes[6] != 0.0 or msg.axes[7] != 0.0:
            self.get_logger().info(f"Steuerkreuz pressed: {msg.axes[6]}, {msg.axes[7]}")

        result = String()
        befehl = None
        #Die Befehle werden von Pacman relativ interpretiert, d.h. die Richtungen werden aus der Sicht des Pacman umgestzt
        #gemappt ist nur das Steuerkreuz, weitere elemente könnten hinzugefügt werden
        if msg.axes[7] == -1.0:
            befehl = "geradeaus"
        elif msg.axes[7] == 1.0:
            befehl = "umkehren"
        elif msg.axes[6] == -1.0:
            befehl = "links"
        elif msg.axes[6] == 1.0:
            befehl = "rechts"
        if befehl and befehl in self.commands:
            result.data = befehl
            self.cmd_pub.publish(result)


def main(args=None):
    rclpy.init(args=args)
    node = CommandPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
