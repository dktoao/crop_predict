"""
Collates crop data and creates a descriptive csv file
"""

from numpy import array, where, mean, var
from skimage.io import imread
from os import listdir
from pandas import read_csv

from landsatutil.scene import LandsatScene

# Very small area
nw_corner = array([396210, 4175310])
se_corner = array([404460, 4167150])

# Calculate file names
fname_post = '_{0}_{1}_{2}_{3}.'.format(nw_corner[0], nw_corner[1], se_corner[0], se_corner[1])
fname_template = 'tmp/{0}' + fname_post + '{1}'

# Open the field mask
fname_field_mask = fname_template.format('field_mask', 'png')
field_mask = imread(fname_field_mask)

# Open the field properties file
fname_field_props = fname_template.format('field_props', 'csv')
field_props = read_csv(fname_field_props)

# Create an output file
result = open(fname_template.format('field_data', 'csv'), 'w')
print(','.join(['label', 'year', 'month', 'day', 'hour',
                'b1_ref', 'b1_var',
                'b2_ref', 'b2_var',
                'b3_ref', 'b3_var',
                'b4_ref', 'b4_var',
                'b5_ref', 'b5_var',
                'b6_ref', 'b6_var',
                'b7_ref', 'b7_var'
                ]), file=result)


# Open a landsat scene for the specified years and write data to csv
# Convert year list items to stings
year_list = ['2008', '2009', '2010', '2011']
# Get list of archives in directory
archive_list = listdir('tmp/')
# Get all files with the year specified
archive_list = [file for file in archive_list if file[9:13] in year_list]

for line in field_props.iterrows():
    props = line[1]
    field_label = props['label']
    field_indices = where(field_mask == field_label)
    nw_corner_field = array([nw_corner[0] + 30*(props['nw_row']),
                             nw_corner[1] - 30*(props['nw_col'])])
    se_corner_field = array([nw_corner[0] + 30*(props['se_row']),
                             nw_corner[1] - 30*(props['se_col'])])
    for archive_name in archive_list:
        fscene = LandsatScene(archive_name)
        year = fscene.year
        month = fscene.month
        day = fscene.day
        hour = fscene.hour
        reflectance = []
        for band in range(1, 8):
            field_reflectance = fscene.get_band_subimage(band, nw_corner_field, se_corner_field)
            single_field_mask = field_mask[props['nw_col']:props['se_col'],
                                           props['nw_row']:props['se_row']]/props['label']
            field_reflectance *= field_reflectance * single_field_mask
            reflectance.append(mean(field_reflectance[where(field_reflectance != 0)]))
            reflectance.append(var(field_reflectance[where(field_reflectance != 0)]))

        data_list = [props['label'], year, month, day, hour] + reflectance
        data_list = [str(x) for x in data_list]
        print(','.join(data_list), file=result)

