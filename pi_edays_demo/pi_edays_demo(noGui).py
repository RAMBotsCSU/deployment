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
import random
from serial.serialutil import SerialException
import PySimpleGUI as sg
import re

sg.theme('DarkGreen2')

table = None
   


mixer.init()
audioFolder = 'Resources/Sounds/'
#used sounds
startup1 = pygame.mixer.Sound(audioFolder + 'startup_1.mp3')
startup2 = pygame.mixer.Sound(audioFolder + 'startup_2.mp3')
error = pygame.mixer.Sound(audioFolder + 'error.mp3')
sheep1 = pygame.mixer.Sound(audioFolder + 'sheep1.mp3')
sheep2 = pygame.mixer.Sound(audioFolder + 'sheep2.mp3')
sheep3 = pygame.mixer.Sound(audioFolder + 'sheep3.mp3')
sheep4 = pygame.mixer.Sound(audioFolder + 'sheep4.mp3')
sheep5 = pygame.mixer.Sound(audioFolder + 'sheep_sounds.mp3')

walkMode = pygame.mixer.Sound(audioFolder + 'walking.mp3')
walkAlternate = pygame.mixer.Sound(audioFolder + 'walking_here.mp3')
pushUpsMode = pygame.mixer.Sound(audioFolder + 'push_ups.mp3')
pushUpsAlternate = pygame.mixer.Sound(audioFolder + 'push_ups_gains.mp3')
legControlMode = pygame.mixer.Sound(audioFolder + 'leg_control.mp3')
legControlAlternate = pygame.mixer.Sound(audioFolder + 'leg_control_brrr.mp3')
gyroMode = pygame.mixer.Sound(audioFolder + 'gyro.mp3')
gyroAlternate = pygame.mixer.Sound(audioFolder + 'gyro_alternate.mp3')
machineLearningMode = pygame.mixer.Sound(audioFolder + 'machine_learning.mp3')
machineLearningAlternate = pygame.mixer.Sound(audioFolder + 'machine_learning_robot.mp3')
pause = pygame.mixer.Sound(audioFolder + 'pause.mp3')

#set volumes
startup1.set_volume(0.2)
startup2.set_volume(0.15)
error.set_volume(0.25)
sheep1.set_volume(0.6)
sheep2.set_volume(0.6)
sheep3.set_volume(0.6)
sheep4.set_volume(0.6)
sheep5.set_volume(0.5)

walkMode.set_volume(0.5)
walkAlternate.set_volume(0.5)
pushUpsMode.set_volume(0.5)
pushUpsAlternate.set_volume(0.5)
legControlMode.set_volume(0.5)
legControlAlternate.set_volume(0.5)
gyroMode.set_volume(0.5)
gyroAlternate.set_volume(0.5)
machineLearningMode.set_volume(0.5)
machineLearningAlternate.set_volume(0.5)
pause.set_volume(0.5)

#sound libraries
sheep_sounds = [sheep1,sheep2,sheep3,sheep4,sheep5]
mode_sounds = [walkMode,walkAlternate,pushUpsMode,pushUpsAlternate,legControlMode,legControlAlternate,gyroMode,gyroAlternate,machineLearningMode,machineLearningAlternate]

process = None

def startML():
    global process
    print("starting machine learning!")
    process = subprocess.Popen(['python3', 'machine_learning/Object_Detection.py','--geometry', '800x600+100+100'])


def killML():
    global process
    if process:
        print("killing machine learning.")
        process.terminate()
        process.wait()


def playModeSounds(mode):
    stopModeSounds()
    if mode == 0:
        pygame.mixer.Sound.play(random.choice([walkMode]*19 + [walkAlternate]*1))
    elif mode == 1:
        pygame.mixer.Sound.play(random.choice([pushUpsMode]*19 + [pushUpsAlternate]*1))
    elif mode == 2:
        pygame.mixer.Sound.play(random.choice([legControlMode]*19 + [legControlAlternate]*1))
    elif mode == 3:
        pygame.mixer.Sound.play(random.choice([gyroMode]*19 + [gyroAlternate]*1))
    elif mode == 4:
        pygame.mixer.Sound.play(random.choice([machineLearningMode]*19 + [machineLearningAlternate]*1))
        

def stopModeSounds():
    for sound in mode_sounds:
        sound.stop()
    
    
def rgb(m):
#    print("hampter")
    bashCommand, filename = os.path.split(os.path.abspath(__file__))
    bashCommand = "sudo bash " + bashCommand + "/controllerColor.sh "
    if m == 0:
        bashCommand = bashCommand + "255 255 255"
    elif m == 1:
        bashCommand = bashCommand + "255 255 0"
    elif m == 2:
        bashCommand = bashCommand + "0 255 0"
    elif m == 3:
        bashCommand = bashCommand + "8 208 96"
    elif m == 4:
        bashCommand = bashCommand + "255 0 255"
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

def serial_read_write(string): # use time library to call every 10 ms in separate thread
    ser.write(padStr(string).encode())
    
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    #window['text'].update(inp)
    print("From teensy: " + inp)
    #update_gui_table(inp)

    return

