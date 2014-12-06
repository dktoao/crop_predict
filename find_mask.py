"""
Script that finds a crop field mask from satellite data
"""

from numpy import array, logical_not, logical_and, int_, uint16, pi, where
import matplotlib.pyplot as plt
from skimage.io import imsave, use_plugin
from skimage.transform import hough_line, hough_line_peaks
from skimage.morphology import binary_erosion, binary_closing, binary_opening, rectangle, remove_small_objects
from skimage.measure import label, regionprops

from landsatutil.temporal import collect_bands, compress_temporal_image
from landsatutil.segmentation import draw_hough_line

# Set plugin
use_plugin('freeimage')

# UTM coordinates zone 13
# Very small area
#nw_corner = array([396210, 4175310])
#se_corner = array([404460, 4167150])

# Small Area
#nw_corner = array([390000, 4188090])
#se_corner = array([423900, 4164000])

# Large Area
nw_corner = array([387494, 4218065])
se_corner = array([440000, 4160000])

# Calculate file names
fname_post = '_{0}_{1}_{2}_{3}.'.format(nw_corner[0], nw_corner[1], se_corner[0], se_corner[1])
fname_template = 'tmp/{0}' + fname_post + '{1}'

# Get temporal bands and compress them into a field mask
print('Collecting Bands')
temporal_band_4 = collect_bands(
    4,
    nw_corner,
    se_corner,
    list(range(2005, 2012)),
    'Bulk Order 397884/L4-5 TM'
)
temporal_band_3 = collect_bands(
    3,
    nw_corner,
    se_corner,
    list(range(2005, 2012)),
    'Bulk Order 397884/L4-5 TM'
)
temporal_nvdi = (temporal_band_4 - temporal_band_3) / (temporal_band_4 + temporal_band_3)
field_mask = compress_temporal_image(temporal_nvdi)
imsave(fname_template.format('temporal_nvdi', 'png'), field_mask)

# Detect Fields
print('Detecting Fields')
field_mask = field_mask >= 10

# Find the area containing the fields
field_area = binary_closing(binary_erosion(field_mask, rectangle(5, 5)), rectangle(50, 50))
between_fields = logical_and(field_area, logical_not(field_mask))

# Find the roads and separate the fields
# Separate out into smaller blocks
print('Separating Fields in image')
for stride in [100, 200, 400]:  # pixels
    num_row_strides = int_(between_fields.shape[0]/stride)
    num_col_strides = int_(between_fields.shape[1]/stride)
    r_stride = int_(between_fields.shape[0]/num_row_strides)
    c_stride = int_(between_fields.shape[1]/num_col_strides)

    for r in range(num_row_strides+1):
        for c in range(num_col_strides+1):
            h, theta, d = hough_line(between_fields[r*r_stride:(r+1)*r_stride, c*c_stride:(c+1)*c_stride])
            threshold = 0  #0.0005*max(h)
            h, theta, d = hough_line_peaks(h, theta, d, min_distance=20, threshold=threshold)
            for n in range(len(theta)):
                if abs(theta[n]) < 0.1 or abs(theta[n]) > ((pi/2) - 0.1):
                    draw_hough_line(field_mask[r*r_stride:(r+1)*r_stride, c*c_stride:(c+1)*c_stride], d[n], theta[n])


# do a few small openings
field_mask = binary_opening(field_mask, rectangle(1, 5))
field_mask = binary_opening(field_mask, rectangle(5, 1))
imsave(fname_template.format('segmented_fields', 'png'), field_mask)

# Label fields
field_mask = label(field_mask, 4, 0) + 1
remove_small_objects(field_mask, 100, 1, True)
field_props = regionprops(field_mask)

# Write field_props to csv file
out_file = open(fname_template.format('field_props', 'csv'), 'w')
print('label,area,center_row,center_col,nw_col,nw_row,se_col,se_row', file=out_file)
for prop in field_props:
    if (prop.area > 100) and (prop.area < 700):
        print(','.join([str(x) for x in [
            prop.label,
            prop.area,
            prop.centroid[0],
            prop.centroid[1],
            prop.bbox[0],
            prop.bbox[1],
            prop.bbox[2],
            prop.bbox[3],
        ]]), file=out_file)
    else:
        field_mask[where(field_mask == prop.label)] = 0

# Visualize Data
plt.figure()
plt.imshow(field_mask)

'''
for prop in field_props:
    plt.annotate(str(prop.label), xy=array([prop.centroid[1], prop.centroid[0]]))
'''
plt.show()

# Save the field mask
save_file_name = fname_template.format('field_mask', 'png')
imsave(save_file_name, uint16(field_mask))
