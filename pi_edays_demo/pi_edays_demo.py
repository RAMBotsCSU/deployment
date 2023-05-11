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


mixer.init()
audioFolder = 'Resources/Sounds/'
#used sounds
startup1 = pygame.mixer.Sound(audioFolder + 'Other/startup_1.mp3')
startup2 = pygame.mixer.Sound(audioFolder + 'Other/startup_2.mp3')
error = pygame.mixer.Sound(audioFolder + 'Other/error.mp3')
pause = pygame.mixer.Sound(audioFolder + 'Other/pause.mp3')
startMLSound = pygame.mixer.Sound(audioFolder + 'Other/starting_ML.mp3')
stopMLSound = pygame.mixer.Sound(audioFolder + 'Other/stopping_ML.mp3')

sheep1 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep1.mp3')
sheep2 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep2.mp3')
sheep3 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep3.mp3')
sheep4 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep4.mp3')
sheep5 = pygame.mixer.Sound(audioFolder + 'Sheeps/sheep_sounds.mp3')

walkMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/walking.mp3')
walkAlternate = pygame.mixer.Sound(audioFolder + 'Mode_Switch/walking_here.mp3')
pushUpsMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/push_ups.mp3')
pushUpsAlternate = pygame.mixer.Sound(audioFolder + 'Mode_Switch/push_ups_gains.mp3')
legControlMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/leg_control.mp3')
legControlAlternate = pygame.mixer.Sound(audioFolder + 'Mode_Switch/leg_control_brrr.mp3')
gyroMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/gyro.mp3')
gyroAlternate = pygame.mixer.Sound(audioFolder + 'Mode_Switch/gyro_alternate.mp3')
machineLearningMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/machine_learning.mp3')
machineLearningAlternate = pygame.mixer.Sound(audioFolder + 'Mode_Switch/machine_learning_robot.mp3')
danceMode = pygame.mixer.Sound(audioFolder + 'Mode_Switch/dance_mode.mp3')
danceAlternate = pygame.mixer.Sound(audioFolder + 'Mode_Switch/dance_mode_alt2.mp3')

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

sheep1.set_volume(0.8)
sheep2.set_volume(0.8)
sheep3.set_volume(0.8)
sheep4.set_volume(0.8)
sheep5.set_volume(0.5)

walkMode.set_volume(0.5)
walkAlternate.set_volume(0.45)
pushUpsMode.set_volume(0.5)
pushUpsAlternate.set_volume(0.5)
legControlMode.set_volume(0.5)
legControlAlternate.set_volume(0.5)
gyroMode.set_volume(0.5)
gyroAlternate.set_volume(0.5)
machineLearningMode.set_volume(0.5)
machineLearningAlternate.set_volume(0.5)
danceMode.set_volume(0.45)
danceAlternate.set_volume(0.45)

song1.set_volume(0.25) #mayahe
song2.set_volume(0.2) #Who let the dogs out
song3.set_volume(0.2) #crazy la pint
song4.set_volume(0.25) #party rock

#sound libraries
sheep_sounds = [sheep1,sheep2,sheep3,sheep4,sheep5]
mode_sounds = [walkMode,walkAlternate,pushUpsMode,pushUpsAlternate,legControlMode,legControlAlternate,gyroMode,gyroAlternate,machineLearningMode,machineLearningAlternate]
songs = [song1,song2,song3,song4]

slider_value = slider_default

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
            update_table_cell(table, 7, 1, "Sh:0,Op:0,Ps:1,L3:0,R3:0")
        else:
            table = window['-TABLE-']
            update_table_cell(table, 0, 1, f"{controller.l3_horizontal / 32767:5.2f}, {controller.l3_vertical / 32767:5.2f}")
            update_table_cell(table, 1, 1, f"{controller.triggerL / 65198:5.2f}")
            update_table_cell(table, 2, 1, f"{controller.r3_horizontal / 32767:5.2f}, {controller.r3_vertical / 32767:5.2f}")
            update_table_cell(table, 3, 1, f"{controller.triggerR / 65198:5.2f}")
            update_table_cell(table, 4, 1, f"{controller.mode}")
            update_table_cell(table, 5, 1, f"←:{controller.dpadArr[0]}  →:{controller.dpadArr[1]}  ↑:{controller.dpadArr[2]}  ↓:{controller.dpadArr[3]}")
            update_table_cell(table, 6, 1, f"□:{controller.shapeButtonArr[0]}  △:{controller.shapeButtonArr[1]}  ○:{controller.shapeButtonArr[2]}  X:{controller.shapeButtonArr[3]}")
            update_table_cell(table, 7, 1, f"Sh:{controller.miscButtonArr[0]},Op:{controller.miscButtonArr[1]},Ps:{controller.miscButtonArr[2]},L3:{controller.miscButtonArr[3]},R3:{controller.miscButtonArr[4]}"    
            )
        time.sleep(0.1)
       



