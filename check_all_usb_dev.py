import pyudev

def list_usb_devices():
    context = pyudev.Context()
    for device in context.list_devices(subsystem='usb'):
        device_info = {}
        device_info['name'] = device.get('ID_MODEL')
        device_info['vendor_id'] = device.get('ID_VENDOR_ID')
        device_info['serial_number'] = device.get('ID_SERIAL_SHORT')
        device_info['model_id'] = device.get('ID_MODEL_ID')
        device_info['mount_point'] = device.device_node
        yield device_info

# List USB devices and print their attributes
for usb_device in list_usb_devices():
    print("Name:", usb_device.get('name'))
    print("Vendor ID:", usb_device.get('vendor_id'))
    print("Serial Number:", usb_device.get('serial_number'))
    print("Model ID:", usb_device.get('model_id'))
    print("Mounting Point:", usb_device.get('mount_point'))
    print()
