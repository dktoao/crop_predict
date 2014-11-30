"""
Simple calculations for converting latitude and longitude to meters
"""

# Imports
from math import pi, cos, sin, pow, tan

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


def utm_to_latlon(zone, easting, northing, n_hemisphere=True):
    """
    Converts UTM coordinates (meters) to latitude and longitude

    :param zone: UTM zone
    :param easting: UTM easting parameter
    :param northing: UTM northing parameter
    :param n_hemisphere:
    :return: decimal (latitude, longitude)
    """
    if not n_hemisphere:
        northing = 10000000 - northing

    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    arc = northing / k0
    mu = arc / (a * (1 - pow(e, 2) / 4.0 - 3 * pow(e, 4) / 64.0 - 5 * pow(e, 6) / 256.0))

    ei = (1 - pow((1 - e * e), (1 / 2.0))) / (1 + pow((1 - e * e), (1 / 2.0)))

    ca = 3 * ei / 2 - 27 * pow(ei, 3) / 32.0

    cb = 21 * pow(ei, 2) / 16 - 55 * pow(ei, 4) / 32
    cc = 151 * pow(ei, 3) / 96
    cd = 1097 * pow(ei, 4) / 512
    phi1 = mu + ca * sin(2 * mu) + cb * sin(4 * mu) + cc * sin(6 * mu) + cd * sin(8 * mu)

    n0 = a / pow((1 - pow((e * sin(phi1)), 2)), (1 / 2.0))

    r0 = a * (1 - e * e) / pow((1 - pow((e * sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * tan(phi1) / r0

    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2

    t0 = pow(tan(phi1), 2)
    Q0 = e1sq * pow(cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * pow(dd0, 4) / 24

    fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * pow(dd0, 6) / 720

    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * pow(dd0, 3) / 6.0
    lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * pow(Q0, 2) + 8 * e1sq + 24 * pow(t0, 2)) * pow(dd0, 5) / 120
    _a2 = (lof1 - lof2 + lof3) / cos(phi1)
    _a3 = _a2 * 180 / pi

    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / pi

    if not n_hemisphere:
        latitude = -latitude

    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

    return latitude, longitude