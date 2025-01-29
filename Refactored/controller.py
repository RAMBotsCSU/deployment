from pyPS4Controller.controller import Controller
from utilities import rgb, joystick_map_to_range, trigger_map_to_range
import threading

class MyController(Controller):
    def __init__(self, audio_manager, gui, ball_queue, shared_queue, **kwargs):
        super().__init__(**kwargs)
        self.audio_manager = audio_manager
        self.gui = gui
        self.ball_queue = ball_queue
        self.shared_queue = shared_queue

        # Controller state variables
        self.l3_horizontal = 0.0
        self.l3_vertical = 0.0
        self.r3_horizontal = 0.0
        self.r3_vertical = 0.0
        self.triggerL = 0.0
        self.triggerR = 0.0

        self.modeMax = 5
        self.mode = 0
        self.trim = 0.0
        self.deadzone = 32767 / 10

        # Button states
        self.dpadArr = [0, 0, 0, 0]            # Left, Right, Up, Down
        self.shapeButtonArr = [0, 0, 0, 0]     # Square, Triangle, Circle, X
        self.miscButtonArr = [0, 0, 0, 0, 0]   # Share, Options, PS, L3, R3

        # Flags
        self.paused = False
        self.pauseChangeFlag = True
        self.running_ML = False
        self.running_autonomous_walk = False
        self.running_stop_mode = False

    # Left Stick (L3) Events
    def on_L3_up(self, value):
        self.l3_vertical = -value if abs(value) > self.deadzone else 0.0

    def on_L3_down(self, value):
        self.l3_vertical = -value if abs(value) > self.deadzone else 0.0

    def on_L3_left(self, value):
        self.l3_horizontal = value if abs(value) > self.deadzone else 0.0

    def on_L3_right(self, value):
        self.l3_horizontal = value if abs(value) > self.deadzone else 0.0

    def on_L3_x_at_rest(self):
        self.l3_horizontal = 0.0

    def on_L3_y_at_rest(self):
        self.l3_vertical = 0.0

    # Right Stick (R3) Events
    def on_R3_up(self, value):
        self.r3_vertical = -value if abs(value) > self.deadzone else 0.0

    def on_R3_down(self, value):
        self.r3_vertical = -value if abs(value) > self.deadzone else 0.0

    def on_R3_left(self, value):
        self.r3_horizontal = -value if abs(value) > self.deadzone else 0.0

    def on_R3_right(self, value):
        self.r3_horizontal = -value if abs(value) > self.deadzone else 0.0

    def on_R3_x_at_rest(self):
        self.r3_horizontal = 0.0

    def on_R3_y_at_rest(self):
        self.r3_vertical = 0.0

    # Trigger Events
    def on_L2_press(self, value):
        self.triggerL = value + 32431

    def on_L2_release(self):
        self.triggerL = 0.0

    def on_R2_press(self, value):
        self.triggerR = value + 32431

    def on_R2_release(self):
        self.triggerR = 0.0

    # Button Events
    def on_L1_press(self):
        if not self.paused:
            self.mode = (self.mode - 1) % (self.modeMax + 1)
            rgb(self.mode)
            self.audio_manager.play_mode_sounds(self.mode)
            self.gui.update_mode_text(self.mode)

    def on_R1_press(self):
        if not self.paused:
            self.mode = (self.mode + 1) % (self.modeMax + 1)
            rgb(self.mode)
            self.audio_manager.play_mode_sounds(self.mode)
            self.gui.update_mode_text(self.mode)

    def on_square_press(self):
        self.shapeButtonArr[0] = 1
        if self.mode == 5:
            self.audio_manager.play_songs(1)

    def on_square_release(self):
        self.shapeButtonArr[0] = 0

    def on_triangle_press(self):
        self.shapeButtonArr[1] = 1
        if self.mode == 0:
            self.running_autonomous_walk = not self.running_autonomous_walk
            state = "Started" if self.running_autonomous_walk else "Stopped"
            print(f"{state} Autonomous Walk")
        elif self.mode == 4:
            self.running_ML = not self.running_ML
            if self.running_ML:
                self.audio_manager.play_sound("startMLSound")
                print("Started Machine Learning Mode")
            else:
                self.audio_manager.play_sound("stopMLSound")
                print("Stopped Machine Learning Mode")
        elif self.mode == 5:
            self.audio_manager.play_songs(2)

    def on_triangle_release(self):
        self.shapeButtonArr[1] = 0

    def on_circle_press(self):
        self.shapeButtonArr[2] = 1
        if not self.running_stop_mode:
            self.running_stop_mode = True
            print("Started Stop Mode")
        else:
            self.running_stop_mode = False
            print("Stopped Stop Mode")
        if self.mode == 5:
            self.audio_manager.play_songs(3)

    def on_circle_release(self):
        self.shapeButtonArr[2] = 0

    def on_x_press(self):
        self.shapeButtonArr[3] = 1
        if self.mode == 5:
            self.audio_manager.play_songs(4)

    def on_x_release(self):
        self.shapeButtonArr[3] = 0

    # D-Pad Events
    def on_up_arrow_press(self):
        self.dpadArr[2] = 1

    def on_up_down_arrow_release(self):
        self.dpadArr[2] = 0
        self.dpadArr[3] = 0

    def on_down_arrow_press(self):
        self.dpadArr[3] = 1

    def on_left_arrow_press(self):
        self.dpadArr[0] = 1
        if self.mode == 0 and self.trim > -1.0:
            self.trim = round(self.trim - 0.01, 2)

    def on_left_right_arrow_release(self):
        self.dpadArr[0] = 0
        self.dpadArr[1] = 0

    def on_right_arrow_press(self):
        self.dpadArr[1] = 1
        if self.mode == 0 and self.trim < 1.0:
            self.trim = round(self.trim + 0.01, 2)

    # Misc Button Events
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
        if self.pauseChangeFlag:
            # Toggle paused state
            self.paused = not self.paused
            self.pauseChangeFlag = False
            rgb(-1 if self.paused else self.mode)
            self.audio_manager.play_sound("pause")
            print("Paused" if self.paused else "Resumed")

    def on_playstation_button_release(self):
        self.miscButtonArr[2] = 0
        self.pauseChangeFlag = True

    # Listening Thread
    def start_listening(self):
        # Start the controller listening in a separate thread
        threading.Thread(target=self.listen, daemon=True).start()
