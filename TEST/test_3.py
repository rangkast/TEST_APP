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
    img_files_before = glob.glob('../simulator/openhmd/result_0303_origin/' + 'C1*.bmp')
    img_files_after = glob.glob('../simulator/openhmd/result/' + 'C1*.bmp')

    if not img_files_before or not img_files_after:
        print('exit')
        sys.exit()

    index = 0
    WIDTH = 640
    HEIGHT = 400
    while True:
        if index >= len(img_files_before) or index >= len(img_files_after):
            break

        img_o_l = cv2.imread(img_files_before[index])
        img_o_r = cv2.imread(img_files_after[index])

        if img_o_l is not None and img_o_r is not None:
            height, width = img_o_l.shape[:2]
            # img_o_l = img_o_l[0:height, 100:int(3*width/4)]
            # img_o_r =  img_o_r[0:height, 100:int(3*width/4)]
            stacked_frame = np.hstack((img_o_l, img_o_r))
            alpha = 0.5
            # stacked_frame = cv2.addWeighted(img_o_l, alpha, img_o_r, alpha, 0)
            if stacked_frame is None:
                print('none')
                break

            # ESC가 입력되면 break
            cv2.imshow('LR cam after', stacked_frame)
        if cv2.waitKey(24) == 27:
            break

        index += 1
        if index >= len(img_files_before) or index >= len(img_files_after):
            index = 0

    cv2.destroyAllWindows()
