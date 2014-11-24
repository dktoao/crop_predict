"""
Collates crop data and creates a descriptive csv file
"""

from numpy import array, max, int_
from skimage.io import imread
from os import listdir

from landsatutil.scene import LandsatScene

# Small Area
nw_corner = array([390000, 4188090])
se_corner = array([423900, 4164000])

# Calculate file names
fname_post = '_{0}_{1}_{2}_{3}.'.format(nw_corner[0], nw_corner[1], se_corner[0], se_corner[1])
fname_template = 'tmp/{0}' + fname_post + '{1}'

# Open the field mask
fname_field_mask = fname_template.format('field_mask', 'png')
field_mask = imread(fname_field_mask)

# Open the field properties file
fname_field_props = fname_template.format('field_props', 'csv')
field_props = open(fname_field_props, 'r')
data_out_header = field_props.readline().split(',')
data_out_header.extend([
    'year', 'month', 'day', 'hour', 'minute',
    'reflect1', 'var1',
    'reflect2', 'var2',
    'reflect3', 'var3',
    'reflect4', 'var4',
    'reflect5', 'var5',
    'reflect6', 'var6',
    'reflect7', 'var7',
])

# Open a landsat scene for the specified years and write data to csv
# Convert year list items to stings
year_list = ['2008', '2009', '2010', '2011']
# Get list of archives in directory
archive_list = listdir('tmp/')
# Get all files with the year specified
archive_list = [file for file in archive_list if file[9:13] in year_list]
# Open a file to write csv data to
data_out = open(fname_template.format('crop_data', 'csv'), 'w')

for archive_path in archive_list:
    scene = LandsatScene(archive_path)
    for band in range(1, 8):
        band_image = scene.get_band_subimage(band, nw_corner, se_corner)
        field_props.seek(1)
        for line in field_props:
            data = [int_(x) for x in line.split(',')]
            data.extend([str(x) for x in [scene.year, scene.month, scene.day, scene.hour, scene.minute]])








