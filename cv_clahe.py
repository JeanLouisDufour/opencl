import ctypes, time
from lnk import *

import numpy as np
import matplotlib.pyplot as plt
"%matplotlib inline"
#import imageio
import matplotlib.image as mpimg

import cv2 as cv
import cv_stub
_borderMap = [ "BORDER_CONSTANT", "BORDER_REPLICATE", "BORDER_REFLECT", "BORDER_WRAP", "BORDER_REFLECT_101" ]

prod = np.prod # from math import prod

ocv_src = "c:/opencv-4.5.1/sources"
#ocv_src = "c:/Users/F074018/Documents/opencv-4.0.1"

kpath = ocv_src + "/modules/imgproc/src/opencl/clahe.cl"
"""
#define : aucun

2 kernels :
	
__kernel void calcLut(__global __const uchar * src, const int srcStep,
                      const int src_offset, __global uchar * lut,
                      const int dstStep, const int dst_offset,
                      const int2 tileSize, const int tilesX,
                      const int clipLimit, const float lutScale)

__kernel void transform(__global __const uchar * src, const int srcStep, const int src_offset,
                        __global uchar * dst, const int dstStep, const int dst_offset,
                        __global uchar * lut, const int lutStep, int lut_offset,
                        const int cols, const int rows,
                        const int2 tileSize,
                        const int tilesX, const int tilesY)

"""

img_path = "E:/github/opencl/Hawkes_Bay_NZ_AVANT.jpg" # shape == (200,300), uint8
img_path = "E:/github/opencl/tsukuba_l.png" # shape == (288, 384, 3), float32 [0..1]
# https://www.geeksforgeeks.org/clahe-histogram-eqalization-opencv/
img_path = "E:/github/opencl/cv_clahe_image29-261x300.jpg" # shape == (300, 261, 3), uint8

##################################################

# def DIVUP_inh(total, grain):
# 	return (((total) + (grain) - 1) // (grain))
# def ROUNDUP(sz, n):
# 	return ((sz) + (n) - 1 - (((sz) + (n) - 1) % (n)))

src = mpimg.imread(img_path)
if len(src.shape) == 2:
	H,W = src.shape
	cn = 1
else:
	H,W,cn = src.shape
assert 1 <= cn <= 4 < min(H,W)
if src.dtype != np.uint8:
	assert src.dtype == np.float32
	# assert len(src.shape) == 2
	src = np.uint8(src*255)

if cn != 1:
	print("warning : color image")
	#src = src[:,:,0]
	image_bw = cv.cvtColor(src, cv.COLOR_BGR2GRAY) # type conserve
	assert len(image_bw.shape) == 2
	cn = 1
else:
	image_bw = src

image_bw = cv.resize(image_bw, (500, 600)) # shape : 600*500

clahe = cv.createCLAHE(clipLimit = 5)
clahe_stub = cv_stub.createCLAHE()
final_img = clahe.apply(image_bw) #  + 30
cv.imshow("ORIGINAL image", image_bw)
cv.imshow("CLAHE image", final_img)


build_d = {
	}
build_options = ' '.join([])


# d = kernel_initiate(kpath,
# 	[ uint8_t*sz, 1, 1, 1, 1, 1,
# 	  uint8_t*sz, 1, 1, 1, 1,
# 	  3.14],
# 	"RIIIIIWIIIIF",
# 	build_d
# 	,dev_kind="GPU"
# 	)
# if 'error' in d:
# 	print('********** ERROR ***********')
# 	print(d['error'])

