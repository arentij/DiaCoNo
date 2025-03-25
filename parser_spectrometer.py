import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time


def linear_decay(x, x1, x2):
    """
    Compute a linear decay from 1 to 0 within the range [x1, x2].

    Parameters:
        x (float): The input value where the decay is calculated.
        x1 (float): The start of the range where the decay begins.
        x2 (float): The end of the range where the decay ends.

    Returns:
        float: The decay value in the range [0, 1].
    """
    if x < x1:
        return 1
    elif x1 <= x <= x2:
        # Linear decay from 1 to 0
        return 1 - (x - x1) / (x2 - x1)
    else:
        return 0

# def wavelength_to_rgb(wavelength):
#     """
#     Convert a wavelength in the visible spectrum to an RGB color with smooth transitions
#     to black outside the visible spectrum (near 380 nm and 780 nm) using exponential functions.
#
#     Parameters:
#         wavelength (float): Wavelength in nanometers (nm).
#
#     Returns:
#         tuple: (R, G, B) values in the range [0, 1].
#     """
#     # Initialize RGB values
#     R = G = B = 0.0
#
#     # Define exponential transition function for smooth decays
#     def exponential_decay(x, start, end):
#         """Returns a smooth decay factor using an exponential function."""
#         if x < start:
#             return 0
#         elif x > end:
#             return 1
#         else:
#             return np.exp(-1 * (x - start) / (end - start))
#
#     # Calculate intensity adjustment factor for smooth transition
#     if wavelength < 360:
#         # Fully black below 360 nm
#         factor = 0
#     elif 360 <= wavelength < 380:
#         # Exponential transition to black from 360 to 380 nm
#         factor = exponential_decay(wavelength, 360, 380)
#     elif 380 <= wavelength <= 720:
#         # Color matching functions for visible range
#         if 380 <= wavelength <= 440:
#             R = -(wavelength - 440) / (440 - 380)
#             G = 0
#             B = 1
#         elif 440 <= wavelength <= 490:
#             R = 0
#             G = (wavelength - 440) / (490 - 440)
#             B = 1
#         elif 490 <= wavelength <= 510:
#             R = 0
#             G = 1
#             B = -(wavelength - 510) / (510 - 490)
#         elif 510 <= wavelength <= 580:
#             R = (wavelength - 510) / (580 - 510)
#             G = 1
#             B = 0
#         elif 580 <= wavelength <= 645:
#             R = 1
#             G = -(wavelength - 645) / (645 - 580)
#             B = 0
#         elif 645 <= wavelength <= 780:
#             R = 1
#             G = 0
#             B = 0
#         factor = 1
#     elif 720 < wavelength <= 800:
#         # Exponential transition to black from 780 to 800 nm
#         factor = exponential_decay(wavelength, 720, 800)
#         # print(wavelength, factor)
#     else:
#         # Fully black beyond 800 nm
#         factor = 0
#
#     # Apply the intensity factor
#     R *= factor
#     G *= factor
#     B *= factor
#
#     # Gamma correction for smoother display
#     # if wavelength > 720:
#     #     R *= max(0, 1 -(wavelength-720)/60)
#     gamma = 0.5
#     if 719 < wavelength <722 :
#         print(f"{wavelength}, {R}, {G}, {B}")
#     R = np.clip(R ** gamma, 0, 1)
#     G = np.clip(G ** gamma, 0, 1)
#     B = np.clip(B ** gamma, 0, 1)
#     if 719 < wavelength <722 :
#         print(f"{wavelength}, {R}, {G}, {B}")
#     # Return the RGB value as a tuple in the range [0, 1]
#     return R, G, B


