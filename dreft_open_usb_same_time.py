import threading
import time

import cv2

class Camera:
    def __init__(self, path):
        self.path = path

        self.cap = cv2.VideoCapture(self.path)
        self.frame = []
        self.ret = False


        self.worker = threading.Thread(target=self.running, args=())


    def running(self):
        while True:
            if not self.ret:
                self.cap = cv2.VideoCapture(self.path)
            ret, frame = self.cap.read()
            self.ret = ret
            if not ret:
                print(f"{self.path} did not read the frame")
                time.sleep(0.01)
                continue
            self.frame = frame
            print(f"{self.path} is OK")
            time.sleep(0.5)


if __name__ == "__main__":
    cam1 = Camera("/dev/video0")
    cam2 = Camera("/dev/video2")
    cam3 = Camera("/dev/video4")
    cam4 = Camera("/dev/video6")
    cam5 = Camera("/dev/video8")
    cam6 = Camera("/dev/video10")

    cam1.worker.start()
    cam2.worker.start()
    cam3.worker.start()
    cam4.worker.start()
    cam5.worker.start()
    cam6.worker.start()


