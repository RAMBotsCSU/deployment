import serial
from serial.serialutil import SerialException
import threading
import time
import sys
import os
import random
#from utilities import pad_str, get_line_serial, kill_program, any_greater_than_one, joystick_map_to_range, trigger_map_to_range

class SerialComm:
  # TODO: Replace print statements with logger
    def __init__(self, audio_manager, controller):
        self.audio_manager = audio_manager
        self.controller = controller
        self.STOP_FLAG = False
        self.pid = os.getpid()

        try:
            self.ser = serial.Serial('/dev/ttyACM0', 9600)
            print("Serial connection established on /dev/ttyACM0 at 9600 baud")
        except SerialException as e:
            print(f"An error occurred: {e}. Please check the connection to the Teensy.")
            self.audio_manager.play_sound("error")
            kill_program()
            sys.exit()

    def serial_read_write(self, string):
        self.ser.write(pad_str(string).encode())
        return get_line_serial(self.ser)

    def driver_thread_funct(self):
        print("Driver thread started")
        audio_manager = self.audio_manager
        controller = self.controller

        audio_manager.play_sound(random.choice(["startup1"] * 19 + ["startup2"] * 1))
        running_mode = 0
        joystick_arr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
        inferred_values = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]

        curr_odrive = ""
        odrive_params = {
            "odrive1": {"axis0": {}, "axis1": {}},
            "odrive2": {"axis0": {}, "axis1": {}},
            "odrive3": {"axis0": {}, "axis1": {}},
            "odrive4": {"axis0": {}, "axis1": {}},
            "odrive5": {"axis0": {}, "axis1": {}},
            "odrive6": {"axis0": {}, "axis1": {}}
        }

        while True:
            running_mode = controller.mode
            paused = controller.paused

            # Get controller values
            joystick_arr = [
                joystick_map_to_range(controller.l3_horizontal),    # 0 = strafe
                joystick_map_to_range(controller.l3_vertical),      # 1 = forward/backward
                trigger_map_to_range(controller.triggerL),          # 2 = roll
                joystick_map_to_range(controller.r3_horizontal),    # 3 = turn
                joystick_map_to_range(controller.r3_vertical),      # 4 = pitch
                trigger_map_to_range(controller.triggerR)           # 5 = unused
            ]

            # Adjust joystick array based on controller state
            if controller.running_ML:
                move = 0.000
                if not controller.ball_queue.empty():
                    move = controller.ball_queue.get()
                joystick_arr = [0.000, 0.000, 0.000, move, 0.000, 0.000]

            if controller.running_stop_mode and self.STOP_FLAG:
                print("Signal Stop.")
                joystick_arr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]

            if controller.running_autonomous_walk:
                if not controller.shared_queue.empty():
                    inferred_values = controller.shared_queue.get()
                joystick_arr = inferred_values

            # Remap values to range between 0 and 2 (controller outputs -1 to 1)
            joystick_arr = [value + 1.000 for value in joystick_arr]

            if any_greater_than_one(joystick_arr):
                joystick_arr[3] += controller.trim

            # Construct data string to send
            data = '''J0:{0:.3f},J1:{1:.3f},J2:{2:.3f},J3:{3:.3f},J4:{4:.3f},J5:{5:.3f},M:{6},LD:{7},RD:{8},UD:{9},DD:{10},Sq:{11},Tr:{12},Ci:{13},Xx:{14},Sh:{15},Op:{16},Ps:{17},L3:{18},R3:{19},#'''.format(
                joystick_arr[0], joystick_arr[1], joystick_arr[2], joystick_arr[3], joystick_arr[4], joystick_arr[5],
                running_mode, controller.dpadArr[0], controller.dpadArr[1],
                controller.dpadArr[2], controller.dpadArr[3], controller.shapeButtonArr[0],
                controller.shapeButtonArr[1], controller.shapeButtonArr[2], controller.shapeButtonArr[3],
                controller.miscButtonArr[0], controller.miscButtonArr[1], controller.miscButtonArr[2],
                controller.miscButtonArr[3], controller.miscButtonArr[4])

            response = self.serial_read_write(data)
            # TODO: Replace these with logger
            # Uncomment the following lines for debugging if needed
            # print(f"Sent data: {data}")
            # print(f"Received response: {response}")

            # Handle specific modes or responses as needed
            if running_mode == 6:
                line = get_line_serial(self.ser)
                print(f"Received line: {line}")
                # Handle ODrive parameters
                if "odrive" in line:
                    curr_odrive = line
                elif "END" in line:
                    controller.mode = 0
                    print("ODrive parameters received. Checking...")
                    has_no_error, error_msgs = self.check_odrive_params(odrive_params)
                    if not has_no_error:
                        for msg in error_msgs:
                            print(msg)
                        kill_program()
                        sys.exit()
                    else:
                        print("ODrive parameters are correct!")
                else:
                    # Parse ODrive parameters
                    self.parse_odrive_parameters(line, curr_odrive, odrive_params)

            time.sleep(0.1)

    def parse_odrive_parameters(self, line, curr_odrive, odrive_params):
        data_return_val_num = len(line.split(" "))
        if data_return_val_num == 2:
            key, value = line.split(" ")
            odrive_params[curr_odrive][key] = value
        elif data_return_val_num == 3:
            axis, key, value = line.split(" ")
            odrive_params[curr_odrive][axis][key] = value

    def check_odrive_params(self, input_dict):
        correct_values_axis0 = {'encoder.config.abs_spi_cs_gpio_pin': '7.00', 'encoder.config.cpr': '16384.00', 'encoder.config.mode': '257.00', 'motor.config.current_lim': '22.00', 'motor.config.current_lim_margin': '9.00', 'motor.config.pole_pairs': '20.00', 'motor.config.torque_constant': '0.03', 'controller.config.vel_gain': '0.10', 'controller.config.vel_integrator_gain': '0.08', 'controller.config.vel_limit': ''}
        correct_values_axis1 = {'encoder.config.abs_spi_cs_gpio_pin': '8.00', 'encoder.config.cpr': '16384.00', 'encoder.config.mode': '257.00', 'motor.config.current_lim': '22.00', 'motor.config.current_lim_margin': '9.00', 'motor.config.pole_pairs': '20.00', 'motor.config.torque_constant': '0.03', 'controller.config.vel_gain': '0.10', 'controller.config.vel_integrator_gain': '0.08', 'controller.config.vel_limit': ''}

        error_list = []
        for odrivename, odrivedict in input_dict.items():
            for axisname, axisdict in odrivedict.items():
                axis_correct_dict = correct_values_axis0 if axisname == "axis0" else correct_values_axis1

                output = self.value_checker(axisdict, axis_correct_dict)

                if not output[0]:
                    value_checker_dict = output[1]
                    for param, value in value_checker_dict.items():
                        error_string = f"In {odrivename}, {axisname}: {param} is {value}, should be: {axis_correct_dict[param]}"
                        error_list.append(error_string)

        return (len(error_list) == 0, error_list)

    def value_checker(self, odrive_values, correct_values):
        if not isinstance(odrive_values, dict):
            return (False, {"Error": "value_checker: nested dictionary was not passed in"})

        error_dict = {}
        for key, expected_value in correct_values.items():
            actual_value = odrive_values.get(key)
            if actual_value != expected_value:
                error_dict[key] = actual_value

        return (len(error_dict) == 0, error_dict)

