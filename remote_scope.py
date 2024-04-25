import time

import pyvisa
import numpy as np
from tqdm import tqdm
import threading
from folder_manager import *
# from main import checker
class Oscilloscope:
    def __init__(self, channels={'INT01': '1', 'INT01_DRIVER': '2', 'INT02': '3', 'INT02_DRIVER': '4'}, nPoints=None, memoryDepth='1M', auto_reset=False, reaching_point='TCPIP::169.254.146.112::INSTR'):
        self.channels = channels
        self.nPoints = nPoints
        self.memoryDepth = memoryDepth
        self.data = {}
        self.connected = False
        self.busy = False

        # self.dsc = 0
        # self.runNumber = 0

        self.rm = pyvisa.ResourceManager('@py')
        self.address = reaching_point
        print('Connecting to the scope')
        self.connectInstrument()

        self.read_and_write_worker = threading.Thread()


        if auto_reset:
            self.reset()
            # self.busy = False
        if self.connected:
            print('Oscilloscope has been initialized successfully.')

    def connectInstrument(self):
        # USB connection, COM port is static
        # instrumentName = self.findIPAddress()
        try:
            self.inst = self.rm.open_resource(self.address, timeout=1000, chunk_size=100000, encoding='latin-1')
            # self.inst = self.rm.open_resource('TCPIP::192.168.1.2::INSTR') # bigger timeout for long mem
            self.connected = True
        except Exception as e:
            print("Couldn't connect to the scope")
            self.connected = False
            time.sleep(1)
            return False
        return True
    def findIPAddress(self):
        resources = self.rm.list_resources()
        breakpoint()
        return resources[0]

    # stop reading data
    def reset(self):
        if self.connected:
        # Reset the internal memory depth
        # if self.co
            try:
                self.inst.write(':RUN')
                # self.inst.write(f'ACQ:MDEP {self.memoryDepth}')
                # self.inst.write(f'ACQ:MDEP AUTO')

                self.inst.write(':CLE') # clear all waveforms from screen
                self.inst.write(':STOP') # stop running scope
                self.inst.write(':SING') # setup for single trigger event

                self.readSuccess = False
            except pyvisa.errors.VisaIOError as e:
                print(f"Couldn't reset the scope due to: {e}")
                time.sleep(0.2)

            self.busy = False
    # def set_runNumber(self, runNumber):
    #     self.runNumber = runNumber

    def read_scope(self):
        if self.connected:
            while self.busy:
                time.sleep(0.1)
                print("the scope is still busy")
            else:
                for channel_name in self.channels:
                    self.get_data(channel_name)
                if self.readSuccess:
                    self.get_time()
                self.busy = False
            return True
        else:
            return False
    def get_data(self, channel_name):
        channel = self.channels[channel_name]
        try:
            # Wait for all pending operations to complete
            self.inst.write('*WAI')

            # check if channel is on
            active = bool(self.inst.query(f':CHAN{channel}:DISP?').strip())

            # Setup scope to read
            self.inst.write(f':WAV:SOUR CHAN{channel}')
            self.inst.write(':WAV:MODE RAW')
            self.inst.write(':WAV:FORM BYTE')

            ### Read data in packets ###
            start = 1 # starting index
            stop = int(float(self.inst.query(':ACQ:MDEP?').strip())) # stopping index is length of internal memory
            loopcount = 1 # initialize the loopcount
            startNum = start # initialize the start of the packet
            packetLength = 100000 # number of samples per packet

            # Determine the number of packets to grab
            if stop - start > packetLength:
                stopnum = start + packetLength - 1
                loopcount = int(np.ceil((stop - start + 1) / packetLength))
            else:
                stopnum = stop

            # Initialize the start and stop position for the first read
            self.inst.write(f':WAV:START {startNum}')
            self.inst.write(f':WAV:STOP {stopnum}')

            # Initialize array to hold read data
            values = np.zeros(stop)
            print(f'Loading data packets from scope channel: {channel_name}')
            if active:
                # loop through all the packets
                for i in tqdm(range(0, loopcount)):
                    values[i * packetLength:(i + 1) * packetLength] = self.inst.query_binary_values(':WAV:DATA?', datatype='B')
                    # set the next loop to jump a packet length
                    if i < loopcount - 2:
                        startnum = stopnum + 1
                        stopnum = stopnum + packetLength
                    # start and stop positions for last loop if packet is not a full size
                    else:
                        startnum = stopnum + 1
                        stopnum = stop
                    self.inst.write(f':WAV:START {startnum}')
                    self.inst.write(f':WAV:STOP {stopnum}')

            # Convert from binary to actual voltages
            wav_pre_str = self.inst.query(':WAV:PRE?')
            wav_pre_list = wav_pre_str.split(',')
            self.get_parameters(wav_pre_list)

            dataarray = (values - self.yref - self.yorigin) * self.yinc
            self.lenMax = len(dataarray)

            self.data[channel_name] = dataarray

            self.readSuccess = True

        except Exception as e:
            print('Exception')
            print(e)
            self.data[channel_name] = np.array([]) # return empty array

        setattr(self, channel_name, self.data[channel_name])

        self.data_size = len(self.data[channel_name])

    def get_parameters(self, wav_pre_list):
        self.format = int(wav_pre_list[0])
        if self.format == 0:
            self.format = 'BYTE'
        elif self.format == 1:
            self.format = 'WORD'
        elif self.format == 2:
            self.format = 'ASC'

        self.type = int(wav_pre_list[1])
        if self.type == 0:
            self.type = 'NORM'
        elif self.type == 1:
            self.type = 'MAX'
        elif self.type == 2:
            self.type = 'RAW'

        self.points = int(wav_pre_list[2])
        self.count = int(wav_pre_list[3])
        self.xinc = float(wav_pre_list[4])
        self.xorigin = float(wav_pre_list[5])
        self.xref = float(wav_pre_list[6])
        self.yinc = float(wav_pre_list[7])
        self.yorigin = float(wav_pre_list[8])
        self.yref = float(wav_pre_list[9])

    def get_time(self):
        # Generate time axis based off parameters
        if self.readSuccess:
            self.time = np.linspace(self.xorigin, self.xorigin + (self.lenMax - 1) * self.xinc, self.data_size)
        else:
            self.time = np.array([])

        try:
            # See if we should use a different time axis
            if (max(np.abs(self.time)) < 1e-3):
                self.time = self.time * 1e6
                self.tUnit = 'us'
            elif (max(np.abs(self.time)) < 1):
                self.time = self.time * 1e3
                self.tUnit = 'ms'
            else:
                self.tUnit = 's'
        except:
            self.tUnit = 's'

        return (self.time, self.tUnit)

    def read_data_and_write_file(self, n, scope_columns, current_folders):
        if self.connected:
            print('Attempting reading data and writing the osc file')
            print(f"N={n}")
            self.read_scope()

            try:
                results = [getattr(self, variable) for variable in scope_columns if
                           hasattr(self, variable)]

                # Creates a data frame which is easier to save to csv formats
                results_df = pd.concat([pd.Series(val) for val in results], axis=1)
                results_df.columns = [scope_columns[variable]['name'] for variable in scope_columns if
                                      hasattr(self, variable)]
                # results_df.to_parquet(f'{saveFolder}/{runDate}/{scope_filename}', index=False)

                # results = [getattr(self, variable) for variable in scope_columns if hasattr(self, variable)]
                scope_filename = f"{current_folders.interferometer_folder}CMFX_{n:05d}_scope.parquet"
                # print(scope_filename)
                save_results_to_parquet(results_df, scope_filename)
                # checker.statuses[4] = 1
            except Exception as e:
                print(e)

            print(self.address)

            return True
        else:
            return False

    def create_worker(self, scope_columns, current_folders, current_experiment):
        self.read_and_write_worker = threading.Thread(target=self.read_data_and_write_file, args=(current_experiment.exp_number, scope_columns, current_folders))


if __name__ == "__main__":
    # This code will only be executed
    # if the script is run as the main program

    scope = Oscilloscope(reaching_point='TCPIP::169.254.146.112::INSTR')
    # scope.reset()
    print('Hello World')
