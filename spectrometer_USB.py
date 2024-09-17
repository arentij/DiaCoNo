import datetime
import threading
import time
import os

import seabreeze
import usb.core

seabreeze.use('pyseabreeze')
from seabreeze.spectrometers import Spectrometer, list_devices

# from seabreeze.spectrometers import Spectrometer, list_devices

import matplotlib.pyplot as plt
import pandas as pd
import numpy

class USB_spectrometer:
    def __init__(self, integ_time=3000, max_time=1, dsc=0, n=0, save_folder="/CMFX_RAW/tests/spectrometer/", serial="USB2G410"):
        self.running = False
        self.connected = False
        self.triggered = False
        self.max_time = max_time

        self.serial = serial # old "USB2G410", new "SR200584"
        self.dsc = dsc
        self.N_exp = n
        self.save_folder = save_folder

        self.index = 0
        self.created = datetime.datetime.now()
        self.accessed = datetime.datetime.now()

        # self.spect = []
        self.time_created = datetime.datetime.now()

        self.devices = []
        self.devices_found = False

        before = datetime.datetime.now()
        self.search_device_worker = threading.Thread(target=self.search_device, args=())
        after = datetime.datetime.now()
        # print(f"Time to create device worker {(after-before).total_seconds()}")
        self.integration_time = integ_time

        self.worker = threading.Thread()

        self.waves = []
        self.spectra = []
        self.times = []

        self.connect = threading.Thread(target=self.connecting, args=())

    def search_device(self):
        print("Launching Spectrometer Device search")
        try:
            self.devices = list_devices()
            self.devices_found = True
            print(f"Found {self.devices}")
        except Exception as e:
            print("couldn't find any device")
            self.devices_found = False
        print("Spectrometer search_device successful")
        return True

    def connecting(self):
        print(f"Attempting connecting to the spectrometer {self.serial}")
        if True:

            try:
                self.spect = Spectrometer.from_serial_number(self.serial)
                # self.spect = Spectrometer.from_serial_number("SR200584")
                self.time_connected = datetime.datetime.now()
                self.spect.integration_time_micros(self.integration_time)

                self.times = datetime.datetime.now()
                self.waves = self.spect.wavelengths()
                self.inten = self.spect.intensities()

                self.connected = True
                print("Spectrometer connected")
                # print(self.waves)
                # print(self.inten)
                # # plt.plot(self.waves, self.inten)
                # plt.show()

            except Exception as e:
                print(f"Could not connect to the spectrometer {self.serial} due to: {e}")
                self.connected = False

                time.sleep(0.1)
        else:
            while not self.devices_found:
                print("Still no devices found")
                # if not self.search_device_worker.is_alive():
                #     try:
                #         self.search_device_worker.start()
                #     except RuntimeError as e:
                #         print(f"Couldn't start the USB spectrometer worker due to {e}")
                time.sleep(1)

            if self.devices_found:
                try:
                    self.spect = Spectrometer(self.devices[self.index])
                    self.time_connected = datetime.datetime.now()
                    self.spect.integration_time_micros(self.integration_time)

                    self.times = datetime.datetime.now()
                    self.waves = self.spect.wavelengths()
                    self.inten = self.spect.intensities()


                    self.connected = True
                    print("Spectrometer connected")
                    # print(self.waves)
                    # print(self.inten)
                    # # plt.plot(self.waves, self.inten)
                    # plt.show()

                except Exception as e:
                    print(f"Could not connect to the spectrometer due to: {e}")
                    self.connected = False

                    time.sleep(0.1)

    # def recording_spectra(self):
    #     while not self.connected:
    #         self.connect()

    def running_reading_writing(self):
        if not self.connected:
            self.connecting()
        print(f"Spectrometer {self.serial} is running and reading")
        time_started_running = datetime.datetime.now()
        time.sleep(0.5)
        try:
            inten_when_started_running = self.spect.intensities()
        except usb.core.USBTimeoutError as e:
            inten_when_started_running = []
            print(f"something went wrong with the spectrometer {self.serial}: {e}")

        self.times_exp = [time_started_running]
        self.times_exp.append(datetime.datetime.now())
        self.inten_exp = [inten_when_started_running]
        self.inten_exp.append(self.spect.intensities())

        while not self.triggered:
            try:
                self.inten_exp = [inten_when_started_running]
                self.inten_exp.append(self.spect.intensities())
                self.times_exp = [time_started_running]
                self.times_exp.append(datetime.datetime.now())
            except Exception as e:
                print(f"something went wrong with the spectrometer ")
        # print(len(self.inten_exp))
        self.time_triggered = datetime.datetime.now()
        while (datetime.datetime.now() - self.time_triggered).total_seconds() < self.max_time:
            # print(f"Times: {(datetime.datetime.now() - self.time_triggered).total_seconds()}")
            # self.times_exp.append(datetime.datetime.now())  # before sep 17 2024 this line was functioning hence it was saving the time BEFORE the spectra was taken for every measurement except the first two ones
            # before_getting_inten = datetime.datetime.now()
            self.inten_exp.append(self.spect.intensities())
            self.times_exp.append(datetime.datetime.now()) # after sep 17 2024 this line was used to indicate the END of the spectra measurement
            # after_getting_inten = datetime.datetime.now()
            # print(f"Reading spectra lasted {(after_getting_inten-before_getting_inten).total_seconds()*1000} ms")
        print(f"Read {self.max_time} s of spectras, time to write")
        self.triggered = False
        self.save_csv()
        return True

    def save_csv(self):
    #     we need to save the waves, the intensities, times, and integration time

        df = pd.DataFrame(numpy.vstack([self.waves, self.inten_exp]))
        dt = pd.DataFrame(numpy.hstack([self.integration_time, self.times_exp]))
        # df = pd.DataFrame(numpy.hstack([dt, df]))
        # df = pd.DataFrame({"Times": dt, "Spectra": df})
        # print(f"Len times {len(dt)}")
        # print(f"Len  df {len(df)}")

        dt.to_csv(f'{self.save_folder}CMFX_{self.N_exp:05d}_spectrometer{self.serial}_times.csv', index=False)
        df.to_csv(f'{self.save_folder}CMFX_{self.N_exp:05d}_spectrometer{self.serial}.csv', index=False)
        print(f"saved the spectrometer {self.serial} files")
        self.triggered = False
    # def running_new_exp(self, current_folders):

    def setup_worker(self, dsc=0, n=0, save_folder="/CMFX_RAW/tests/spectrometer/"):

        self.dsc = dsc
        self.N_exp = n
        self.save_folder = save_folder
        self.triggered = False
        self.worker = threading.Thread(target=self.running_reading_writing, args=())
        return True


