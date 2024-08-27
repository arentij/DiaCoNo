import cv2
import serial
import os
from datetime import datetime
import time

# Configure serial port and camera
serial_port = '/dev/ttyUSB0'  # Change to your serial port
baud_rate = 9600
camera_index = 2
frame_folder = 'images'

# Create folder if it doesn't exist
if not os.path.exists(frame_folder):
    os.makedirs(frame_folder)

def initialize_camera(index):
    """Initialize the camera and return the VideoCapture object."""
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Camera at index {index} not available.")
    return cap

def save_frame(frame):
    """Save the captured frame to a file with a unique name."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = os.path.join(frame_folder, f'frame_{timestamp}.jpg')
    cv2.imwrite(filename, frame)
    print(f'Saved frame as {filename}')


# Initialize serial and camera
ser = serial.Serial(serial_port, baud_rate, timeout=1)
cap = initialize_camera(camera_index)

while True:
    # Check if the camera is still available
    if not cap.isOpened():
        print("Reinitializing camera...")
        cap = initialize_camera(camera_index)
        time.sleep(2)  # Wait before retrying

    # Capture video frame
    ret, frame = cap.read()
    if not ret:
        print('Failed to capture image')
        cap.release()
        cap = initialize_camera(camera_index)
        time.sleep(2)  # Wait before retrying
        continue

    # Display the video feed
    cv2.imshow('Live Stream', frame)

    # Check for serial input
    if ser.in_waiting > 0:
        command = ser.readline().decode().strip()
        if command == 'F':
            save_frame(frame)

    # Exit condition (press 'q' to quit)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
ser.close()
cv2.destroyAllWindows()
