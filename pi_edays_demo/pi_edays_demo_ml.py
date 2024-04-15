#TODO:
#implement teensy_serial_main_demo [MAKE SURE TO SUBTRACT 1 FROM MOVEMENT ARR VALUES]
#add trigger lock and roll
#add bountds to mode 0=walk, 1=pushups, 2=left side right side control, 3=machine learning????, 4=gyro demo

from pyPS4Controller.controller import Controller
import serial
import threading
import time
import subprocess
import os
import pygame
from pygame import mixer
from pygame import font
import random
from serial.serialutil import SerialException
import PySimpleGUI as sg
import signal
from math import cos, sin, pi
import csv
from adafruit_rplidar import RPLidar
#from rplidar import RPLidar
import queue
from pycoral.utils import edgetpu
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import time
import sys
#FOR ML MODE
import re
import cv2
import numpy as np
import math
from pycoral.utils import edgetpu
from pycoral.utils import dataset
from pycoral.adapters import common
from pycoral.adapters import classify
import tflite_runtime.interpreter as tflite
from PIL import Image

ball_queue = queue.Queue()

shared_queue = queue.Queue() # for sharing data accross two threads
lidar_view = []

sg.theme('DarkGreen2')

table = None

# Get the process ID of the current process
pid = os.getpid()

# Slider settings
slider_min = 0
slider_max = 100
slider_default = 100
slider_step = 1

tab1_layout = [
    [
        sg.Column([[sg.T('MOVEMENT ARRAY', font=("Helvetica", 14))]]),
        sg.Column([[sg.T('                            ', font=("Helvetica", 14))]]),
        sg.Column([[sg.Text("MODE 1: WALKING", font=("Helvetica", 14), key='-MODE_TEXT-', pad=(25, 0))]])
    ],
    [
        sg.Table(
            values=[['Left Stick', 'Loading GUI'], ['Left Trigger', 'Please wait!'], ['Right Stick', ' 	⊂(◉‿◉)つ            '], ['Right Trigger', ''],['Mode', ''],
                    ['Dpad Array', ''], ['Shape Button Array', ''], ['Misc Button Array', ''], ['           ', '           ']],
            headings=['Parameter', 'Value'],
            key='-TABLE-',
            num_rows=9,
            hide_vertical_scroll=True,
            pad=(0, 0)
        ),
        #TODO: volume slider
        #sg.Column([
        #    [sg.Slider(range=(slider_min, slider_max), default_value=slider_default, orientation='h', size=(40, 20), key='-SLIDER-', resolution=slider_step, pad=(50, 0))],
        #    [sg.Text('', justification='center', size=(10, 10) , pad=(0, 0))]
        #])
    ],
    [sg.Image('./Resources/RamBOTs_Logo_Small.png')],
]

layout = [tab1_layout]

window = sg.Window('RamBOTs', layout, size=(800, 420))

STOP_FLAG = False

AUDIO_ENABLED = False
audio_dict = {"startMLSound": None, 
              "stopMLSound": None,
              "walkMode": None,
              "pushUpsMode": None,
              "legControlMode": None,
              "gyroMode": None,
              "machineLearningMode": None,
              "danceMode": None,
              "song1": None,
              "song2": None,
              "song3": None,
              "song4": None,
              "startup1": None,
              "startup2": None,
              "pause": None,
              "error": None
              }

