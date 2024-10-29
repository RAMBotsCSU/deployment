import threading
import time
import numpy as np
import cv2
from PIL import Image
from pycoral.utils import edgetpu
from utilities import calculate_direction, bbox_center_point
import queue
import os

class MachineLearningHandler:

    def __init__(self, controller, ball_queue):
        """
        Initializes the MachineLearningHandler with the given controller and ball_queue.

        Args:
            controller (MyController): The controller instance.
            ball_queue (queue.Queue): Queue to communicate movement commands based on ball tracking.
        """
        self.controller = controller
        self.ball_queue = ball_queue

        # Paths to the machine learning model
        self.ball_model_path = '../../machine_learning/tennisBall/BallTrackingModelQuant_edgetpu.tflite'

        # Camera settings
        self.CAMERA_WIDTH = 320
        self.CAMERA_HEIGHT = 240
        self.INPUT_WIDTH_AND_HEIGHT = 224

        # Initialize the interpreter for ball tracking
        #self.ball_interpreter = None
        #self.input_index = None
        #self.initialize_ball_model()