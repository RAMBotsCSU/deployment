import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from lidar import LidarHandler  # Assuming LidarHandler is in lidar.py

class TestLidarHandler(unittest.TestCase):
    @patch("lidar.RPLidar")  # Mock RPLidar to avoid hardware dependency
    def setUp(self, mock_lidar):
        self.mock_lidar_instance = mock_lidar.return_value
        self.mock_lidar_instance.iter_scans.return_value = iter([
            [(0, 1.0, 100.0), (90, 1.0, 150.0), (180, 1.0, 200.0)],
            [(0, 1.0, 120.0), (90, 1.0, 140.0), (180, 1.0, 180.0)]
        ])
        self.lidar_handler = LidarHandler()
        self.lidar_handler.lidar = self.mock_lidar_instance
    
    def test_preprocess_lidar_data(self):
        data = [(0, 1.0, 100.0), (90, 1.0, 150.0), (180, 1.0, 200.0)]
        expected = np.array([100.0, 150.0, 200.0])
        result = self.lidar_handler.preprocess_lidar_data(data)
        np.testing.assert_array_almost_equal(result, expected)
    
    @patch("lidar.tflite_interpreter")  # Mock ML model inference
    def test_postprocess_predictions(self, mock_tflite_interpreter):
        mock_tflite_interpreter.get_tensor.return_value = np.array([0.1, 0.7, 0.2])
        result = self.lidar_handler.postprocess_predictions()
        self.assertEqual(result, 1)  # Expected class index with highest probability
    
    def test_lidar_connection(self):
        self.lidar_handler.connect_lidar()
        self.mock_lidar_instance.connect.assert_called()
    
    def tearDown(self):
        self.lidar_handler.disconnect_lidar()
        self.mock_lidar_instance.stop.assert_called()
        self.mock_lidar_instance.disconnect.assert_called()

if __name__ == "__main__":
    unittest.main()