if __name__ == "__main__":
    # print("Started")
    USB2k_spec = USB_spectrometer(integ_time=2000, serial="SR200584")
    print("Created the object")

    before = datetime.datetime.now()
    USB2k_spec.connect.start()
    after = datetime.datetime.now()
    print(f"Starting device connect {(after - before).total_seconds()} s")

    # before = datetime.datetime.now()
    # USB2k_spec.search_device_worker.start()
    # after = datetime.datetime.now()
    # print(f"Starting device worker takes {(after - before).total_seconds()} s")
    # print("Started device worker")




    print(f"Started connecting!!!!!!")

    time.sleep(0.1)
    print("Waiting for the trigger")
    while not USB2k_spec.connected:
        time.sleep(1)
    time.sleep(1)

    USB2k_spec.setup_worker(0, 0)
    USB2k_spec.worker.start()

    time.sleep(4)
    print("Triggering!")
    USB2k_spec.triggered = True

    while True:
        time.sleep(1)





# def recording_spectrometer(N_exp):
#     saveFolder = '/CMFX/INT'
#     # print('Connecting to the spectrometer')
#     spectrometer_filename_csv = f'CMFX_{N_exp:05d}_spectrometer.csv'
#     spectrometer_log_filename_csv = f'CMFX_{N_exp:05d}_spectrometer_log.csv'
#     now = datetime.datetime.now()
#     runDate = now.date().strftime('%Y_%m_%d')
#     # Create a folder for today's date if it doesn't already exist
#     # print('Making folder')
#     if runDate not in os.listdir(saveFolder):
#         os.mkdir(f'{saveFolder}/{runDate}')
#     time.sleep(1)
#     print('Looking for the spectrometer')
#     devices = list_devices()
#     start_read = datetime.datetime.now()
#     print(devices)
#     spect = Spectrometer(devices[0])
#     print('Found the spectrometer')
#     integration_time = 3000 # ms
#     spect.integration_time_micros(integration_time)
#     print('integration time ')
#     print(integration_time)
#
#     start_making_array = datetime.datetime.now()
#     reading_times = []
#
#     print('Starting reading spectra')
#     while not trigger.triggered:
#         # print(trigger.triggered)
#         trigger.running = True
#         start_making_array = datetime.datetime.now()
#         waves = spect.wavelengths()
#         inten = spect.intensities()
#         # print(trigger.triggered)
#
#
#     print('The spectrometer received the trigger')
#     while True:
#         aq_time = datetime.datetime.now()
#         if (aq_time - start_making_array).total_seconds() > 0.5:
#             trigger.triggered = False
#             trigger.running   = False
#             break
#         reading_times.append((aq_time - start_making_array).total_seconds()*1000)
#         inten = numpy.vstack([inten, spect.intensities()])
#         # print('I Read another spectra')
#     # now let's write the files
#     print('writing spectra files')
#     df = pd.DataFrame(numpy.vstack([waves, inten]))
#     df.to_csv(f'{saveFolder}/{runDate}/{spectrometer_filename_csv}')
#     print('saved spectra to')
#     print(f'{saveFolder}/{runDate}/{spectrometer_filename_csv}')
#     with open(f'{saveFolder}/{runDate}/{spectrometer_log_filename_csv}', 'w') as log_file:
#         log_file.write(aq_time.strftime('%H:%M:%S.%f') + '\n')
#         for num in reading_times:
#             log_file.write(str(num) + '\n')
#
#
#     trigger.running = False
#     trigger.triggered= False
#     spect.close()
#     return True
