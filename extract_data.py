from skimage.io import imread, imsave
from skimage.morphology import white_tophat, disk, binary_opening, binary_erosion, watershed, binary_opening, rectangle
from skimage.filter import threshold_otsu, sobel
from numpy import int16, uint8, min, max, abs, zeros_like
import matplotlib.pyplot as plt

band4 = int16(imread('/home/dktoao/Desktop/LT40340341989186XXX05/LT40340341989186XXX05_B4.TIF'))
band1 = int16(imread('/home/dktoao/Desktop/LT40340341989186XXX05/LT40340341989186XXX05_B1.TIF'))
band2 = int16(imread('/home/dktoao/Desktop/LT40340341989186XXX05/LT40340341989186XXX05_B2.TIF'))
band3 = int16(imread('/home/dktoao/Desktop/LT40340341989186XXX05/LT40340341989186XXX05_B3.TIF'))

print('Subtracting Images')
fields = band4 - band3
#fields2 = band4 - band1
print('Normalizing Images')
fields = fields + abs(min(fields))
#fields2 = fields2 + abs(min(fields2))
fields = uint8((255/max(fields))*fields)[1400:5500, 5000:7000]
#fields2 = uint8((255/max(fields2))*fields2)[1400:5500, 5000:7000]
print('Finding Tophat')
fields = white_tophat(fields, disk(15))
#fields2 = white_tophat(fields2, disk(15))
print('Thresholding Image')
#elevation_map = sobel(fields)
#markers = zeros_like(fields)
threshold = threshold_otsu(fields, nbins=1)
#threshold2 = threshold_otsu(fields2, nbins=1)
#markers[fields >= threshold] = 1
#fields = watershed(elevation_map, markers)
fields = fields >= threshold
#fields2 = fields2 >= threshold2
print('Separating fields')
fields = binary_opening(fields, rectangle(15, 2))
fields = binary_opening(fields, rectangle(2, 15))
plt.imshow(fields)
plt.show()
imsave('fields.png', uint8(fields)*255)