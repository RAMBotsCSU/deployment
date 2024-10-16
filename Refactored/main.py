import threading
import time
import queue
#from controller import MyController
#from gui import GUI
from audio import AudioManager
#from serial_comm import SerialComm
#from lidar import LidarHandler
#from machine_learning import MachineLearningHandler

def main():
    # Initialize shared queues for complex synchronization
    ball_queue = queue.Queue()
    shared_queue = queue.Queue()  # For sharing data across threads

    # Initialize components
    audio_manager = AudioManager()
    audio_manager.init_audio()

    #controller = MyController(audio_manager=audio_manager)
    #gui = GUI(controller)
    #serial_comm = SerialComm()
    #lidar_handler = LidarHandler(controller, shared_queue)
    #ml_handler = MachineLearningHandler(controller, ball_queue)

    # Start threads
    #threading.Thread(target=gui.gui_handler, daemon=True).start()
    time.sleep(1)  # Give GUI time to initialize
    #threading.Thread(target=gui.gui_table_handler, daemon=True).start()
    #threading.Thread(target=controller.listen, daemon=True).start()
    #threading.Thread(target=serial_comm.driver_thread_funct, args=(controller,), daemon=True).start()
    #threading.Thread(target=lidar_handler.lidar_thread_funct, daemon=True).start()
    #threading.Thread(target=ml_handler.ball_thread_funct, daemon=True).start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()