def wavelength_to_rgb(wavelength):
    """
    Convert a wavelength in the visible spectrum to an RGB color with smooth transitions
    to black outside the visible spectrum (near 380 nm and 780 nm) using polynomial transitions.

    Parameters:
        wavelength (float): Wavelength in nanometers (nm).

    Returns:
        tuple: (R, G, B) values in the range [0, 1].
    """
    def smooth_transition(x, center, width):
        """Smooth transition function using polynomial."""
        if x < center - width:
            return 0
        elif center - width <= x < center:
            t = (x - (center - width)) / width
            return t ** 2
        elif center <= x <= center + width:
            t = (x - center) / width
            return 1 - t ** 2
        else:
            return 1

    # Initialize RGB values
    R = G = B = 0.0

    # Color matching functions for visible range
    if wavelength < 320:
        factor = smooth_transition(wavelength, 320, 20)
    elif 320 <= wavelength < 360:
        factor = smooth_transition(wavelength, 360, 20)
    elif 360 <= wavelength <= 780:
        if 360 <= wavelength <= 440:
            R = -(wavelength - 440) / (440 - 360)
            G = 0
            B = 1
        elif 440 <= wavelength <= 490:
            R = 0
            G = (wavelength - 440) / (490 - 440)
            B = 1
        elif 490 <= wavelength <= 510:
            R = 0
            G = 1
            B = -(wavelength - 510) / (510 - 490)
        elif 510 <= wavelength <= 580:
            R = (wavelength - 510) / (580 - 510)
            G = 1
            B = 0
        elif 580 <= wavelength <= 645:
            R = 1
            G = -(wavelength - 645) / (645 - 580)
            B = 0
        elif 645 <= wavelength <= 780:
            R = 1
            G = 0
            B = 0
        factor = 1
    elif 780 <= wavelength < 800:
        factor = smooth_transition(wavelength, 780, 20)
    elif 800 <= wavelength <= 950:
        factor = smooth_transition(wavelength, 800, 20)
    else:
        factor = 0

    # Apply the intensity factor
    R *= factor
    G *= factor
    B *= factor

    # Gamma correction for smoother display
    gamma = 0.8
    factor2 = 1
    if wavelength > 730:
        factor2 = linear_decay(wavelength, 730, 790)
    elif wavelength < 380:
        factor2 = 1 - linear_decay(wavelength, 360, 380)
    R = np.clip(R ** gamma*factor2, 0, 1)
    G = np.clip(G ** gamma, 0, 1)
    B = np.clip(B ** gamma*factor2, 0, 1)

    # Return the RGB value as a tuple in the range [0, 1]
    return R, G, B


# def process_files(folder_path):
#     # List all files in the folder
#     files = os.listdir(folder_path)
#
#     # Create a dictionary to store file paths by experiment number and model
#     file_dict = {}
#
#     for file in files:
#         if file.endswith('_times.csv'):
#             exp_number = file.split('_')[1]
#             model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
#             key = (exp_number, model)
#             if key not in file_dict:
#                 file_dict[key] = {}
#             file_dict[key]['times'] = os.path.join(folder_path, file)
#         elif file.endswith('.csv') and '_times' not in file:
#             exp_number = file.split('_')[1]
#             model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
#             key = (exp_number, model)
#             if key not in file_dict:
#                 file_dict[key] = {}
#             file_dict[key]['spectra'] = os.path.join(folder_path, file)
#
#     print("File dictionary:", file_dict)  # Debugging line to check the dictionary content
#
#     # Process each experiment and model
#     for (exp_number, model), paths in file_dict.items():
#         print(f"Processing: Experiment {exp_number}, Model {model}")  # Debugging line
#         if 'times' in paths and 'spectra' in paths:
#             process_experiment(folder_path, exp_number, model, paths['times'], paths['spectra'])
#         else:
#             print(f"Missing files for Experiment {exp_number}, Model {model}: {paths}")  # Debugging line

# def process_files(folder_path):
#     while True:
#         # List all files in the folder
#         files = os.listdir(folder_path)
#
#         # Create a dictionary to store file paths by experiment number and model
#         file_dict = {}
#
#         for file in files:
#             if file.endswith('_times.csv'):
#                 exp_number = file.split('_')[1]
#                 model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
#                 key = (exp_number, model)
#                 if key not in file_dict:
#                     file_dict[key] = {}
#                 file_dict[key]['times'] = os.path.join(folder_path, file)
#             elif file.endswith('.csv') and '_times' not in file:
#                 exp_number = file.split('_')[1]
#                 model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
#                 key = (exp_number, model)
#                 if key not in file_dict:
#                     file_dict[key] = {}
#                 file_dict[key]['spectra'] = os.path.join(folder_path, file)
#
#         # print("File dictionary:", file_dict)  # Debugging line to check the dictionary content
#
#         # Process each experiment and model
#         for (exp_number, model), paths in file_dict.items():
#             output_folder = os.path.join(folder_path, f"/CMFX/spectrometer/CMFX_{exp_number}/{model}")
#
#             # Skip processing if the output folder already exists
#             if os.path.exists(output_folder):
#                 print(f"Skipping already processed: Experiment {exp_number}, Model {model}")
#                 continue
#
#             print(f"Processing: Experiment {exp_number}, Model {model}")  # Debugging line
#             if 'times' in paths and 'spectra' in paths:
#                 process_experiment(folder_path, exp_number, model, paths['times'], paths['spectra'])
#             else:
#                 print(f"Missing files for Experiment {exp_number}, Model {model}: {paths}")  # Debugging line
#
#         print("Waiting for 30 seconds before checking for new files...")
#         time.sleep(10)  # Wait for 30 seconds before checking again


