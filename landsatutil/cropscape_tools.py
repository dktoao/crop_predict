"""
File with functions for extracting data from cropscape
"""

from urllib.request import urlretrieve
from skimage.io import imread
from skimage.transform import resize


def get_crop_data(filename, shape, nw_corner, se_corner, year):
    """
    Downloads cropscape data to an image file

    :param filename: Name of the image file to save to (will add .png extension)
    :param size: size of the image
    :param nw_corner: northwest corner in decimal coordinates (lat, lon)
    :param se_corner: southeast corner in decimal coordinates (lat, lon
    :param year: year to extract data for
    :return: image of crop data
    """

    if '.png' not in filename:
        filename += '.png'

    request = 'http://129.174.131.7/cgi/wms_cdlall.cgi?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=cdl_{0:d}&STYLES=&SRS=EPSG:4326&BBOX={1:f},{2:f},{3:f},{4:f}&WIDTH={5:d}&HEIGHT={6:d}&FORMAT=image/png'.format(
        year, nw_corner[1], se_corner[0], se_corner[1], nw_corner[0], 2000, 2000
    )

    urlretrieve(request, filename)
    crop_data = imread(filename)
    crop_data = resize(crop_data, shape, order=0)
    return crop_data