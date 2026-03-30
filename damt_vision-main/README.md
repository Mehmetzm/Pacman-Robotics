# damt_vision

This project contains all ROS2 nodes required to control an Emaros robot for a physical Pac-Man application.

---

## Features
- **Vision-based Line Detection:** Identifies floor markings using a camera.
- **Path Following:** Tracks lines and detects intersections or turns in real-time.
- **Manual Control:** Supports manual robot steering, e.g., via a controller.
- **Autonomous Navigation:** Features semi-intelligent pathfinding for the game environment.
- **Object Recognition:** Detects in-game entities such as ghosts and items.

---

## Project Structure
- **`damt_vision/`**: Core source files.
  - **`cam_encoder`**: Handles camera initialization, image capture, compression, and publishing.
  - **`cam_decoder`**: Subscribes to and decompresses images, performs line following, detects intersections, and manages driving behavior.
  - **`cam_combined`**: A unified version of the encoder and decoder classes.
  - **`controllhub`**: Manages communication between peripherals and the drive control system.
  - **`pac_logik`**: Calculates driving decisions based on the current game state.
- **`Messungen/`**: Performance metrics regarding the computational load of various nodes.
- **`Deprecated/`**: Legacy or alternative versions no longer in active development.
  - **`object_detector`**: An early-stage object detection system for ghosts and items.
- All other files follow standard ROS2 package conventions.

---

## Prerequisites
- **Software:** ROS2 installation and a Python environment.
- **Hardware:** Dual cameras, motors, and a suitable ArUco marker.
- **Dependencies:** - **Emaros packages:** `emaros_controll motor_controll` is required.
  - **Damt packages:** `pac_logik` requires the [damt_game_msg](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_game_msg) package.
  - **Optional:** `emaros_xbox_bt xbox_publisher` for controller support and `emaros_status_information` for CPU monitoring.

---

## Installation & Usage
1. Copy the repository into the **src/** folder of your ROS2 workspace.
2. Build and source the workspace.
3. Start the system using either:
   - `emaros_controll motor_controll` + `damt_vision cam_combined`
   - `emaros_controll motor_controll` + `damt_vision decoder` + `damt_vision encoder`
4. Use a dark map with light-colored lines (compatible with [damt_map](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_map/-/tree/main?ref_type=heads)).
5. The robot drives fully autonomously; if no specific commands are given, it explores the map randomly.

#### Important Notes:
- **Lighting:** Ambient light significantly impacts line detection accuracy.
- **Blind Spot:** The cameras have a ~10cm blind spot directly in front of the robot at ground level.
- **Motor Calibration:** Motor response is not calibrated and may vary between individual robots or directions.
- **Inertia:** Motors exhibit lag; they take time to reach target speeds and have a braking distance at high speeds.
- **Debugging:** For image streaming/debugging, run the `decoder` locally on a machine with a display if `rqt_image_view` is unavailable. For production, use `cam_combined` to improve performance.

---

## Project Status
The goal was to utilize camera-based line following and state detection to implement a physical Pac-Man game.

### Successes
- Stable line following under proper lighting conditions.
- Reliable intersection detection and traversal.
- Self-correction: The robot recovers and realigns if it deviates from the path.
- Localized decision-making is optimized for each intersection.
- Flexible control: Xbox controller support is integrated and easily expandable.

### Known Issues
- **Lighting Sensitivity:** Camera auto-adjustment can sometimes reduce the contrast between the map and the lines.
- **Path Recovery:** Navigation logic after losing the path could be further refined.
- **Motor Precision:** High-precision steering is currently complex and could be simplified, especially for slow turns.
- **Object Detection Limitations:** Bright objects can blend into lines, while dark objects can break the line-following logic. 
- **Resources:** Running all nodes simultaneously consumes a significant amount of system resources.

## Conclusion
The project was successfully completed. All core functionalities are implemented, and Pac-Man runs without major errors. While there is room for optimization, the current system is well-suited for its application. Due to its modular design, specific functionalities can be easily extracted for other intersection-based navigation tasks.
