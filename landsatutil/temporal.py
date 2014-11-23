"""
Tools for temporal data extraction
"""

# Imports
from os import listdir
from os.path import join
from numpy import min, max, average, empty, array
from skimage.util import img_as_uint

from .scene import LandsatScene


def collect_bands(band, nw_coords, se_coords, year_list, directory):
    """
    Collects sub-images of each band for each year and puts them
    into a 3-dimensional array with the 3rd dimension being time

    :param band: band of interest
    :param nw_coords: UTM coordinates (meters) of the north west corner of interest
    :param se_coords; UTM coordinates (meters) of the south east corner of interest
    :param year_list: list of years to collect
    :param directory: directory to search for available datasets
    :return: A three dimensional numpy array with the images stacked in dimension 3
    """

    # Convert year list items to stings
    year_list = [str(x) for x in year_list]
    # Get list of archives in directory
    archive_list = listdir(directory)
    # Get all files with the year specified
    archive_list = [file for file in archive_list if file[9:13] in year_list]
    # Create list to hold subimages before fusion
    subimage_list = []

    for archive in archive_list:
        scene = LandsatScene(join(directory, archive))
        subimage_list.append(scene.get_band_subimage(band, nw_coords, se_coords))

    # Make sure that all images have the same shape (they should) but
    # truncate extra values anyway (just in-case)
    y_extent = min([image.shape[0] for image in subimage_list])
    x_extent = min([image.shape[1] for image in subimage_list])

    temporal_image = empty((len(subimage_list), y_extent, x_extent))
    for n, image in enumerate(subimage_list):
        temporal_image[n, :, :] = image[:y_extent, :x_extent]

    return temporal_image


def compress_temporal_image(temporal_image):
    """
    Averages frames in the image and then normalizes them to values between [0, 2^16]

    :param temporal_image: Image to compress
    :return: 2D numpy image array of type ubyte
    """
    # Take average of frames
    average_image = average(temporal_image, 0)

    # Normalize the image to values between [-1 and 1]
    image_center = average([min(average_image), max(average_image)])
    image_shift = average_image - image_center
    image_normalized = image_shift/max([-min(image_shift), max(image_shift)])

    # Change image to a ubyte and return
    return img_as_uint(image_normalized)