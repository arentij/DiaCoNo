import datetime
import subprocess
import time

import pyudev
import cv2
import threading
from folder_manager import Folder, check_create_folder

import random
import os
from folder_manager import check_create_folder

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
    # print(command) v4l2-ctl -d /dev/video0 --set-fmt-video pixelformat=MJPG

    try:
        time.sleep(0.01)
        subprocess.run(command, check=True)
        # subprocess.run(capture_output=)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def set_resolution_and_pixelformat(device, resolution, pixelformat, fps):

    command = ["v4l2-ctl", "-d", device, "--set-fmt-video", f"width={resolution[0]},height={resolution[1]},pixelformat={pixelformat}", f"--set-parm={fps}"]
    # command = ["v4l2-ctl", "-d", "/dev/video2", "--set-fmt-video=width=1920,height=1080,pixelformat=MJPG"]
    command2 = ["v4l2-ctl", "-d", device, "--set-fmt-video", f"pixelformat=MJPG"]
    print(f"For {device}")
    print(*command)
    try:
        # time.sleep(1)
        subprocess.run(command, capture_output=True, text=True, check=True)
        # subprocess.run()

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
        print(f"self.path={self.path}")
        self.file_format = 'MJPG'
        self.time_triggered = []
        self.frames_times = []
        self.time_created = datetime.datetime.now()
        self.vid_mid = vid_mid
        self.hdmi = False
        self.cap = []
        self.current_folders = Folder()
        self.frames_times = []
        self.frames = []
        # print(self.vid_mid)
        cam260_param = {"name": "usb260", "fps": 260, 'resolution': [640, 360], 'auto_exposure': 1,
                        "exposure_time_absolute": 30, "exposure_time_absolute_br": 80, 'adjust': True, 'notes': 'fast but low res'}
        cam120_param = {"name": "usb120bw", "fps": 120, 'resolution': [640, 480], 'auto_exposure': 1,
                        "exposure_time_absolute": 30, "exposure_time_absolute_br": 80, 'adjust': True, 'notes': 'medium fast BW'}
        cam121_param = {"name": "usb121bw", "fps": 120, 'resolution': [640, 480], 'auto_exposure': 1,
                        "exposure_time_absolute": 30, "exposure_time_absolute_br": 80, 'adjust': True,
                        'notes': 'medium fast BW 2'}

        cam090_param = {"name": "usb90", "fps": 90, 'resolution': [640, 480], 'auto_exposure': 1,
                        "exposure_time_absolute": 30, "exposure_time_absolute_br": 80, 'adjust': True, 'notes': 'slow but high res'}
        hdmi_stream1 = {"name": "hdmi_usb1", "fps": 60, 'resolution': [1920, 1080],
                        'adjust': False, 'notes': "HDMI 2 USB V1"}

        vendorID_modelID_param = {"1e4e:7103": hdmi_stream1, "32e4:4689": cam260_param,
                                       "32e4:0234": cam090_param, "0c45:6366": cam120_param, "0c45:636d": cam121_param}
        self.parameters = vendorID_modelID_param[self.vid_mid]
        self.resolution = self.parameters['resolution']
        self.fps = self.parameters['fps']
        self.type = self.parameters['name']
        if self.type == "hdmi_usb1":
            self.hdmi = True

        self.setup_for_exp()
        time.sleep(0.01)
        # self.setup_size_format()

        self.running_worker = threading.Thread(target=self.running_and_writing, args=())

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
            set_resolution_and_pixelformat(self.path, self.parameters['resolution'], self.file_format, self.fps)
        return True

    def setup_worker(self, current_folders):
        self.current_folders = current_folders
        self.running_worker = threading.Thread(target=self.running_and_writing, args=())
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
            image_filename = f"{self.current_folders.image_folder}{video_source_name}.jpg"
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

    def running_and_writing(self, time_to_record=7):
        self.cap = cv2.VideoCapture(self.path, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        time_initiated = datetime.datetime.now()

        # cap_north.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        # cap_north.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        # cap_north.set(cv2.CAP_PROP_FPS, fps)
        #

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # fourcc = cv2.VideoWriter_fourcc(*'MJPG')

        start_time = cv2.getTickCount() / cv2.getTickFrequency()

        while True:
            # lets read every frame till we get to the trigger

            time_attempted_to_reach_frame = datetime.datetime.now()
            ret, frame = self.cap.read()
            time_after_read = datetime.datetime.now()

            # if not ret:
            #     print(f"Error: Cannot read frame at {self.path}")
            #     camera_reached = False
            #     break
            while not self.triggered:
                start_time = cv2.getTickCount() / cv2.getTickFrequency()
                self.frames = [frame]
                self.frames_times = [datetime.datetime.now()]


            # Write the frame
            self.frames.append(frame)
            self.frames_times.append(datetime.datetime.now())

            # Check for 10 seconds recording limit
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            if (current_time - start_time) > time_to_record:
                print(f"For {self.path} we got {len(self.frames)} frames")
                # print(self.frames_times)
                break
            if (datetime.datetime.now() - time_initiated).total_seconds() > 10*60:
                break

#         now we need to write the files and close the cams
        self.cap.release()
        self.triggered = False

        time_to_wait_to_write = float(self.path[10:])
        # print(float(self.path[10:]))
        print(f"Now {self.path} needs to wait {time_to_wait_to_write} s to write")
        time.sleep(time_to_wait_to_write)
        output_file = f"{self.current_folders.video_folder}{self.path[5:]}.avi"
        print(output_file)
        out = cv2.VideoWriter(output_file, fourcc, self.fps, self.resolution)

        for frame in self.frames:
            # cv2.imshow('frame', frame)
            out.write(frame)

        count = 0
        if True:
            fldr = f"{self.current_folders.video_folder}{self.path[5:]}"
            check_create_folder(fldr)

            for frame in self.frames:
                try:
                    cv2.imwrite(fldr + "/frame%d.jpg" % count, frame)
                    count += 1

                except cv2.error as e:
                    print(f"couldn't write the jpg due to {e}")
                    continue

        output_file2 = output_file[0:-4] + ".txt"
        output_file3 = output_file[0:-4] + "_param.txt"
        # Open the file in write mode
        with open(output_file2, 'w') as file:
            # Iterate over each number in the list

            for timestamp in self.frames_times:
                # Write each number to the file
                file.write(str(timestamp) + '\n')
        self.triggered = False

        out.release()
        self.frames = []
        self.frames_times = []
        print(f"Closing cam on {self.path}")

        try:
            output_cam_param = subprocess.check_output(['v4l2-ctl', '-d', self.path, '--all'], stderr=subprocess.STDOUT,
                                                       universal_newlines=True)
            with open(output_file3, 'w') as f:
                f.write(output_cam_param)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e.output}")

        return True


