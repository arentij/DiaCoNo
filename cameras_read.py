import datetime
import subprocess
import time

import pyudev
import cv2
import threading
from folder_manager import Folder, check_create_folder

import random

def list_usb_cameras():
    context = pyudev.Context()
    for device in context.list_devices(subsystem='video4linux'):
        camera_info = {}
        camera_info['name'] = device.get('ID_MODEL')
        camera_info['vendor'] = device.get('ID_VENDOR')
        camera_info['serial'] = device.get('ID_SERIAL_SHORT')
        camera_info['bus'] = device.get('ID_BUS')
        camera_info['vendor_id'] = device.get('ID_VENDOR_ID')
        camera_info['model_id'] = device.get('ID_MODEL_ID')
        camera_info['path'] = device.device_node
        # camera_info['openable'] = 'video' in device.device_node
        cap = cv2.VideoCapture(device.device_node)
        if not cap.isOpened():
            # print("Error: Unable to open the video capture device.")
            camera_info['openable'] = False

        else:
            camera_info['openable'] = True

        yield camera_info

# List USB cameras


def get_v4l2_output(device):
    command = ["v4l2-ctl", "-d", device, "--all"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def write_v4l2_param(device, parameter, value):
    # command = f"v4l2-ctl", "-d", device, "-c", parameter, '='

    command = ["v4l2-ctl", "-d", device, "-c", f"{parameter}={value}"]
    # print(command)
    try:
        subprocess.run(command, check=True)
        # subprocess.run(capture_output=)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def set_resolution_and_pixelformat(device, resolution, pixelformat):

    command = ["v4l2-ctl", "-d", device, "--set-fmt-video", f"width={resolution[0]},height={resolution[1]},pixelformat={pixelformat}"]
    # command = ["v4l2-ctl", "-d", "/dev/video2", "--set-fmt-video=width=1920,height=1080,pixelformat=MJPG"]
    # print(*command)
    try:
        # time.sleep(1)
        subprocess.run(command)
        # print("Resolution and pixel format set successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting resolution and pixel format: {e}")
# Specify the video device (e.g., '/dev/video0')
# video_device = "/dev/video0"
# output = get_v4l2_output(video_device)
# if output:
#     print(output)
# else:
#     print("Failed to get v4l2-ctl output.")


class Camera:
    def __init__(self, mounting_point, vid_mid):
        self.initiated = datetime.datetime.now()
        self.triggered = False
        self.running = False

        self.path = mounting_point
        self.file_format = 'MJPG'
        self.time_triggered = []
        self.frames_times = []
        self.time_created = datetime.datetime.now()
        self.vid_mid = vid_mid
        self.hdmi = False
        self.cap = []

        # print(self.vid_mid)
        cam260_param = {"name": "usb260", "fps": 260, 'resolution': [640, 360], 'auto_exposure': 1,
                        "exposure_time_absolute": 2, "exposure_time_absolute_br": 100, 'adjust': True, 'notes': 'fast but low res'}
        cam120_param = {"name": "usb120bw", "fps": 120, 'resolution': [1280, 720], 'auto_exposure': 1,
                        "exposure_time_absolute": 3, "exposure_time_absolute_br": 100, 'adjust': True, 'notes': 'medium fast BW'}
        cam090_param = {"name": "usb90", "fps": 90, 'resolution': [1920, 1080], 'auto_exposure': 1,
                        "exposure_time_absolute": 1, "exposure_time_absolute_br": 100, 'adjust': True, 'notes': 'slow but high res'}
        hdmi_stream1 = {"name": "hdmi_usb1", "fps": 60, 'resolution': [1920, 1080],
                        'adjust': False, 'notes': "HDMI 2 USB V1"}

        vendorID_modelID_param = {"1e4e:7103": hdmi_stream1, "32e4:4689": cam260_param,
                                       "32e4:0234": cam090_param, "0c45:6366": cam120_param}
        self.parameters = vendorID_modelID_param[self.vid_mid]
        self.resolution = self.parameters['resolution']
        self.fps = self.parameters['fps']
        self.type = self.parameters['name']
        if self.type == "hdmi_usb1":
            self.hdmi = True

        self.setup_for_exp()
        time.sleep(0.01)
        # self.setup_size_format()

    def setup_for_exp(self):
        if self.parameters['adjust']:
            write_v4l2_param(self.path, 'auto_exposure', self.parameters['auto_exposure'])
            time.sleep(0.01)
            write_v4l2_param(self.path, 'exposure_time_absolute', self.parameters['exposure_time_absolute'])
            print(f"Path: {self.path}, Type:{self.parameters['name']}")
            return True

    def setup_for_bright(self, abs_exposure=100):
        if self.parameters['adjust']:
            write_v4l2_param(self.path, 'auto_exposure', self.parameters['auto_exposure'])
            time.sleep(0.01)
            write_v4l2_param(self.path, 'exposure_time_absolute', self.parameters['exposure_time_absolute_br'])

            return True

    def setup_size_format(self):
        if self.parameters['adjust']:
            set_resolution_and_pixelformat(self.path, self.parameters['resolution'], self.file_format)
        return True


    def take_bright_pic(self, abs_exposure = 100):
        self.setup_for_bright()
        self.cap = cv2.VideoCapture(self.path)
        # if not self.cap.isOpened():
        #     print(f"Could not open video device: {self.path}")

        # time.sleep(random.uniform(0,2))
        time_attempted_writing = datetime.datetime.now()
        # self.cap.release()

        while (datetime.datetime.now() - time_attempted_writing).total_seconds() < 20:
            self.cap = cv2.VideoCapture(self.path)
            if not self.cap.isOpened():
                print(f"Could not open video device: {self.path}")
                continue

            ret, frame = self.cap.read()
            if not ret:
                continue
            time.sleep(random.uniform(0.001, 0.010))
            video_source_name = f"Video{self.fps}_{self.path.split('/')[-1][5:]}"
            image_filename = f"{save_folder.image_folder}/{video_source_name}.jpg"
            # print(image_filename)

            try:

                cv2.imwrite(image_filename, frame)
                print(f"{image_filename} is written")
                break
            except cv2.error as e:
                # time.sleep(random.uniform(0.001, 0.002))
                self.cap.release()
                print(f"{self.path} wasn't able to write the file due to: {e}")
                continue
        self.cap.release()

        return True

    def bright_pic_worker(self, abs_exposure=100):
        threading.Thread(target=self.take_bright_pic, args=(abs_exposure,))
        return threading.Thread(target=self.take_bright_pic, args=(abs_exposure,))




if __name__ == "__main__":
    save_folder = Folder()

    time_before = datetime.datetime.now()
    working_cameras = []


    for camera in list_usb_cameras():
        print(f"Name: {camera['name']}, Vendor: {camera['vendor']}, Serial: {camera['serial']}")
        print(f"Bus: {camera['bus']}, Vendor ID: {camera['vendor_id']}, Model ID: {camera['model_id']}")
        print(f"PATH: {camera['path']}, Openable: {camera['openable']}")

        if camera['openable']:
            continue

            working_cameras.append(Camera(camera['path'], f"{camera['vendor_id']}:{camera['model_id']}"))

            print()

    for working_usb_cam in working_cameras:
        working_usb_cam.setup_for_exp()
        working_usb_cam.setup_size_format()
        # working_usb_cam.take_bright_pic()
        working_usb_cam.bright_pic_worker().start()
    # save_folder.update_folders(1, 10)
    while True:
        time.sleep(0.001)
