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

import numpy
from seabreeze.spectrometers import Spectrometer, list_devices
from setting_loggers import *

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



def run_web_app():
    app.run(host='0.0.0.0', port=80)


class Experiment:
    def __init__(self, n=0, dsc=0):
        self.discharge = dsc
        self.exp_number = n
        self.time_of_exp = datetime.datetime.now()
        self.charging = False


def update_diagnostics(dsc=0, n=0):
    # here we need to define saving folders, files, check if the devices are ready
    # updating save folders
    current_folders.update_folders(dsc, n)
    current_experiment.exp_number = n
    current_experiment.discharge = dsc
    # for scope in scopes:
    #     # scope.runNumber = last_experiment.exp_number
    #     # scope.dsc = dsc
    #     print(f"arm diagnostics N={last_experiment.exp_number}")
    return True


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

    update_diagnostics(dsc=0, n=0)
    # print(f"Current folder 1 interf={current_folders.interferometer_folder}")

    while True:
        now = datetime.datetime.now()
        if trigger.time_to_clear:
            scope_DHO4204.reset()
            trigger.time_to_clear = False

        if trigger.triggered:
            # print(f"Current folder 2 interf={current_folders.interferometer_folder}")
            # current_folders.update_folders()
            print(f"The scope was triggered at {trigger.last_time_triggered.strftime('%Y%m%d-%H%M%S')}")
            # let's write the moment of the trigger to the experiment object
            current_experiment.time_of_exp = trigger.last_time_triggered
            # now it's time to save the data
            print("time to sleep and wait for the scope to record data")
            time.sleep(2)
            try:
                # scope_DHO4204.set_runNumber(last_experiment.exp_number)
                scope_DHO4204.create_worker(scope_columns, current_folders, current_experiment)
                scope_DHO4204.read_and_write_worker.start()

                # These results are listed in accordance with the 'columns' variable in constants.py
                # If the user would like to add or remove fields please make those changes in constant.py

                trigger.triggered = False
            except Exception as e:
                print(f"Something went wrong with the scope during reading and writing: {e}")



        time.sleep(0.001)