def get_file_dict(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)

    # Create a dictionary to store file paths by experiment number and model
    file_dict = {}

    for file in files:
        if file.endswith('_times.csv'):
            exp_number = file.split('_')[1]
            model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
            key = (exp_number, model)
            if key not in file_dict:
                file_dict[key] = {}
            file_dict[key]['times'] = os.path.join(folder_path, file)
        elif file.endswith('.csv') and '_times' not in file:
            exp_number = file.split('_')[1]
            model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
            key = (exp_number, model)
            if key not in file_dict:
                file_dict[key] = {}
            file_dict[key]['spectra'] = os.path.join(folder_path, file)

    return file_dict


def process_files(folder_path):
    processed_files = set()  # Track processed files
    while True:
        file_dict = get_file_dict(folder_path)
        new_files_detected = False

        sorted_keys = sorted(file_dict.keys(), reverse=True)
        sorted_file_dict = {key: file_dict[key] for key in sorted_keys}

        for (exp_number, model), paths in sorted_file_dict.items():
            output_folder = os.path.join(folder_path, f"/CMFX/spectrometer/CMFX_{exp_number}/{model}")

            try:   # THIS IS TEMPORAL FOR NOT TO PARSE WHILE WE ARE RUNNING
                if int(exp_number) < 1200:
                    continue
            except Exception as e:
                print(f"Smth  is wrong: {e}")
                continue
            # Skip processing if the output folder already exists
            if os.path.exists(output_folder):
                continue

            # Check if this set of files has already been processed
            files_key = (paths.get('times'), paths.get('spectra'))
            if files_key in processed_files:
                continue

            # Mark files as detected new files
            new_files_detected = True
            print(f"Processing: Experiment {exp_number}, Model {model}")  # Debugging line
            if 'times' in paths and 'spectra' in paths:
                # Wait 29 seconds before processing new files
                print("New files detected. Waiting for 29 seconds...")
                time.sleep(0.1)
                process_experiment(folder_path, exp_number, model, paths['times'], paths['spectra'])
                # Mark these files as processed
                processed_files.add(files_key)
            else:
                print(f"Missing files for Experiment {exp_number}, Model {model}: {paths}")  # Debugging line

        if not new_files_detected:
            print("No new files detected. Waiting for 30 seconds before checking again...")
        else:
            print("Waiting for 30 seconds before checking for new files again...")

        time.sleep(10)  # Wait for 30 seconds before checking again


def process_experiment(folder_path, exp_number, model, times_file, spectra_file):
    # Create output directory
    output_folder = os.path.join(folder_path, f"/CMFX/spectrometer/CMFX_{exp_number}/{model}")
    os.makedirs(output_folder, exist_ok=True)

    print(f"Reading times file: {times_file}")  # Debugging line
    print(f"Reading spectra file: {spectra_file}")  # Debugging line

    # Read times file
    try:
        times_df = pd.read_csv(times_file, header=None)
    except Exception as e:
        print(f"Error reading times file {times_file}: {e}")
        return

    exposure_time = float(times_df.iloc[1, 0]) / 1000  # Convert from microseconds to milliseconds
    measurement_times = pd.to_datetime(times_df.iloc[2:].values.flatten())

    # Read spectra file
    try:
        spectra_df = pd.read_csv(spectra_file, header=None)
    except Exception as e:
        print(f"Error reading spectra file {spectra_file}: {e}")
        return
    try:
        wavelengths = spectra_df.iloc[1].values
        intensities = spectra_df.iloc[2:].values.astype(float)
    except IndexError:
        print(f"Index error oops")
        return None

    # Initial measurement
    initial_intensities = intensities[0]

    # Determine global y-limits based on all measurements for the model
    min_y = np.min(intensities - initial_intensities)
    max_y = np.max(intensities - initial_intensities)

    # Generate plots
    for i, intensity in enumerate(intensities[1:], start=1):
        plt.figure(figsize=(10, 6))
        adjusted_intensity = intensity - initial_intensities
        times_diff = (measurement_times[i] - measurement_times[1]).total_seconds() * 1000  # milliseconds

        # Plot each wavelength as a line from zero to its intensity
        for j, (wavelength, intensity_value) in enumerate(zip(wavelengths, adjusted_intensity)):
            color = wavelength_to_rgb(wavelength)
            plt.plot([wavelength, wavelength], [0, intensity_value], color=color, lw=0.5,
                     label=f'{wavelength} nm')
            # print(f"{wavelength}, {color}")

        plt.plot(wavelengths, adjusted_intensity, lw=0.15, color='black')
        plt.title(f"CMFX_{exp_number}, {model} - Time: {times_diff-exposure_time:.2f} - {times_diff:.2f} ms")
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Counts")
        plt.ylim(0, max_y)  # Set consistent y-limits
        # plt.legend(loc='best', fontsize='small')
        plt.grid()
        # Save the plot
        # plt.show()
        plt.savefig(os.path.join(output_folder, f"frame{i}.png"))
        plt.close()


