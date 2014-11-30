"""
File with functions for extracting data from cropscape
"""

from urllib.request import urlretrieve
from skimage.io import imread
from skimage.transform import resize

from .earth_calc import utm_to_latlon


def get_crop_data(filename, shape, zone, nw_corner, se_corner, year, n_hemisphere=True):
    """
    Downloads cropscape data to an image file

    :param filename: Name of the image file to save to (will add .png extension)
    :param shape: pixel shape of the image
    :param zone: UTM coordinate zone
    :param nw_corner: northwest corner in UTM coordinates (easting, northing) (meters)
    :param se_corner: southeast corner in UTM coordinates (easting, northing) (meters)
    :param year: year to extract data for
    :return: image of crop data
    """

    nw_lat, nw_lon = utm_to_latlon(zone, nw_corner[0], nw_corner[1], n_hemisphere=n_hemisphere)
    se_lat, se_lon = utm_to_latlon(zone, se_corner[0], se_corner[1], n_hemisphere=n_hemisphere)

    if '.png' not in filename:
        filename += '.png'

    request = 'http://129.174.131.7/cgi/wms_cdlall.cgi?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=cdl_{0:d}&STYLES=&SRS=EPSG:4326&BBOX={1:f},{2:f},{3:f},{4:f}&WIDTH={5:d}&HEIGHT={6:d}&FORMAT=image/png'.format(
        year, nw_lon, se_lat, se_lon, nw_lat, shape[0], shape[1]
    )

    urlretrieve(request, filename)
    crop_data = imread(filename)
    return crop_data