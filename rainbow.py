import numpy as np
import matplotlib.pyplot as plt


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
    if wavelength < 360:
        factor = smooth_transition(wavelength, 360, 20)
    elif 360 <= wavelength < 380:
        factor = smooth_transition(wavelength, 380, 20)
    elif 380 <= wavelength <= 780:
        if 380 <= wavelength <= 440:
            R = -(wavelength - 440) / (440 - 380)
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
    R = np.clip(R ** gamma, 0, 1)
    G = np.clip(G ** gamma, 0, 1)
    B = np.clip(B ** gamma, 0, 1)

    # Return the RGB value as a tuple in the range [0, 1]
    return R, G, B

# Generate wavelengths and RGB values
wavelengths = np.linspace(200, 950, 1000)
colors = np.array([wavelength_to_rgb(w) for w in wavelengths])

# Plot RGB values
plt.figure(figsize=(12, 6))

# Red channel
plt.subplot(3, 1, 1)
plt.plot(wavelengths, colors[:, 0], color='red')
plt.title('Red Channel')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity')

# Green channel
plt.subplot(3, 1, 2)
plt.plot(wavelengths, colors[:, 1], color='green')
plt.title('Green Channel')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity')

# Blue channel
plt.subplot(3, 1, 3)
plt.plot(wavelengths, colors[:, 2], color='blue')
plt.title('Blue Channel')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity')

plt.tight_layout()
plt.show()
