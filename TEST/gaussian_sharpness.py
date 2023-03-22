import cv2
import os
import numpy as np
from PIL import Image

def increase_grayscale_sharpness(image):
    # Convert the image to grayscale
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a sharpening filter to the grayscale image
    kernel = np.array([[-1,-1,-1], [-1,10,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(image, -1, kernel)
    cv2.imshow('filtered', sharpened)
    cv2.waitKey(0)
    # Add the sharpened image back to the original grayscale image
    sharpened = cv2.addWeighted(image, 1.5, sharpened, -0.5, 0)

    # Normalize the resulting image to ensure that pixel values are between 0 and 255
    sharpened = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

    return sharpened

PATH = os.getcwd()
print('path', PATH)
CAP_PROP_FRAME_WIDTH = 1280
CAP_PROP_FRAME_HEIGHT = 960

# Read the image file
img = cv2.imread('./TEST_APP/sync_test/40cm_1/80us/CAM0_2643939471749.bmp')
img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))

# Convert to Pillow image
pillow_image = Image.fromarray(img)
# Save the image in a different file
pillow_image.save('./TEST_APP/sync_test/40cm_1/50us/CAM0_2643939471749_resize.bmp')

ret, img_contour_binary = cv2.threshold(img, 100, 255, cv2.THRESH_TOZERO)
draw_frame = cv2.cvtColor(img_contour_binary, cv2.COLOR_BGR2GRAY)
contours, hierarchy = cv2.findContours(draw_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



# Apply Gaussian blur to the image array with a kernel size of 5
from scipy.ndimage import gaussian_filter
blurred = cv2.GaussianBlur(draw_frame, (0, 0), 3)

# Increase the sharpness of the image
sharpened = increase_grayscale_sharpness(blurred)

# Display the original and sharpened images side by side
cv2.imshow('origin', draw_frame)
cv2.imshow('blurred', blurred)
cv2.imshow('Sharpened', sharpened)
cv2.waitKey(0)
cv2.destroyAllWindows()

# # Subtract the blurred image from the original image to produce an edge image
# edge = cv2.addWeighted(draw_frame, 1.5, blurred, -0.5, 0)
# # Add the edge image back to the original image to produce a sharpened version
# sharpened = cv2.addWeighted(draw_frame, 1.5, edge, -0.5, 0)

# # Display the original and sharpened images side by side
# cv2.imshow('blurred', blurred)
# cv2.imshow('Original', draw_frame)
# cv2.imshow('Sharpened', sharpened)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# # Draw the contours around the object in red (BGR color format) with thickness of 2 pixels
# cv2.drawContours(draw_frame, contours, -1, (255), 1)
# # Display the image with the object border using OpenCV
# cv2.imshow('Image with Object Border', draw_frame)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# bboxes = []
# # Check if the image was successfully loaded
# if img is None:
#     print('Failed to load image file')
# else:
#     while True:
#         # Display the image using OpenCV
#         cv2.imshow('Image', draw_frame)
#         if len(bboxes) > 0:
#             for i, data in enumerate(bboxes):
#                 (x, y, w, h) = data['bbox']
#                 IDX = data['idx']
#                 cv2.rectangle(draw_frame, (int(x), int(y)), (int(x + w), int(y + h)), (255, 255, 255), 1, 1)
#         KEY = cv2.waitKey(0)
#         if KEY == ord('a'):
#             # set graysum area by bbox
#             bbox = cv2.selectROI("Image", draw_frame)
#             while True:
#                 inputs = input('input led number: ')
#                 if inputs.isdigit():
#                     input_number = int(inputs)
#                     if input_number in range(0, 25):
#                         print('led num ', input_number)
#                         print('bbox ', bbox)
#                         (x, y, w, h) = bbox
#                         bboxes.append({'idx': input_number, 'bbox': bbox})
#                         break
#                     else:
#                         print('led range over')
#                 else:
#                     if inputs == 'exit':
#                         bboxes.clear()
#                         break
#         elif KEY & 0xFF == 27:
#             cv2.destroyAllWindows()
#             break

# print(bboxes)

#         elif KEY & 0xFF == 27:
#             cv2.destroyAllWindows()
#             break

# print(bboxes)
