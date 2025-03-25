import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np


# Open the Parquet file
def plot_spectrogram_from_parquet(parquet_file):
    # Load the Parquet file
    df = pd.read_parquet(parquet_file)
    # print(df.columns)

    # Assuming the first column is time, and the second and third are the data for spectrogram
    time = df.iloc[:, 0].values  # First column as time
    # phase1 = df.iloc[:, 1].values  # Second column as signal 1
    # phase2 = df.iloc[:, 2].values  # Third column as signal 2
    lambda_red = 632e-9
    lambda_co2 = 10.54e-6
    # distance1 = np.unwrap(phase1)*lambda1
    # distance2 = np.unwrap(phase2)*lambda2
    phase_co2 = df['phase_differences_co2_fft'].values  # CO2 phase differences column
    phase_red = df['phase_differences_red_fft'].values  # Red phase differences column
    time = df['t_fft'].values
    # Unwrap the phases to remove discontinuities
    distance_co2 = lambda_co2 / 2 / np.pi * np.unwrap(phase_co2)
    num_samples = len(distance_co2)
    first_20_percent_index = int(num_samples * 0.2)

    distance_co2 = distance_co2 - np.mean(distance_co2[:first_20_percent_index])
    distance_red = lambda_red / 2 / np.pi * np.unwrap(phase_red)
    distance_red = -distance_red + np.mean(distance_red[:first_20_percent_index])

    # plt.figure()
    # plt.plot(time, distance_co2)
    # plt.plot(time, distance_red)
    # plt.plot(time, distance_red-distance_co2)
    #
    # # plt.plot(time, distance2)
    # plt.show()
    # plt.close()
    # Plot the spectrogram for signal1
    # plt.figure(figsize=(12, 6))
    #
    # plt.subplot(2, 1, 1)
    # f, t, Sxx = signal.spectrogram(distance_co2, fs=1/(time[1]-time[0]))  # Use time to estimate the sampling frequency
    # plt.pcolormesh(t, f, Sxx, shading='gouraud')
    # plt.title('Spectrogram of CO2')
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [s]')
    # plt.colorbar(label='Intensity')
    #
    # # Plot the spectrogram for signal2
    # plt.subplot(2, 1, 2)
    # f, t, Sxx = signal.spectrogram(distance_red, fs=1/(time[1]-time[0]))
    # plt.pcolormesh(t, f, Sxx, shading='gouraud')
    # plt.title('Spectrogram of Red')
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [s]')
    # plt.colorbar(label='Intensity')
    #
    # plt.tight_layout()
    # plt.show()
    fft_co2 = np.fft.fft(distance_co2)
    fft_red = np.fft.fft(distance_red)
    freqs = np.fft.fftfreq(len(time), d=(time[1] - time[0]))

    fs = 1 / (time[1] - time[0])

    # Compute Welch power spectral density for both signals
    f_co2, Pxx_co2 = signal.welch(distance_co2, fs=fs, nperseg=1024)
    f_red, Pxx_red = signal.welch(distance_red, fs=fs, nperseg=1024)

    # Plot FFT
    # plt.figure(figsize=(12, 10))
    #
    # plt.subplot(2, 1, 1)
    # plt.plot(freqs[:len(freqs) // 2], np.abs(fft_co2)[:len(freqs) // 2], label='FFT (CO2)', color='b')
    # plt.plot(freqs[:len(freqs) // 2], np.abs(fft_red)[:len(freqs) // 2], label='FFT (Red)', color='r')
    # plt.title('FFT of Unwrapped Phases (CO2 and Red)')
    # plt.xlabel('Frequency [Hz]')
    # plt.ylabel('Magnitude')
    # plt.legend()
    #
    # # Plot Welch Power Spectral Density (PSD)
    # plt.subplot(2, 1, 2)
    # plt.semilogy(f_co2, Pxx_co2, label='Welch PSD (CO2)', color='b')
    # plt.semilogy(f_red, Pxx_red, label='Welch PSD (Red)', color='r')
    # plt.title('Welch Power Spectral Density (CO2 and Red)')
    # plt.xlabel('Frequency [Hz]')
    # plt.ylabel('Power/Frequency [dB/Hz]')
    # plt.legend()
    #
    # plt.tight_layout()
    # plt.show()

    # Sampling frequency
    # Sampling frequency
    fs = 1 / (time[1] - time[0])
    window_length = 0.05  # 50 ms
    nperseg = int(window_length * fs)

    # Compute the spectrogram for CO2
    f_co2, t_co2, Sxx_co2 = signal.spectrogram(distance_co2, fs=fs, nperseg=nperseg, noverlap=nperseg // 2)

    # Compute the spectrogram for Red
    f_red, t_red, Sxx_red = signal.spectrogram(distance_red, fs=fs, nperseg=nperseg, noverlap=nperseg // 2)

    # Plot 2D Heatmap for Welch Power Spectral Density (PSD)
    plt.figure(figsize=(12, 10))

    # Spectrogram for CO2
    plt.subplot(2, 1, 1)
    plt.pcolormesh(t_co2, f_co2, 10 * np.log10(Sxx_co2), shading='gouraud')
    plt.title('Welch Power Spectral Density (CO2)')
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')
    plt.colorbar(label='Power/Frequency [dB/Hz]')

    # Spectrogram for Red
    plt.subplot(2, 1, 2)
    plt.pcolormesh(t_red, f_red, 10 * np.log10(Sxx_red), shading='gouraud')
    plt.title('Welch Power Spectral Density (Red)')
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')
    plt.colorbar(label='Power/Frequency [dB/Hz]')

    plt.tight_layout()
    plt.show()

# Example usage
parquet_file = '/CMFX/interferometer/CMFX_01380_scope_results_fft.parquet'
# parquet_file = 'your_file.parquet'  # Replace with the path to your Parquet file
plot_spectrogram_from_parquet(parquet_file)
