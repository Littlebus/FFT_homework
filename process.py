import numpy as np
import cv2
import cmath
from FFT import *
import os

if __name__ == '__main__':
    data_dir = './data'
    output_dir = './output'
    imgs = os.listdir(data_dir)
    for img in imgs:
        print(img)
        name_list = img.split('.')
        fft_img,ifft_img = fft_and_ifft(os.path.join(data_dir,img))
        '''
        cv2.imshow('fft',fft_img)
        cv2.imshow('ifft',ifft_img)
        cv2.waitKey(1000)
        '''
        cv2.imwrite(os.path.join(output_dir,name_list[0]+'_fft.'+name_list[1]),fft_img)
        cv2.imwrite(os.path.join(output_dir,name_list[0]+'_ifft.'+name_list[1]),ifft_img)