def driver_thread_funct(controller):
    #Create variables
    pygame.mixer.Sound.play(random.choice([startup1]*9 + [startup2]*1)) # dont mind this line
    runningMode = 0
    joystickArr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
    rgb(0)
    #running section
    while True:
        
        runningMode = controller.mode
        paused = controller.paused
        #0 = strafe, 1 = forback, 2 = roll, 3 = turn, 4 = pitch
        #0 = L3LR, 1 = L3UD, 2 = triggerL, 3 = R3LR, 4 = R3UD, 5 = triggerR
        joystickArr[0] = joystick_map_to_range(controller.l3_horizontal)+1
        joystickArr[1] = joystick_map_to_range(controller.l3_vertical)+1
        joystickArr[2] = trigger_map_to_range(controller.triggerL)+1
        joystickArr[3] = joystick_map_to_range(controller.r3_horizontal)+1
        joystickArr[4] = joystick_map_to_range(controller.r3_vertical)+1
        joystickArr[5] = trigger_map_to_range(controller.triggerR)+1


        serial_read_write(''',{0:.3f},{1:.3f},{2:.3f},{3:.3f},{4:.3f},{5:.3f},M:{6},LD:{7},RD:{8},UD:{9},DD:{10},Sq:{11},Tr:{12},Ci:{13},Xx:{14},Sh:{15},Op:{16},Ps:{17},L3:{18},R3:{19}'''
        .format(joystickArr[0], joystickArr[1], joystickArr[2], joystickArr[3], joystickArr[4], joystickArr[5],
        runningMode, controller.dpadArr[0], controller.dpadArr[1],
        controller.dpadArr[2], controller.dpadArr[3], controller.shapeButtonArr[0],
        controller.shapeButtonArr[1], controller.shapeButtonArr[2], controller.shapeButtonArr[3],
        controller.miscButtonArr[0], controller.miscButtonArr[1], controller.miscButtonArr[2],
        controller.miscButtonArr[3], controller.miscButtonArr[4]))
        
#        print(''',{0:.3f},{1:.3f},{2:.3f},{3:.3f},{4:.3f},{5:.3f},M:{6},LD:{7},RD:{8},UD:{9},DD:{10},Sq:{11},Tr:{12},Ci:{13},Xx:{14},Sh:{15},Op:{16},Ps:{17},L3:{18},R3:{19}'''
#        .format(joystickArr[0], joystickArr[1], joystickArr[2], joystickArr[3], joystickArr[4], joystickArr[5],
#        runningMode, controller.dpadArr[0], controller.dpadArr[1],
#        controller.dpadArr[2], controller.dpadArr[3], controller.shapeButtonArr[0],
#        controller.shapeButtonArr[1], controller.shapeButtonArr[2], controller.shapeButtonArr[3],
#        controller.miscButtonArr[0], controller.miscButtonArr[1], controller.miscButtonArr[2],
#        controller.miscButtonArr[3], controller.miscButtonArr[4]))
        
        #time.sleep(0.01)

class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.l3_horizontal = 0
        self.l3_vertical = 0
        self.r3_horizontal = 0
        self.r3_vertical = 0
        self.triggerL = 0
        self.triggerR = 0
        self.modeMax = 4
        self.mode = 0
        self.dpadArr = [0,0,0,0] #L,R,U,D
        self.shapeButtonArr = [0,0,0,0] #Sq, Tr, Cir, X
        self.miscButtonArr = [0,0,0,0,0] #Share, Options, PS, L3, R3
        self.paused = False
        self.pauseChangeFlag = True
        self.deadzone = 32767/10
        self.running_ML = False

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
        
    def on_square_release(self):
        self.shapeButtonArr[0] = 0
        
    def on_triangle_press(self):
        self.shapeButtonArr[1] = 1
        if (self.mode == 4 and not self.running_ML):
            self.running_ML = True
            startML()
        elif self.mode == 4 and self.running_ML:
            self.running_ML = False
            killML()
        
    def on_triangle_release(self):
        self.shapeButtonArr[1] = 0
        
    def on_circle_press(self):
        self.shapeButtonArr[2] = 1
        
    def on_circle_release(self):
        self.shapeButtonArr[2] = 0
        
    def on_x_press(self):
        self.shapeButtonArr[3] = 1
        
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
        
    def on_left_right_arrow_release(self):
        self.dpadArr[0] = 0
        self.dpadArr[1] = 0
        
    def on_right_arrow_press(self):
        self.dpadArr[1] = 1
        
    def on_L3_press(self):
        self.miscButtonArr[3] = 1
        pygame.mixer.Sound.play(random.choice(sheep_sounds))        
    
    def on_L3_release(self):
        self.miscButtonArr[3] = 0
        
    def on_R3_press(self):
        self.miscButtonArr[4] = 1
        
    def on_R3_release(self):
        self.miscButtonArr[4] = 0
        
    def on_options_press(self):
        self.miscButtonArr[1] = 1
        
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
        pygame.mixer.Sound.play(pause)

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
    pygame.mixer.Sound.play(error)

    while(1):
        pass


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)


time.sleep(3) # give GUI time to wake up

driver_thread = threading.Thread(target=driver_thread_funct, args=(controller,))
driver_thread.daemon = True
driver_thread.start()





controller.listen()
