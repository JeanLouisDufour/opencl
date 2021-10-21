import ctypes, time
from lnk import *

import numpy as np

import cv2 as cv
import cv_stub
_borderMap = [ "BORDER_CONSTANT", "BORDER_REPLICATE", "BORDER_REFLECT", "BORDER_WRAP", "BORDER_REFLECT_101" ]

prod = np.prod # from math import prod

ocv_src = "c:/opencv-4.5.1/sources"
#ocv_src = "c:/Users/F074018/Documents/opencv-4.0.1"

kpath = ocv_src + "/modules/core/src/opencl/copymakeborder.cl"
"""
#define :
	cn (1 ou 3)
	T
	T1 si cn == 3
	BORDER_xx
	ST

1 kernel :
	
__kernel void copyMakeBorder(__global const uchar * srcptr, int src_step, int src_offset, int src_rows, int src_cols,
                             __global uchar * dstptr, int dst_step, int dst_offset, int dst_rows, int dst_cols,
                             int top, int left, ST nVal)


"""
# copy.cpp / ocl_copyMakeBorder
type_ = "uchar"
borderType = cv_stub.BORDER_CONSTANT
depth = ""
cn = 1
sctype = "int"
rowsPerWI = 1

build_d = {
	"T": type_,
	_borderMap[borderType]: None,
	"T1": depth,
	"cn": cn,
	"ST": sctype,
	"rowsPerWI": rowsPerWI,
	}

# build_options = ' '.join([])

d = kernel_initiate(kpath,
 	[ uint8_t*100, 1, 1, 1, 1, 
 	  uint8_t*100, 1, 1, 1, 1,
 	  1,1,0],
 	"RIIIIWIIIIIII",
 	build_d
 	,dev_kind="GPU"
 	)
if 'error' in d:
 	print('********** ERROR ***********')
 	print(d['error'])

