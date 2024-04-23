import subprocess

def set_resolution_and_pixelformat(device, resolution, pixelformat):
    command = ["v4l2-ctl", "-d", device, "--set-fmt-video", f"width={resolution[0]},height={resolution[1]},pixelformat={pixelformat}"]
    try:
        print(*command)
        subprocess.run(command, check=True)
        print("Resolution and pixel format set successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting resolution and pixel format: {e}")

# Example usage:
device = '/dev/video8'
resolution = (1280, 720)  # Set your desired resolution here
pixelformat = 'MJPG'      # Set your desired pixel format here

set_resolution_and_pixelformat(device, resolution, pixelformat)