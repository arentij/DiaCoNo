import os
import pandas as pd
import matplotlib.pyplot as plt


def process_files(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)

    # Create a dictionary to store file paths by experiment number and model
    file_dict = {}

    for file in files:
        if file.endswith('_times.csv'):
            exp_number = file.split('_')[1]
            model = file.split('_')[2]
            key = (exp_number, model)
            if key not in file_dict:
                file_dict[key] = {}
            file_dict[key]['times'] = os.path.join(folder_path, file)
        elif file.endswith('.csv') and '_times' not in file:
            exp_number = file.split('_')[1]
            model = file.split('_')[2]
            key = (exp_number, model)
            if key not in file_dict:
                file_dict[key] = {}
            file_dict[key]['spectra'] = os.path.join(folder_path, file)

    # Process each experiment and model
    for (exp_number, model), paths in file_dict.items():
        if 'times' in paths and 'spectra' in paths:
            print(f"Found files {paths}")
            # process_experiment(folder_path, exp_number, model, paths['times'], paths['spectra'])


def process_experiment(folder_path, exp_number, model, times_file, spectra_file):
    # Create output directory
    output_folder = os.path.join(folder_path, f"spectrometer/{exp_number}/{model}")
    os.makedirs(output_folder, exist_ok=True)

    # Read times file
    times_df = pd.read_csv(times_file, header=None)
    exposure_time = times_df.iloc[1, 0] / 1000  # Convert from microseconds to milliseconds
    measurement_times = pd.to_datetime(times_df.iloc[2:].values.flatten())

    # Read spectra file
    spectra_df = pd.read_csv(spectra_file, header=None)
    wavelengths = spectra_df.iloc[1].values
    intensities = spectra_df.iloc[2:].values.astype(float)

    # Initial measurement
    initial_intensities = intensities[0]

    # Generate plots
    for i, intensity in enumerate(intensities[1:], start=1):
        plt.figure()
        adjusted_intensity = intensity - initial_intensities
        times_diff = (measurement_times[i] - measurement_times[1]).total_seconds() * 1000  # milliseconds

        plt.plot(wavelengths, adjusted_intensity)
        plt.title(f"{model} - Time: {times_diff:.2f} ms")
        plt.xlabel("Wavelength")
        plt.ylabel("Intensity")

        # Save the plot
        plt.savefig(os.path.join(output_folder, f"frame{i}.png"))
        plt.close()


if __name__ == "__main__":
    folder_path = "/CMFX/apps/spectra_tests"  # Update this path to your folder
    process_files(folder_path)
