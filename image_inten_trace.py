from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime


def get_total_signal(image_path):
    """Calculate the total signal (sum of pixel values) of an image."""
    with Image.open(image_path) as img:
        img_array = np.array(img)
        # Convert to grayscale if necessary
        if len(img_array.shape) == 3:  # RGB image
            img_array = np.mean(img_array, axis=2)  # Convert to grayscale
        return np.sum(img_array)


def read_timestamps(timestamp_file):
    """Read timestamps from a file and return a list of datetime objects."""
    timestamps = []
    with open(timestamp_file, 'r') as f:
        for line in f:
            timestamp = datetime.strptime(line.strip(), '%Y-%m-%d %H:%M:%S.%f')
            timestamps.append(timestamp)
    return timestamps


def plot_signal_vs_time(image_folder, timestamp_file):
    """Plot the total signal of images as a function of time after the second frame."""
    frame_numbers = []
    total_signals = []
    timestamps = read_timestamps(timestamp_file)

    # Ensure there are at least 2 timestamps
    if len(timestamps) < 2:
        raise ValueError("There should be at least two timestamps in the file.")

    # Get the reference timestamp (second frame's timestamp)
    reference_time = timestamps[1]

    # List all files in the directory and process them
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith(".jpg"):
            frame_number = int(filename.replace("frame", "").replace(".jpg", ""))
            frame_path = os.path.join(image_folder, filename)

            total_signal = get_total_signal(frame_path)
            frame_numbers.append(frame_number)
            total_signals.append(total_signal)

            # Compute the time difference from the reference time
            frame_time = timestamps[frame_number]
            time_diff = (frame_time - reference_time).total_seconds() * 1000  # Convert to milliseconds

            # Update the frame number with the time difference
            frame_numbers[-1] = time_diff

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(frame_numbers, total_signals, marker='o')
    plt.xlabel('Time (ms) After Second Frame')
    plt.ylabel('Total Signal')
    plt.title('Total Signal vs Time After Second Frame')
    plt.grid(True)
    plt.show()


# Example usage
image_folder = '/CMFX_RAW/video/CMFX_01370/video0'
timestamp_file = '/CMFX_RAW/video/CMFX_01370/video0.txt'
plot_signal_vs_time(image_folder, timestamp_file)

# Example usage
# image_folder = '/CMFX_RAW/video/CMFX_01340/video6'
# plot_signal_vs_frame(image_folder)