if __name__ == "__main__":
    current_folders = Folder()
    time_before = datetime.datetime.now()
    working_cameras = []
    current_folders.update_folders(dsc=0, n=28)
    print(f"starting ")

    for camera in list_usb_cameras():
        # print(f"Name: {camera['name']}, Vendor: {camera['vendor']}, Serial: {camera['serial']}")
        # print(f"Bus: {camera['bus']}, Vendor ID: {camera['vendor_id']}, Model ID: {camera['model_id']}")
        # print(f"PATH: {camera['path']}, Openable: {camera['openable']}")

        if camera['openable']:
            # continue

            working_cameras.append(Camera(camera['path'], f"{camera['vendor_id']}:{camera['model_id']}"))

            # print()

    # for working_usb_cam in working_cameras:
    #     # break
    #     working_usb_cam.setup_size_format()
    #     working_usb_cam.take_bright_pic()
    #
    #     #
        # working_usb_cam.bright_pic_worker().start()

    print("Now lets set up for the exp")

    for working_usb_cam in working_cameras:

        working_usb_cam.setup_size_format()
        time.sleep(0.1)
        # working_usb_cam.setup_for_exp()

    time_after = datetime.datetime.now()
    print(f"It took {(time_after-time_before).total_seconds()} s to initiate the cams")

    for t_step in range(1):
        time.sleep(1)

    # now lets initiate the runners and wait
    for working_usb_cam in working_cameras:
        working_usb_cam.triggered = False
        working_usb_cam.setup_worker(current_folders)
        working_usb_cam.running_worker.start()
        print(f"Camera {working_usb_cam.path} started ")
    time.sleep(3)

    print(f"triggering")
    for working_usb_cam in working_cameras:
        working_usb_cam.triggered = True
    # now it might be a time for a trigger

    # print('Waiting 20 sec')
    time.sleep(20)


    #
    # print("Arming again")
    # current_folders.update_folders(dsc=1, n=18)
    #
    # for working_usb_cam in working_cameras:
    #     working_usb_cam.triggered = False
    #     working_usb_cam.setup_worker(current_folders)
    #     try:
    #         working_usb_cam.running_worker.start()
    #         print(f"Camera {working_usb_cam.path} started ")
    #     except RuntimeError as e:
    #         print(f"Couldnt start cuz {e}")
    #
    # print("AAAND")
    # print(3)
    # time.sleep(1)
    # print(2)
    # time.sleep(1)
    # print(1)
    # time.sleep(1)
    # print(f"triggering again!!!")
    # for working_usb_cam in working_cameras:
    #     working_usb_cam.triggered = True
    # # now it might be a time for a trigger
    #
    # for working_usb_cam in working_cameras:
    #     working_usb_cam.running_worker.join()
    #
    # print('Waiting till joined (huh?)')
    # time.sleep(1)

