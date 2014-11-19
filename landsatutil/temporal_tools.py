"""
Tools for temporal data extraction
"""

# Imports
from os import listdir

def collect_bands(band, year_list, directory):
    """
    Collects sub-images of each band for each year and puts them
    into a 3-dimensional array with the 3rd dimension being time

    :param band: band of interest
    :param year_list: list of years to collect
    :param directory: directory to search for available datasets
    :return: A three dimensional numpy array with the images
    """

    # Get list of archives in directory
    archive_list =