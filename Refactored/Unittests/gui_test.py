import unittest
from unittest.mock import MagicMock, patch
import PySimpleGUI as sg
from gui import GUI

class TestGUI(unittest.TestCase):
    
    @patch("PySimpleGUI.Window")
    def setUp(self, mock_window):
        """Set up a GUI instance for testing with a mocked window."""
        self.gui = GUI()
        self.gui.window = MagicMock()
        self.gui.table = MagicMock()
    
    def test_initialization(self):
        """Test if GUI initializes correctly."""
        self.assertIsNotNone(self.gui.window)
        self.assertIsNotNone(self.gui.table)
        self.assertIsNone(self.gui.controller)
    
    def test_set_controller(self):
        """Test setting a controller in the GUI."""
        mock_controller = MagicMock()
        self.gui.set_controller(mock_controller)
        self.assertEqual(self.gui.controller, mock_controller)
    
    def test_update_table(self):
        """Test updating the GUI table with mock controller values."""
        mock_controller = MagicMock()
        mock_controller.l3_horizontal = 16383
        mock_controller.l3_vertical = -16383
        mock_controller.r3_horizontal = 32767
        mock_controller.r3_vertical = -32767
        mock_controller.triggerL = 32599
        mock_controller.triggerR = 65198
        mock_controller.mode = 2
        mock_controller.dpadArr = [1, 0, 1, 0]
        mock_controller.shapeButtonArr = [1, 1, 0, 0]
        mock_controller.miscButtonArr = [0, 1, 1, 0, 1]
        
        self.gui.set_controller(mock_controller)
        self.gui.update_table()
        
        expected_values = [
            ['Left Stick', '0.50, -0.50'],
            ['Left Trigger', '0.50'],
            ['Right Stick', '1.00, -1.00'],
            ['Right Trigger', '1.00'],
            ['Mode', '2'],
            ['D-Pad Array', 'L:1, R:0, U:1, D:0'],
            ['Shape Button Array', 'Sq:1, Tr:1, Ci:0, X:0'],
            ['Misc Button Array', 'Sh:0, Op:1, Ps:1, L3:0, R3:1'],
            ['           ', '           ']
        ]
        
        self.gui.window['-TABLE-'].update.assert_called_once_with(values=expected_values)
    
    def test_update_mode_text(self):
        """Test updating the mode text in the GUI."""
        self.gui.update_mode_text(3)
        self.gui.window['-MODE_TEXT-'].update.assert_called_once_with("MODE 4: GYRO CONTROL")
    
    def test_update_mode_text_unknown(self):
        """Test updating mode text with an unknown mode."""
        self.gui.update_mode_text(99)
        self.gui.window['-MODE_TEXT-'].update.assert_called_once_with("UNKNOWN MODE")

if __name__ == "__main__":
    unittest.main()