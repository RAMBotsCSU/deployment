      #**********************************************************************************
      #* pi_serial_main.py  :Created 10/2022 by Evan Hassman with contribtuions from    *
      #*  Eric Percin and Thomas Veldhuizen                                             *
      #*                                                                                *
      #* This program _____                                                             *
      #*                                                                                *
      #*                                                                                *
      #*                                                                                *
      #**********************************************************************************
import serial
from multiprocessing import Process, Queue
import pygame
from pygame import mixer
import time
import subprocess
import math
import random

'''mixer.init()
sheep1 = pygame.mixer.Sound('Sounds/sheep1.mp3')
sheep2 = pygame.mixer.Sound('Sounds/sheep2.mp3')
sheep3 = pygame.mixer.Sound('Sounds/sheep3.mp3')
sheep4 = pygame.mixer.Sound('Sounds/sheep4.mp3')
sheep_sounds = [sheep1,sheep2,sheep3,sheep4]
#pygame.mixer.Sound.play(random.choice(sheep_sounds))
pygame.mixer.Sound.play(random.choice(sheep_sounds))'''


#Function to change the RGB of the controller based on mode
def rgb(m):
    if m == 0:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 255 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 0 0"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == 2:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 0 255 0"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    elif m == -1:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 0 0 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    else:
        bashCommand = "sudo bash /home/pi/Desktop/RAMBots_Git/testing/pi/color_test.sh 255 0 255"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        
        
#Function to pad the output chars to length 120 (127- serial ad-ons)
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
    
    
#Function to communicate and output to teensy by a given string
def serialWrite_Read(output):
    #Write out what the pi is sending
    #print("Pi: " + output)
    output = padStr(output)
    
    #Write out to the serial buffer
    ser.write(output.encode())
    
    #Collect from serial buffer, trim the extra bits, then print
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    print(inp)
    
def serialRead():
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    print(inp)
   
#Function to round to the nearest 0.05 for joysticks and triggers
def round_val(val):
    roundTo = 0.2
    returnVal = round(round(val/roundTo)*roundTo,-int(math.floor(math.log10(roundTo))))
    if (returnVal < -1*roundTo and returnVal > roundTo):
        returnVal = 0.
    #print("roundedVal = ", returnVal)
    #The -int part removes values of .00000000000001
    return returnVal

