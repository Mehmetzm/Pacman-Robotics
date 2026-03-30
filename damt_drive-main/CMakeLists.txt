cmake_minimum_required(VERSION 3.8)
project(damt_drive)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(emaros_floor_sensors REQUIRED)
find_package(tf2_msgs REQUIRED)
find_package(emaros_i2c_lib REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Motor driver
add_executable(motor_driver src/motor_driver.cpp)
ament_target_dependencies(motor_driver
  rclcpp 
  geometry_msgs
  emaros_i2c_lib
  nav_msgs
)
install(TARGETS
  motor_driver 
  DESTINATION lib/${PROJECT_NAME})


# Line follower
add_executable(line_follower src/line_follower.cpp)
ament_target_dependencies(line_follower
  rclcpp
  std_msgs
  geometry_msgs
  emaros_floor_sensors
  tf2_msgs
)
install(TARGETS
  line_follower
  DESTINATION lib/${PROJECT_NAME})


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
