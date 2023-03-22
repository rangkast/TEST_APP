import cv2
import os
import numpy as np
from PIL import Image
import time
import glob
import sys

from blur import *

# Add Trackers
trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
def createTrackerByName(trackerType):
    # Create a tracker based on tracker name
    if trackerType == trackerTypes[0]:
        tracker = cv2.legacy.TrackerBoosting_create()
    elif trackerType == trackerTypes[1]:
        tracker = cv2.legacy.TrackerMIL_create()
    elif trackerType == trackerTypes[2]:
        tracker = cv2.legacy.TrackerKCF_create()
    elif trackerType == trackerTypes[3]:
        tracker = cv2.legacy.TrackerTLD_create()
    elif trackerType == trackerTypes[4]:
        tracker = cv2.legacy.TrackerMedianFlow_create()
    elif trackerType == trackerTypes[5]:
        tracker = cv2.legacy.TrackerGOTURN_create()
    elif trackerType == trackerTypes[6]:
        tracker = cv2.TrackerMOSSE_create()
    elif trackerType == trackerTypes[7]:
        tracker = cv2.legacy.TrackerCSRT_create()
    else:
        tracker = None
        print('Incorrect tracker name')
        print('Available trackers are:')
        for t in trackerTypes:
            print(t)

    return tracker


def find_center(frame, SPEC_AREA):
    x_sum = 0
    t_sum = 0
    y_sum = 0
    g_c_x = 0
    g_c_y = 0

    (X, Y, W, H) = SPEC_AREA

    # print(X, Y, W, H)

    s = ""
    width_coord = 0
    for h in range(Y, Y + H):
        if width_coord == 0:
            s = s + '%4s' % 'xy'
            for w in range(X, X + W):
                s = s + '%4d' % w
            s = s + '\n'
            width_coord = 1
        s = s + '%4d' % h
        for w in range(X, X + W):
            s = s + '%4d' % frame[h][w]
        s = s + '\n'
    print(s)

    for y in range(Y, Y + H):
        for x in range(X, X + W):
            x_sum += x * frame[y][x]
            t_sum += frame[y][x]


    for x in range(X, X + W):
        for y in range(Y, Y + H):
            y_sum += y * frame[y][x]

    if t_sum != 0:
        g_c_x = x_sum / t_sum
        g_c_y = y_sum / t_sum

    return g_c_x, g_c_y



if __name__ == '__main__':
    print('start test')
    dataset_path = '../simulator/openhmd/dataset_0322/'
    PATH = os.getcwd()
    print('path', PATH)
    img_files_l = glob.glob(dataset_path + 'CAM0*.bmp')
    img_files_r = glob.glob(dataset_path + 'CAM1*.bmp')
    if not img_files_l or not img_files_r:
        print('exit')
        sys.exit()

    index = 0

    print('l cam:', len(img_files_l), ' r cam:', len(img_files_r))
    bboxes = []
    thres = 50
    while True:
        if index >= len(img_files_l) or index >= len(img_files_r):
            break
        imgL = cv2.imread(img_files_l[index])
        imgR = cv2.imread(img_files_l[index])
        if imgL is not None and imgR is not None:
            img = np.hstack((imgL, imgR))

            cv2.imshow('img', img)
            # _, img_gray_filter= filter_1(img, 80, 180, (1280 * 2, 800))
            # cv2.imshow('filter_1', img_gray_filter)

            # _, img_gray_filter = filter_2(img, 100, 170, (640 * 2, 400))
            # cv2.imshow('filter_2', img_gray_filter)

            # _, img_gray_filter = filter_4(img, 100, 255, (640 * 2, 400))
            # cv2.imshow('filter_4', img_gray_filter)

            _, img_gray_filter = filter_7(img, 100, 255, (640 * 2, 400))
            cv2.imshow('filter_7', img_gray_filter)


            # if len(bboxes) > 0:
            #     for i, data in enumerate(bboxes):
            #         (x, y, w, h) = data['bbox']
            #         IDX = data['idx']
            #         gx, gy = find_center(img, (x, y, w, h))                
            #         print('o:', gx, gy, '\n')
            #         cv2.rectangle(img, (int(x), int(y)), (int(x + w), int(y + h)), (255, 255, 255), 1, 1)
            #         cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            #         cv2.circle(img, (int(gx), int(gy)), 1, color=(0, 0, 255), thickness=-1)

            #         gxf, gyf = find_center(img_gray_filtered, (x, y, w, h))
            #         print('f:', gxf, gyf, '\n')
            #         cv2.rectangle(img_gray_filtered, (int(x), int(y)), (int(x + w), int(y + h)), (255, 255, 255), 1, 1)
            #         cv2.cvtColor(img_gray_filtered, cv2.COLOR_GRAY2RGB)
            #         cv2.circle(img_gray_filtered, (int(gxf), int(gyf)), 1, color=(0, 0, 255), thickness=-1)

            #         gxa, gya = find_center(img_gray_th_add, (x, y, w, h))
            #         print('a:', gxa, gya, '\n')
            #         cv2.rectangle(img_gray_th_add, (int(x), int(y)), (int(x + w), int(y + h)), (255, 255, 255), 1, 1)
            #         cv2.cvtColor(img_gray_th_add, cv2.COLOR_GRAY2RGB)
            #         cv2.circle(img_gray_th_add, (int(gxa), int(gya)), 1, color=(0, 0, 255), thickness=-1)
                    
            # img_gray = cv2.resize(img, (640, 400))
            # img_gray_filtered = cv2.resize(img_gray_filtered, (640, 400))
            # img_gray_th_add = cv2.resize(img_gray_th_add, (640, 400))
            # stacked_frame = np.vstack((np.hstack((img_gray, img_gray_filtered)),
            #                             np.hstack((img_gray, img_gray_th_add))))

            # if stacked_frame is None:
            #     print('none')
            #     break

        KEY = cv2.waitKey(8)

        if KEY == ord('a'):
            # set graysum area by bbox
            cv2.imshow("img", stacked_frame)
            # bbox = cv2.selectROI("img", stacked_frame)

            while True:
                inputs = input('input led number: ')
                if inputs.isdigit():
                    input_number = int(inputs)
                    if input_number in range(0, 25):
                        print('led num ', input_number)
                        print('bbox ', bbox)
                        (x, y, w, h) = bbox
                        bboxes.append({'idx': input_number, 'bbox': bbox})
                        break
                    else:
                        print('led range over')
                else:
                    if inputs == 'exit':
                        bboxes.clear()
                        break
  

        elif KEY == 27:
            break

        # cv2.imshow('img', stacked_frame)
        index += 1
        if index >= len(img_files_l) or index >= len(img_files_r):
            index = 0

    cv2.destroyAllWindows()

