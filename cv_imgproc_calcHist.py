from matplotlib import pyplot as plt
import cv2
import numpy as np
from lnk import *

image_name = "cv_clahe_image29-261x300.jpg"
image_name = "tire_AVANT.tif"                    # (205,232,3)
image = cv2.imread(image_name)
if len(image.shape) > 2:
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
if image.dtype != np.uint8:
	assert False
	
hist = cv2.calcHist([image], [0], None, [256], [0, 256])
# attention : hist : (256,1)
hist = hist[:,0]
assert sum(hist) == np.prod(image.shape)

# histogram.cpp: 1205  ocl_calcHist1

ocv_src = "c:/opencv-4.5.1/sources"
#ocv_src = "c:/Users/F074018/Documents/opencv-4.0.1"

kpath = ocv_src + "/modules/imgproc/src/opencl/histogram.cl"

BINS = 256
compunits = 16	# dev.maxComputeUnits()
wgs = 1			# dev.maxWorkGroupSize()
size = image.shape
use16 = size[1] % 16 == 0
kercn = 4

build_d = {
	"BINS": BINS,
	"HISTS_COUNT": compunits,
	"WGS": f'{wgs}u',
	"kercn": kercn,
	"T": "int",
	"HAVE_SRC_CONT": None
	}

sz = np.prod(size)

d = kernel_initiate(kpath,
	[ uint8_t*sz, 1, 1, 1, 1, 1,
	  uint8_t*sz, 1, 1, 1, 1,
	  3.14],
	"RIIIIIWIIIIF",
	build_d
	,dev_kind="GPU"
	)