"""
Landsat scene extraction data abstraction utilities.
"""

# Imports
import tarfile
from numpy import array, abs, float_
from numpy import int32 as int_
from skimage.io import imread
from os.path import isdir, basename, join
from os import listdir

# Constants
TMP_DIR = 'tmp'


class LandsatScene(object):

    def __init__(self, archive_path):
        """
        Create a LandsatScene object from a Landsat data product archive

        :param archive_path: path to the archive
        :return: LandsatScene object
        """

        # Check if the archive has already been extracted
        self.archive_name = join(TMP_DIR, basename(archive_path).split('.')[0])
        if not isdir(self.archive_name):
            archive = tarfile.open(archive_path)
            archive.extractall(self.archive_name)
            archive.close()

        # Open the archive
        file_list = listdir(self.archive_name)
        try:
            self.metadata_file = [name for name in file_list if 'MTL.txt' in name][0]
        except IndexError:
            print('Could not find metadata file in archive')

        # Read the metadata file
        self._read_metadata()

        # Get the scene id
        self.scene_id = self.metadata['METADATA_FILE_INFO/LANDSAT_SCENE_ID']

        # Get image size info pixel
        self.pixel_size = float(self.metadata['PROJECTION_PARAMETERS/GRID_CELL_SIZE_REFLECTIVE'])
        # Get the number of pixels in the images
        self.image_size = array([
            int_(self.metadata['PRODUCT_METADATA/REFLECTIVE_SAMPLES']),
            int_(self.metadata['PRODUCT_METADATA/REFLECTIVE_LINES']),
        ], dtype=int_)

        # Get UTM (per unit pixel) coordinate extents (4x2 matrix with columns NW, NE, SW, SE and rows X, Y)
        self.coords = array([
            [
                float(self.metadata['PRODUCT_METADATA/CORNER_UL_PROJECTION_X_PRODUCT']),
                float(self.metadata['PRODUCT_METADATA/CORNER_UL_PROJECTION_Y_PRODUCT']),
            ],
            [
                float(self.metadata['PRODUCT_METADATA/CORNER_UR_PROJECTION_X_PRODUCT']),
                float(self.metadata['PRODUCT_METADATA/CORNER_UR_PROJECTION_Y_PRODUCT']),
            ],
            [
                float(self.metadata['PRODUCT_METADATA/CORNER_LL_PROJECTION_X_PRODUCT']),
                float(self.metadata['PRODUCT_METADATA/CORNER_LL_PROJECTION_Y_PRODUCT']),
            ],
            [
                float(self.metadata['PRODUCT_METADATA/CORNER_LR_PROJECTION_X_PRODUCT']),
                float(self.metadata['PRODUCT_METADATA/CORNER_LR_PROJECTION_Y_PRODUCT']),
            ],
        ])/self.pixel_size

        # Get the radiance correction functions
        n = 1
        self.band_correction = []
        while True:
            # Get the key names
            data_mult_key = 'RADIOMETRIC_RESCALING/RADIANCE_MULT_BAND_{0:d}'.format(n)
            data_add_key = 'RADIOMETRIC_RESCALING/RADIANCE_ADD_BAND_{0:d}'.format(n)

            # Make sure that the key name exists
            if data_mult_key not in self.metadata.keys():
                break

            # create coefficients for linear equation m*x + b
            m = float(self.metadata[data_mult_key])
            b = float(self.metadata[data_add_key])
            self.band_correction.append(lambda x: m*x + b)

            n += 1

    def _read_metadata(self):
        """
        Extract contents of metadata file into a dictionary
        """

        # Create Empty Dictionary
        self.metadata = {}
        # Set group to None
        group = 'NONE'

        # Open the data file
        md_file = open(join(self.archive_name, self.metadata_file), 'r')

        # Extract data from each line
        for line in md_file:
            line_items = line.split('=')
            if len(line_items) != 2:
                continue
            param = line_items[0].strip(' \"\n')
            value = line_items[1].strip(' \"\n')

            if param == 'GROUP':
                group = value
            elif param == 'END_GROUP':
                pass
            else:
                self.metadata['{0}/{1}'.format(group, param)] = value

    def coords_to_pixel(self, coords):
        """
        Function for interpolating the pixel location of the given UTM coordinates

        :param coords: array with [x, y] coordinates (meters)
        :return: pixel coordinates as an array [r, c]
        """

        # Divide Through by Pixel Size and subtract offset
        # negative values in the y must be flipped as image and utm y coordinates
        # are in opposite directions
        pixel_coords = abs(coords/self.pixel_size - self.coords[0, :])

        return int_(pixel_coords)

    def get_band_subimage(self, band, nw_coords, se_coords, convert=True):
        """
        Gets a sub-image from the specified band from the north west coordinates
        to the south east coordinates.

        :param band: Band of interest (1: blue, 2: green, etc)
        :param nw_coords: North west coordinates in UTM (meters)
        :param se_coords: South east coordinates in UTM (meters)
        :param convert: If true, converts the image to radiance
        :return: Scene subimage at at the desired coordinates as numpy float array
        """
        # Read the file
        image_file = '{0}/{1}/{1}_B{2:d}.TIF'.format(TMP_DIR, self.scene_id, band)
        band_image = float_(imread(image_file))

        # Get pixel coordinates
        nw_pixel = self.coords_to_pixel(nw_coords)
        se_pixel = self.coords_to_pixel(se_coords)

        # Truncate
        subimage = band_image[nw_pixel[1]:se_pixel[1], nw_pixel[0]:se_pixel[0]]
        # Convert to radiance if needed
        if convert:
            return self.band_correction[band](subimage)
        else:
            return subimage
