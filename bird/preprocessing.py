import numpy as np
import utils
from skimage import morphology

def extract_noise_part(spectrogram):
    """ Extract the noise part of a spectrogram
    """
    mask = compute_noise_mask(spectrogram)
    noise_part = extract_masked_part(mask, spectrogram)
    return noise_part

def extract_signal_part(spectrogram):
    """ Extract the signal part of a spectrogram
    """
    mask = compute_signal_mask(spectrogram)
    signal_part = extract_masked_part(mask, spectrogram)
    return signal_part

def extract_masked_part(mask, spectrogram):
    """ Extract the masked part of the spectrogram
    """
    # the mask is binary and numpy arrays use boolean masks
    mask = mask==1
    return spectrogram[:,mask]

def compute_signal_mask(spectrogram):
    """ Computes a binary noise mask (convenience function)

    # Arguments
        spectrogram : a numpy array representation of a spectrogram (2-dim)

    # Returns
        binary_mask : the binary signal mask
    """
    threshold = 3
    mask = compute_binary_mask(spectrogram, threshold)
    return mask

def compute_noise_mask(spectrogram):
    """ Computes a binary noise mask (convenience function)

    # Arguments
        spectrogram : a numpy array representation of a spectrogram (2-dim)

    # Returns
        binary_mask : the binary noise mask
    """
    threshold = 2.5
    mask = compute_binary_mask(spectrogram, threshold)
    # invert mask
    return 1-mask

def compute_binary_mask(spectrogram, threshold):
    """ Computes a binary mask for the spectrogram
    # Arguments
        spectrogram : a numpy array representation of a spectrogram (2-dim)
        threshold   : a threshold for times larger than the median
    # Returns
        binary_mask : the binary mask
    """
    norm_spectrogram = normalize(spectrogram)
    binary_structure = mark_cells_times_larger_than_median(norm_spectrogram, threshold)

    n_hood = np.ones((4, 4))
    binary_structure = morphology.binary_erosion(binary_structure, n_hood)
    binary_structure = morphology.binary_dilation(binary_structure, n_hood)

    # TODO: transpose is O(n^2)
    mask = np.array([np.max(col) for col in np.transpose(binary_structure)])
    mask = smooth_mask(mask)

    return mask

def smooth_mask(mask):
    """ Smooths a binary mask using 4x4 dilation
        # Arguments
            mask : the binary mask
        # Returns
            mask : a smoother binary mask
    """
    n_hood = np.ones(4)
    mask = morphology.binary_dilation(mask, n_hood)
    mask = morphology.binary_dilation(mask, n_hood)

    # type casting is a bitch
    return 1*mask

def mark_cells_times_larger_than_median(spectrogram, number_times_larger):
    """ Compute binary image from spectrogram where cells are marked as 1 if
    number_times_larger than the row AND column median, otherwise 0
    """
    row_medians = np.median(spectrogram, axis=1)
    col_medians = np.median(spectrogram, axis=0)
    for row in range(spectrogram.shape[0]):
        for col in range(spectrogram.shape[1]):
            if spectrogram[row][col] > 3*row_medians[row] \
               and spectrogram[row][col] > 3*col_medians[col]:
                spectrogram[row][col] = 1
            else:
                spectrogram[row][col] = 0

    return spectrogram

def remove_low_and_high_frequency_bins(spectrogram, nb_low=5, nb_high=25):
    """ Removes low and high frequency bins from a spectrogram

    # Argmuents
        nb_low  : the number of lower frequency bins to remove
        nb_high : the number of higher frequency bins to remove
    # Returns
        spectrogram : the narrowed spectrogram
    """
    return spectrogram[nb_low:spectrogram.shape[0]-nb_high]

def normalize(X):
    """ Normalize numpy array to interval [0, 1]
    """
    mi = np.min(X)
    ma = np.max(X)

    X = (X-mi)/(ma-mi)
    return X