process = None

def startML():
    pygame.mixer.Sound.play(startMLSound)
    global process
    print("starting machine learning!")
    process = subprocess.Popen(['python3', 'machine_learning/Object_Detection.py','--geometry', '800x600+100+100'])


def killML():
    pygame.mixer.Sound.play(stopMLSound)
    global process
    if process:
        print("killing machine learning.")
        process.terminate()
        process.wait()


def playModeSounds(mode):
    stopSounds()
    if mode == 0:
        pygame.mixer.Sound.play(random.choice([walkMode]*19 + [walkAlternate]*1))
        window['-MODE_TEXT-'].update("MODE 1: WALK")
    elif mode == 1:
        pygame.mixer.Sound.play(random.choice([pushUpsMode]*19 + [pushUpsAlternate]*1))
        window['-MODE_TEXT-'].update("MODE 2: PUSH-UPS")
    elif mode == 2:
        pygame.mixer.Sound.play(random.choice([legControlMode]*19 + [legControlAlternate]*1))
        window['-MODE_TEXT-'].update("MODE 3: LEG CONTROL")
    elif mode == 3:
        pygame.mixer.Sound.play(random.choice([gyroMode]*19 + [gyroAlternate]*1))
        window['-MODE_TEXT-'].update("MODE 4: GYRO CONTROL")
    elif mode == 4:
        pygame.mixer.Sound.play(random.choice([machineLearningMode]*19 + [machineLearningAlternate]*1))
        window['-MODE_TEXT-'].update("MODE 5: MACHINE LEARNING")
    elif mode == 5:
        pygame.mixer.Sound.play(random.choice([danceMode]*19 + [danceAlternate]*1))
        window['-MODE_TEXT-'].update("MODE 6: DANCE")
        playSongs(-1)
        

def stopSounds():
    for sound in mode_sounds:
        sound.stop()
    for sound in songs:
        sound.stop()
    
def playSongs(song):
    for sound in songs:
        sound.stop()
    if(song == -1):
        pygame.mixer.Sound.play(random.choice(songs))
    elif(song == 1):
        pygame.mixer.Sound.play(song1)
    elif(song == 2):
        pygame.mixer.Sound.play(song2)
    elif(song == 3):
        pygame.mixer.Sound.play(song3)
    elif(song == 4):
        pygame.mixer.Sound.play(song4)
    
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
    #print("From teensy: " + inp)
#     if (gui_counter == 5):
#         update_gui_table(inp)
#         gui_counter = 0
#     gui_counter = gui_counter + 1
    return

def driver_thread_funct(controller):
    #Create variables
    pygame.mixer.Sound.play(random.choice([startup1]*19 + [startup2]*1)) # dont mind this line
    runningMode = 0
    joystickArr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
    rgb(0)
    gui_update_counter = 0
    
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
                
       # time.sleep(0.01)
        #update_gui_table_controller(controller)


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
        self.shapeButtonArr[1] = 1
        if (self.mode == 4 and not self.running_ML):
            self.running_ML = True
            startML()
        elif self.mode == 4 and self.running_ML:
            self.running_ML = False
            killML()
        elif(self.mode == 5):
            playSongs(2)
        
    def on_triangle_release(self):
        self.shapeButtonArr[1] = 0
        
    def on_circle_press(self):
        self.shapeButtonArr[2] = 1
        if(self.mode == 5):
            playSongs(3)
        
    def on_circle_release(self):
        self.shapeButtonArr[2] = 0
        
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
        stopSounds()
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


controller.listen()

