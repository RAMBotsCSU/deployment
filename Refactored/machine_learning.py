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