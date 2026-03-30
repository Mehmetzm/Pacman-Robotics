# damt_map

This project contains all the nodes and scripts responsible for the Pac-Man game logic, environment, and tracking.

---

## Features
- **Field Rendering:** Visual representation of the game board.
- **Core Game Mechanics:** Implementation of items, ghosts, scoring systems, and the main game loop.
- **ArUco Marker Tracking:** Tracks a physical ArUco marker to represent Pac-Man's position in the game.

---

## Project Structure
While structured as a ROS2 package, the project is primarily launched as a standard Python script. However, it is possible to run the game as a ROS node (though not recommended for this specific implementation).

- **`damt_game/`**: Contains all Pac-Man relevant classes.
  - **`images/`**: PNG assets used for the game interface.
  - **`sounds/`**: Audio files for game effects.
  - **`gamestate`**: Manages global game states.
  - **`ghost`**: Implements behavior for both ghosts and Pac-Man.
  - **`main`**: The entry point that initializes the game loop and manages other scripts as threads.
  - **`map_node`**: A ROS node started via a thread in `main`; handles communication with Pac-Man via ROS topics.
  - **`pylon_camera_aruco`**: A threaded script that accesses the camera and performs ArUco marker recognition.
  - **`renderer`**: Handles the visual output of the game map.
  - **`score`**: Manages items and the points system.
  - **`settings`**: Defines global configurations and constants.
- All other files follow standard ROS2 package conventions.

---

## Prerequisites
- **Software:** ROS2 installation and a Python environment with `pypylon`, `opencv-python` (`cv2`), and `pygame`.
- **Hardware:** An external computer with a camera and projector (independent of the robot).
- **Dependencies:** Requires the [damt_game_msg](https://gitlabti.informatik.uni-osnabrueck.de/lehre/hardwarepraktikum/2025/emaros/roboter-anwendung/damt_game_msg) package for the `map_node`.

---

## Installation & Usage
1. Copy the repository into a path accessible by ROS2.
2. Build and source the `damt_game_msg` package.
3. Start the application using: `python3 main.py`.
4. Place the robot (with the ArUco marker) on the projected map within the camera's field of view.

#### Important Notes:
- **Path & Installation Errors:**
  - Ensure `pygame` is correctly installed for `main.py`.
  - Verify that `map_node` can locate the ROS2 environment and the `damt_game_msg` installation.
  - Ensure `pypylon` and `cv2` have correct camera access permissions.
- **Exit:** The game window can be closed with 'ESC', though threads may require manual termination.
- **Alignment:** Ensure the projected game field and the camera's field of view overlap correctly.

---

## Project Status
The objective was to utilize external hardware to create a digital Pac-Man environment for the Emaros robot.

### Successes
- Fully functional game implementing the core features of the original Pac-Man.
- Successful tracking of the Emaros robot via marker, integrating its physical position into the game logic.
- Stable information publishing via ROS topics, with an easily expandable architecture.

### Known Issues / To-Dos
- **Tracking Stability:** The ArUco tracker is occasionally disrupted by the high contrast of the projected white lines on a black background.
- **Ghost Interference:** Frightened ghosts are sometimes misidentified as ArUco markers because `pylon_camera_aruco` processes images in grayscale.
- **Gameplay Enhancements:** Future updates could include targeted ghost AI, additional levels, and more items.
- **Optimization:** The system could be further refined for thread safety and dynamic map support.

## Conclusion
The project was successfully completed with all planned functionalities operational. The game runs without errors, though the tracking interference remains the primary area for future improvement. Due to its modularity, the system provides a solid foundation for further development.
