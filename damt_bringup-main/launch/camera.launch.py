import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, ExecuteProcess, TimerAction
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
#kopiert von emaros_bringup

    status_node = Node(
            package='emaros_status_information',
            executable='emaros_status_information',
            name='emaros_status_information',
            output='screen'
            )

    motor_controller_node = Node(
            package='emaros_control',
            executable='motor_control',
            name='emaros_motor_controller_node',
            output='screen'
            )
    
    camera_node = Node(
            package='damt_vision',
            executable='encoder',
            name='encoder',
            output='screen'
            )
    
    xbox_bt_node = Node(
            package='emaros_xbox_bt',
            executable='xbox_publisher',
            name='xbox_bt',
            output='screen'
            )
    
    controllhub = Node(
            package='damt_vision',
            executable='controllhub',
            name='controllhub',
            output='screen'
            )
    
    logik_node = Node(
            package='damt_vision',
            executable='pac_logik',
            name='pac_logik',
            output='screen'
            )

    decoder_node = Node(
            package='damt_vision',
            executable='decoder',
            name='decoder',
            output='screen'
            )
    
    combined_node = Node(
            package='damt_vision',
            executable='cam_combined',
            name='cam_combined',
            output='screen'
            )

    return LaunchDescription([
        status_node,
        motor_controller_node,
        #camera_node,
        xbox_bt_node,
        controllhub,
        logik_node,
        #decoder_node,
        combined_node
    ])