if (AUDIO_ENABLED):

    mixer.init()
    audioFolder = 'Resources/Sounds/'
    #used sounds
    startup1 = pygame.mixer.Sound(audioFolder + 'Other/startup_1.mp3')
    startup2 = pygame.mixer.Sound(audioFolder + 'Other/startup_2.mp3')
    error = pygame.mixer.Sound(audioFolder + 'Other/error.mp3')
    pause = pygame.mixer.Sound(audioFolder + 'Other/pause.mp3')
    startMLSound = pygame.mixer.Sound(audioFolder + 'Other/starting_ML.mp3')
    stopMLSound = pygame.mixer.Sound(audioFolder + 'Other/stopping_ML.mp3')

    # sheep1 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep1.mp3')
    # sheep2 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep2.mp3')
    # sheep3 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep3.mp3')
    # sheep4 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep4.mp3')
    # sheep5 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep_sounds.mp3')

    # hi1 = pygame.mixer.Sound(audioFolder + 'Hello/hi1.mp3')
    # hi2 = pygame.mixer.Sound(audioFolder + 'Hello/hi2.mp3')
    # hi3 = pygame.mixer.Sound(audioFolder + 'Hello/hi3.mp3')

    # mergedHi1 = pygame.mixer.Sound(audioFolder + 'MergedHellos/MergedHi1.mp3')
    # mergedHi2 = pygame.mixer.Sound(audioFolder + 'MergedHellos/MergedHi2.mp3')
    # mergedHi3 = pygame.mixer.Sound(audioFolder + 'MergedHellos/MergedHi3.mp3')

    walkMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/walking.mp3')
    pushUpsMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/push_ups.mp3')
    legControlMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/leg_control.mp3')
    gyroMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/gyro.mp3')
    machineLearningMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/machine_learning.mp3')
    danceMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/dance_mode.mp3')

    song1 = pygame.mixer.Sound(audioFolder + 'Songs/mayahe.mp3')
    song2 = pygame.mixer.Sound(audioFolder + 'Songs/WhoLetTheDogsOut.mp3')
    song3 = pygame.mixer.Sound(audioFolder + 'Songs/Crazy_La_Paint.mp3')
    song4 = pygame.mixer.Sound(audioFolder + 'Songs/Party_Rock.mp3')



    #set volumes
    startup1.set_volume(0.2)
    startup2.set_volume(0.125)
    pause.set_volume(0.4)
    error.set_volume(0.25)
    startMLSound.set_volume(0.4)
    stopMLSound.set_volume(0.4)

    # sheep1.set_volume(0.8)
    # sheep2.set_volume(0.8)
    # sheep3.set_volume(0.8)
    # sheep4.set_volume(0.8)
    # sheep5.set_volume(0.5)

    # hi1.set_volume(0.5)
    # hi2.set_volume(0.5)
    # hi3.set_volume(0.5)

    # mergedHi1.set_volume(0.9)
    # mergedHi2.set_volume(0.9)
    # mergedHi3.set_volume(0.9)

    walkMode.set_volume(0.5)
    pushUpsMode.set_volume(0.5)
    legControlMode.set_volume(0.5)
    gyroMode.set_volume(0.5)
    machineLearningMode.set_volume(0.5)
    danceMode.set_volume(0.45)

    song1.set_volume(0.25) #mayahe
    song2.set_volume(0.2) #Who let the dogs out
    song3.set_volume(0.2) #crazy la pint
    song4.set_volume(0.25) #party rock

    audio_dict = {
                    "startMLSound": startMLSound, 
                    "stopMLSound": stopMLSound,
                    "walkMode": walkMode,
                    "pushUpsMode": pushUpsMode,
                    "legControlMode": legControlMode,
                    "gyroMode": gyroMode,
                    "machineLearningMode": machineLearningMode,
                    "danceMode": danceMode,
                    "song1": song1,
                    "song2": song2,
                    "song3": song3,
                    "song4": song4,
                    "startup1": startup1,
                    "startup2": startup2,
                    "pause": pause,
                    "error": error
                    }


    #sound libraries
    # sheep_sounds = [sheep1,sheep2,sheep3,sheep4,sheep5]
    # hi_sounds = [hi1,hi2,hi3]
    # merged_sounds = [mergedHi1, mergedHi2, mergedHi3]
    # mode_sounds = [walkMode,walkAlternate,pushUpsMode,pushUpsAlternate,legControlMode,legControlAlternate,gyroMode,gyroAlternate,machineLearningMode,machineLearningAlternate]
    # songs = [song1,song2,song3,song4]


def kill_program():
    # Send SIGTERM signal
    os.kill(pid, signal.SIGTERM)

    # Or send SIGINT signal (equivalent to pressing Ctrl+C)
    os.kill(pid, signal.SIGINT) 


def playSound(soundStr):
    if (AUDIO_ENABLED):
        pygame.mixer.Sound.play(audio_dict[soundStr])

def gui_handler(controller,window): # manage the GUI

    print("hello from gui")
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:           # way out of UI
            print("brealong")
            break

def update_table_cell(table, row, col, value):
    table.Widget.set(table.Widget.get_children()[row], "#" + str(col + 1), value)

def gui_table_handler(controller): # update the GUI table with controller inputs every x seconds
    print("hello from gui handler")
    global table

    while True:

        if (controller.paused):
            update_table_cell(table, 8, 1, "Sh:0,Op:0,Ps:1,L3:0,R3:0")
        else:
            table = window['-TABLE-']
            update_table_cell(table, 0, 1, f"{controller.l3_horizontal / 32767:5.2f}, {controller.l3_vertical / 32767:5.2f}")
            update_table_cell(table, 1, 1, f"{controller.triggerL / 65198:5.2f}")
            update_table_cell(table, 2, 1, f"{controller.r3_horizontal / 32767:5.2f}, {controller.r3_vertical / 32767:5.2f}")
            update_table_cell(table, 3, 1, f"{controller.triggerR / 65198:5.2f}")
            update_table_cell(table, 4, 1, f"{controller.mode}")
            update_table_cell(table, 5, 1, f"←:{controller.dpadArr[0]}  →:{controller.dpadArr[1]}  ↑:{controller.dpadArr[2]}  ↓:{controller.dpadArr[3]}")
            update_table_cell(table, 6, 1, f"□:{controller.shapeButtonArr[0]}  △:{controller.shapeButtonArr[1]}  ○:{controller.shapeButtonArr[2]}  X:{controller.shapeButtonArr[3]}")
            update_table_cell(table, 7, 1, f"Sh:{controller.miscButtonArr[0]},Op:{controller.miscButtonArr[1]},Ps:{controller.miscButtonArr[2]},L3:{controller.miscButtonArr[3]},R3:{controller.miscButtonArr[4]}")
            update_table_cell(table, 8, 1, f"Trim: {controller.trim}")
        time.sleep(0.1)

