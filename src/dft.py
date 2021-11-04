"""
dft.py

Very simple discrete fourier transform. Can work on complex values.
Uses the primitive O(N^2) algorithm!

Uses the 1/N normalization factor on the transform!

Uses TQDM to print progress bars.
Part of my fourier-image generator script. Should not be used as-is.

By +ɛ (2021) (https://github.com/Sasszem)
"""
import cmath
from tqdm import tqdm


def _get_bin(points, bin_no, n_samples):
    """Get DFT bin value by evaluatin the DFT sum"""
    return 1/n_samples * sum(
        point*cmath.rect(1, - 2*cmath.pi*bin_no*i / n_samples)
        for i, point in enumerate(points)
    )
    # just evaluating the sum
    # .rect is polar->complex conversion


def do_dft(points, progress=False):
    """Get all DFT bins at once"""
    n_samples = len(points)
    iterator = tqdm(range(n_samples),
                    "Running DFT") if progress else range(n_samples)
    return [_get_bin(points, i, n_samples) for i in iterator]
