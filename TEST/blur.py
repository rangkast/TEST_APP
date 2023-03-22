import cv2
import os
import numpy as np
from PIL import Image
import time
import glob
import sys
import json
import traceback
import re
import matplotlib.pyplot as plt
import time



def zoom_factory(ax, base_scale=2.):
    def zoom_fun(event):
        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        xdata = event.xdata
        ydata = event.ydata
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)
        # set new limits
        ax.set_xlim([xdata - cur_xrange * scale_factor,
                     xdata + cur_xrange * scale_factor])
        ax.set_ylim([ydata - cur_yrange * scale_factor,
                     ydata + cur_yrange * scale_factor])
        # force re-draw
        plt.draw()

    # get the figure of interest
    fig = ax.get_figure()
    # attach the call back
    fig.canvas.mpl_connect('scroll_event', zoom_fun)

    # return the function
    return zoom_fun



def init_coord_json(file):
    print(init_coord_json.__name__)
    try:
        json_file = open(file)
        jsonObject = json.load(json_file)
        model_points = jsonObject.get('TrackedObject').get('ModelPoints')
        pts = [0 for i in range(len(model_points))]
        for data in model_points:
            idx = data.split('Point')[1]
            x = model_points.get(data)[0]
            y = model_points.get(data)[1]
            z = model_points.get(data)[2]
            u = model_points.get(data)[3]
            v = model_points.get(data)[4]
            w = model_points.get(data)[5]
            r1 = model_points.get(data)[6]
            r2 = model_points.get(data)[7]
            r3 = model_points.get(data)[8]

            pts[int(idx)] = np.array([x, y, z])

            print(''.join(['{ .pos = {{', f'{x}', ',', f'{y}', ',', f'{z}',
                                ' }}, .dir={{', f'{u}', ',', f'{v}', ',', f'{w}', ' }}, .pattern=', f'{idx}', '},']))
    except:
        print('exception')
        traceback.print_exc()
    return pts



def get_pose(path):
    data = {}
    with open(path, 'r') as f:
        current_key = ''
        for line in f:
            # Split the line into key-value pairs
            pairs = line.strip().split(':')
            if len(pairs) == 2:
                # If the line contains a key-value pair, add it to the dictionary
                key = pairs[0].strip()
                values = [float(v.strip()) for v in pairs[1].split(',')]
                data.setdefault(current_key, {})[key] = values
            elif len(pairs) == 1:
                # If the line only contains a key, update the current key
                current_key = pairs[0].strip()
                extension = []
            else:
                extension.append(line.strip())
                data.setdefault(current_key, {})['extension'] = extension

    RPE = {'F0': [], 'F1': [], 'L0': [], 'L1': []}
    for key, value in data.items():
        if 'extension' in value:
            for d in data[key]['extension']:
                parse = d.split(' ')
                if float(parse[4].split(':')[1]) > 0.0:
                    RPE[parse[0].split(':')[0]].append(float(parse[4].split(':')[1]))
                else:
                    RPE[parse[0].split(':')[0]].append(0.0)

    return data, RPE


def contrast(p, num):
    pic = p.copy()
    pic = pic.astype('int16')
    pic = np.clip(pic + (pic - 128) * num, 0, 255)
    pic = pic.astype('uint8')
    return pic

def increase_grayscale_sharpness(image):
    kernel = np.array([[-1,-1,-1], [-1,10,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(image, -1, kernel)
    sharpened = cv2.addWeighted(image, 1.5, sharpened, -0.5, 0)
    sharpened = cv2.add(sharpened, 40)
    sharpened = contrast(sharpened, 2)
    # sharpened = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    return sharpened


def filter_1(img, minthres, maxthres, RES):
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img_gray_th= cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_BINARY)
    blurred = cv2.GaussianBlur(img_gray_th, (0, 0), 2.0)
    sharpened = increase_grayscale_sharpness(blurred)

    return img_gray_th, sharpened



def filter_2(img, minthres, maxthres, RES):
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_binary = cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_BINARY)
    blurred = cv2.GaussianBlur(img_binary, (5, 5), 2.0)
    return img_gray, blurred


def filter_3(img, minthres, maxthres, RES):
    import math
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    array = np.array(img_gray)
    for i, data in enumerate(array):
        for ii, blob in enumerate(data):
            if blob < minthres:
                array[i][ii] = 0
            elif blob >= maxthres:
                array[i][ii] = maxthres
    blurred = cv2.GaussianBlur(array, (3, 3), 2.0)
    return img_gray, blurred


def filter_4(img, minthres, maxthres, RES):
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_binary = cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_TOZERO)
    blurred = cv2.GaussianBlur(img_binary, (3, 3), 2.0)
    kernel = np.array([[-1,-1,-1], [-1,10,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(blurred, -1, kernel)
    sharpened = cv2.addWeighted(blurred, 1.5, sharpened, -0.4, 0)

    return img_gray, sharpened



def filter_5(img, minthres, maxthres, RES):
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_binary = cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_TOZERO)

    img_median = cv2.medianBlur(img_binary, 5)
    blurred = cv2.GaussianBlur(img_median, (3, 3), 2.0)

    return img_gray, blurred


def filter_6(img, minthres, maxthres, RES):
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_binary = cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_TOZERO)

    blurred = cv2.GaussianBlur(img_binary, (5, 5), 2.0)

    return img_gray, blurred


def filter_7(img, minthres, maxthres, RES):
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_binary = cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_TOZERO)
    blurred = cv2.GaussianBlur(img_binary, (3,3), 5.0)
    # ret, img_binary = cv2.threshold(blurred, minthres, maxthres, cv2.THRESH_TOZERO)
    # img_binary = cv2.normalize(img_binary, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    return img_gray, blurred

# def filter_8(img, minthres, maxthres, RES):
#     (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
#     img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))

#     img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     ret, img_binary = cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_TOZERO)
#     # Define a structuring element (kernel) for dilation
#     kernel = np.ones((3,3), np.uint8)

#     # Apply morphology dilation with kernel
#     img_dilated = cv2.dilate(img_binary, kernel, iterations=1)
#     return img_gray, img_dilated

def filter_8(img, minthres, maxthres, RES):
    (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
    img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    img_median = cv2.medianBlur(img_gray, 3)
    ret, img_binary = cv2.threshold(img_median, minthres, maxthres, cv2.THRESH_TOZERO)
    blurred = cv2.GaussianBlur(img_binary, (3, 3), 3.5)

    return img_gray, blurred


# def filter_9(img, minthres, maxthres, RES):
#     (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT) = RES
#     img = cv2.resize(img, (CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT))

#     img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     cimg = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
#     ret, img_binary = cv2.threshold(img_gray, minthres, maxthres, cv2.THRESH_BINARY)

#     # blurred = cv2.medianBlur(img_binary, 3)
#     blurred = cv2.GaussianBlur(img_binary, (5, 5), 2.0)
#     circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 2, param1=80, param2=10, minRadius=2, maxRadius=15)

#     if type(circles) != type(None):
#         circles = np.uint16(np.around(circles))
#         for i in circles[0, :]:
#             cv2.circle(cimg, (i[0], i[1]), i[2], (0,255,0), 1)
#             cv2.circle(cimg, (i[0], i[1]), 1, (0,0,255), 1)


#     return img_gray, cimg

