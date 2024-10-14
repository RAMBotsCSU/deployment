
lidar_view = []

## class gui
sg.theme('DarkGreen2')

## class gui
# used in tab1_layout, update_table_cell, gui_table_handler
table = None

## class main ?
# Get the process ID of the current process
pid = os.getpid()

## class gui
# currently unused - for TODO volume settings
# Slider settings
slider_min = 0
slider_max = 100
slider_default = 100
slider_step = 1

## class gui
# initial gui layout
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

## class gui
# only used here and in window as argument
layout = [tab1_layout]

## class gui or main ?
# used by gui_handler and lidar_thread_funct
window = sg.Window('RamBOTs', layout, size=(800, 420))

## class lidar or class main ?
# flag raised to indicate override of controller values if obstacle is detected
STOP_FLAG = False


# kill_program()
# This function is used to kill the program when called
# TODO: needs exception called 
def kill_program():
    # Send SIGTERM signal
    os.kill(pid, signal.SIGTERM)

    # Or send SIGINT signal (equivalent to pressing Ctrl+C)
    os.kill(pid, signal.SIGINT) 



## class gui
# gui_handler(controlled, window)
# called by threading.thread
# opens and continuously updates the GUI with parameters from window
# controller is not used?
def gui_handler(controller,window): # manage the GUI

    print("hello from gui")
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:           # way out of UI
            print("brealong")
            break

## class gui
# update_table_cell(table, row, col, value)
# updates specified row and col in table with controller inputs
def update_table_cell(table, row, col, value):
    table.Widget.set(table.Widget.get_children()[row], "#" + str(col + 1), value)

## class gui
# gui_table_handler(controller)
# called by threading.thread
# updates table values for gui every 0.1 seconds
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

## audio class 
# called when triangle press in ml mode
def startML():
    playSound("startMLSound")
    print("starting machine learning!")
## audio class 
# called when triangle press in ml mode
def killML():
    playSound("stopMLSound")
    print("killing machine learning.")

## class lidar
# postprocess_prediction(output_values)
# called by run_lidar_inference
# part of lidar ml path prediction
def postprocess_prediction(output_values):
    dequantized_prediction = (output_values.astype(np.float32) / 255.0).reshape(1, -1)
    prediction_reversed = dequantized_prediction * 2
    return prediction_reversed

## class lidar
# preprocess_lidar_data(lidar_data)
# called by runLidarInference
# normalize lidar_data to range [0, 1]
def preprocess_lidar_data(lidar_data):
    lidar_max_value = 12000
    uint8_max_value = 255

    # Normalize the output labels to the range [0, 1]
    data_normalized = lidar_data / lidar_max_value
    data_mapped = (data_normalized * uint8_max_value).astype(np.uint8)
    return data_mapped

## class lidar
# runLidarInference(lidar_data, interpreter)
# run ML model for autonomous_walk lidar mode
# get outputs from tflite model on lidar data
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


## driver class
# rgb(m)
# controls lighting on controller (maybe)
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

## class driver
## joystick_map_to_range
def joystick_map_to_range(original_value):
    mapped_value = ((original_value + 32767) / 65535) * 2 - 1
    return mapped_value

## class driver
# trigger_map_to range
#Function to map a range of [-65534,65198] to [-1,1] with 0 in the middle
def trigger_map_to_range(value):
    if(value < 0):
        return (value/65534)
    elif(value > 0):
        return (value/65198)
    else:
        return 0

#Function to map a range of [-65534,65198] to [-1,1] with 0 in the middle
#def joey_trigger_map_to_range(value):
#    newValue = (value+168)/65366
#    return newValue

## driver class
# value_checker(odrive_values, correct_values)
# checks odrive values
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

## class driver
# check_odrive_params(input_dict)
# checks odrive vs expected params
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

## class driver
# padStr(val)
# process output data to teensy
def padStr(val):
    for _ in range (120-len(val)):
        val = val + "~"
    return val

## class driver
# rmPadStr(val)
# process input data from teensy
# function to remove all ~ padding
def rmPadStr(val):
    outputStr = ""
    for curChar in val:
        if curChar != '~':
            outputStr += curChar
    return outputStr


## class driver
# getLineSerial(ser)
# gets info from teensy
def getLineSerial(ser):
    line = str(ser.readline())
    line = line[2:-5]
    line = rmPadStr(line)
    return line

## class driver
# any_greater_than_one(arr)
# determines if trim is needed - I think to compensate for tilting or turning
def any_greater_than_one(arr):
    for value in arr:
        if value > 1.1 or value < 0.9:
            return True
    return False


## class AI
# ball_thread_funct(controller)
# runs ML model for tennis ball tracking
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

            if x1 == 57:
                x1 = 0
            if x2 == 57:
                x2 == 0
            if y1 == 42:
                y1 = 42
            if y2 == 42:
                y2 == 42

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
            ball_queue.put(-0.1)
        elif (0 <= X < increment):
            ball_queue.put(0.1)
        elif (increment <= X < (2*increment)):
            ball_queue.put(0)

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

