"""
Utilities for segmenting features from landsat data
"""
from numpy import cos, sin, pi, int_
from skimage.draw import line


def draw_hough_line(image, dist, theta, color=0):
    """
    Draws a line described by the hough transform to an image

    :param image: Image to draw on
    :param dist: Hough transform distance
    :param theta: Hough transform angle
    :param color: intensity to draw line
    """

    rows, cols = image.shape

    if abs(theta) < pi/4:
        # Find the x (col) intercepts
        x0 = int_(dist/cos(theta))
        x1 = int_(x0 - rows * sin(theta))
        intercepts = (0, x0, rows, x1)

    else:
        # Find the y (row) intercepts
        y0 = int_(dist/sin(theta))
        y1 = int_(y0 + cols * cos(theta))
        intercepts = (y0, 0, y1, cols)

    r, c = line(*intercepts)

    # Check to make sure each point stays in the image bounds and draw it
    for n in range(r.size):
        if r[n] >= 0 and c[n] >= 0:
            if r[n] < rows and c[n] < cols:
                image[r[n], c[n]] = color