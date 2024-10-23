"""Video Processing."""

import numpy as np


def rgb_to_grayscale(rgb_frame: np.ndarray) -> np.ndarray:
    """
    Convert an RGB image to grayscale.

    The grayscale conversion is done by applying weighted coefficients to the R, G, and B channels.

    Args:
        rgb_frame (np.ndarray): A NumPy array representing the RGB image with shape (height, width, 3).

    Returns:
        np.ndarray: A NumPy array representing the grayscale image with shape (height, width, 3).
    """
    # Weighted coefficients for RGB
    r, g, b = 0.2989, 0.587, 0.114
    grayscale_frame = np.dot(rgb_frame[..., :3], [r, g, b])

    # Restoring the dimension to (height, width, 3)
    grayscale_frame = np.stack([grayscale_frame] * 3, axis=-1)
    return grayscale_frame.astype(np.uint8)
