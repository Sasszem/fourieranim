"""
Fourier image generator

By +ɛ (https://github.com/sasszem), 2021

Generates a fourier-based rotating circle animation from an SVG file's paths.
Note: only handles PATHs, not POLYs, so you should convert them to paths or they'll get skipped!

Usage:
- (install python3 & pipenv if not already installed)
- pipenv run main.py --help for usage
or
- pipenv shell
- python3 main.py ...

------------
- WARNING! -
------------
Can consume a LOT of memory, that can possibly lead to system issues!

---------------------
- Working principle -
---------------------
the module "read_image" reads and parses the image, and returns a bunch of complex numbers
in the 1.7*(-1-1j; 1+1j) bounding box. (image is scaled and translated so it fits)
The interpolation factor (points per unit distance) is user-selectable.
The points then get DFTd (by a simple approach, inverse transform & image generation
is a bigger bottleneck, so I did not implement a proper FFT).
Then when inverse-transforming the image data, circles are drawn before adding each term
in the summation.
The resulting frames are then saved as a gif.
"""


import click
from read_image import read_image
from dft import do_dft
from gen_gif import gen_gif


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--interpolation-factor",
                help="Interpolation factor (how many points per unit distance)",
                show_default=True,
                default=50
            )
@click.option("--point-size",
                help="Radius of a single point drawn in relative units.",
                default=0.01,
                show_default=True
            )
@click.option("--save-last",
                help="Save last image as a separate PNG (y/n)",
                type=lambda x: x.lower() in ("y", "yes", "true", "1", "yep"),
                default="nope"
            )
@click.option("--duration",
                help="Duration of a single frame in ms. Must be a multiple of 2.",
                default=20,
                type=int
            )
@click.option("--image-size",
                help="Size of the (square) image in pixels",
                type=lambda x: (int(x), int(x)),
                default=500
            )
def main(input_path, interpolation_factor, point_size, output, save_last, duration, image_size):
    """Main method. Implements CLI for the program via click"""
    points = read_image(input_path, interpolation_factor, True)
    coeffs = do_dft(points, True)
    gen_gif(coeffs, output, save_last, duration,
            point_size, image_size, True)

if __name__=="__main__":
    main()
