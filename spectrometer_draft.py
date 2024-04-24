import numpy
from seabreeze.spectrometers import Spectrometer, list_devices
import matplotlib.pyplot as plt
from datetime import datetime
print('SpectrometerInitiated')
start_read = datetime.now()
# devices = list_devices()
# print(*devices)
# spect = Spectrometer.from_first_available()
# spect = Spectrometer(devices[0])


spect = Spectrometer.from_serial_number("USB2G410")
# spect.is_open
print('Found the spectrometer')

after_read = datetime.now()
time_to_read = (after_read - start_read).total_seconds()
print(f"Time to open: {time_to_read}")
# print(f'Serial number: {spect.serial_number}')
print(f"Features {spect.features}")
spect.integration_time_micros(3000)

print(spect.pixels)
print(spect.integration_time_micros_limits)


for i_aquisition in range(4):
    waves = spect.wavelengths()

    start_mkaing_array = datetime.now()
    if i_aquisition == 0:
        inten = spect.intensities()
    else:
        inten = numpy.vstack([inten ,spect.intensities()])
    print((datetime.now()-start_mkaing_array).total_seconds())
    if i_aquisition >0:
        plt.plot(waves, inten[i_aquisition])
        plt.show()
# for i in range(10):

spect.close()


