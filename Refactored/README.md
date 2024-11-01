# **RamBOTs Control System**

## **Overview**

This project is a control system for the RamBOTs robot, integrating various functionalities such as manual control via a PS4 controller, graphical user interface (GUI) display, audio feedback, serial communication with hardware, LiDAR data processing, and machine learning for autonomous behaviors.

The system is organized into several Python modules, each responsible for a specific aspect of the application. This modular design enhances readability, maintainability, and scalability.

---

## **Table of Contents**

- [Project Structure](#project-structure)
- [Module Summaries](#module-summaries)
  - [main.py](#mainpy)
  - [controller.py](#controllerpy)
  - [gui.py](#guipy)
  - [audio.py](#audiopy)
  - [serial_comm.py](#serial_commpy)
  - [lidar.py](#lidarpy)
  - [machine_learning.py](#machine_learningpy)
  - [utilities.py](#utilitiespy)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Controller Inputs](#controller-inputs)
  - [Modes and Features](#modes-and-features)
- [Dependencies](#dependencies)
- [Further Improvements](#further-improvements)
- [License](#license)

---

## **Project Structure**


---

## **Module Summaries**

### **`main.py`**

**Description:**

The entry point of the application. It initializes all components, sets up threading for concurrent execution, and starts the main loop.

**Key Functions:**

- Initializes shared queues for inter-thread communication.
- Creates instances of `AudioManager`, `GUI`, `MyController`, `SerialComm`, `LidarHandler`, and `MachineLearningHandler`.
- Starts threads for GUI handling, controller listening, serial communication, LiDAR processing, and machine learning tasks.
- Keeps the main thread alive and handles graceful termination upon user interruption.

---

### **`controller.py`**

**Description:**

Contains the `MyController` class, which extends the `Controller` class from the `pyPS4Controller` library. It handles all PS4 controller inputs and state management.

**Key Features:**

- Processes joystick movements, button presses, and trigger inputs.
- Manages different robot modes (e.g., walking, push-ups, machine learning).
- Toggles features like autonomous walk, machine learning mode, and stop mode based on controller inputs.
- Communicates with the `AudioManager` to play sounds and with the `GUI` to update display elements.
- Implements a deadzone for joystick inputs to prevent unintentional movements.
- Provides methods to start listening to controller events in a separate thread.

---

### **`gui.py`**

**Description:**

Manages the graphical user interface using PySimpleGUI. It displays the robot's current state, controller inputs, and allows for real-time monitoring.

**Key Features:**

- Displays a table with parameters such as joystick positions, trigger values, mode, and button arrays.
- Shows the current mode of the robot at the top of the window.
- Updates GUI elements based on controller inputs and state changes.
- Runs GUI event handling in the main thread and updates in a separate thread.
- Provides methods to set the controller instance and update mode text.

---

### **`audio.py`**

**Description:**

Handles audio playback and sound effects. It manages the initialization of sounds and provides methods to play specific sounds based on events.

**Key Features:**

- Loads sound files for startup, mode switching, errors, pauses, and songs.
- Sets volume levels for each sound.
- Plays sounds corresponding to different robot modes.
- Allows playing of random or specific songs in dance mode.
- Integrates with the `MyController` class to respond to controller events.

---

### **`serial_comm.py`**

**Description:**

Manages serial communication with external hardware devices like the Teensy microcontroller. It handles sending and receiving data over the serial port.

**Key Features:**

- Initializes the serial connection to the hardware device.
- Constructs data strings based on controller inputs and sends them to the robot.
- Reads responses from the robot and processes them accordingly.
- Handles specific modes, such as checking ODrive parameters for errors.
- Provides methods to parse and validate ODrive parameters.
- Integrates with the `AudioManager` for playing sounds on errors.

---

### **`lidar.py`**

**Description:**

Handles LiDAR data collection and processing. It manages the LiDAR sensor readings and processes the data for use in autonomous behaviors.

**Key Features:**

- Initializes and configures the LiDAR sensor.
- Continuously reads LiDAR data in a separate thread.
- Preprocesses LiDAR data for machine learning inference.
- Runs inference using a machine learning model and shares results via a queue.
- Handles exceptions and ensures resources are released properly.

---

### **`machine_learning.py`**

**Description:**

Contains the `MachineLearningHandler` class, which manages machine learning tasks such as ball tracking for autonomous behaviors.

**Key Features:**

- Initializes the Edge TPU interpreter for the ball tracking model.
- Captures video frames from the camera and preprocesses them.
- Runs inference on video frames to detect a tennis ball.
- Processes detection results to calculate movement commands.
- Communicates movement commands to the driver thread via a queue.
- Optionally displays video frames with detection results for debugging.

---

### **`utilities.py`**

**Description:**

Includes utility functions used across the application. These functions provide common operations needed by multiple modules.

**Key Functions:**

- `kill_program()`: Gracefully terminates the program.
- `rgb(mode)`: Changes the color of the controller's LED based on the mode.
- `pad_str(val)`: Pads a string for serial communication.
- `rm_pad_str(val)`: Removes padding from a string.
- `get_line_serial(ser)`: Reads a line from the serial port.
- `any_greater_than_one(arr)`: Checks if any value in an array exceeds specified bounds.
- `joystick_map_to_range(value)`: Normalizes joystick inputs.
- `trigger_map_to_range(value)`: Normalizes trigger inputs.
- `value_checker(odrive_values, correct_values)`: Validates ODrive parameters.
- `check_odrive_params(input_dict)`: Checks ODrive parameters against expected values.
- Functions for machine learning preprocessing and postprocessing.

---

## **Setup and Installation**

### **Prerequisites**

- **Operating System:** Linux-based system (e.g., Raspberry Pi OS).
- **Python Version:** Python 3.6 or higher.
- **Hardware:**
  - PS4 Controller.
  - Edge TPU (e.g., Coral USB Accelerator).
  - LiDAR Sensor (e.g., RPLidar).
  - Camera compatible with OpenCV.
  - Teensy microcontroller connected via USB.

### **Dependencies**

Install the required Python packages:

```bash
pip install pyPS4Controller
pip install PySimpleGUI
pip install pygame
pip install pyserial
pip install numpy
pip install opencv-python
pip install Pillow
