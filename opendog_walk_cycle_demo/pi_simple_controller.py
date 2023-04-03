from pyPS4Controller.controller import Controller
import serial
import threading
import time


def print_controller_values(controller):
    while True:
        serial_write("L3: ({}, {}) R3: ({}, {})".format(controller.l3_horizontal, controller.l3_vertical, controller.r3_horizontal, controller.r3_vertical))
        time.sleep(0.01)
        
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

def serial_write(string):   # use time library to call every 10 ms in separate thread
    ser.write(padStr(string).encode())
    
    inp = str(ser.readline())
    inp = inp[2:-5]
    inp = rmPadStr(inp)
    print("From teensy: " + inp)
    return

class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.l3_horizontal = 0
        self.l3_vertical = 0
        self.r3_horizontal = 0
        self.r3_vertical = 0

    def on_L3_up(self, value):
        self.l3_vertical = -value
        
    def on_L3_down(self, value):
        self.l3_vertical = -value

    def on_L3_left(self, value):
        self.l3_horizontal = value
        
    def on_L3_right(self, value):
        self.l3_horizontal = value
        
    def on_L3_x_at_rest(self):
        self.l3_horizontal = 0
        
    def on_L3_y_at_rest(self):
        self.l3_vertical = 0

# Right joystick

    def on_R3_up(self, value):
        self.r3_vertical = -value
        
    def on_R3_down(self, value):
        self.r3_vertical = -value

    def on_R3_left(self, value):
        self.r3_horizontal = value
        
    def on_R3_right(self, value):
        self.r3_horizontal = value
        
    def on_R3_x_at_rest(self):
        self.r3_horizontal = 0
         
    def on_R3_y_at_rest(self):
        self.r3_vertical = 0


print("hello world")
ser = serial.Serial('/dev/ttyACM0',9600)

controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

print_controller_thread = threading.Thread(target=print_controller_values, args=(controller,))
print_controller_thread.daemon = True
print_controller_thread.start()



controller.listen()
