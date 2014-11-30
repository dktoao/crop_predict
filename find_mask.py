"""
Scipt that finds a crop field mask from satellite data
"""

from numpy import array, logical_not, logical_and, int_, uint8, max, pi
import matplotlib.pyplot as plt
from skimage.io import imsave, use_plugin
from skimage.transform import hough_line, hough_line_peaks
from skimage.morphology import disk, white_tophat, binary_closing, rectangle, remove_small_objects, binary_opening
from skimage.measure import label, regionprops

from landsatutil.temporal import collect_bands, compress_temporal_image
from landsatutil.segmentation import draw_hough_line

# Set plugin
use_plugin('freeimage')

# UTM coordinates zone 13
# Very small area
nw_corner = array([396210, 4175310])
se_corner = array([404460, 4167150])

# Small Area
#nw_corner = array([390000, 4188090])
#se_corner = array([423900, 4164000])

# Large Area
#nw_corner = array([387494, 4218065])
#se_corner = array([440000, 4160000])

# Calculate file names
fname_post = '_{0}_{1}_{2}_{3}.'.format(nw_corner[0], nw_corner[1], se_corner[0], se_corner[1])
fname_template = 'tmp/{0}' + fname_post + '{1}'

# Get temporal bands and compress them into a field mask
print('Collecting Bands')
temporal_band_4 = collect_bands(
    4,
    nw_corner,
    se_corner,
    list(range(2000, 2012)),
    'Bulk Order 397884/L4-5 TM'
)
temporal_band_3 = collect_bands(
    3,
    nw_corner,
    se_corner,
    list(range(2000, 2010)),
    'Bulk Order 397884/L4-5 TM'
)
temporal_nvdi = temporal_band_4 - temporal_band_3
field_mask = compress_temporal_image(temporal_nvdi)
print('Detecting Fields')
field_mask = white_tophat(field_mask, disk(14))
field_mask = field_mask >= 2

# Find the area containing the fields
field_area = binary_closing(field_mask, rectangle(50, 50))
between_fields = logical_and(field_area, logical_not(field_mask))

# Find the roads and separate the fields
# Separate out into smaller blocks
print('Separating Fields in image')
stride = 200  # pixels
num_col_strides = int_(between_fields.shape[0]/stride)
num_row_strides = int_(between_fields.shape[1]/stride)
r_stride = int_(between_fields.shape[0]/num_col_strides)
c_stride = int_(between_fields.shape[1]/num_row_strides)

for r in range(num_row_strides):
    for c in range(num_col_strides):
        h, theta, d = hough_line(between_fields[r*r_stride:(r+1)*r_stride, c*c_stride:(c+1)*c_stride])
        threshold = 0  #0.0005*max(h)
        h, theta, d = hough_line_peaks(h, theta, d, min_distance=20, threshold=threshold)
        for n in range(len(theta)):
            if abs(theta[n]) < 0.1 or abs(theta[n]) > ((pi/2) - 0.1):
                draw_hough_line(field_mask[r*r_stride:(r+1)*r_stride, c*c_stride:(c+1)*c_stride], d[n], theta[n])

# do a few small openings and then remove small objects
#field_mask = binary_opening(field_mask, rectangle(1, 3))
#field_mask = binary_opening(field_mask, rectangle(3, 1))
remove_small_objects(field_mask, 100, 1, True)
field_mask = label(field_mask, 4, 0)
field_props = regionprops(field_mask)

# Write field_props to csv file
out_file = open(fname_template.format('field_props', 'csv'), 'w')
print('label,area,nw_col,nw_row,se_col,se_row', file=out_file)
for prop in field_props:
    print(','.join([str(x) for x in [
        prop.label,
        prop.area,
        prop.bbox[0],
        prop.bbox[1],
        prop.bbox[2],
        prop.bbox[3],
    ]]), file=out_file)

# Visualize Data
plt.figure()
plt.imshow(field_mask)
plt.show()

# Save the field mask
save_file_name = fname_template.format('field_mask', 'png')
imsave(save_file_name, uint8(field_mask)+1)
