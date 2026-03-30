# damt_game_msg

This ROS2 package defines the custom message interfaces used for data transmission throughout the Pac-Man robotic system.

---

## Features
- **Simplified Data Transfer:** Standardizes the game state communication between different nodes.
- **Bandwidth Efficiency:** Uses arrays of 16-bit integers (`int16`) for coordinates to minimize network load during wireless transmission.
- **Cross-Language Compatibility:** Implemented as a C++ package to ensure the messages can be reliably built and used by both Python and C++ nodes, such as `damt_map` and `damt_vision`.

---

## Project Structure
- **`msg/`**: Contains the definition files for the custom messages.
  - [cite_start]**`IntPoint.msg`**: Defines a 2D coordinate point ($x, y$)[cite: 1, 3].
  - [cite_start]**`GameData.msg`**: A comprehensive structure containing positions for ghosts, Pac-Man, pellets, power pellets, and cherries[cite: 2, 3].
- All other files are standard ROS2/CMake configuration files required for the build process.

---

## Dependencies
While this package provides no standalone functionality, it is a **required dependency** for [damt_map](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_map) and [damt_vision](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_vision).

---

## Installation & Setup
1. Copy this package into the **`src/`** directory of your ROS2 workspace.
2. **Crucial:** Because these messages are used by both the publisher (game simulation) and the subscriber (robot), this package must be installed on **both machines**.
3. Build the package to generate the message headers/libraries:
   ```bash
   colcon build --symlink-install
   source install/setup.bash
   ```

#### Important Notes:
- **Build Errors:** Ensure the directory structure is exactly as provided to avoid common path and build failures.
- **Customization:** If high-precision coordinates are needed, `GameData.msg` can be modified to use standard ROS2 floating-point arrays instead of 16-bit integers.
