import datetime
import threading
import time
import os
from seabreeze.spectrometers import Spectrometer, list_devices


class USB_spectrometer:
    def __init__(self, integ_time, max_time=0.5):
        self.running = False
        self.connected = False

        self.created = datetime.datetime.now()
        self.accessed = datetime.datetime.now()

        self.spect = Spectrometer()


        self.worker = threading.Thread()

    def connect(self):
        try:
            devices = list_devices()
            self.spect = Spectrometer(devices[0])
            self.connected = True
        except Exception as e:
            print(f"Could not connect to the spectrometer due to: {e}")
            self.connected = False

    def recording_spectra(self):
        while not self.connected:
            self.connect()

def recording_spectrometer(N_exp):
    saveFolder = '/CMFX/INT'
    # print('Connecting to the spectrometer')
    spectrometer_filename_csv = f'CMFX_{N_exp:05d}_spectrometer.csv'
    spectrometer_log_filename_csv = f'CMFX_{N_exp:05d}_spectrometer_log.csv'
    now = datetime.datetime.now()
    runDate = now.date().strftime('%Y_%m_%d')
    # Create a folder for today's date if it doesn't already exist
    # print('Making folder')
    if runDate not in os.listdir(saveFolder):
        os.mkdir(f'{saveFolder}/{runDate}')
    time.sleep(1)
    print('Looking for the spectrometer')
    devices = list_devices()
    start_read = datetime.datetime.now()
    print(devices)
    spect = Spectrometer(devices[0])
    print('Found the spectrometer')
    integration_time = 3000 # ms
    spect.integration_time_micros(integration_time)
    print('integration time ')
    print(integration_time)

    start_making_array = datetime.datetime.now()
    reading_times = []

    print('Starting reading spectra')
    while not trigger.triggered:
        # print(trigger.triggered)
        trigger.running = True
        start_making_array = datetime.datetime.now()
        waves = spect.wavelengths()
        inten = spect.intensities()
        # print(trigger.triggered)

    print('The spectrometer received the trigger')
    while True:
        aq_time = datetime.datetime.now()
        if (aq_time - start_making_array).total_seconds() > 0.5:
            trigger.triggered = False
            trigger.running   = False
            break
        reading_times.append((aq_time - start_making_array).total_seconds()*1000)
        inten = numpy.vstack([inten, spect.intensities()])
        # print('I Read another spectra')
    # now let's write the files
    print('writing spectra files')
    df = pd.DataFrame(numpy.vstack([waves, inten]))
    df.to_csv(f'{saveFolder}/{runDate}/{spectrometer_filename_csv}')
    print('saved spectra to')
    print(f'{saveFolder}/{runDate}/{spectrometer_filename_csv}')
    with open(f'{saveFolder}/{runDate}/{spectrometer_log_filename_csv}', 'w') as log_file:
        log_file.write(aq_time.strftime('%H:%M:%S.%f') + '\n')
        for num in reading_times:
            log_file.write(str(num) + '\n')


    trigger.running = False
    trigger.triggered= False
    spect.close()
    return True