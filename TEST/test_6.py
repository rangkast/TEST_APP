import cv2
import os
import numpy as np
from PIL import Image
import time
import glob
import sys

if __name__ == '__main__':
    print('start test')
    PATH = os.getcwd()
    print('path', PATH)
    img_files_o_l = glob.glob('../blurred_gaussian/' + 'CAM0*.bmp')
    img_files_o_r = glob.glob('../blurred_gaussian/' + 'CAM1*.bmp')
    img_files_l = glob.glob('../blurred/' + 'CAM0*.bmp')
    img_files_r = glob.glob('../blurred/' + 'CAM1*.bmp')

    if not img_files_l or not img_files_r:
        print('exit')
        sys.exit()

    index = 0
    print('origin len', len(img_files_o_l), len(img_files_o_r))
    print('result len', len(img_files_l), len(img_files_r))
    while True:
        if index >= len(img_files_l) or index >= len(img_files_r):
            break

        img_o_l = cv2.imread(img_files_o_l[index])
        img_o_r = cv2.imread(img_files_o_r[index])

        img_l = cv2.imread(img_files_l[index])
        img_r = cv2.imread(img_files_r[index])

        if img_o_l is not None and img_o_r is not None and \
                img_l is not None and img_r is not None:
            stacked_frame_after = np.hstack((img_l, img_r))
            stacked_frame_before = np.hstack((img_o_l, img_o_r))

            # stacked_frame = np.vstack((stacked_frame_before, stacked_frame_after))
            if stacked_frame_before is None:
                print('none')
                break

            # ESC가 입력되면 break
            cv2.imshow('LR cam after', stacked_frame_after)
            cv2.imshow('LR cam before', stacked_frame_before)
            # cv2.imshow('img', stacked_frame)
        if cv2.waitKey(24) == 27:
            break

        index += 1
        if index >= len(img_files_l) or index >= len(img_files_r):
            index = 0

    cv2.destroyAllWindows()
