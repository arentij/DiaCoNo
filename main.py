from flask import Flask, render_template, request, jsonify
from flask import send_from_directory, render_template_string, abort
from datetime import timedelta
import threading
import datetime
import time
import cv2, os
from matplotlib import pyplot as plt
from flask import request
# from remote_scope import *
import pandas as pd
import serial
from trigger_setup import Trigger
from remote_scope import Oscilloscope
from folder_manager import *
from spectrometer_USB import *
import numpy
from seabreeze.spectrometers import Spectrometer, list_devices
from setting_loggers import *
from cameras_read import *


app = Flask(__name__, static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Define the directory to list
BASE_DIR = '/CMFX'

EXTERNAL_IMAGE_DIR = "/CMFX_RAW/video"  # Set this to your external image folder

def get_file_info(path):
    """ Returns information about a file or directory. """
    full_path = os.path.join(BASE_DIR, path)
    is_dir = os.path.isdir(full_path)
    size = None
    if not is_dir:
        size = os.path.getsize(full_path)
    return {
        'name': os.path.basename(full_path),
        'path': os.path.relpath(full_path, BASE_DIR),
        'is_dir': is_dir,
        'size': size
    }


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/video", methods=["GET", "POST"])
def video():
    folder_number = "01212"  # Default folder number
    time_input = 0  # Default time in milliseconds since zero time

    if request.method == "POST":
        folder_number = request.form.get("folder_number", "01212")
        folder_number = folder_number.zfill(5)
        time_input = int(request.form.get("time_input", 0))  # Time input in milliseconds

    # Calculate time offset for each frame based on user input
    image_data = find_images_by_time(folder_number, time_input)

    return render_template("video.html", image_data=image_data, folder_number=folder_number, time_input=time_input)


@app.route('/data')
def data():
    return list_files('')


@app.route('/files/<path:path>')
def list_files(path):
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        abort(404)
    items = []
    for name in sorted(os.listdir(full_path), key=lambda n: (not os.path.isdir(os.path.join(full_path, n)), n)):
        item_path = os.path.join(full_path, name)
        items.append(get_file_info(os.path.relpath(item_path, BASE_DIR)))
    return render_template('file_listing.html', items=items)


@app.route('/download/<path:path>')
def download_file(path):
    return send_from_directory(BASE_DIR, path, as_attachment=True)


@app.route('/view_image/<path:path>')
def view_image(path):
    return send_from_directory(BASE_DIR, path)


@app.route('/update_index')
def update_index():
    now = datetime.datetime.now()
    device_statuses = [0, 0, 0, 1]
    dsc = 0
    N_experiment = current_experiment.exp_number
    interf_filename = 0
    device_statuses = ['green' if x else 'red' for x in device_statuses]
    try:
        dsc = index_data.dsc
        # N_exp=index_data.exp_n
    except Exception as e:
        print(e)
        return True

    try:
        scope_status = scope_DHO4204.status
    except Exception as e:
        print(e)
        scope_status = 'UWAGA'
    # print(f"Current N: {N_experiment}")
    # print(f"Current Status: {scope_status}")
    int_status_color = 'red'
    if scope_status == "Ready":
        int_status_color = 'green'
    elif scope_status == "Writing Scope Files":
        int_status_color = 'orange'

    return jsonify(time=now.strftime("%d/%m/%Y, %H:%M:%S"),
                   dsc=dsc,
                   N_exp=N_experiment,
                   int_fname=index_data.interf_file,
                   int_write_status='red',
                   system_stat=index_data.system_status,
                   scope_stat=scope_status,
                   scope_color=int_status_color)


@app.route('/arm_diagnostics')
def arm_diagnostics():
    N_exp = request.args.get("n", 0, type=int)
    discharging = request.args.get("dsc", 0, type=float)
    disc_duration = request.args.get("dt", 0, type=float)
    now = datetime.datetime.now()

    update_diagnostics(discharging, N_exp)

    return jsonify(time=now, n=N_exp, dsc=discharging, duration=disc_duration)


@app.route("/images/<folder_number>/<subfolder>/<filename>")
def serve_image(folder_number, subfolder, filename):
    image_directory = os.path.join(EXTERNAL_IMAGE_DIR, f"CMFX_{folder_number}", subfolder)
    # print(f"Image directory {image_directory}, filename {filename}")
    return send_from_directory(image_directory, filename)
# @app.route('/status')
# def status():
#     return jsonify(scope=checker.statuses[0], spectr=checker.statuses[1], N_exp=checker.statuses[2], trigger=checker.statuses[3], wrote=checker.statuses[4])


def find_images_by_time(folder_number, time_input):
    base_folder = os.path.join(EXTERNAL_IMAGE_DIR, f"CMFX_{folder_number}")
    image_data = []
    max_frames = 0
    first_frame_time = None

    # Store times for each folder and identify folder with the most frames
    folder_times = {}

    if os.path.exists(base_folder):
        for subfolder in os.listdir(base_folder):
            subfolder_path = os.path.join(base_folder, subfolder)
            if not os.path.isdir(subfolder_path):
                continue
            # txt_file = os.path.join(subfolder_path, f"{base_folder}.txt")
            txt_file = os.path.join(base_folder, f"{subfolder}.txt")
            print(f"Txt file {txt_file}")
            print(f"exist= {os.path.exists(txt_file)}")
            if os.path.isdir(subfolder_path) and subfolder.startswith("video") and os.path.exists(txt_file):
                # Check if the folder contains images
                images_exist = any(
                    fname.startswith("frame") and fname.endswith(".jpg") for fname in os.listdir(subfolder_path))
                if not images_exist:
                    continue

                with open(txt_file, 'r') as f:
                    times = [datetime.datetime.strptime(line.strip(), "%Y-%m-%d %H:%M:%S.%f") for line in f.readlines()]
                    folder_times[subfolder] = times
                    # Check for the folder with the most frames
                    if len(times) > max_frames:
                        max_frames = len(times)
                        first_frame_time = times[0]

    # No valid frames
    if first_frame_time is None:
        return image_data
    print(True)
    # Convert user input from milliseconds to a timedelta
    input_time_delta = timedelta(milliseconds=time_input)

    # Find and return frames close to the specified time along with their relative time in ms
    for subfolder, times in folder_times.items():
        subfolder_path = os.path.join(base_folder, subfolder)
        for i, frame_time in enumerate(times):
            relative_time = frame_time - first_frame_time
            # print(f"Relative time {relative_time}, i={i}")
            # print(f"Current time {frame_time-first_frame_time}")
            # if i > 0:
            #     print(f"Current time {(frame_time-first_frame_time).total_seconds()*1000}")
            #     print(f"Current time {(times[i]-first_frame_time).total_seconds()*1000}")
            #     # print(f"Current time {times[i]-first_frame_time}")

            if relative_time >= input_time_delta:
                adjusted_i = max(0, i)
                previous_i = max(0, i-1)
                frame_filename = f"frame{adjusted_i}.jpg"
                frame_path = os.path.join(subfolder_path, frame_filename)
                if os.path.exists(frame_path):
                    relative_time = times[adjusted_i]-first_frame_time
                    relative_time_m1 = times[previous_i]-first_frame_time
                    relative_time_ms = int(relative_time.total_seconds() * 1000)  # Convert to milliseconds
                    relative_time_ms_m1 = int(relative_time_m1.total_seconds() * 1000)  # Convert to milliseconds

                    image_data.append({
                        "image_path": f"/images/{folder_number}/{subfolder}/{frame_filename}",
                        "time_in_ms": relative_time_ms,
                        "time_in_ms_m1": relative_time_ms_m1
                    })
                break  # Only add the first frame matching or exceeding the time
    # print(f"imge data {image_data}")
    return image_data


def run_web_app():
    app.run(host='0.0.0.0', port=80)


class Experiment:
    def __init__(self, n=0, dsc=0):
        self.discharge = dsc
        self.exp_number = n
        self.time_of_exp = datetime.datetime.now()
        self.charging = False
        self.armed = False
        trigger.triggered = False

def update_diagnostics(dsc=0, n=0):
    # here we need to define saving folders, files, check if the devices are ready
    # updating save folders
    before = datetime.datetime.now()

    current_folders.update_folders(dsc, n)
    current_experiment.exp_number = n
    current_experiment.discharge = dsc
    current_experiment.armed = True

    for scope in scopes:
        scope.reset()
        scope.status = 'Armed'

    for spectrometer in spectrometers:
        spectrometer.triggered = False

        spectrometer.setup_worker(current_experiment.discharge, current_experiment.exp_number, current_folders.spectrometer_folder)
        spectrometer.worker.start()
        print(f"Spectrometer worker started")

    for working_usb_cam_n in working_cameras:
        working_usb_cam_n.triggered = False
        working_usb_cam_n.setup_worker(current_folders)
        working_usb_cam_n.running_worker.start()
        print(f"Camera {working_usb_cam_n.path} started ")

    # for scope in scopes:
    #     # scope.runNumber = last_experiment.exp_number
    #     # scope.dsc = dsc
    #     print(f"arm diagnostics N={last_experiment.exp_number}")
    after = datetime.datetime.now()

    index_data.dsc = dsc
    index_data.n_exp = current_experiment.exp_number
    # print(f"EXP_NUMBER {index_data.n_exp}")
    index_data.system_status = 'Armed'

    print(f"Updating experiment took {(after - before).total_seconds()} s")
    return True


class Checker:
    def __init__(self, scope, spectrometer, experiment, trigger):
        self.active = False
        self.worker = threading.Thread()

        self.scope = scope
        self.spectrometer = spectrometer
        self.experiment = experiment
        self.trigger = trigger

        self.statuses = [0, 0, 0, 0, 1]

    def running_and_checking(self):
        if self.scope.connected:
            self.statuses[0] = 1
        else:
            self.statuses[0] = 0
        if self.spectrometer.connected:
            self.statuses[1] = 1
        else:
            self.statuses[1] = 0
        self.statuses[2] = self.experiment.exp_number

        if self.trigger.triggered:
            self.statuses[3] = 1
        else:
            self.statuses[3] = 0
        print(f"Statuses: {self.statuses}")
        time.sleep(3)


class IndexData:
    def __init__(self):
        self.dsc = 0
        self.exp_n = 1
        self.interf_file = ''
        self.int_status = 'Initiat'
        self.system_status = 'Started'


if __name__ == "__main__":

    print('Started program')
    index_data = IndexData()

    web_app_worker = threading.Thread(target=run_web_app, args=())
    web_app_worker.start()
    print('Web app started')
    #
    # camera_update_worker = threading.Thread(target=read_camera, args=())
    # camera_update_worker.start()
    #
    # The trigger object to indicate discharges
    trigger = Trigger()
    trigger.worker.start()

    # The object to have the proper file management
    current_folders = Folder()

    # The object to store the information about the current experiment
    current_experiment = Experiment()

    scope_DHO4204 = Oscilloscope()
    scopes = [scope_DHO4204]
    
    usb_spec2000 = USB_spectrometer(integ_time=53000, max_time=10)
    usb_specSR2 =  USB_spectrometer(integ_time=50000, serial="SR200584", max_time=10)


    # spectrometers = []
    # spectrometers = [usb_spec2000]
    # spectrometers = [usb_specSR2]
    spectrometers = [usb_spec2000, usb_specSR2]
    spectrometers = [usb_spec2000]

    for spectrometer in spectrometers:
        spectrometer.connect.start()

    # usb_spec2000.search_device_worker.start()

    # while True:
    #     time.sleep(5)
    #     print(5)
    time.sleep(1)
    for scope in scopes:
        scope.reset()

    # WUT?
    scope_columns = {'INT01': {'name': 'INT01 (V)', 'type': 'array'},
                     'INT02': {'name': 'INT02 (V)', 'type': 'array'},
                     'INT01_DRIVER': {'name': 'INT01 Driver (V)', 'type': 'array'},
                     'INT02_DRIVER': {'name': 'INT02 Driver (V)', 'type': 'array'},
                     'ACC01': {'name': 'ACC01 (V)', 'type': 'array'},
                     'ACC02': {'name': 'ACC02 (V)', 'type': 'array'}}
    #

    time.sleep(3)
    # working_cameras = []
    # update_diagnostics(dsc=0, n=1)
    # print(f"Current folder 1 interf={current_folders.interferometer_folder}")

    checker = Checker(scope_DHO4204, usb_spec2000, current_experiment, trigger)


    # checker.worker.start()

    # Now cameras
    time_before_cams = datetime.datetime.now()
    working_cameras = []
    using_cameras = True
    for camera in list_usb_cameras():
        # print(f"Name: {camera['name']}, Vendor: {camera['vendor']}, Serial: {camera['serial']}")
        # print(f"Bus: {camera['bus']}, Vendor ID: {camera['vendor_id']}, Model ID: {camera['model_id']}")
        # print(f"PATH: {camera['path']}, Openable: {camera['openable']}")
        if camera['openable'] and using_cameras:
            working_cameras.append(Camera(camera['path'], f"{camera['vendor_id']}:{camera['model_id']}"))

    for working_usb_cam in working_cameras:
        working_usb_cam.setup_size_format()
        time.sleep(0.1)
        working_usb_cam.setup_for_exp()

    time_after_cams = datetime.datetime.now()
    print(f"It took {(time_after_cams - time_before_cams).total_seconds()} s to initiate the cams")

    # here we arm the app to gather the data
    update_diagnostics(dsc=0, n=206)

    print(f"The app is fully ready!!!!!")
    while True:
        # if not current_experiment.armed and trigger.triggered:  # meaning the trigger happened while exp was not armed
        #     trigger.triggered = False
        # print(f"Triggered = {trigger.triggered}")
        now = datetime.datetime.now()
        if trigger.time_to_clear:
            for scope in scopes:
                scope.reset()
                scope.status = 'Reset'
            trigger.time_to_clear = False
        # print(f"Spectrometer status triggered = {usb_spec2000.triggered}")
        if trigger.triggered and current_experiment.armed:
            # First let everyone know that the trigger event happened
            for spectrometer in spectrometers:
                spectrometer.triggered = True
            checker.statuses[4] = 0

            for working_usb_cam in working_cameras:
                working_usb_cam.triggered = True
            # Now let's deal with the rest of this hell (oscilloscope)

            # print(f"Current folder 2 interf={current_folders.interferometer_folder}")
            # current_folders.update_folders()
            print(f"The app was triggered at {trigger.last_time_triggered.strftime('%Y%m%d-%H%M%S')}")
            # let's write the moment of the trigger to the experiment object
            current_experiment.time_of_exp = trigger.last_time_triggered
            # now it's time to save the data
            print("time to sleep and wait for the scope to record data")
            for scope in scopes:
                scope.status = 'Triggered'
            time.sleep(28)
            try:
                print(f"Time to read the scope")
                # scope_DHO4204.set_runNumber(last_experiment.exp_number)
                for scope in scopes:
                    scope.create_worker(scope_columns, current_folders, current_experiment)
                    scope.read_and_write_worker.start()
                # These results are listed in accordance with the 'columns' variable in constants.py
                # If the user would like to add or remove fields please make those changes in constant.py

            except Exception as e:
                print(f"Something went wrong with the scope during reading and writing: {e}")

            try:
                True
                # print("spectrometer hehe")
            except Exception as e:
                print(f"Something went wrong with the spectrometer during reading and writing: {e}")

            trigger.triggered = False
            current_experiment.armed = False
            print("Ready for a new shot")
        time.sleep(0.001)
