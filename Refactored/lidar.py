import sys, os # acces the operating system
import time # loop delays
import pygame # lidar map display
import queue # sharing information between threads
from pycoral.utils import edgetpu # allows work with TPU's for machine learning
from adafruit_rplidar import RPLidar
from math import floor, pi, cos, sin
from utilities import joystick_map_to_range, trigger_map_to_range

class LidarHandler:

    def __init__(self, controller, shared_queue, port_name = '/dev/ttyUSB0'):

        self.shared_queue = shared_queue
        self.port_name = port_name
        self.controller = controller
        # self.ready = False

        # threshholds
        self.red_dot_threshold = 700 # 500=.5m (?); threshhold for detecting close object
        self.white_dot_threshold = 2000 # furthest distance factored into calculations
        self.display_width = 400
        self.display_scale = int(self.white_dot_threshold/self.display_width)

        self.lidar_view = []
        self.STOP_FLAG = False
   
        # self.scan_data = [white_dot_threshold] * 360

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
    def preprocess_lidar_data(self, lidar_data):
        lidar_max_value = 12000
        uint8_max_value = 255

        # Normalize the output labels to the range [0, 1]
        data_normalized = lidar_data / lidar_max_value
        data_mapped = (data_normalized * uint8_max_value).astype(np.uint8)
        return data_mapped

    # run ML model for autonomous_walk lidar mode
    # get outputs from tflite model on lidar data
    def runLidarInference(self, lidar_data, interpreter):
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

            self.shared_queue.put(output_values)
        else:
            print("lidar view data incorrect")

    # def start_display(self):
    #     # Set up pygame and the display
    #     os.putenv('SDL_FBDEV', '/dev/fb1')
    #     pygame.init()
    #     lcd = pygame.display.set_mode((self.display_width, self.display_width))
    #     lcd.fill((0,0,0))
    #     pygame.display.update()
    
    def connect_to_lidar(self):
        
        try:
            lidar = RPLidar(None, self.port_name, timeout=3)
            print("Lidar connected.")
            
            
            return lidar
        except: 
            print("Error connecting to lidar. Trying again")
            time.sleep(1)

        
    def update_lidar_map(self, data, lcd):
        lcd.fill((0,0,0))
        # Initialize a list to store Lidar data
        for angle in range(360):
            distance = float(data[angle])
            if distance > 0:                  # ignore initially ungathered data points
                radians = angle * pi / 180.0
                y = -distance * cos(radians)
                x = distance * sin(radians)
                point = (int(int(x)/self.display_scale + self.display_width/2), int(int(y)/self.display_scale + self.display_width/2))
                if distance <= self.red_dot_threshold:
                    lcd.set_at(point, pygame.Color(255, 0, 0))
                elif distance <= self.white_dot_threshold:
                    lcd.set_at(point, pygame.Color(255, 255, 255))
                # else:
                #     point = ((-int(white_dot_threshold * sin(radians)), int(white_dot_threshold * cos(radians))))
                #     lcd.set_at(point, pygame.Color(255, 255, 255))
        pygame.draw.line(lcd, pygame.Color(255,255,255), (0, self.display_width/2), (self.display_width, self.display_width/2), 1)
        pygame.draw.line(lcd, pygame.Color(255,255,255), (self.display_width/2, 0), (self.display_width/2, self.display_width), 1)
        for i in range(-self.white_dot_threshold + int(self.white_dot_threshold%500), self.white_dot_threshold, 500): # tick every .5 meters
            if i == 0 or i == -self.white_dot_threshold:
                continue
            tick_placement = int(i/(self.display_scale*2))+int(self.display_width/2)
            pygame.draw.line(lcd, pygame.Color(255, 255, 255), (tick_placement, (self.display_width/2)+2), (tick_placement, (self.display_width/2)-2), 1) # x-ticks
            pygame.draw.line(lcd, pygame.Color(255, 255, 255), ((self.display_width/2)+2, tick_placement), ((self.display_width/2)-2, tick_placement), 1) # y-ticks
            # label = str(i/1000)
            # font = pygame.font.SysFont("Helvetica", 12)
            # text = font.render(label, True, (255, 255, 255))
            # lcd.blit(text, (int(map_width/2 + 5), tick_placement - 5)) # x-axis
            # lcd.blit(text, (tick_placement - 5, int(map_width/2 + 5))) # y-axis
        pygame.display.update()

    # avg_dist is updated to the average data set of all data sets in dist_buffer
    def update_avg_dist(dist_buffer):
        temp_avg = [self.white_dot_threshold]*360
        for angle_step in range(0, 360, 5):                            # 360 angle values
            dist_sum = 0                                    # temp hold distance sum of each angle
            for i in range(5):
                for arr in dist_buffer:                     # check same angle of each data set
                    dist_sum += arr[angle_step + i]                  # sum all distances at one angle
            temp_avg[angle_step] = dist_sum / (len(dist_buffer)*5) # average distance by size of dist_buffer
        return temp_avg

    # def initialize_path_following(self):
        
        # #Create variables
        # model_path = '../../machine_learning/lidar_model_quantized_edgetpu.tflite'
        # interpreter = edgetpu.make_interpreter(model_path, device='usb')
        # interpreter.allocate_tensors()
        
        # # CSV file name
        # output_file = 'lidar_data.csv'



    def lidar_thread_funct(self):
        
        # self.start_display()
        # self.initialize_path_following()

        # Set up pygame and the display
        os.putenv('SDL_FBDEV', '/dev/fb1')
        pygame.init()
        #map_width = 400 # printed map size
        lcd = pygame.display.set_mode((self.display_width, self.display_width))
        lcd.fill((0,0,0))
        pygame.display.update()

        #Create variables
        model_path = '../../machine_learning/lidar_model_quantized_edgetpu.tflite'
        interpreter = edgetpu.make_interpreter(model_path, device='usb')
        interpreter.allocate_tensors()
        
        # CSV file name
        output_file = 'lidar_data.csv'

        # Define Parameters
        #red_dot_threshold = 700 # 500=.5m (?); threshhold for detecting close object
        #white_dot_threshold = 2000 # furthest distance factored into calculations

        print("Lidar setup initialized.\nPrinted Map Range: ", self.white_dot_threshold/1000,
               " m\nStop proximity: ", self.red_dot_threshold/1000, " m")
        
        # Scale parameters to map
        # self.display_scale = int(white_dot_threshold/self.display_width)

        scan_data = [self.white_dot_threshold] * 360
        lidar_data = []

        joystickArr = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]

        # define parameters for stop mode
        starttime = time.time()
        window = 10
        # dist = [white_dot_threshold]*360 # stores lidar distances
        avg_dist = [self.white_dot_threshold]*(int(360/5)) # stores moving averages
        dist_buffer = [[]*360]

        lidar = self.setup_lidar_connection()
        
        try:        
            while(True):

                try:
                    for scan in lidar.iter_scans():
                        for (_, angle, distance) in scan:
                            scan_data[min([359, int(angle)])] = distance 
                        self.update_lidar_map(scan_data, lcd)

                        if self.controller.running_stop_mode:
                            if (time.time() - starttime) > 0.05: # every .05s
                                starttime = time.time() # restart timer
                                dist_buffer.append(scan_data) # add new data set to dist_buffer
                                if len(dist_buffer) > window: # more data sets than window parameter
                                    dist_buffer.pop(0) # remove oldest data set
                                    avg_dist = self.update_avg_dist(dist_buffer) # get average of all data sets
                                    if min(avg_dist) <= self.red_dot_threshold: # any distance within stop proximity?
                                        self.STOP_FLAG = True
                                        print("STOP_FLAG raised.")
                                    else:
                                        self.STOP_FLAG = False
                                        print("STOP_FLAG reset. Okay to walk.")

                    # running ML model for navigating hallways around BC infill
                    if self.controller.running_autonomous_walk:

                        if time.time() - start_time > 0.2:
                            start_time = time.time()
                            self.lidar_view = scan_data
                            self.runLidarInference(scan_data, interpreter)

                            joystickArr[0] = joystick_map_to_range(self.controller.l3_horizontal)+1
                            joystickArr[1] = joystick_map_to_range(self.controller.l3_vertical)+1
                            joystickArr[2] = trigger_map_to_range(self.controller.triggerL)+1
                            joystickArr[3] = joystick_map_to_range(self.controller.r3_horizontal)+1
                            joystickArr[4] = joystick_map_to_range(self.controller.r3_vertical)+1
                            joystickArr[5] = trigger_map_to_range(self.controller.triggerR)+1

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
                    lidar = self.setup_lidar_connection()

        except KeyboardInterrupt:
            print("Program Ended")
        finally:
            lidar.stop()
            lidar.disconnect()
            print("Lidar stopped.")
            
