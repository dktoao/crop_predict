"""
Simple calculations for converting latitude and longitude to meters
"""

# Imports
from math import pi, cos

R_EARTH = (6.371*10e6)/2.0


def dist_lat(lat_diff):
    """
    Calculates the distance in meters along a latitude difference

    :param lat_diff: latitude difference in degrees
    :return: distance in meters
    """

    return lat_diff*(pi/180.0)*R_EARTH


def dist_lon(lon_diff, lat):
    """
    Calculates the distance in meters along a longitude difference at a given
    latitude

    :param lon_diff: longitude difference in degrees
    :param lat: latitude to calculate distance in degrees
    :return: distance along the longitude distance in meters
    """

    radius = cos(lat*(pi/180.0))*R_EARTH
    return lon_diff*(pi/180.0)*radius