# Code for image processing once drone sends picture back to computer

import cv2

cv2.namedWindow("The Window", cv2.WINDOW_AUTOSIZE)

# reading in and opening image in processing window
orig = cv2.imread("test.jpg")
cv2.imshow("The Window", orig)
cv2.waitKey(5000)

# since images are in color, need to decide parameters for thresholding
# to make easier, switch color scheme to hue format (HSV) (on a plane: hue = x, value = y, saturation = z)
# in opencv, hue ranges from 0 to 180, value ranges from 0 to 255
hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)
cv2.imshow("The Window", hsv)
cv2.waitKey(5000)

# defining the threshold to define "edges" in the image
# creating a 'binary' image - anything less than xyz becomes black, anything over xyz becomes white
thresh = cv2.inRange(hsv, (160, 128, 128), (180, 255, 255))
cv2.imshow("The Window", thresh)
cv2.waitKey(5000)

# isolating the contours of only the white pixels (ie the ring only)
# and returning a list of lists for x-y coordinate chains, representing the pixels
_, outlines, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

print("Num contours =", len(outlines))

# returning to RGB color scheme, with the designated contours (-1 indicates all)
# colored specifically to highlight those areas
cv2.drawContours(orig, outlines, -1, (0, 255, 0), 3)
cv2.imshow("The Window", orig)
cv2.waitKey(5000)

# loop to go through each pixel chain and do more detailed processing
for line in outlines:
    # removes any chain under our predetermined minimum length (in this case, 5)
    if len(line) >= 5:
        # fitEllipse returns (image coordinates of center of ellipse, pair of vertical and horizontal 'lengths' of ellipse
        # (when they are equal = a circle), and )
        ellipse = cv2.fitEllipse(line)
        print("length =", len(line), "\nParams =", ellipse)
        # printing ellipses onto original image
        cv2.ellipse(orig, ellipse, (255, 0, 0), 2)
    else:
        print("length =", len(line))

# if orig is not None:
#     if orig is not False:



