"""
gen_gif.py - Generate GIF animation from DFT coefficents

Use the coeffs to generate a rotating-circle drawer animation as a GIF file.

Part of my fourier-image generator script. Should not be used as-is.
Uses tqdm for progress display and PIL for image generation.

WARNING! This thing EATS memory!

By +ɛ (https://github.com/sasszem), 2021
"""

import cmath
from PIL import Image, ImageDraw
from tqdm import tqdm


def _complex_to_point(comp, image_size):
    """Complex number in (-1-1j, 1+1j) box to point on the (square) image"""
    return (comp.real+1) * image_size[0] / 2, (comp.imag+1) * image_size[1] / 2

def _draw_frame(coeffs, k, prev_frame, point_size, image_size):
    """Draw the kth timestep's frame on prev_frame"""
    n_coeffs = len(coeffs)

    # Uses two frames - one will only contain the points
    # and that will be used by the next iteration as a base
    my_frame = prev_frame.copy()
    next_base = prev_frame.copy()
    draw_own = ImageDraw.Draw(my_frame)
    draw_base = ImageDraw.Draw(next_base)

    # Current center point
    point = 0+0j
    for i, coeff in enumerate(coeffs):
        # Elipse (circle) drawing needs a bounding box
        # that will be (point - delta, point + delta)
        delta = complex(abs(coeff), abs(coeff))

        # draw current circle
        draw_own.ellipse((_complex_to_point(point-delta, image_size),
                          _complex_to_point(point+delta, image_size)), outline=(0, 255, 0))

        # draw line segment
        # (calculate using primitive inverse DFT step)
        nextpoint = point + coeff * cmath.rect(1, 2*cmath.pi*k * i / n_coeffs)
        draw_own.line((_complex_to_point(point, image_size),
                       _complex_to_point(nextpoint, image_size)), (255, 255, 255))
        # update point
        point = nextpoint

    # Draw point (filled circle)
    # (same bounding box problem)
    delta = complex(point_size, point_size)
    draw_own.ellipse((_complex_to_point(point - delta, image_size),
                      _complex_to_point(point+delta, image_size)), (255, 0, 0))
    draw_base.ellipse((_complex_to_point(point - delta, image_size),
                       _complex_to_point(point+delta, image_size)), (255, 0, 0))

    return my_frame, next_base


def _gen_images(coeffs, point_size, image_size, progress):
    """generate all images of the anumation"""

    # each iteration generates two images: one with the circles and one with only the points
    # the later one will be used as a base by the next iteration

    i = Image.new("RGB", image_size)
    base = i

    images = []
    iterator = range(len(coeffs))

    for i in tqdm(iterator, "Generating images") if progress else iterator:
        img, base = _draw_frame(coeffs, i, base, point_size, image_size)
        images.append(img)

    images.append(base)
    return images


def _save_images(images, path, save_last, duration, progress):
    """Save images with the saving options"""

    if progress:
        print("Saving...")
    images[0].save(f"{path}.gif", save_all=True, append_images=images[1:],
                   optimize=True, duration=[duration]*(len(images)-1)+[2**15], loop=1)
    if save_last:
        images[-1].save(f"{path}.png")
    if progress:
        print("Done!")


def gen_gif(coeffs, path, save_last, duration, point_size, image_size, progress):
    """Generate and save images from DFT coeffs"""
    images = _gen_images(coeffs, point_size, image_size, progress)
    _save_images(images, path, save_last, duration, progress)
