import cv2
import os
import numpy as np
from PIL import Image
import time
import glob
import sys
from blur import *


def save_file(name, image):
    # convert the NumPy array to an image object
    img = Image.fromarray(image)
    # img = Image.fromarray(image, mode='GRAY')
    file_name = name.split("/")
    print(file_name)
    for finder in file_name:
        if '.bmp' in finder:
            file = finder.split(".")
            file_blur = f'{file[0]}' + '.bmp'            
            img.save('../simulator/openhmd/dataset/'f'{file_blur}')


if __name__ == '__main__':
    print('start test')
    dataset_path = '../simulator/openhmd/dataset_0303/datsset_front_35us_40cm/'
    PATH = os.getcwd()
    print('path', PATH)
    img_files_l = glob.glob(dataset_path + 'CAM0*.bmp')
    img_files_r = glob.glob(dataset_path + 'CAM1*.bmp')
    CAP_PROP_FRAME_WIDTH = 1280
    CAP_PROP_FRAME_HEIGHT = 800
    # CAP_PROP_FRAME_WIDTH = 640
    # CAP_PROP_FRAME_HEIGHT = 400
    if not img_files_l or not img_files_r:
        print('exit')
        sys.exit()

    index = 0
    thres = 50
    print('l cam:', len(img_files_l), ' r cam:', len(img_files_r))

    while True:
        if index >= len(img_files_l) or index >= len(img_files_r):
            break

        imgL = cv2.imread(img_files_l[index])
        imgR = cv2.imread(img_files_r[index])

        # idea 1
        # 1280 x 800
        # _, imgL_s = filter_1(imgL, 80, 180, (1280, 800))
        # _, imgR_s = filter_1(imgR, 80, 180, (1280, 800))

        # idea 2
        # _, imgL_s = filter_2(imgL, 100, 170, (640, 400))
        # _, imgR_s = filter_2(imgR, 100, 170, (640, 400))

        # idea 3
        # _, imgL_s = filter_3(imgL, 100, 170, (640, 400))
        # _, imgR_s = filter_3(imgR, 100, 170, (640, 400))

        # idea 4
        # _, imgL_s = filter_4(imgL, 100, 255, (640, 400))
        # _, imgR_s = filter_4(imgR, 100, 255, (640, 400))

        # idea 5
        # _, imgL_s = filter_5(imgL, 80, 255, (1280, 800))
        # _, imgR_s = filter_5(imgR, 80, 255, (1280, 800))

        # idea 6
        # _, imgL_s = filter_6(imgL, 80, 255, (1280, 800))
        # _, imgR_s = filter_6(imgR, 80, 255, (1280, 800))

        # idea 7
        # _, imgL_s = filter_7(imgL, 80, 255, (1280, 800))
        # _, imgR_s = filter_7(imgR, 80, 255, (1280, 800))
    

        # # idea 8
        _, imgL_s = filter_8(imgL, 100, 255, (640, 400))
        _, imgR_s = filter_8(imgR, 100, 255, (640, 400))



        # stacked_frame_before = np.hstack((imgL, imgR))
        stacked_frame_after = np.hstack((imgL_s, imgR_s))
        stacked_frame_after = cv2.cvtColor(stacked_frame_after, cv2.COLOR_GRAY2RGB)

        save_file(img_files_l[index], cv2.resize(imgL_s, (640, 400)))
        save_file(img_files_r[index], cv2.resize(imgR_s, (640, 400)))

        if stacked_frame_after is None:
            print('none')
            break

        # ESC가 입력되면 break
        cv2.imshow('LR cam after', stacked_frame_after)
        # cv2.imshow('LR cam before', stacked_frame_before)
        if cv2.waitKey(24) == 27:
            break

        index += 1
        # if index >= len(img_files_l) or index >= len(img_files_r):
        #     index = 0

    cv2.destroyAllWindows()

    # for i in os.listdir(dataset_path):
    #     path = dataset_path + i
    #     if 'CAM0' in path:
    #         print('path:', path)
    #         img_gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    #         cv2.imshow("image", img_gray)
    #
    #
    # cv2.destroyAllWindows()