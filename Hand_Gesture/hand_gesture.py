import re
import cv2
import numpy as np
import time
from pycoral.utils import edgetpu
from pycoral.utils import dataset
from pycoral.adapters import common
from pycoral.adapters import classify
from pycoral.adapters.common import input_size
from pycoral.adapters.classify import get_classes
from pycoral.utils.edgetpu import make_interpreter

def load_model(model_path):
    interpreter = edgetpu.make_interpreter(model_path, device='usb')
    interpreter.allocate_tensors()
    return interpreter

def load_labels(labels_path):
    with open(labels_path, 'r') as f:
        return {int(line.split()[0]): line.strip().split(maxsplit=1)[1] for line in f.readlines()}

def setup_camera(camera_index=0, width=320, height=480):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise ValueError("Error: Camera not found or could not be opened.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 30)

    return cap

def preprocess_frame(frame, input_shape, input_details):
    """Preprocess the frame for UINT8 model input."""
    # Resize and convert to RGB
    resized_frame = cv2.resize(frame, input_shape)
    resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # Handle UINT8 quantized model input
    scale, zero_point = input_details[0]['quantization']
    if scale > 0:
        resized_frame = ((resized_frame / 255.0) / scale + zero_point).astype(np.uint8)

    # Expand dimensions for batch input
    input_tensor = np.expand_dims(resized_frame, axis=0)
    return input_tensor

def run_inference(interpreter, input_tensor):
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]['index'], input_tensor)
    interpreter.invoke()
    
    # Logging raw model outputs for debugging
    output_details = interpreter.get_output_details()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    print("Raw model output:", output_data)
    
    return get_classes(interpreter, top_k=1)

def display_results(frame, classes, labels, position=(10, 30)):
    """Display the inference results on the frame."""
    for c in classes:
        label = labels.get(c.id, f"Class {c.id}")
        score = c.score
        cv2.putText(frame, f"{label}: {score:.2f}", position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return frame

def run_hand_gesture():
    MODEL_FILE = "hand_command_edgetpu.tflite"
    LABELS_FILE = "labels.txt"

    # Load model and labels
    interpreter = load_model(MODEL_FILE)
    print("Model loaded")
    labels = load_labels(LABELS_FILE) if LABELS_FILE else {}
    print("Labels loaded")
    print(labels)
    input_shape = input_size(interpreter)
    input_details = interpreter.get_input_details()

    # Set up the camera
    cap = setup_camera()
    print("Camera setup correctly")

    print("Press 'q' to quit.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read from the camera.")
                break

            # Preprocess the frame, run inference, and display results
            input_tensor = preprocess_frame(frame, input_shape, input_details)
            classes = run_inference(interpreter, input_tensor)
            frame = display_results(frame, classes, labels)

            # Show frame
            cv2.imshow("Hand Gesture Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_hand_gesture()
