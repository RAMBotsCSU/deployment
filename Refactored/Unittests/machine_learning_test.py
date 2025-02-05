import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from machine_learning import MachineLearningHandler
import queue

class TestMachineLearningHandler(unittest.TestCase):
    def setUp(self):
        self.mock_controller = MagicMock()
        self.ball_queue = queue.Queue()
        self.ml_handler = MachineLearningHandler(self.mock_controller, self.ball_queue)

    def test_process_ball_detection_valid(self):
        positions = np.array([[50, 50, 100, 100]])  # Sample bounding box
        confidences = np.array([1.0])  # Confidence above threshold
        result = self.ml_handler.process_ball_detection(positions, confidences)
        self.assertIsNotNone(result)
        self.assertIn('pos', result)

    def test_process_ball_detection_invalid_confidence(self):
        positions = np.array([[50, 50, 100, 100]])
        confidences = np.array([0.5])  # Confidence below threshold
        result = self.ml_handler.process_ball_detection(positions, confidences)
        self.assertIsNone(result)

    def test_process_ball_detection_invalid_area(self):
        positions = np.array([[5, 5, 10, 10]])  # Too small bounding box
        confidences = np.array([1.0])
        result = self.ml_handler.process_ball_detection(positions, confidences)
        self.assertIsNone(result)

    def test_area_calculation(self):
        pos = [50, 50, 100, 100]
        expected_area = (50 * np.sqrt(2)) ** 2  # Distance-based square area
        self.assertAlmostEqual(self.ml_handler.area(pos), expected_area, places=2)

    def test_distance_calculation(self):
        point1 = (0, 0)
        point2 = (3, 4)
        self.assertEqual(self.ml_handler.distance(point1, point2), 5.0)  # 3-4-5 triangle

if __name__ == '__main__':
    unittest.main()
