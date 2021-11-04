"""
Read SVG image and generate points

Scales & translates points to the 1.7*(-1-1j; 1+1j) bounding box.

Part of my fourier-image generator script. Should not be used as-is.
"""



import svg.path
from lxml import etree as ET
from tqdm import tqdm


def _interpolate(elem, invstep, trans, scale):
    """Interpolate SVG path element so on average we have ~invstep points per unit distance"""
    dist = abs(elem.start - elem.end) * scale
    steps = max(1, int(dist * invstep))
    return [scale * (elem.point(i/steps)+trans) for i in range(steps)]


def _get_paths(filepath):
    """Read and parse all paths in file"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    return [svg.path.parse_path(node.get("d")) for node in tree.findall(".//path", root.nsmap)]


def _find_bounding_box(paths):
    """Find bounding box of SVG paths"""
    minx, miny, maxx, maxy = 10**10, 10**10, 0, 0
    for path in paths:
        for elem in path:
            minx = min(minx, elem.start.real, elem.end.real)
            miny = min(miny, elem.start.imag, elem.end.imag)
            maxx = max(maxx, elem.start.real, elem.end.real)
            maxy = max(maxy, elem.start.imag, elem.end.imag)
    return minx, miny, maxx, maxy


def _parse_image(filepath, interpolation_factor, progress):
    """Read image, parse & interpolate points"""
    if progress:
        print("Parsing image")

    paths = _get_paths(filepath)
    image_points = []

    minx, miny, maxx, maxy = _find_bounding_box(paths)
    trans = -complex(maxx+minx, maxy+miny) / 2
    scale = 1.7/max(maxx-minx, maxy-miny)

    for path in tqdm(paths, "Interpolating paths") if progress else paths:
        for elem in path:
            if isinstance(elem, svg.path.Move):
                continue
            image_points.extend(_interpolate(
                elem, interpolation_factor, trans, scale))
    return image_points


def _filter_points(points, interpolation_factor, progress):
    """Filter points so points too close to each other will get removed"""
    min_distance =  2/3 * 1/interpolation_factor
    filtered_points = []

    for point in tqdm(points, "Filtering points") if progress else points:
        skip = False
        for existing_point in filtered_points:
            if abs(existing_point-point) < min_distance:
                skip = True
                break
        if not skip:
            filtered_points.append(point)

    return filtered_points


def read_image(filepath, interpolation_factor, progress=False):
    """Read SVG and return list of complex numbers"""
    return _filter_points(
            _parse_image(filepath, interpolation_factor, progress),
            interpolation_factor,
            progress
        )
