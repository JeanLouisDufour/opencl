import ctypes, time
from lnk import *

import numpy as np
import matplotlib.pyplot as plt
"%matplotlib inline"
#import imageio
import matplotlib.image as mpimg

import cv2 as cv
#import cv_stub as cv
_borderMap = [ "BORDER_CONSTANT", "BORDER_REPLICATE", "BORDER_REFLECT", "BORDER_WRAP", "BORDER_REFLECT_101" ]

prod = np.prod # from math import prod

ocv_src = "c:/opencv-4.5.1/sources"
#ocv_src = "c:/Users/F074018/Documents/opencv-4.0.1"

kpath = ocv_src + "/modules/imgproc/src/opencl/filter2DSmall.cl"
"""
__kernel void filter2D(
	__global const uchar * srcptr,
	int src_step,
	int srcOffsetX,
	int srcOffsetY,
	int srcEndX,
	int srcEndY,
	__global uchar * dstptr,
	int dst_step,
	int dst_offset,
	int rows,
	int cols,
	float delta)
"""

img_path = "E:/github/opencl/Hawkes_Bay_NZ_AVANT.jpg" # shape == (200,300), uint8
img_path = "E:/github/opencl/tsukuba_l.png" # shape == (288, 384, 3), float32 [0..1]

##################################################

def DIVUP_inh(total, grain):
	return (((total) + (grain) - 1) // (grain))
def ROUNDUP(sz, n):
	return ((sz) + (n) - 1 - (((sz) + (n) - 1) % (n)))

src = mpimg.imread(img_path)
if len(src.shape) == 2:
	H,W = src.shape
	cn = 1
else:
	H,W,cn = src.shape
assert 1 <= cn <= 4 < min(H,W)
if src.dtype != np.float32:
	assert src.dtype == np.uint8
	assert len(src.shape) == 2
	src = np.float32(src) / 255

if cn != 1:
	print("warning : first plan only")
	src = src[:,:,0]
	assert len(src.shape) == 2
	cn = 1
sz = H*W

def kerToStr(k):
	""
	xl = [f"DIG({x}f)" for x in k.flat]
	s = ''.join(xl)
	return s

kernel= np.array([[1.0, 2.0, 1.0],
			[2.0, 4.0, 2.0],
			[1.0, 2.0, 1.0]], dtype = np.float32) * (1/16)

kernel = np.array([[0,0,0],[0,2,0],[0,0,0]], dtype = np.float32)

KH,KW = kernel.shape
anchor = KW//2, KH//2
pxLoadNumPixels = 1 if cn != 1 or W % 4 != 0 else 4
pxLoadVecSize = cn * pxLoadNumPixels

pxPerWorkItemX = 1
pxPerWorkItemY = 1
if cn <= 2 and KW <= 4 and KH <= 4:
	pxPerWorkItemX = 8 if W % 8 == 0 else 4 if W % 4 == 0 else 2 if W % 2 == 0 else 1
	pxPerWorkItemY = 2 if H % 2 == 0 else 1
elif cn < 4 or (KW <= 4 and KH <= 4):
	pxPerWorkItemX = 2 if W % 2 == 0 else 1
	pxPerWorkItemY = 2 if H % 2 == 0 else 1

globalsize = (W // pxPerWorkItemX, H // pxPerWorkItemY)

privDataWidth = ROUNDUP(pxPerWorkItemX + KW - 1, pxLoadNumPixels)

wgRound = 256
globalsize = (ROUNDUP(globalsize[0], wgRound), globalsize[1])

borderType = cv.BORDER_REFLECT_101
isolated = (borderType & cv.BORDER_ISOLATED) != 0 # 16
assert not isolated
borderType &= ~cv.BORDER_ISOLATED




build_d = {
		"cn": cn,
		"ANCHOR_X": anchor[0],
		"ANCHOR_Y": anchor[1],
		"KERNEL_SIZE_X": KW,
		"KERNEL_SIZE_Y": KH,
		"PX_LOAD_VEC_SIZE": pxLoadVecSize,
		"PX_LOAD_NUM_PX": pxLoadNumPixels,
		"PX_PER_WI_X": pxPerWorkItemX,
		"PX_PER_WI_Y": pxPerWorkItemY,
		"PRIV_DATA_WIDTH": privDataWidth,
		_borderMap[borderType]: None,
		"BORDER_ISOLATED" if isolated else "NO_BORDER_ISOLATED": None,
		"PX_LOAD_X_ITERATIONS": privDataWidth // pxLoadNumPixels,
		"PX_LOAD_Y_ITERATIONS": pxPerWorkItemY + KH - 1,
		"srcT": 'float',
		"srcT1": 'float',
		"dstT": 'float',
		"dstT1": 'float',
		"WT": 'float',
		"WT1": 'float',
		"convertToWT": '(float)',
		"convertToDstT": '(float)',
		"COEFF": kerToStr(kernel)
	}
build_options = ' '.join([])


d = kernel_initiate(kpath,
	[ uint8_t*sz, 1, 1, 1, 1, 1,
	  uint8_t*sz, 1, 1, 1, 1,
	  3.14],
	"RIIIIIWIIIIF",
	build_d
	,dev_kind="GPU"
	)
if 'error' in d:
	print('********** ERROR ***********')
	print(d['error'])

