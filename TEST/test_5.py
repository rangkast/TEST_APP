import cv2
import os
import numpy as np
from PIL import Image
import time
import glob
import sys

import csv
from blur import *

if __name__ == '__main__':
    print('start test')
    PATH = os.getcwd()
    print('path', PATH)

    # img_files_o_l = glob.glob('../simulator/openhmd/result_0303_origin/' + 'C0*.bmp')
    # img_files_o_r = glob.glob('../simulator/openhmd/result_0303_origin/' + 'C1*.bmp')
    # img_files_l = glob.glob('../simulator/openhmd/result/' + 'C0*.bmp')
    # img_files_r = glob.glob('../simulator/openhmd/result/' + 'C1*.bmp')
    # left = init_coord_json('../simulator/openhmd_2/dataset/rifts_left.json')
    # right = init_coord_json('../simulator/openhmd_2/dataset/rifts_right.json')

    blob_data = {}
    with open('../simulator/openhmd/result.csv') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if len(row[0]) != '':
                # print(i, row)
                for ii, blob in enumerate(row):
                    if ii % 2 == 1 and blob != '':
                        idx = str(int((ii - 1)/2))
                        blob_x = float(row[ii - 1])
                        blob_y =  float(row[ii])
                        if idx in blob_data:
                            blob_data[idx][0].append(blob_x)
                            blob_data[idx][1].append(blob_y)
                        else:
                            blob_data[idx] = [[blob_x], [blob_y]]
    
    # calc data
    STD_ARRAY = []
    plt.style.use('default')
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot()
    max_x = 0
    max_y = 0
    min_x = 640
    min_y = 400
    for key, value in blob_data.items():
        # print('B', int(key) + 1)
        stdev_x = float(np.std(value[0], ddof=0))
        stdev_y = float(np.std(value[1], ddof=0))
        maxx = np.max(value[0])
        maxy = np.max(value[1])
        minx = np.min(value[0])
        miny = np.min(value[1])

        if maxx > max_x:
            max_x = maxx
        if minx < min_x:
            min_x = minx
        if maxy > max_y:
            max_y = maxy
        if miny < min_y:
            min_y = miny

            
        std_a = stdev_x * (200/295) * 3
        std_b = stdev_y * (200/295) * 3
        STD = float(np.sqrt(np.power(std_a, 2) + np.power(std_b, 2)))
        ax.scatter(value[0], value[1], marker='o', s=15, color='blue', alpha=0.3)
        # print(stdev_x, stdev_y)
        # print(std_a, std_b)
        # print(STD)
        STD_ARRAY.append(STD)

    for STD_DATA in STD_ARRAY:
        print('%0.6f' % STD_DATA)
    print('Mean')
    print('%0.6f' % np.mean(STD_ARRAY))

    ax.set_xlim([min_x - 10, max_x + 10])
    ax.set_ylim([min_y - 10, max_y + 10])
    scale = 1.5
    f = zoom_factory(ax, base_scale=scale)

    print('\n')

    # debug, RPE =  get_pose('../simulator/openhmd_2/debug_origin.txt')
    # print("origin RPE")
    # print('F1', len(RPE['F1']), '%0.6f' % np.mean(RPE['F1']))
    # print('F0', len(RPE['F0']), '%0.6f' % np.mean(RPE['F0']))
    # print('L1', len(RPE['L1']), '%0.6f' % np.mean(RPE['L1']))
    # print('L0', len(RPE['L0']), '%0.6f' % np.mean(RPE['L0']))


    debug_F, RPE_F =  get_pose('../simulator/openhmd/debug.txt')
    print("RPE")
    print('F1', len(RPE_F['F1']), '%0.6f' % np.mean(RPE_F['F1']))
    print('F0', len(RPE_F['F0']), '%0.6f' % np.mean(RPE_F['F0']))
    print('L1', len(RPE_F['L1']), '%0.6f' % np.mean(RPE_F['L1']))
    print('L0', len(RPE_F['L0']), '%0.6f' % np.mean(RPE_F['L0']))

    P0_R = [[],[],[]]
    P0_T = [[],[],[],[]]
    P1_R = [[],[],[]]
    P1_T = [[],[],[],[]]

    LEDS = {}

    for key, value in debug_F.items():
        # print(key)
        for item in value:
            if 'L' in item:
                if 'C0' in key:
                    led_key = str('C0_' + f'{item}')
                    x = float(value[item][0])
                    y = float(value[item][1])
                    if led_key in LEDS:
                        LEDS[led_key][0].append(x)
                        LEDS[led_key][1].append(y)
                    else:
                        LEDS[led_key] = [[x], [y]]
                if 'C1' in key:
                    led_key = str('C1_' + f'{item}')
                    x = float(value[item][0])
                    y = float(value[item][1])
                    if led_key in LEDS:
                        LEDS[led_key][0].append(x)
                        LEDS[led_key][1].append(y)
                    else:
                        LEDS[led_key] = [[x], [y]]

            if '[1]P' in item :
                # print(value['[1]P'])
                if 'C0' in key:
                    for i in range(len(value['[1]P'])):
                        P0_R[i].append(value['[1]P'][i])
                if 'C1' in key:
                    for i in range(len(value['[1]P'])):
                        P1_R[i].append(value['[1]P'][i])
            if '[1]O' in item :
                # print(value['[1]O'])
                if 'C0' in key:
                    for i in range(len(value['[1]O'])):
                        P0_T[i].append(value['[1]O'][i])
                if 'C1' in key:
                    for i in range(len(value['[1]O'])):
                        P1_T[i].append(value['[1]O'][i])

    
    stddevs_P0_R = np.apply_along_axis(np.std, 1, np.array(P0_R))
    stddevs_PO_T = np.apply_along_axis(np.std, 1, np.array(P1_R))
    stddevs_P1_R = np.apply_along_axis(np.std, 1, np.array(P0_T))
    stddevs_P1_T = np.apply_along_axis(np.std, 1, np.array(P1_T))

    # Print the results
    print('P0_R', stddevs_P0_R, 'M %0.6f' % np.mean(stddevs_P0_R))
    print('P0_T', stddevs_PO_T, 'M %0.6f' % np.mean(stddevs_PO_T))
    print('P1_R', stddevs_P1_R, 'M %0.6f' %  np.mean(stddevs_P1_R))
    print('P1_T', stddevs_P1_T, 'M %0.6f' % np.mean(stddevs_P1_T))
    # plt.show()                    
    print('\n')
   
     # calc data
    LED_STD_ARRAY = {}
    for key, value in LEDS.items():
        # print('B', int(key) + 1)
        stdev_x = float(np.std(value[0], ddof=0))
        stdev_y = float(np.std(value[1], ddof=0))
            
        std_a = stdev_x * (200/295) * 3
        std_b = stdev_y * (200/295) * 3
        STD = float(np.sqrt(np.power(std_a, 2) + np.power(std_b, 2)))
        # print(stdev_x, stdev_y)
        # print(std_a, std_b)
        # print(STD)
        LED_STD_ARRAY[key] = STD

    C0_LED = []
    C1_LED = []
    TOTAL = []
    for key, STD_DATA in LED_STD_ARRAY.items():
        print(key, '%0.6f' % STD_DATA)
        TOTAL.append(STD_DATA)
        if 'C0' in key:
            C0_LED.append(STD_DATA)
        if 'C1' in key:
            C1_LED.append(STD_DATA)
    print('Mean')
    print('C0', '%0.6f' % np.mean(C0_LED))
    print('C1', '%0.6f' % np.mean(C1_LED))

    print('T', '%0.6f' % np.mean(TOTAL))