import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, ExecuteProcess, TimerAction
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
#kopiert von emaros_bringup

    # urdf_file = os.path.join(
    #         get_package_share_directory('emaros_description'),
    #         'urdf',
    #         'emaros.urdf' 
    #         )

    # with open(urdf_file, 'r') as infp:
    #     robot_description = infp.read()
    sensor_node = Node(
            package='emaros_floor_sensors',
            executable='floor_sensors_node',
            name='floor_sensors_node',
            output='screen'
            )

    motor_controller_node = Node(
            package='emaros_control',
            executable='motor_control',
            name='emaros_motor_controller_node',
            output='screen'
            )
  
    driver_node = Node(
            package='damt_drive',
            executable='motor_driver',
            name='motor_driver',
            output='screen'
            )

    delayed_line_node = TimerAction(
        period=3.0,  # Sekunden warten
        actions=[
            Node(
                package='damt_drive',
                executable='line_follower',
                name='line_follower',
                output='screen'
            )
        ]
    ) 
    line_node = Node(
            package='damt_drive',
            executable='line_follower',
            name='line_follower',
            output='screen'
            )





    return LaunchDescription([
        sensor_node,
        motor_controller_node,
        driver_node,
        #line_node,
        delayed_line_node,
        ])



