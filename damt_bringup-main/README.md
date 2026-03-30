# damt_bringup

This ROS2 package is a customized version of the `emaros_bringup` package, specifically optimized to simplify the initialization and launching of all nodes required for the Pac-Man game.

---

## Features
- **Centralized Launching:** Orchestrates the startup of multiple nodes (vision, map, logic, and drive) using ROS2 launch files.
- **Workflow Optimization:** Reduces the manual effort required to start individual components of the Pac-Man robotic system.

---

## Project Structure
- **`launch/`**: Contains the `.launch.py` files used to boot the complete Pac-Man environment.
- **`config/`**: Stores parameter files and configurations for the robot's hardware and game settings.
- The remaining files follow standard ROS2 package conventions (`package.xml`, `CMakeLists.txt`).

---

## Dependencies
This package is a **non-essential utility**. It is not required by any other node to function correctly. If you prefer to launch your nodes manually or via custom scripts, this package can be safely ignored or deleted.

---

## Usage
To launch the entire Pac-Man system:
1. Ensure all other `damt` packages are built and sourced.
2. Execute the bringup launch file (replace `[launch_file]` with your specific file name):
   ```bash
   ros2 launch damt_bringup [launch_file].launch.py
   ```

---

## Project Status
This package served as the primary orchestrator during the final testing phase of the project, ensuring that the camera-based vision, game logic, and motor controls were synchronized from the start.
