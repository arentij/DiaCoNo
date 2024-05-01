import seabreeze
seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb

# import seabreeze.spectrometers as sb

# https://github.com/ap--/python-seabreeze

devices = sb.list_devices()
print(devices)

spec = sb.Spectrometer(devices[1])
print(spec)


print(spec.pixels)
print(spec.integration_time_micros_limits)
print(spec.features)