if __name__ == "__main__":
    folder_path = "/CMFX_RAW/spectrometer/"  # Update this path to your folder
    process_files(folder_path)

# import os
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
#
#
# def process_files(folder_path):
#     # List all files in the folder
#     files = os.listdir(folder_path)
#
#     # Create a dictionary to store file paths by experiment number and model
#     file_dict = {}
#
#     for file in files:
#         if file.endswith('_times.csv'):
#             exp_number = file.split('_')[1]
#             model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
#             key = (exp_number, model)
#             if key not in file_dict:
#                 file_dict[key] = {}
#             file_dict[key]['times'] = os.path.join(folder_path, file)
#         elif file.endswith('.csv') and '_times' not in file:
#             exp_number = file.split('_')[1]
#             model = file.split('_')[2].replace('.csv', '')  # Remove the file extension
#             key = (exp_number, model)
#             if key not in file_dict:
#                 file_dict[key] = {}
#             file_dict[key]['spectra'] = os.path.join(folder_path, file)
#
#     print("File dictionary:", file_dict)  # Debugging line to check the dictionary content
#
#     # Process each experiment and model
#     for (exp_number, model), paths in file_dict.items():
#         print(f"Processing: Experiment {exp_number}, Model {model}")  # Debugging line
#         if 'times' in paths and 'spectra' in paths:
#             process_experiment(folder_path, exp_number, model, paths['times'], paths['spectra'])
#         else:
#             print(f"Missing files for Experiment {exp_number}, Model {model}: {paths}")  # Debugging line
#
#
# def process_experiment(folder_path, exp_number, model, times_file, spectra_file):
#     # Create output directory
#     output_folder = os.path.join(folder_path, f"/CMFX/spectrometer/{exp_number}/{model}")
#     os.makedirs(output_folder, exist_ok=True)
#
#     print(f"Reading times file: {times_file}")  # Debugging line
#     print(f"Reading spectra file: {spectra_file}")  # Debugging line
#
#     # Read times file
#     try:
#         times_df = pd.read_csv(times_file, header=None)
#     except Exception as e:
#         print(f"Error reading times file {times_file}: {e}")
#         return
#     print(times_df.iloc[1, 0])
#     exposure_time = float(times_df.iloc[1, 0]) / 1000  # Convert from microseconds to milliseconds
#     measurement_times = pd.to_datetime(times_df.iloc[2:].values.flatten())
#
#     # Read spectra file
#     try:
#         spectra_df = pd.read_csv(spectra_file, header=None)
#     except Exception as e:
#         print(f"Error reading spectra file {spectra_file}: {e}")
#         return
#
#     wavelengths = spectra_df.iloc[1].values
#     intensities = spectra_df.iloc[2:].values.astype(float)
#
#     # Initial measurement
#     initial_intensities = intensities[0]
#
#     # Determine global y-limits based on all measurements for the model
#     min_y = np.min(intensities - initial_intensities)
#     max_y = np.max(intensities - initial_intensities)
#
#     # Generate plots
#     for i, intensity in enumerate(intensities[1:], start=1):
#         plt.figure()
#         adjusted_intensity = intensity - initial_intensities
#         times_diff = (measurement_times[i] - measurement_times[1]).total_seconds() * 1000  # milliseconds
#
#         # Plot each wavelength as a line from zero to its intensity
#         for j, (wavelength, intensity_value) in enumerate(zip(wavelengths, adjusted_intensity)):
#             plt.plot([wavelength, wavelength], [0, intensity_value], color=plt.cm.jet(j / len(wavelengths)),
#                      label=f'{wavelength} nm')
#
#         plt.title(f"{model} - Time: {times_diff:.2f} ms")
#         plt.xlabel("Wavelength")
#         plt.ylabel("Intensity")
#         plt.ylim(0, max_y)  # Set consistent y-limits
#         # plt.legend(loc='best', fontsize='small')
#
#         # Save the plot
#         plt.savefig(os.path.join(output_folder, f"frame{i}.png"))
#         plt.show()
#         plt.close()
#
#
#
# if __name__ == "__main__":
#     folder_path = "/CMFX/apps/spectra_tests/"  # Update this path to your folder
#     process_files(folder_path)