def postprocess_prediction(output_values):
    dequantized_prediction = (output_values.astype(np.float32) / 255.0).reshape(1, -1)
    prediction_reversed = dequantized_prediction * 2
    return prediction_reversed

def preprocess_lidar_data(lidar_data):
    lidar_max_value = 12000
    uint8_max_value = 255

    # Normalize the output labels to the range [0, 1]
    data_normalized = lidar_data / lidar_max_value
    data_mapped = (data_normalized * uint8_max_value).astype(np.uint8)
    return data_mapped

def runLidarInference(lidar_data, interpreter):
    if len(lidar_data) == 360:
        print("Running lidar inference")
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        lidar_data = np.array(lidar_data)
        
        lidar_data_processed = preprocess_lidar_data(lidar_data)

        # Set input tensor data
        input_tensor = interpreter.tensor(input_details[0]['index'])
        input_tensor()[0] = lidar_data_processed

        # Run inference
        interpreter.invoke()

        # Get the output tensor
        output_tensor = interpreter.tensor(output_details[0]['index'])

        # Get the output values as a NumPy array
        output_values = np.array(output_tensor())
        output_values = postprocess_prediction(output_values)

        shared_queue.put(output_values)
    else:
        print("lidar view data incorrect")


def playModeSounds(mode):
    # stopSounds()
    if mode == 0:
        playSound("walkMode")
        window['-MODE_TEXT-'].update("MODE 1: WALK")
    elif mode == 1:
        playSound("pushUpsMode")
        window['-MODE_TEXT-'].update("MODE 2: PUSH-UPS")
    elif mode == 2:
        playSound("legControlMode")
        window['-MODE_TEXT-'].update("MODE 3: LEG CONTROL")
    elif mode == 3:
        playSound("gyroMode")
        window['-MODE_TEXT-'].update("MODE 4: GYRO CONTROL")
    elif mode == 4:
        playSound("machineLearningMode")
        window['-MODE_TEXT-'].update("MODE 5: MACHINE LEARNING")
    elif mode == 5:
        playSound("danceMode")
        window['-MODE_TEXT-'].update("MODE 6: DANCE")
        playSongs(-1)


def stopSounds():
    for sound in mode_sounds:
        sound.stop()
    for sound in songs:
        sound.stop()

def playSongs(song):
    # for sound in songs:
    #     sound.stop()
    if(song == -1):
        playSound(random.choice(["song1", "song2", "song3", "song4"]))
    elif(song == 1):
        playSound("song1")
    elif(song == 2):
        playSound("song2")
    elif(song == 3):
        playSound("song3")
    elif(song == 4):
        playSound("song4")

def rgb(m):
    bashCommand, filename = os.path.split(os.path.abspath(__file__))
    bashCommand = "sudo bash " + bashCommand + "/controllerColor.sh "
    if m == 0:
        bashCommand = bashCommand + "255 255 255"
    elif m == 1:
        bashCommand = bashCommand + "255 255 0"
    elif m == 2:
        bashCommand = bashCommand + "255 111 0"
    elif m == 3:
        bashCommand = bashCommand + "8 208 96"
    elif m == 4:
        bashCommand = bashCommand + "255 0 255"
    elif m == 5:
        bashCommand = bashCommand + "0 255 0"
    elif m == -1:
        bashCommand = bashCommand + "255 0 0"
    else:
        bashCommand = bashCommand + "255 0 0"
    subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

def joystick_map_to_range(original_value):
    mapped_value = ((original_value + 32767) / 65535) * 2 - 1
    return mapped_value

#Function to map a range of [-65534,65198] to [-1,1] with 0 in the middle
def trigger_map_to_range(value):
    if(value < 0):
        return (value/65534)
    elif(value > 0):
        return (value/65198)
    else:
        return 0

#Function to map a range of [-65534,65198] to [-1,1] with 0 in the middle
def joey_trigger_map_to_range(value):
    newValue = (value+168)/65366
    return newValue

def value_checker(odrive_values, correct_values):
    #checks the values against the correct values

    if (type(odrive_values) is not dict):
        return (False, {"Error": "value_checker: nested dictionary was not passed in"})

    error_dict = {}

    if (odrive_values == correct_values):
        return (True, {})
    
    
    for key, expected_value in correct_values.items():
        actual_value = odrive_values[key]

        if (actual_value != expected_value):
            error_dict[key] = actual_value

    return (len(error_dict) == 0, error_dict)
        
