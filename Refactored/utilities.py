import os
import signal
import subprocess
import sys
import math
import numpy as np

def kill_program():
    """
    Terminates the program gracefully by sending a SIGTERM signal to the current process.
    """
    pid = os.getpid()
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as e:
        print(f"Error sending signal: {e}")
        sys.exit(1)

def rgb(mode):
    """
    Changes the color of the controller's LED based on the provided mode.
    """
    # Get the path of the current script
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    bash_command = f"sudo bash {script_dir}/controllerColor.sh "

    # Map modes to RGB values
    mode_colors = {
        0: "255 255 255",   # White
        1: "255 255 0",     # Yellow
        2: "255 111 0",     # Orange
        3: "8 208 96",      # Greenish
        4: "255 0 255",     # Purple
        5: "0 255 0",       # Green
        -1: "255 0 0"       # Red (Paused/Error)
    }

    rgb_values = mode_colors.get(mode, "255 0 0")  # Default to red if mode not found
    bash_command += rgb_values

    subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

def pad_str(val):
    """
    Pads a string with '~' characters to a total length of 120 characters.
    """
    return val.ljust(120, '~')

def rm_pad_str(val):
    """
    Removes '~' padding characters from a string.
    """
    return val.replace('~', '')

def get_line_serial(ser):
    """
    Reads a line from the serial port and removes padding.
    """
    line = ser.readline().decode(errors='ignore').strip()
    return rm_pad_str(line)

def any_greater_than_one(arr):
    """
    Checks if any value in the array is greater than 1.1 or less than 0.9.
    """
    return any(value > 1.1 or value < 0.9 for value in arr)

def joystick_map_to_range(value):
    """
    Maps joystick input from its original range to a normalized range of [-1, 1].
    """
    if abs(value) < 32767 / 10:
        return 0.0
    return value / 32767

def trigger_map_to_range(value):
    """
    Maps trigger input from its original range to a normalized range of [-1, 1].
    """
    if value < 0:
        return value / 65534
    elif value > 0:
        return value / 65198
    else:
        return 0.0

def value_checker(odrive_values, correct_values):
    """
    Checks the odrive_values against the correct_values and returns a tuple:
    (is_correct, error_dict)
    """
    if not isinstance(odrive_values, dict):
        return (False, {"Error": "value_checker: nested dictionary was not passed in"})

    error_dict = {}
    for key, expected_value in correct_values.items():
        actual_value = odrive_values.get(key)
        if actual_value != expected_value:
            error_dict[key] = actual_value

    return (len(error_dict) == 0, error_dict)

def check_odrive_params(input_dict):
    """
    Checks the ODrive parameters against expected values and returns a tuple:
    (has_no_error, error_list)
    """
    correct_values_axis0 = {
        'encoder.config.abs_spi_cs_gpio_pin': '7.00',
        'encoder.config.cpr': '16384.00',
        'encoder.config.mode': '257.00',
        'motor.config.current_lim': '22.00',
        'motor.config.current_lim_margin': '9.00',
        'motor.config.pole_pairs': '20.00',
        'motor.config.torque_constant': '0.03',
        'controller.config.vel_gain': '0.10',
        'controller.config.vel_integrator_gain': '0.08',
        'controller.config.vel_limit': ''
    }
    correct_values_axis1 = {
        'encoder.config.abs_spi_cs_gpio_pin': '8.00',
        'encoder.config.cpr': '16384.00',
        'encoder.config.mode': '257.00',
        'motor.config.current_lim': '22.00',
        'motor.config.current_lim_margin': '9.00',
        'motor.config.pole_pairs': '20.00',
        'motor.config.torque_constant': '0.03',
        'controller.config.vel_gain': '0.10',
        'controller.config.vel_integrator_gain': '0.08',
        'controller.config.vel_limit': ''
    }

    error_list = []
    for odrivename, odrivedict in input_dict.items():
        for axisname, axisdict in odrivedict.items():
            axis_correct_dict = correct_values_axis0 if axisname == "axis0" else correct_values_axis1

            is_correct, errors = value_checker(axisdict, axis_correct_dict)

            if not is_correct:
                for param, value in errors.items():
                    error_string = f"In {odrivename}, {axisname}: {param} is {value}, should be: {axis_correct_dict[param]}"
                    error_list.append(error_string)

    return (len(error_list) == 0, error_list)

