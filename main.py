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

import numpy
from seabreeze.spectrometers import Spectrometer, list_devices

app = Flask(__name__, static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/")
def index():
    return render_template('index.html')

def run_web_app():
    app.run(host='0.0.0.0', port=80)


class Experiment:
    def __init__(self, n=0, dsc=0):
        self.discharge = dsc
        self.exp_number = n



if __name__ == "__main__":
    print('Started program')
    web_app_worker = threading.Thread(target=run_web_app, args=())
    # web_app_worker.start()
    print('Web app started')
    #
    # camera_update_worker = threading.Thread(target=read_camera, args=())
    # camera_update_worker.start()
    #
    trigger = Trigger()
    trigger.worker.start()

    last_experiment = Experiment()

    scope_DHO4204 = Oscilloscope()
    time.sleep(2)
    scope_DHO4204.reset()

    # WUT?
    scope_columns = {'INT01': {'name': 'INT01 (V)', 'type': 'array'},
                     'INT02': {'name': 'INT02 (V)', 'type': 'array'},
                     'INT01_DRIVER': {'name': 'INT01 Driver (V)', 'type': 'array'},
                     'INT02_DRIVER': {'name': 'INT02 Driver (V)', 'type': 'array'},
                     'ACC01': {'name': 'ACC01 (V)', 'type': 'array'},
                     'ACC02': {'name': 'ACC02 (V)', 'type': 'array'}}
    #

    while True:
        now = datetime.datetime.now()
        if trigger.time_to_clear:
            scope_DHO4204.reset()
            trigger.time_to_clear = False

        if trigger.triggered:
            print(f"The trigger was triggered at {trigger.last_time_triggered.strftime('%Y%m%d-%H%M%S')}")
            # now it's time to save the data
            time.sleep(2)
            # scope_DHO4204.read_scope()
            scope_DHO4204.set_runNumber(last_experiment.exp_number)
            scope_DHO4204.create_worker()
            scope_DHO4204.read_and_write_worker.start()

            # results = [getattr(scope_DHO4204, variable) for variable in scope_columns if hasattr(scope_DHO4204, variable)]

            trigger.triggered = False

        time.sleep(0.001)
