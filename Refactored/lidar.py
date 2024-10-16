





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
