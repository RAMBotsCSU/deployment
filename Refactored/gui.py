import PySimpleGUI as sg
import threading
import time

class GUI:
    def __init__(self):
        """
        Initializes the GUI with a predefined layout.
        """
        # Set the theme for the GUI
        sg.theme('DarkGreen2')

        # Define the layout of the table and other GUI elements
        tab1_layout = [
            [
                sg.Column([[sg.Text('MOVEMENT ARRAY', font=("Helvetica", 14))]]),
                sg.Column([[sg.Text('                            ', font=("Helvetica", 14))]]),
                sg.Column([[sg.Text("MODE 1: WALKING", font=("Helvetica", 14), key='-MODE_TEXT-', pad=(25, 0))]])
            ],
            [
                sg.Table(
                    values=[
                        ['Left Stick', 'Loading GUI'],
                        ['Left Trigger', 'Please wait!'],
                        ['Right Stick', '⊂(◉‿◉)つ'],
                        ['Right Trigger', ''],
                        ['Mode', ''],
                        ['D-Pad Array', ''],
                        ['Shape Button Array', ''],
                        ['Misc Button Array', ''],
                        ['           ', '           ']
                    ],
                    headings=['Parameter', 'Value'],
                    key='-TABLE-',
                    num_rows=9,
                    hide_vertical_scroll=True,
                    pad=(0, 0)
                )
            ],
            [sg.Image('./Resources/RamBOTs_Logo_Small.png')],
        ]

        # Combine all elements into the window layout
        layout = [tab1_layout]

        # Create the window
        self.window = sg.Window('RamBOTs', layout, size=(800, 420))
        self.table = self.window['-TABLE-']

        # Initialize variables to hold controller states
        self.controller = None  # This will be set later
        self.update_interval = 0.1  # Time between GUI updates in seconds

    def set_controller(self, controller):
        """
        Sets the controller instance to access its state.

        Args:
            controller (MyController): The controller instance.
        """
        self.controller = controller

    def gui_handler(self):
        """
        Handles GUI events in the main thread.
        """
        print("GUI handler started.")
        while True:
            event, _ = self.window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                print("GUI window closed.")
                break
            # Additional event handling can be added here if needed

        # Close the window when the loop exits
        self.window.close()

    def gui_table_handler(self):
        """
        Updates the table in the GUI with the latest controller states.
        This function runs in a separate thread.
        """
        print("GUI table handler started.")
        while True:
            if self.controller is None:
                time.sleep(self.update_interval)
                continue

            # Update the table with the latest controller values
            self.update_table()
            time.sleep(self.update_interval)

    def update_table(self):
        """
        Updates the table in the GUI with the current controller states.
        """
        # Retrieve controller values
        l3_horizontal = self.controller.l3_horizontal
        l3_vertical = self.controller.l3_vertical
        r3_horizontal = self.controller.r3_horizontal
        r3_vertical = self.controller.r3_vertical
        triggerL = self.controller.triggerL
        triggerR = self.controller.triggerR

        mode = self.controller.mode
        dpadArr = self.controller.dpadArr
        shapeButtonArr = self.controller.shapeButtonArr
        miscButtonArr = self.controller.miscButtonArr

        # Format values for display
        left_stick = f"{l3_horizontal / 32767:.2f}, {l3_vertical / 32767:.2f}"
        right_stick = f"{r3_horizontal / 32767:.2f}, {r3_vertical / 32767:.2f}"
        left_trigger = f"{triggerL / 65198:.2f}"
        right_trigger = f"{triggerR / 65198:.2f}"
        mode_str = f"{mode}"
        dpad_str = f"L:{dpadArr[0]}, R:{dpadArr[1]}, U:{dpadArr[2]}, D:{dpadArr[3]}"
        shape_str = f"Sq:{shapeButtonArr[0]}, Tr:{shapeButtonArr[1]}, Ci:{shapeButtonArr[2]}, X:{shapeButtonArr[3]}"
        misc_str = f"Sh:{miscButtonArr[0]}, Op:{miscButtonArr[1]}, Ps:{miscButtonArr[2]}, L3:{miscButtonArr[3]}, R3:{miscButtonArr[4]}"

        # Update the table values
        new_values = [
            ['Left Stick', left_stick],
            ['Left Trigger', left_trigger],
            ['Right Stick', right_stick],
            ['Right Trigger', right_trigger],
            ['Mode', mode_str],
            ['D-Pad Array', dpad_str],
            ['Shape Button Array', shape_str],
            ['Misc Button Array', misc_str],
            ['           ', '           ']
        ]

        # Update the table in the GUI
        self.window['-TABLE-'].update(values=new_values)

    def update_mode_text(self, mode):
        """
        Updates the mode text displayed in the GUI.

        Args:
            mode (int): The current mode number.
        """
        mode_texts = {
            0: "MODE 1: WALKING",
            1: "MODE 2: PUSH-UPS",
            2: "MODE 3: LEG CONTROL",
            3: "MODE 4: GYRO CONTROL",
            4: "MODE 5: MACHINE LEARNING",
            5: "MODE 6: DANCE MODE"
        }
        text = mode_texts.get(mode, "UNKNOWN MODE")
        self.window['-MODE_TEXT-'].update(text)
