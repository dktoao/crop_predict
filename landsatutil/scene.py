"""
Landsat scene extraction data abstraction utilities.
"""

# Imports
import tarfile


class LandsatScene(object):

    def __init__(self, archive_path):
        """
        Create a LandsatScene object from a Landsat data product archive

        :param archive_path: path to the archive
        :return: LandsatScene object
        """

        # Open the archive
        self.archive = tarfile.open(archive_path)
        # Get the metadata file
        try:
            self.metadata_file = [name for name in self.archive.getnames() if 'MTL.txt' in name][0]
        except IndexError:
            print('Could not find metadata file in archive')

        # Read the metadata file
        self._read_metadata()

        #TODO: Fix this
        # Get coordinate Extents
        self.latitude_extent = (
            float(self.metadata['PRODUCT_METADATA/CORNER_LR_LAT_PRODUCT']),
            float(self.metadata['PRODUCT_METADATA/CORNER_UL_LAT_PRODUCT']),
        )
        self.longitude_extent = (
            float(self.metadata['PRODUCT_METADATA/CORNER_LL_LON_PRODUCT']),
            float(self.metadata['PRODUCT_METADATA/CORNER_UR_LON_PRODUCT']),
        )

        # Get the number of pixels in the images
        self.image_size = (
            int(self.metadata['PRODUCT_METADATA/REFLECTIVE_SAMPLES']),
            int(self.metadata['PRODUCT_METADATA/REFLECTIVE_LINES'])
        )

    def __del__(self):
        """
        Closes the archive upon exit
        """
        self.archive.close()

    def _read_metadata(self):
        """
        Extract contents of metadata file into a dictionary
        """

        # Create Empty Dictionary
        self.metadata = {}
        # Set group to None
        group = 'NONE'

        # Open the data file
        md_file = self.archive.extractfile(self.metadata_file).read().decode().splitlines()

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

    def coords_to_pixel(self, lat, lon):
        """
        Function for interpolating the pixel location of the given coordinates

        :param lat: decimal latitude of the desired pixel
        :param lon: decimal longitude of the desired pixel
        :return: pixel coordinates as an int tuple (r, c)
        """

        # Check that the coordinates are contained in the image
        if (lat <= self.latitude_extent[0]) or (lat >= self.latitude_extent[1]):
            raise ValueError('Provided Latitude is out of image bounds')
        if (lon <= self.longitude_extent[1]) or (lon >= self.longitude_extent[1]):
            raise ValueError('Provided Longitude is out of image bounds')

        row_fraction = (lat - self.latitude_extent[0]) / \
                       (self.latitude_extent[1] - self.latitude_extent[0])
        col_fraction = (lon - self.longitude_extent[0]) / \
                       (self.longitude_extent[1] - self.longitude_extent[0])

        return row_fraction * self.image_size[0], col_fraction * self.image_size[1]