def check_odrive_params(input_dict):
    correct_values_axis0 = {'encoder.config.abs_spi_cs_gpio_pin': '7.00', 'encoder.config.cpr': '16384.00', 'encoder.config.mode': '257.00', 'motor.config.current_lim': '22.00', 'motor.config.current_lim_margin': '9.00', 'motor.config.pole_pairs': '20.00', 'motor.config.torque_constant': '0.03', 'controller.config.vel_gain': '0.10', 'controller.config.vel_integrator_gain': '0.08', 'controller.config.vel_limit': ''}
    correct_values_axis1 = {'encoder.config.abs_spi_cs_gpio_pin': '8.00', 'encoder.config.cpr': '16384.00', 'encoder.config.mode': '257.00', 'motor.config.current_lim': '22.00', 'motor.config.current_lim_margin': '9.00', 'motor.config.pole_pairs': '20.00', 'motor.config.torque_constant': '0.03', 'controller.config.vel_gain': '0.10', 'controller.config.vel_integrator_gain': '0.08', 'controller.config.vel_limit': ''}

    error_list = []
    for odrivename, odrivedict in input_dict.items():
        for axisname, axisdict in odrivedict.items():
            if axisname == "axis0":
                axis_correct_dict = correct_values_axis0
            else:
                axis_correct_dict = correct_values_axis1
            
            output = value_checker(axisdict, axis_correct_dict)

            if output[0] is False:
                value_checker_dict = output[1]

                for param, value in value_checker_dict.items():
                    error_string = "In " + odrivename + ", " + axisname + ": "
                    error_string += param + " is " + value + ", should be: " + axis_correct_dict[param]
                    error_list.append(error_string)
    
    return (len(error_list) == 0, error_list)

def padStr(val):
    for _ in range (120-len(val)):
        val = val + "~"
    return val

#Function to remove all ~ padding
def rmPadStr(val):
    outputStr = ""
    for curChar in val:
        if curChar != '~':
            outputStr += curChar
    return outputStr

def serial_read_write(string, ser): # use time library to call every 10 ms in separate thread
    ser.write(padStr(string).encode())
    return getLineSerial(ser)

def getLineSerial(ser):
    line = str(ser.readline())
    line = line[2:-5]
    line = rmPadStr(line)
    return line

def any_greater_than_one(arr):
    for value in arr:
        if value > 1.1 or value < 0.9:
            return True
    return False

def driver_thread_funct(controller):
    global STOP_FLAG
    playSound(random.choice(["startup1"]*19 + ["startup2"]*1)) # dont mind this line
    runningMode = 0
    joystickArr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
    rgb(0)
    gui_update_counter = 0
    inferred_values = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000] # gets updated by machine learning inference
    
    curr_odrive = ""
    odrive_params = {"odrive1": {"axis0":{}, "axis1": {}},
                     "odrive2": {"axis0":{}, "axis1": {}},
                     "odrive3": {"axis0":{}, "axis1": {}},
                     "odrive4": {"axis0":{}, "axis1": {}},
                     "odrive5": {"axis0":{}, "axis1": {}},
                     "odrive6": {"axis0":{}, "axis1": {}}}
    hasCheckedOdrives = False

    #running section
    while True:

        runningMode = controller.mode
        paused = controller.paused
        # get controller values
        joystickArr = [joystick_map_to_range(controller.l3_horizontal),    # 0 = strafe, leftStick/L3 Left-Right
                       joystick_map_to_range(controller.l3_vertical),      # 1 = forback, leftStick/L3 Up-Down
                       joystick_map_to_range(controller.triggerL),         # 2 = roll, triggerL/L2
                       joystick_map_to_range(controller.r3_horizontal),    # 3 = turn, rightStick/R3 Left-Right
                       joystick_map_to_range(controller.r3_vertical),      # 4 = pitch, rightStick/R3 Up-Down
                       joystick_map_to_range(controller.triggerR)]         # 5 = does nothing, triggerR/R2
        # Note : the joystickArr[4]/pitch is not used in walk mode

        if controller.running_ML:
            # with global_float_lock:
            #     value = global_float
            if not ball_queue.empty():
                move = ball_queue.get()
            print("Move Value:", move)
            joystickArr = [0, 0, 0, move, 0, 0]
            print("Joytick Array [3] value:", joystickArr)

        if controller.running_stop_mode and STOP_FLAG:
            print("Signal Stop.")
            joystickArr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]

        if controller.running_autonomous_walk:
            if not shared_queue.empty():
                inferred_values = shared_queue.get() # update inferred values from lidar thread
            joystickArr = inferred_values # set joystickArr equal regardless of updating inferred_values
            # Note: inferred values gets updated slower than data is output to teensy

        # print("Joystick values:", joystickArr)

        # remap values to range between 0 and 2 (controller outputs -1 to 1)
        for x in range(len(joystickArr)):
            joystickArr[x] += 1.000

        if (any_greater_than_one(joystickArr)):
            joystickArr[3] += controller.trim
        
        # Send data to the connected USB serial device
        data = '''J0:{0:.3f},J1:{1:.3f},J2:{2:.3f},J3:{3:.3f},J4:{4:.3f},J5:{5:.3f},M:{6},LD:{7},RD:{8},UD:{9},DD:{10},Sq:{11},Tr:{12},Ci:{13},Xx:{14},Sh:{15},Op:{16},Ps:{17},L3:{18},R3:{19},#'''.format(joystickArr[0], joystickArr[1], joystickArr[2], joystickArr[3], joystickArr[4], joystickArr[5],
        runningMode, controller.dpadArr[0], controller.dpadArr[1],
        controller.dpadArr[2], controller.dpadArr[3], controller.shapeButtonArr[0],
        controller.shapeButtonArr[1], controller.shapeButtonArr[2], controller.shapeButtonArr[3],
        controller.miscButtonArr[0], controller.miscButtonArr[1], controller.miscButtonArr[2],
        controller.miscButtonArr[3], controller.miscButtonArr[4])

        response = serial_read_write(data, ser)
        # print("Output:", response)

        if (runningMode == 6):
            line = getLineSerial(ser)
            print(line)
            if ("odrive" in line):
                # Header print statement indicating which odrive is being dumped
                curr_odrive = line

                while True:
                    line = getLineSerial(ser)

                    print(line)
                    if ("END" in line):
                        # runningMode = 0
                        controller.mode = 0
                        print("Params:",odrive_params)
                        hasNoError, errorMsgs = check_odrive_params(odrive_params)
                        if (not hasNoError):
                            for msg in errorMsgs:
                                print(msg)
                            kill_program()
                            sys.exit()
                            
                        else:
                            print("Odrive params all good!")

                        break

                    elif ("odrive" in line):
                        # Header print statement indicating which odrive is being dumped
                        curr_odrive = line

                    else:
                        data_return_val_num = len(line.split(" "))
                        if data_return_val_num == 2:
                            key = line.split(" ")[0]
                            value = line.split(" ")[1]
                            odrive_params[curr_odrive][key] = value
                        elif data_return_val_num == 3:
                            axis = line.split(" ")[0]
                            key = line.split(" ")[1]
                            value = line.split(" ")[2]
                            odrive_params[curr_odrive][axis][key] = value



       # time.sleep(0.01)
        #update_gui_table_controller(controller)

