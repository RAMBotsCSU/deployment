import unittest
import numpy as np
import cv2
import math
from pycoral.utils import edgetpu
from unittest.mock import MagicMock
from pi_edays_demo import ball_thread_funct, process_image, distance, area, display_result, bboxCenterPoint, calculate_direction

class TestBallThreadFunct(unittest.TestCase):

    def setUp(self):
        # Initialize variables required for the tests
        self.controller = MagicMock()  # Mock the controller
        self.model_path = '../../machine_learning/tennisBall/BallTrackingModelQuant_edgetpu.tflite'

    def test_camera_initialization(self):
        # Test camera initialization
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        ret, frame = cap.read()
        self.assertTrue(ret, "Camera should capture a frame successfully.")
        self.assertEqual(frame.shape, (240, 320, 3), "Captured frame shape should be (240, 320, 3).")

        cap.release()

    def test_model_initialization(self):
        # Test TensorFlow Lite model initialization
        interpreter = edgetpu.make_interpreter(self.model_path, device='usb')
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()

        self.assertEqual(input_details[0]['shape'], [1, 224, 224, 3], "Model input shape should be [1, 224, 224, 3].")

    def test_process_image(self):
        # Test process_image functionality
        interpreter = edgetpu.make_interpreter(self.model_path, device='usb')
        interpreter.allocate_tensors()
        input_index = interpreter.get_input_details()[0]['index']

        # Create a mock image (all-black image)
        image = np.zeros((224, 224, 3), dtype=np.uint8)
        result = process_image(interpreter, image, input_index)  # Use imported process_image

        self.assertIsInstance(result, list, "Result should be a list.")

    def test_distance(self):
        # Test the distance function
        point1 = (1, 1)
        point2 = (4, 5)
        result = distance(point1, point2)
        expected_distance = 5.0  # sqrt( (4-1)^2 + (5-1)^2 )= 5
        self.assertAlmostEqual(result, expected_distance, "Distance calculation is incorrect.")

    def test_area(self):
        # Test the area function
        pos = (1, 1, 4, 5)  
        result = area(pos)
        expected_area = 25.0  # 5^2 = 25
        self.assertEqual(result, expected_area, "Area calculation is incorrect.")


    # def test_display_result(self):
    #     # Test bounding box scaling
    #     pos = [50, 50, 150, 150]  # Simulated output from the model
    #     frame = np.zeros((240, 320, 3), dtype=np.uint8)  # Placeholder frame

    #     # Call display_result with a single bounding box
    #     display_result([{ 'pos': pos }], frame)

    #     # Here, we would need to check the scaled positions in the frame (can be further implemented)
    #     # This requires more specific implementations depending on your expected behavior.

    def test_calculate_direction(self):
        # Test calculate_direction functionality
        ball_queue = MagicMock()

        for x in [0, 50, 150, 250]:
            calculate_direction(x)
            if 0 <= x < (320 / 3):
                ball_queue.put.assert_called_with(0.1)
            elif (320 / 3) <= x < (2 * (320 / 3)):
                ball_queue.put.assert_called_with(0)
            elif (2 * (320 / 3)) <= x <= 320:
                ball_queue.put.assert_called_with(-0.1)

    def test_confidence_threshold(self):
        # Test confidence threshold filtering in process_image
        interpreter = edgetpu.make_interpreter(self.model_path, device='usb')
        interpreter.allocate_tensors()
        input_index = interpreter.get_input_details()[0]['index']

        # Simulated inputs with varying confidence
        image = np.zeros((224, 224, 3), dtype=np.uint8)

        # Mock output for positions and confidence
        interpreter.get_tensor = MagicMock(side_effect=[
            np.array([[10, 10, 50, 50]]),  # positions
            np.array([0.95])                # low confidence
        ])

        result = process_image(interpreter, image, input_index)
        self.assertEqual(result, [], "Should filter out low-confidence predictions.")

        # Simulate high confidence
        interpreter.get_tensor = MagicMock(side_effect=[
            np.array([[10, 10, 50, 50]]),  # positions
            np.array([1.0])                 # high confidence
        ])

        result = process_image(interpreter, image, input_index)
        self.assertEqual(len(result), 1, "Should include high-confidence predictions.")

if __name__ == '__main__':
    unittest.main()
