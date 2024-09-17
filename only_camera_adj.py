from flask import Flask, render_template, request, redirect, url_for
import subprocess
import re

app = Flask(__name__)


# Helper function to get list of video devices
def get_video_devices():
    devices = []
    for i in range(10):  # Adjust range if needed
        device = f'/dev/video{i}'
        try:
            # Check if the device exists and is a video device
            subprocess.check_output(['v4l2-ctl', '-d', device, '--all'], stderr=subprocess.STDOUT)
            devices.append(device)
        except subprocess.CalledProcessError:
            pass
    return devices


# Helper function to get camera parameters
def get_camera_parameters(device):
    try:
        output = subprocess.check_output(['v4l2-ctl', '-d', device, '--all'], text=True)
        return output
    except subprocess.CalledProcessError:
        return "Error retrieving parameters"


# Helper function to set exposure time
def set_exposure_time(device, value):
    try:
        subprocess.check_output(['v4l2-ctl', '-d', device, '--set-ctrl=exposure_time_absolute=' + str(value)])
        return True
    except subprocess.CalledProcessError:
        return False


@app.route('/')
def index():
    devices = get_video_devices()
    return render_template('index.html', devices=devices)


@app.route('/camera', methods=['GET', 'POST'])
def camera():
    device = request.args.get('device')
    print(f"Device {device}")
    if request.method == 'POST':
        exposure_time = request.form.get('exposure_time')
        if exposure_time and device:
            success = set_exposure_time(device, exposure_time)
            if not success:
                return redirect(url_for('camera', device=device, error='Failed to set exposure time'))
        return redirect(url_for('camera', device=device))

    parameters = get_camera_parameters(device)
    return render_template('camera.html', device=device, parameters=parameters)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