## class lidar
# lidar_thread_funct(controller) 
# contains lidar map, stop mode, and ML path following model
def lidar_thread_funct(controller):
    # global lidar
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
    red_dot_threshold = 700 # 500=.5m (?); threshhold for detecting close object
    white_dot_threshold = 2000 # furthest distance factored into calculations

    print("Lidar setup initialized.\nPrinted Map Range: ", white_dot_threshold/1000, " m"
           " m\nStop proximity: ", red_dot_threshold/1000, " m")

    # Scale parameters to map
    scale_data = int(white_dot_threshold/map_width)

    def update_lidar_map(data):
        lcd.fill((0,0,0))
        # Initialize a list to store Lidar data
        for angle in range(360):
            distance = float(data[angle])
            if distance > 0:                  # ignore initially ungathered data points
                radians = angle * pi / 180.0
                y = -distance * cos(radians)
                x = distance * sin(radians)
                point = (int(int(x)/scale_data + map_width/2), int(int(y)/scale_data + map_width/2))
                if distance <= red_dot_threshold:
                    lcd.set_at(point, pygame.Color(255, 0, 0))
                elif distance <= white_dot_threshold:
                    lcd.set_at(point, pygame.Color(255, 255, 255))
                # else:
                #     point = ((-int(white_dot_threshold * sin(radians)), int(white_dot_threshold * cos(radians))))
                #     lcd.set_at(point, pygame.Color(255, 255, 255))
        pygame.draw.line(lcd, pygame.Color(255,255,255), (0, map_width/2), (map_width, map_width/2), 1)
        pygame.draw.line(lcd, pygame.Color(255,255,255), (map_width/2, 0), (map_width/2, map_width), 1)
        for i in range(-white_dot_threshold + int(white_dot_threshold%500), white_dot_threshold, 500): # tick every .5 meters
            if i == 0 or i == -white_dot_threshold:
                continue
            tick_placement = int(i/(scale_data*2))+int(map_width/2)
            pygame.draw.line(lcd, pygame.Color(255, 255, 255), (tick_placement, (map_width/2)+2), (tick_placement, (map_width/2)-2), 1) # x-ticks
            pygame.draw.line(lcd, pygame.Color(255, 255, 255), ((map_width/2)+2, tick_placement), ((map_width/2)-2, tick_placement), 1) # y-ticks
            # label = str(i/1000)
            # font = pygame.font.SysFont("Helvetica", 12)
            # text = font.render(label, True, (255, 255, 255))
            # lcd.blit(text, (int(map_width/2 + 5), tick_placement - 5)) # x-axis
            # lcd.blit(text, (tick_placement - 5, int(map_width/2 + 5))) # y-axis
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
    
    PORT_NAME = '/dev/ttyUSB0'

    ## setup_lidar_connection
    # trying to connect to lidar
    def setup_lidar_connection():
        while(True):
            try:
                lidar = RPLidar(None, PORT_NAME, timeout=3)
                print("Lidar connected.")
                return lidar
            except: 
                print("Error connecting to lidar. Trying again")
                time.sleep(1)
            
    lidar = setup_lidar_connection()
    try:        
        while(True):

            try:
                for scan in lidar.iter_scans():
                    for (_, angle, distance) in scan:
                        scan_data[min([359, int(angle)])] = distance 
                    update_lidar_map(scan_data)

                    if controller.running_stop_mode:
                        if (time.time() - starttime) > 0.05: # every .05s
                            starttime = time.time() # restart timer
                            dist_buffer.append(scan_data) # add new data set to dist_buffer
                            if len(dist_buffer) > window: # more data sets than window parameter
                                dist_buffer.pop(0) # remove oldest data set
                                avg_dist = update_avg_dist(dist_buffer) # get average of all data sets
                                if min(avg_dist) <= red_dot_threshold: # any distance within stop proximity?
                                    STOP_FLAG = True
                                    print("STOP_FLAG raised.")
                                else:
                                    STOP_FLAG = False
                                    print("STOP_FLAG reset. Okay to walk.")

                # running ML model for navigating hallways around BC infill
                if controller.running_autonomous_walk:

                    if time.time() - start_time > 0.2:
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
                print("Exception occured: ", e)
                lidar.stop()
                lidar.disconnect()
                print("Lidar stopped.")
                lidar = setup_lidar_connection()

    except KeyboardInterrupt:
        print("Program Ended")
    finally:
        lidar.stop()
        lidar.disconnect()
        print("Lidar stopped.")
    
## controller class
# MyController(Controller)
# initiates the controller and maps controller input to functions
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
            startML()
        elif self.mode == 4 and self.running_ML:
            self.running_ML = False
            killML()
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
# end of class

## start of main thread, no functions beyond this point
print("hello world")

# connect to teensy
try:
    ser = serial.Serial('/dev/ttyACM0', 9600)
except SerialException as e:
    print(f"An error occurred: {e}. \nPlease unplug the USB to the Teensy, press stop, and plug it in again.")
    #play sound here
    playSound("error")

    kill_program()

# initiate remote controller
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

## initiates gui interface
pi_gui_thread = threading.Thread(target=gui_handler, args=(controller,window))
pi_gui_thread.daemon = True
pi_gui_thread.start()

time.sleep(3) # give GUI time to wake up

## initiates pi_gui_table
pi_gui_table_thread = threading.Thread(target=gui_table_handler, args=(controller,))
pi_gui_table_thread.daemon = True
pi_gui_table_thread.start()

## initiates driver thread
driver_thread = threading.Thread(target=driver_thread_funct, args=(controller,))
driver_thread.daemon = True
driver_thread.start()

## initiates machine learning
ball_thread = threading.Thread(target=ball_thread_funct, args=(controller,))
ball_thread.daemon = True
ball_thread.start()

## initiates lidar
# lidar_thread_funct called in main thread, not seperate thread
# lidar_thread = threading.Thread(target=lidar_thread_funct, args=(controller,))
# lidar_thread.daemon = True
# lidar_thread.start()
lidar_thread_funct(controller)

# controller.listen()

dthread = threading.Thread(target=controller.listen)
dthread.daemon = True
dthread.start()
