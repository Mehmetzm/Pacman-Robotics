# Line-Follower

This project implements a ROS2 C++ node for ground-sensor-based line following using the Emaros robot platform.

---

## Features
- **Sensor Data Evaluation:** Accesses the Emaros ground sensors and LEDs to distinguish dark lines from a light-colored floor.
- **Offset Correction:** Calculates real-time steering adjustments based on the line's position relative to the sensors.
- **Intersection Detection:** Uses outer sensors to identify turns or crossroads.
- **Autonomous Turning:** When a turn is detected, the node suspends line following to execute a precise 90° rotation.

---

## Project Structure
- **`src/line_follower.cpp`**: The core C++ source file implementing all logic and sensor integration.
- **`Messdaten/` (Measurement Data)**: Contains multiple `.txt` files with sensor logs from various test runs, including a small C++ utility for data analysis.
- **`Deprecated/`**: Includes an alternative node designed for hybrid control, combining drive commands from this package with the `damt_vision` project.
- **Standard ROS2 Files**: Includes the required `package.xml`, `CMakeLists.txt`, and configuration files.

---

## Prerequisites
### Hardware
- **Emaros Robot**: Requires access to all ground sensors, floor LEDs, and motors.
- **Environment**: A light-colored floor with a dark line (max. width: 2–3 cm).

### Software
- **ROS2 installation** with a functional C++ build environment.
- **Emaros Nodes**: The `floor_sensors_node` and `motor_control` must be active.
- **Dependencies**: All libraries specified in the `CMakeLists.txt`.

---

## Installation & Usage
1. Clone the package into your ROS2 workspace `src` folder.
2. Build and source the workspace:
   ```bash
   colcon build --symlink-install
   source install/setup.bash
   ```
3. **Execution**: Ensure all dependencies are fully running before starting the node to prevent incorrect sensor initialization.
   ```bash
   ros2 run damt_drive line_follower
   ```

---

## Development Notes
- **Sensor Mapping**: Currently, the two inner sensors handle line following, while the outer sensors manage intersection detection.
- **Calibration**: LED brightness and sensor sensitivity must be tuned according to the ambient lighting and floor material.
- **PID Control**: The implementation includes several anti-oversteering mechanisms. These can be simplified if the application requirements are less demanding.

---

## Project Status
The original goal was to use this ground-sensor logic as the primary navigation for a physical Pac-Man game.

### Successes
- Achieved stable line following using only two sensors without losing the path.

### Challenges
- **Intersection Reliability**: The state detection proved inconsistent. Slight offsets in positioning caused the robot to misinterpret straight lines as intersections or miss actual crossroads entirely.

### Conclusion
Due to the hardware limitations in resolving intersection ambiguity reliably, development on this ground-sensor approach was discontinued in favor of the camera-based vision system found in the **`damt_vision`** package.
