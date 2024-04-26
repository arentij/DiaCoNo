from flask import Flask, render_template, request, jsonify
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


@app.route("/")
def index():
    return render_template('index.html')



@app.route('/arm_diagnostics')
def arm_diagnostics():
    N_exp = request.args.get("n", 0, type=int)
    discharging = request.args.get("dsc", 0, type=float)
    disc_duration = request.args.get("dt", 0, type=float)
    now = datetime.datetime.now()

    update_diagnostics(discharging, N_exp)

    return jsonify(time=now, n=N_exp, dsc=discharging, duration=disc_duration)



# @app.route('/status')
# def status():
#     return jsonify(scope=checker.statuses[0], spectr=checker.statuses[1], N_exp=checker.statuses[2], trigger=checker.statuses[3], wrote=checker.statuses[4])

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

    scope_DHO4204.reset()

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


if __name__ == "__main__":

    print('Started program')
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

    usb_spec2000 = USB_spectrometer(integ_time=3000, max_time=0.5)
    spectrometers = [usb_spec2000]
    usb_spec2000.connect.start()

    # usb_spec2000.search_device_worker.start()

    # while True:
    #     time.sleep(5)
    #     print(5)
    time.sleep(1)
    scope_DHO4204.reset()

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
    for camera in list_usb_cameras():
        # print(f"Name: {camera['name']}, Vendor: {camera['vendor']}, Serial: {camera['serial']}")
        # print(f"Bus: {camera['bus']}, Vendor ID: {camera['vendor_id']}, Model ID: {camera['model_id']}")
        # print(f"PATH: {camera['path']}, Openable: {camera['openable']}")
        if camera['openable']:
            working_cameras.append(Camera(camera['path'], f"{camera['vendor_id']}:{camera['model_id']}"))

    for working_usb_cam in working_cameras:
        working_usb_cam.setup_size_format()
        time.sleep(0.1)
        working_usb_cam.setup_for_exp()

    time_after_cams = datetime.datetime.now()
    print(f"It took {(time_after_cams - time_before_cams).total_seconds()} s to initiate the cams")

    # here we arm the app to gather the data
    update_diagnostics(dsc=1, n=15)

    print(f"The app is fully ready!!!!!")
    while True:
        # if not current_experiment.armed and trigger.triggered:  # meaning the trigger happened while exp was not armed
        #     trigger.triggered = False
        # print(f"Triggered = {trigger.triggered}")
        now = datetime.datetime.now()
        if trigger.time_to_clear:
            scope_DHO4204.reset()
            trigger.time_to_clear = False
        # print(f"Spectrometer status triggered = {usb_spec2000.triggered}")
        if trigger.triggered and current_experiment.armed:
            # First let everyone know that the trigger event happened
            usb_spec2000.triggered = True
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
            time.sleep(28)
            try:
                print(f"Time to read the scope")
                # scope_DHO4204.set_runNumber(last_experiment.exp_number)
                scope_DHO4204.create_worker(scope_columns, current_folders, current_experiment)
                scope_DHO4204.read_and_write_worker.start()
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
        time.sleep(0.001)
