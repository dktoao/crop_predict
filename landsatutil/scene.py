"""
Landsat scene extraction data abstraction utilities.
"""

# Imports
import tarfile
from glob import glob
from shutil import rmtree

class LandsatScene(object):

    def __init__(self, archive_path):
        """
        Create a LandsatScene object from a Landsat data product archive

        :param archive_path: path to the archive
        :return: LandsatScene object
        """

        # Open and extract the archive
        archive = tarfile.open(archive_path)
        archive.extractall('tmp/')
        # Get the name of the metadata file
        self.metadata_file = glob('tmp/*MTL.txt')[0]

        # Read the metadata file and create a dictionary of important parameters
        self._read_metadata()

    def __del__(self):
        """
        Remove the /tmp directory that was created
        """

        rmtree('/tmp')


    def _read_metadata(self):
        """
        Extract contents of metadata file into a dictionary
        """

        # Create Empty Dictionary
        self.metadata = {}
        # Set group to None
        group = 'NONE'

        # Open the data file
        md_file = open(self.metadata_file)

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

    '''
    def __del__(self):
        """
        Deletes the files extracted by __init__
        """

        # Check if the archive exists
    '''