#*********************
#* Controller Thread *
#*********************
def controllerCode(q):
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    mode = 0
    rgb(mode)
    message = ""
    threadTerm = 0
    heightChange = 0
    triggerLock = 0
    #0 = strafe, 1 = forback, 2 = roll, 3 = turn, 4 = pitch, 5 = height, 6 = yaw
    #Create arrays for Lx, Ly, L2, Rx, Ry, R2
    #Lx = strafe, Ly = forback, L2,R2 = roll, Rx = turn, Ry = pitch, D-pad up/down = height
    oldAxisArr = [0., 0., 0., 0., 0., 0.]
    newAxisArr = [0., 0., 0., 0., 0., 0.]
    axisLabelArr = ["Lx", "Ly", "L2", "Rx", "Ry", "R2"]
    while(threadTerm == 0):
        using_controller = True

        while using_controller:
            events = pygame.event.get()
            for event in events:
                #print(event)
                #Axis event
                if (mode == 0): #0 means full controller
                    if event.type == pygame.JOYAXISMOTION:
                        #for i in range(6):
                        i = event.axis
                        if (i == 1 or i == 4):
                            newAxisArr[i] = -1.*round_val(j.get_axis(i))
                        #L2
                        elif (i == 2 and triggerLock != 1):
                            triggerLock = 2
                            newAxisArr[i] = -1.*round_val((j.get_axis(i)+1.)/2)
                            #print("newAxisArr: ", newAxisArr[i], "i:",i,"triggerLock:",triggerLock)
                            if (newAxisArr[i] > -0.2):
                                triggerLock = 0
                            #print("triggerLock is now: ", triggerLock)
                        #R2
                        elif (i == 5 and triggerLock != 2):
                            triggerLock = 1
                            i = 2
                            newAxisArr[i] = round_val((j.get_axis(5)+1.)/2)
                            #print("newAxisArr: ", newAxisArr[i], "i:",i,"triggerLock:",triggerLock)
                            if (newAxisArr[i] < 0.2):
                                triggerLock = 0
                            #print("triggerLock is now: ", triggerLock)
                        elif (i == 0 or i == 3):
                            newAxisArr[i] = round_val(j.get_axis(i))
                        if (i == 5):
                            i = 2
                        #print("newAxisArr: ", newAxisArr[i])
                        #print("oldAxisArr: ", oldAxisArr[i])
                        if (oldAxisArr[i] != newAxisArr[i]):
                            
                            #print(axisLabelArr[i], ": ", newAxisArr[i])
                            message = "AR{}:{},".format(i,newAxisArr[i])
                            q.put(message)
                        oldAxisArr[i] = newAxisArr[i]
                        
                        
                            
                    #Button Event
                    elif event.type == pygame.JOYBUTTONDOWN:
                        #X
                        if j.get_button(0):
                            print("X")
                        #Circle
                        elif j.get_button(1):
                            print("Circle")
                        #Triangle
                        elif j.get_button(2):
                            print("Triangle")
                        #Square
                        elif j.get_button(3):
                            print("Movement Test")
                            message = "SQ"
                            q.put(message)
                        #L2 Half Way
                        elif j.get_button(6):
                            pass
                            #print("L2")
                        #R2 Half Way
                        elif j.get_button(7):
                            pass
                            #print("R2")
                        #Share
                        elif j.get_button(8):
                            print("Share")
                        #Option
                        elif j.get_button(9):
                            print("Option")
                        #L3 (Joystick Press)
                        elif j.get_button(11):
                            print("L3")
                        #R3 (Joystick Press)
                        elif j.get_button(12):
                            print("R3")
                    
                    #Hat Event
                    elif event.type == pygame.JOYHATMOTION:                        
                        #D-Pad Values
                        dx,dy = j.get_hat(0)
                        if(dx == 1):
                            print("Right")
                        elif(dx == -1):
                            #pygame.mixer.Sound.play(random.choice(sheep_sounds))
                            print("Left")
                        if(dy == 1):
                            #print("Up")
                            heightChange = 1
                            message = "AR{}:{},".format(5,0.2)
                            q.put(message)
                        elif(dy == -1):
                            #print("Down")
                            heightChange = 1
                            message = "AR{}:{},".format(5,-0.2)
                            q.put(message)
                        elif(dy == 0):
                            #print("D-Pad: released")
                            if(heightChange == 1):
                                message = "AR{}:{},".format(5,0.)
                                q.put(message)
                                heightChange = 0
                    
                if (event.type == pygame.JOYBUTTONDOWN):
                    #L1
                    if j.get_button(4):
                        mode =  3 if mode <= 0 else mode - 1
                        message = "MS:{},".format(mode)
                        q.put(message)
                        rgb(mode)
                    #R1
                    elif j.get_button(5):
                        mode =  0 if mode >= 3 else mode + 1
                        message = "MS:{},".format(mode)
                        q.put(message)
                        rgb(mode)
                    #Playstation Button
                    elif j.get_button(10):
                        q.put("TM")
                        threadTerm = 1
                        using_controller = False

            
    #After leaving ThreadTerm
    print("CONTROLLER TERMINATING")

#*****************
#* Driver Thread *
#*****************
def driver(q):
    threadTerm = 0
    mode = 0
    keyWord = ""
    message = ""
    #followMeThread = Process(target=MachineLearningCode, args=(q,))
    #followMeThread.daemon = True
    while (threadTerm == 0):
        #Main Loop
        '''
        if (mode == 1 and thread not started):
            followMe.start()
            followMeActive = 1
        else if (mode == 2 and thread not started:
            followMe.exit()
            start other thread
        '''
        if (not q.empty()):   #If item in queue
            item = q.get()
            if(len(item)!=0): #Ensure item is not blank
                #print ("Running", item)
                keyWord = item[0:2]
                #Array Modification
                if (keyWord == "AR"):
                    serialWrite_Read(item)
                #Mode set
                elif (keyWord == "MS"):
                    for i in range(6):
                        message = "AR{}:{},".format(i,0.)
                        serialWrite_Read(message)
                    mode = item[item.index(":")+1:item.index(",")]
                    print("Setting mode to: " + mode)
                #Test Movement
                elif (keyWord == "SQ"):
                    message = "SQ"
                    serialWrite_Read(message)
                #Terminate
                elif (item == "TM"):
                    time.sleep(0.5)
                    threadTerm = 1
            else:
                print("Recived nothing")
    print("DRIVER TERMINATING")
        

#********
#* Main *
#********
if __name__ == '__main__':
    #Main
    odrvs = 2
    
    ser = serial.Serial('/dev/ttyACM0',9600)
    
    print("Hello! Waiting for Arduino Response")
    for i in range(odrvs*2+1):
        serialRead()
    
    q = Queue()
    controllerThread = Process(target=controllerCode, args=(q,))
    controllerThread.daemon = True
    driverThread = Process(target=driver, args=(q,))
    driverThread.daemon = True
    controllerThread.start()
    driverThread.start()
    controllerThread.join()
    driverThread.join()
    rgb(-1)
    print("Exiting :)")