def ball_thread_funct(controller):
    # global TURN_FACTOR
    #Create Variables
    model_path = '../../machine_learning/tennisBall/BallTrackingModelQuant_edgetpu.tflite'
    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
    INPUT_WIDTH_AND_HEIGHT = 224

    # Functions
    def process_image(interpreter, image, input_index):
        input_data = (np.array(image)).astype(np.uint8)
        input_data = input_data.reshape((1, 224, 224, 3))

        # Process
        interpreter.set_tensor(input_index, input_data)
        interpreter.invoke()

        # Get outputs
        output_details = interpreter.get_output_details()
    
        process_image.prevAreaPos = getattr(process_image, "prevAreaPos", 0)

        positions = (interpreter.get_tensor(output_details[0]['index']))
        conf = (interpreter.get_tensor(output_details[1]['index'])/255)
        result = []

        for idx, score in enumerate(conf):
            pos = positions[0]
            areaPos = area(pos)
            if score > 0.99 and  (350 <= areaPos < 50176) and process_image.prevAreaPos > 400:
                result.append({'pos': positions[idx]})
            process_image.prevAreaPos = areaPos  # Update prevAreaPos for the next iteration

        return result


    def distance(point1, point2):
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

    def area(pos):
        side_length = distance((pos[0], pos[1]), (pos[2], pos[3]))
        return side_length ** 2

    def display_result(result, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        size = 0.6
        color = (255, 255, 0)  # Blue color
        thickness = 2

        for obj in result:
            pos = obj['pos']
            scale_x = CAMERA_WIDTH / INPUT_WIDTH_AND_HEIGHT
            scale_y = CAMERA_HEIGHT / INPUT_WIDTH_AND_HEIGHT
            x1 = int(pos[0] * scale_x)
            y1 = int(pos[1] * scale_y)
            x2 = int(pos[2] * scale_x)
            y2 = int(pos[3] * scale_y)

            cv2.putText(frame, 'Tennis Ball', (x1, y1), font, size, color, thickness)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            center = bboxCenterPoint(x1, y1, x2, y2)
            calculate_direction(center[0])
        
        cv2.imshow('Tracking!', frame)
        #shared_queue.put(frame)

    def bboxCenterPoint(x1, y1, x2, y2):
        bbox_center_x = int((x1 + x2) / 2)
        bbox_center_y = int((y1 + y2) / 2)

        return [bbox_center_x, bbox_center_y]

    def calculate_direction(X, frame_width=CAMERA_WIDTH):
        increment = frame_width / 3
        if ((2*increment) <= X <= frame_width):
            ball_queue.put(1)
            time.sleep(5)
        elif (0 <= X < increment):
            ball_queue.put(-1)
            time.sleep(5)
        elif (increment <= X < (2*increment)):
            ball_queue.put(0)
            time.sleep(5)

    # Set up Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("Set up Camera")

    # Set up Interpreter
    interpreter = edgetpu.make_interpreter(model_path, device = 'usb')
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()

    # Get Width and Height
    input_shape = input_details[0]['shape']
    height = input_shape[1]
    width = input_shape[2]

    input_index = input_details[0]['index']
    
    print("Set up Interpreter!")

    while True:

        ret, frame = cap.read()
        
        if not ret:
            print('Capture failed')
            break
        
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image = image.resize((width, height))

        top_result = process_image(interpreter, image, input_index)

        display_result(top_result, frame)
        
    cap.release()
    cv2.destroyAllWindows()

def lidar_thread_funct(controller):
    global lidar_view
    global STOP_FLAG
    # Set up pygame and the display
    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    map_width = 400 # printed map size
    lcd = pygame.display.set_mode((map_width, map_width))
    lcd.fill((0,0,0))
    pygame.display.update()


    #Create variables
    model_path = '../../machine_learning/lidar_model_quantized_edgetpu.tflite'
    interpreter = edgetpu.make_interpreter(model_path, device='usb')
    interpreter.allocate_tensors()

    # CSV file name
    output_file = 'lidar_data.csv'

    # Define Parameters
    red_dot_threshold = 400 # 500=.5m (?); threshhold for detecting close object
    white_dot_threshold = 4000 # furthest distance factored into calculations

    print("Lidar setup initialized.\nInitial Collection Range = ", white_dot_threshold/1000,
           " m\nStop proximity: ", red_dot_threshold/1000, " m")

    # Scale parameters to map
    scale_data = int(white_dot_threshold/map_width)

    def setup_lidar_connection():
        # Setup the RPLidar
        PORT_NAME = '/dev/ttyUSB0'

        while True:
            try:
                # lidar = RPLidar(None, PORT_NAME, timeout=3, baudrate=256000)
                # print("Lidar connected", lidar.info)
                # lidar.clear_input()
                lidar = RPLidar(PORT_NAME)

                info = lidar.get_info()
                print(info)

                health = lidar.get_health()
                print(health)
                break
            except Exception as e:
                print(e)
                print("Error connecting to lidar. Trying again")
                time.sleep(1)
        return lidar
  
    def update_lidar_map(data):
        lcd.fill((0,0,0))
        # Initialize a list to store Lidar data
        for angle in range(360):
            distance = float(data[angle])
            if distance > 0:                  # ignore initially ungathered data points
                radians = angle * pi / 180.0
                x = distance * cos(radians)
                y = distance * sin(radians)
                point = (int(int(x)/scale_data + map_width/2), int(int(y)/scale_data + map_width/2))
                if distance <= red_dot_threshold:
                    lcd.set_at(point, pygame.Color(255, 0, 0))
                elif distance <= white_dot_threshold:
                    lcd.set_at(point, pygame.Color(255, 255, 255))
        pygame.draw.line(lcd, pygame.Color(255,255,255), (0, map_width/2), (map_width, map_width/2), 1)
        pygame.draw.line(lcd, pygame.Color(255,255,255), (map_width/2, 0), (map_width/2, map_width), 1)
        for i in range(-white_dot_threshold + int(white_dot_threshold%500), white_dot_threshold, 500): # tick every .5 meters
            if i == 0 or i == -white_dot_threshold:
                continue
            tick_placement = int(i/(scale_data*2))+int(map_width/2)
            pygame.draw.line(lcd, pygame.Color(255, 255, 255), (tick_placement, (map_width/2)+2), (tick_placement, (map_width/2)-2), 1) # x-ticks
            pygame.draw.line(lcd, pygame.Color(255, 255, 255), ((map_width/2)+2, tick_placement), ((map_width/2)-2, tick_placement), 1) # y-ticks
            label = str(i/1000)
            font = pygame.font.SysFont("Helvetica", 12)
            text = font.render(label, True, (255, 255, 255))
            lcd.blit(text, (int(map_width/2 + 5), tick_placement - 5)) # x-axis
            lcd.blit(text, (tick_placement - 5, int(map_width/2 + 5))) # y-axis
        pygame.display.update()
    
    scan_data = [white_dot_threshold] * 360
    lidar_data = []
    start_time = 0
    joystickArr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]

    # define parameters for stop mode
    starttime = time.time()
    window = 10
    # dist = [white_dot_threshold]*360 # stores lidar distances
    avg_dist = [white_dot_threshold]*(int(360/5)) # stores moving averages
    dist_buffer = [[]*360]

    # avg_dist is updated to the average data set of all data sets in dist_buffer
    def update_avg_dist(dist_buffer):
        temp_avg = [white_dot_threshold]*360
        for angle_step in range(0, 360, 5):                            # 360 angle values
            dist_sum = 0                                    # temp hold distance sum of each angle
            for i in range(5):
                for arr in dist_buffer:                     # check same angle of each data set
                    dist_sum += arr[angle_step + i]                  # sum all distances at one angle
            temp_avg[angle_step] = dist_sum / (len(dist_buffer)*5) # average distance by size of dist_buffer
        return temp_avg
    
    while(True):
        lidar = setup_lidar_connection()
        try:
            for scan in lidar.iter_scans():
                for (_, angle, distance) in scan:
                    scan_data[min([359, int(angle)])] = distance 
                update_lidar_map(scan_data)

                if controller.running_stop_mode:

                    if (time.time() - starttime) > 0.25: # every .25s
                        starttime = time.time() # restart timer
                        dist_buffer.append(scan_data) # add new data set to dist_buffer
                        if len(dist_buffer) > window: # more data sets than window parameter
                            dist_buffer.pop(0) # remove oldest data set
                            avg_dist = update_avg_dist(dist_buffer) # get average of all data sets
                            if min(avg_dist) <= red_dot_threshold: # any distance within stop proximity?
                                STOP_FLAG = True
                                print("Stop Proximity.")
                            else:
                                STOP_FLAG = False

            if controller.running_autonomous_walk:

                if time.time() - start_time > .2:
                    start_time = time.time()
                    lidar_view = scan_data
                    runLidarInference(scan_data, interpreter)

                    joystickArr[0] = joystick_map_to_range(controller.l3_horizontal)+1
                    joystickArr[1] = joystick_map_to_range(controller.l3_vertical)+1
                    joystickArr[2] = trigger_map_to_range(controller.triggerL)+1
                    joystickArr[3] = joystick_map_to_range(controller.r3_horizontal)+1
                    joystickArr[4] = joystick_map_to_range(controller.r3_vertical)+1
                    joystickArr[5] = trigger_map_to_range(controller.triggerR)+1

                    lidar_data.append(scan_data + joystickArr)

            elif len(lidar_data) > 0:
                with open(output_file, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerows(lidar_data)
                print(f'Lidar data saved to {output_file}')
                lidar_data = []

        except Exception as e:
            print(e)
            time.sleep(1)
            lidar.stop()
            lidar.disconnect()
            print("Lidar disconnected.")


class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.l3_horizontal = 0
        self.l3_vertical = 0
        self.r3_horizontal = 0
        self.r3_vertical = 0
        self.triggerL = 0
        self.triggerR = 0
        self.modeMax = 5
        self.mode = 0
        self.dpadArr = [0,0,0,0] #L,R,U,D
        self.shapeButtonArr = [0,0,0,0] #Sq, Tr, Cir, X
        self.miscButtonArr = [0,0,0,0,0] #Share, Options, PS, L3, R3
        self.paused = False
        self.pauseChangeFlag = True
        self.deadzone = 32767/10
        self.running_ML = False
        self.running_autonomous_walk = False
        self.running_stop_mode = False
        self.trim = 0.0

    def on_L3_up(self, value):
        if (abs(value) > self.deadzone):
            self.l3_vertical = -value
        else:
            self.l3_vertical = 0

    def on_L3_down(self, value):
        if (abs(value) > self.deadzone):
            self.l3_vertical = -value
        else:
            self.l3_vertical = 0

    def on_L3_left(self, value):
        if (abs(value) > self.deadzone):
            self.l3_horizontal = value
        else:
            self.l3_horizontal = 0

    def on_L3_right(self, value):
        if (abs(value) > self.deadzone):
            self.l3_horizontal = value
        else:
            self.l3_horizontal = 0

    def on_L3_x_at_rest(self):
        self.l3_horizontal = 0

    def on_L3_y_at_rest(self):
        self.l3_vertical = 0

    def on_R3_up(self, value):
        if (abs(value) > self.deadzone):
            self.r3_vertical = -value
        else:
            self.r3_vertical = 0

    def on_R3_down(self, value):
        if (abs(value) > self.deadzone):
            self.r3_vertical = -value
        else:
            self.r3_vertical = 0

    def on_R3_left(self, value):
        if (abs(value) > self.deadzone):
            self.r3_horizontal = -value
        else:
            self.r3_horizontal = 0

    def on_R3_right(self, value):
        if (abs(value) > self.deadzone):
            self.r3_horizontal = -value
        else:
            self.r3_horizontal = 0

    def on_R3_x_at_rest(self):
        self.r3_horizontal = 0

    def on_R3_y_at_rest(self):
        self.r3_vertical = 0

    def on_L1_press(self):
        if(not self.paused):
            if self.mode <= 0:
                self.mode = self.modeMax
            else:
                self.mode = self.mode-1
            rgb(self.mode)
            playModeSounds(self.mode)



    def on_L1_release(self):
        pass

    def on_R1_press(self):
        if(not self.paused):
            if self.mode >= self.modeMax:
                self.mode = 0
            else:
                self.mode = self.mode+1
            rgb(self.mode)
            playModeSounds(self.mode)


    def on_R1_release(self):
        pass

    def on_square_press(self):
        self.shapeButtonArr[0] = 1
        if(self.mode == 5):
            playSongs(1)

    def on_square_release(self):
        self.shapeButtonArr[0] = 0

    def on_triangle_press(self):
        self.shapeButtonArr[1] = 1 # triangle button is pressed
        if (self.mode == 0 and not self.running_autonomous_walk): 
            self.running_autonomous_walk = True # if autonomous walk is not running, start autonomous walk
            print("Started Autonomous Walk") 
        elif self.mode == 0 and self.running_autonomous_walk:
            self.running_autonomous_walk = False # if autonomous walk is running, stop autonomous walk
            print("Stopped Autonomous Walk")
        if (self.mode == 4 and not self.running_ML):
            self.running_ML = True
            print("Value of running_ML should be True, ", self.running_ML)
        elif self.mode == 4 and self.running_ML:
            self.running_ML = False
        elif(self.mode == 5):
            playSongs(2)

    def on_triangle_release(self):
        self.shapeButtonArr[1] = 0

    def on_circle_press(self):
        self.shapeButtonArr[2] = 1 # circle button pressed down
        if(not self.running_stop_mode):
            self.running_stop_mode = True # if stop mode is not running, start stop mode
            print("Started Stop Mode")
        elif(self.running_stop_mode):
            self.running_stop_mode = False # if stop mode is running, stop 'stop mode'
            print("Stop Stop Mode")
        if(self.mode == 5):
            playSongs(3)

    def on_circle_release(self):
        self.shapeButtonArr[2] = 0 # circle button released

    def on_x_press(self):
        self.shapeButtonArr[3] = 1
        if(self.mode == 5):
            playSongs(4)

    def on_x_release(self):
        self.shapeButtonArr[3] = 0

    def on_up_arrow_press(self):
        self.dpadArr[2] = 1

    def on_up_down_arrow_release(self):
        self.dpadArr[2] = 0
        self.dpadArr[3] = 0

    def on_down_arrow_press(self):
        self.dpadArr[3] = 1

    def on_left_arrow_press(self):
        self.dpadArr[0] = 1
        if(self.mode == 0 and self.trim > -1):
            self.trim = round(self.trim - 0.01, 2)

    def on_left_right_arrow_release(self):
        self.dpadArr[0] = 0
        self.dpadArr[1] = 0

    def on_right_arrow_press(self):
        self.dpadArr[1] = 1
        if(self.mode == 0 and self.trim < 1):
            self.trim = round(self.trim + 0.01, 2)
            

    def on_L3_press(self):
        self.miscButtonArr[3] = 1
        #playSound(random.choice(merged_sounds))
        #playSound(random.choice(hi_sounds))
        #playSound(random.choice(sheep_sounds))        
    
    def on_L3_release(self):
        self.miscButtonArr[3] = 0

    def on_R3_press(self):
        # stopSounds()
        self.miscButtonArr[4] = 1

    def on_R3_release(self):
        self.miscButtonArr[4] = 0

    def on_options_press(self):
        self.miscButtonArr[1] = 1
        # playSound(random.choice(merged_sounds))
        
    def on_options_release(self):
        self.miscButtonArr[1] = 0

    def on_share_press(self):
        self.miscButtonArr[0] = 1

    def on_share_release(self):
        self.miscButtonArr[0] = 0

    def on_playstation_button_press(self):
        self.miscButtonArr[2] = 1

        if (self.pauseChangeFlag):
            # true change flag means we can update the paused mode again
            # swap the pause flag
            self.paused = not self.paused # false flag means the program is paused
            self.pauseChangeFlag = False
        if(self.paused):
            rgb(-1)
        else:
            rgb(self.mode)
        playSound("pause")

    def on_playstation_button_release(self):
        self.miscButtonArr[2] = 0
        if (not self.pauseChangeFlag):
            self.pauseChangeFlag = True # true flag means program is not paused

    def on_R2_press(self,value):
        self.triggerR = value + 32431

    def on_R2_release(self):
        self.triggerR = 0

    def on_L2_press(self,value):
        self.triggerL = value + 32431

    def on_L2_release(self):
        self.triggerL = 0



print("hello world")

try:
    ser = serial.Serial('/dev/ttyACM0',9600)
except SerialException as e:
    print(f"An error occured: {e}. \nPlease unplug the USB to the Teensy, press stop, and plug it in again.")
    #play sound here
    playSound("error")

    while(1):
        pass


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

pi_gui_thread = threading.Thread(target=gui_handler, args=(controller,window))
pi_gui_thread.daemon = True
pi_gui_thread.start()

time.sleep(3) # give GUI time to wake up

pi_gui_table_thread = threading.Thread(target=gui_table_handler, args=(controller,))
pi_gui_table_thread.daemon = True
pi_gui_table_thread.start()

driver_thread = threading.Thread(target=driver_thread_funct, args=(controller,))
driver_thread.daemon = True
driver_thread.start()

ball_thread = threading.Thread(target=ball_thread_funct, args=(controller,))
ball_thread.daemon = True
ball_thread.start()

#lidar_thread = threading.Thread(target=lidar_thread_funct, args=(controller,))
#lidar_thread.daemon = True
#lidar_thread.start()

controller.listen()
