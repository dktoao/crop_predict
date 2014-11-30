from numpy import array
from skimage.io import imsave

from landsatutil.cropscape_tools import get_crop_data

# Very small area
nw_corner = array([396210, 4175310])
se_corner = array([404460, 4167150])

# Calculate file names
fname_post = '_{0}_{1}_{2}_{3}.'.format(nw_corner[0], nw_corner[1], se_corner[0], se_corner[1])
fname_template = 'tmp/{0}' + fname_post + '{1}'

field_shape = (300,300)

for year in [2008, 2009, 2010, 2011, 2012]:
    crops = get_crop_data(fname_template.format(str(year), 'png'), field_shape, 13, nw_corner, se_corner, year)