def process_image(interpreter, image, input_index):
    """
    Processes an image using the given interpreter and returns the result.
    """
    input_data = np.array(image).astype(np.uint8)
    input_data = input_data.reshape((1, 224, 224, 3))

    # Process
    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()

    # Get outputs
    output_details = interpreter.get_output_details()
    positions = interpreter.get_tensor(output_details[0]['index'])
    conf = interpreter.get_tensor(output_details[1]['index']) / 255.0
    result = []

    prev_area_pos = getattr(process_image, "prev_area_pos", 0)

    for idx, score in enumerate(conf):
        pos = positions[0]
        area_pos = area(pos)
        if score > 0.99 and (350 <= area_pos < 50176) and prev_area_pos > 400:
            result.append({'pos': positions[idx]})
        process_image.prev_area_pos = area_pos  # Update prev_area_pos for the next iteration

    return result

def area(pos):
    """
    Calculates the area of a bounding box given by pos.
    """
    side_length = distance((pos[0], pos[1]), (pos[2], pos[3]))
    return side_length ** 2

def distance(point1, point2):
    """
    Calculates the Euclidean distance between two points.
    """
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def calculate_direction(X, frame_width=320):
    """
    Calculates the direction based on the X coordinate of the object.
    """
    increment = frame_width / 3
    if (2 * increment) <= X <= frame_width:
        return -0.1  # Turn left
    elif 0 <= X < increment:
        return 0.1   # Turn right
    elif increment <= X < (2 * increment):
        return 0.0   # Move forward or maintain heading

def bbox_center_point(x1, y1, x2, y2):
    """
    Calculates the center point of a bounding box.
    """
    bbox_center_x = int((x1 + x2) / 2)
    bbox_center_y = int((y1 + y2) / 2)
    return [bbox_center_x, bbox_center_y]

def preprocess_lidar_data(lidar_data):
    """
    Preprocesses LiDAR data for inference.
    """
    lidar_max_value = 12000
    uint8_max_value = 255

    # Normalize the output labels to the range [0, 1]
    data_normalized = lidar_data / lidar_max_value
    data_mapped = (data_normalized * uint8_max_value).astype(np.uint8)
    return data_mapped

def postprocess_prediction(output_values):
    """
    Postprocesses the prediction output from the model.
    """
    dequantized_prediction = (output_values.astype(np.float32) / 255.0).reshape(1, -1)
    prediction_reversed = dequantized_prediction * 2
    return prediction_reversed

def run_lidar_inference(lidar_data, interpreter, shared_queue):
    """
    Runs inference on LiDAR data using the given interpreter and puts the result in shared_queue.
    """
    if len(lidar_data) == 360:
        print("Running lidar inference")
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        lidar_data_processed = preprocess_lidar_data(np.array(lidar_data))

        # Set input tensor data
        interpreter.set_tensor(input_details[0]['index'], [lidar_data_processed])

        # Run inference
        interpreter.invoke()

        # Get the output tensor
        output_values = interpreter.get_tensor(output_details[0]['index'])
        output_values = postprocess_prediction(output_values)

        shared_queue.put(output_values)
    else:
        print("LiDAR data is not of length 360.")

def update_avg_dist(dist_buffer, white_dot_threshold=2000):
    """
    Updates the average distance by averaging over the distance buffers.
    """
    num_angles = 360
    temp_avg = [white_dot_threshold] * num_angles
    num_buffers = len(dist_buffer)

    for angle in range(num_angles):
        dist_sum = sum(buffer[angle] for buffer in dist_buffer)
        temp_avg[angle] = dist_sum / num_buffers

    return temp_avg
