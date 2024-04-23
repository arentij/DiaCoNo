import threading
from datetime import datetime
import serial
import time


class Trigger:
    def __init__(self):
        self.initiated = datetime.now()
        self.last_time_triggered = datetime.now()
        self.triggered = False
        self.running = False
        self.connected = False
        self.time_to_clear = False

        # self.arduino_port = '/dev/ttyACM1'
        self.arduino_port = '/dev/myArduino1'
        self.arduino_baudrate = 1000000

        self.connect()
        self.worker = threading.Thread(target=self.communicate, args=())

        # self.arduino = serial.Serial(port=self.arduino_port, baudrate=self.arduino_baudrate)

        # self.
    def connect(self):
        try:
            self.arduino = serial.Serial(port=self.arduino_port, baudrate=self.arduino_baudrate)
            self.connected = True
            print('Arduino connected')
            return True
        except:
            print("couldn't initiate arduino ")
            self.connected = False
            return False

    def communicate(self):
        print("Communication attempted")
        while True:
            if not self.connected:
                print("During communication with arduino it was not able to connect, trying to reconnect")
                time.sleep(1)
                self.connect()
                continue
            try:
                data = self.arduino.readline().decode().strip()
                print(f"Arduino said {data}")
                if data == 'X':
                    self.triggered = True
                    self.last_time_triggered = datetime.now()

                if data == 'C':
                    self.time_to_clear = True
                time.sleep(0.001)
            except Exception as e:
                print(f"Communication error: {e}")
                self.connected = False
                time.sleep(1)
            # print(f"{self.triggered}_{datetime.now().strftime("%Y%m%d-%H%M%S")}")


if __name__ == "__main__":

    trigger = Trigger()
    trigger.worker.start()

    while True:
        continue
# trigger.worker().start
# arduino = serial.Serial(port='/dev/ttyACM0', baudrate=1000000)
#     try:
#         while True:
#             #Read data from serial port
#             data = arduino.readline().decode().strip()
#
#             if data == 'X':
#                 trigger.triggered = True
#                 print('Scope has been triggered')
#                 print('Sleeping for a few seconds...')
#                 time.sleep(15)
#                 break
#
#             # Delay for a bit to prevent busy-waiting
#             time.sleep(0.001)
#
#     except KeyboardInterrupt:
#         arduino.close()
#         print('\nArduino closed')

