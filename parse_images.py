import os
import time
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime
import re

RAW_DIR = '/CMFX_RAW/video'
PROCESSED_DIR = '/CMFX/video'


def get_total_signal(image_path):
    """Calculate the total signal (sum of pixel values) of an image."""
    with Image.open(image_path) as img:
        img_array = np.array(img)
        if len(img_array.shape) == 3:  # RGB image
            img_array = np.mean(img_array, axis=2)  # Convert to grayscale
        return np.mean(img_array)


def read_timestamps(timestamp_file):
    """Read timestamps from a file and return a list of datetime objects."""
    timestamps = []
    with open(timestamp_file, 'r') as f:
        for line in f:
            try:
                timestamp = datetime.strptime(line.strip(), '%Y-%m-%d %H:%M:%S.%f')
                timestamps.append(timestamp)
            except ValueError:
                try:
                    format_string = '%Y-%m-%d %H:%M:%S'
                    timestamp = datetime.strptime(line.strip(), format_string)
                    timestamps.append(timestamp)
                except ValueError:
                    continue
    return timestamps


def extract_frame_number(filename):
    """Extract the frame number from a filename."""
    match = re.search(r'frame(\d+)\.jpg', filename)
    return int(match.group(1)) if match else -1


def read_columns_from_file(file_path):
    times_ms = []
    total_signals = []

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                try:
                    time_ms = float(parts[0])
                    signal = float(parts[1])
                    times_ms.append(time_ms)
                    total_signals.append(signal)
                except ValueError:
                    print(f"Warning: Could not convert line to floats: {line.strip()}")

    return times_ms, total_signals

def is_valid_experiment_folder(folder_name):
    """Check if the folder name matches 'CMFX_XXXXX' and XXXXX is a valid integer."""
    match = re.match(r'^CMFX_(\d+)$', folder_name)
    if match:
        return match.group(1).isdigit()
    return False


def process_images(experiment_number):
    """Process images and create plots."""
    base_dir = f'{PROCESSED_DIR}/CMFX_{experiment_number:05d}'
    raw_dir = f'{RAW_DIR}/CMFX_{experiment_number:05d}'

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    else:
        return None

    for subfolder in range(23):
        raw_subfolder = os.path.join(raw_dir, f'video{subfolder}')
        if os.path.exists(raw_subfolder):
            timestamp_file = os.path.join(raw_dir, f'video{subfolder}.txt')
            timestamps = read_timestamps(timestamp_file) if os.path.exists(timestamp_file) else []

            inten_file =  os.path.join(raw_dir, f'video{subfolder}_inten.txt')

            if len(timestamps) < 2:
                continue  # Skip if there are not enough timestamps

            total_signals = []
            times_ms = []

            if os.path.exists(inten_file):
                times_ms, total_signals = read_columns_from_file(inten_file)

                # print(f"hehehe")
            else:
                # Get and sort filenames numerically
                filenames = sorted(os.listdir(raw_subfolder), key=extract_frame_number)

                for filename in filenames:
                    if filename.endswith('.jpg'):
                        frame_number = extract_frame_number(filename)
                        frame_path = os.path.join(raw_subfolder, filename)

                        total_signal = get_total_signal(frame_path)
                        total_signals.append(total_signal)

                        if frame_number < len(timestamps):
                            frame_time = timestamps[frame_number]
                            reference_time = timestamps[1]
                            time_diff = (frame_time - reference_time).total_seconds() * 1000  # Convert to milliseconds
                            times_ms.append(time_diff)
            try:
                # now making the png with intensities
                plt.figure(figsize=(10, 6))
                plt.plot(times_ms[1:], total_signals[1:], marker='o')
                plt.xlabel('Time (ms) After Second Frame')
                plt.ylabel('Total Signal')
                plt.title(f'CMFX_{experiment_number:05d} - video{subfolder}')
                plt.grid(True)
                plot_file = os.path.join(base_dir, f'video{subfolder}.png')
                plt.savefig(plot_file)
                # plt.show()
                plt.close()
            except Exception:
                print(f"Something went bad during plotting but whatever")

def monitor_and_process():
    """Monitor the /CMFX_RAW/video directory and process existing and new subfolders starting from the largest number."""
    processed_experiments = set()

    # Get all valid experiment folders
    all_folders = [folder for folder in os.listdir(RAW_DIR) if is_valid_experiment_folder(folder)]
    experiment_numbers = [int(folder.replace('CMFX_', '')) for folder in all_folders]

    # Sort experiment numbers in descending order
    experiment_numbers.sort(reverse=True)
    cutoff_n = 800
    # Process existing folders
    for experiment_number in experiment_numbers:
        base_dir = f'{PROCESSED_DIR}/CMFX_{experiment_number:05d}'
        if not os.path.exists(base_dir):

            if experiment_number > cutoff_n:
                print(f"Processing existing experiment: {experiment_number}")
                process_images(experiment_number)
            processed_experiments.add(experiment_number)
        else:
            print(f"This one exists already {base_dir}")
            processed_experiments.add(experiment_number)

    while True:
        current_experiments = set()
        for folder_name in os.listdir(RAW_DIR):
            if is_valid_experiment_folder(folder_name):
                experiment_number = int(folder_name.replace('CMFX_', ''))
                if experiment_number > cutoff_n:
                    current_experiments.add(experiment_number)

        new_experiments = current_experiments - processed_experiments
        for experiment_number in new_experiments:
            if experiment_number > cutoff_n:
                print(f"Processing new experiment: {experiment_number}, but waiting 60 s")
                time.sleep(60)
                process_images(experiment_number)
                processed_experiments.add(experiment_number)
        print(f"Waiting for more data, GIMME MOAR!!!")
        
        time.sleep(10)  # Wait for one minute before checking again


