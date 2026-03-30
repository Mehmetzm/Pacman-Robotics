cmake_minimum_required(VERSION 3.8)
project(damt_game_msgs)

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/GameData.msg"
  "msg/IntPoint.msg"
)

ament_package()