if __name__ == '__main__':
    monitor_and_process()

# import os
# import time
# import numpy as np
# from PIL import Image
# import matplotlib.pyplot as plt
# from datetime import datetime
#
# RAW_DIR = '/CMFX_RAW/video'
# PROCESSED_DIR = '/CMFX/video'
#
#
# def get_total_signal(image_path):
#     """Calculate the total signal (sum of pixel values) of an image."""
#     with Image.open(image_path) as img:
#         img_array = np.array(img)
#         if len(img_array.shape) == 3:  # RGB image
#             img_array = np.mean(img_array, axis=2)  # Convert to grayscale
#         return np.sum(img_array)
#
#
# def read_timestamps(timestamp_file):
#     """Read timestamps from a file and return a list of datetime objects."""
#     timestamps = []
#     with open(timestamp_file, 'r') as f:
#         for line in f:
#             timestamp = datetime.strptime(line.strip(), '%Y-%m-%d %H:%M:%S.%f')
#             timestamps.append(timestamp)
#     return timestamps
#
#
# def process_images(experiment_number):
#     """Process images and create plots."""
#     base_dir = f'{PROCESSED_DIR}/CMFX_{experiment_number:05d}'
#     raw_dir = f'{RAW_DIR}/CMFX_{experiment_number:05d}'
#
#     if not os.path.exists(base_dir):
#         os.makedirs(base_dir)
#
#     for subfolder in range(23):
#         raw_subfolder = os.path.join(raw_dir, f'video{subfolder}')
#         if os.path.exists(raw_subfolder):
#             timestamp_file = os.path.join(raw_dir, f'video{subfolder}.txt')
#             timestamps = read_timestamps(timestamp_file) if os.path.exists(timestamp_file) else []
#
#
#             if len(timestamps) < 2:
#                 continue  # Skip if there are not enough timestamps
#
#             total_signals = []
#             times_ms = []
#             for filename in sorted(os.listdir(raw_subfolder)):
#                 if filename.endswith('.jpg'):
#                     frame_number = int(filename.replace("frame", "").replace(".jpg", ""))
#                     frame_path = os.path.join(raw_subfolder, filename)
#
#                     total_signal = get_total_signal(frame_path)
#                     total_signals.append(total_signal)
#
#                     frame_time = timestamps[frame_number]
#                     reference_time = timestamps[1]
#                     time_diff = (frame_time - reference_time).total_seconds() * 1000  # Convert to milliseconds
#                     times_ms.append(time_diff)
#
#             plt.figure(figsize=(10, 6))
#             plt.plot(times_ms, total_signals, marker='o')
#             plt.xlabel('Time (ms) After Second Frame')
#             plt.ylabel('Total Signal')
#             plt.title(f'CMFX_{experiment_number:05d} - video{subfolder}')
#             plt.grid(True)
#             plot_file = os.path.join(base_dir, f'video{subfolder}.png')
#             plt.savefig(plot_file)
#             plt.show()
#             plt.close()
#
#
# def monitor_and_process():
#     """Monitor the /CMFX_RAW/video directory and process existing and new subfolders."""
#     processed_experiments = set()
#
#     # Process existing folders
#     for folder_name in sorted(os.listdir(RAW_DIR), reverse=True):
#         # print(f"folder name {folder_name}")
#         if folder_name.startswith('CMFX_'):
#             # print(f"folder name {folder_name}")
#             try:
#                 experiment_number = int(folder_name.replace('CMFX_', ''))
#             except ValueError:
#                 continue
#
#             base_dir = f'{PROCESSED_DIR}/CMFX_{experiment_number:05d}'
#             print(f"base dir {base_dir}")
#             if not os.path.exists(base_dir):
#                 print(f"Processing existing experiment: {experiment_number}")
#                 process_images(experiment_number)
#                 # processed_experiments.add(experiment_number)
#
#     while True:
#         current_experiments = set()
#         for folder_name in os.listdir(RAW_DIR):
#             if folder_name.startswith('CMFX_'):
#                 try:
#                     experiment_number = int(folder_name.replace('CMFX_', ''))
#                     current_experiments.add(experiment_number)
#                 except ValueError:
#                     continue
#
#         new_experiments = current_experiments - processed_experiments
#         for experiment_number in new_experiments:
#             print(f"Processing new experiment: {experiment_number}")
#             process_images(experiment_number)
#             processed_experiments.add(experiment_number)
#
#         time.sleep(60)  # Wait for one minute before checking again
#
#
# if __name__ == '__main__':
#     monitor_and_process()
