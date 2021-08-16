import numpy as np
import cv2 as cv_true

CV_8U, CV_8S, CV_16U, CV_16S, CV_32S, CV_32F, CV_64F = range(7)

CV_8UC3, CV_8SC3, CV_16UC3, CV_16SC3, CV_32SC3, CV_32FC3, CV_64FC3 = range(16,16+7)

NORM_INF, NORM_L1, NORM_L2 = 1,2,4

def add(src1, src2, dst=None, mask=None, dtype=None): # ->	dst
	"""
	"""
	assert mask is None and dtype is None
	assert dst is not None
	assert src1.dtype == src2.dtype == dst.dtype
	np.add(src1,src2,out=dst)
	return dst

def countNonZero(src): # ->	retval
	"""
	"""
	return np.count_nonzero(src)

def max(src1, src2, dst=None): # ->	dst
	"""
	"""
	assert dst is None
	assert src1.dtype == np.float32
	assert isinstance(src2, (int,float))
	dst = np.maximum(src1,src2)
	return dst

def norm(src1, normType=NORM_L2, mask=None):
	"""
	cv.norm(	src1      [, normType[, mask]]	) ->	retval
	cv.norm(	src1, src2[, normType[, mask]]	) ->	retval

	"""
	if mask is not None:
		assert src1.shape == mask.shape
	assert normType == NORM_L1
	#r = cv_true.norm(src1, normType, mask)
	assert mask is None
	assert src1.dtype == np.float32
	# GET_OPTIMIZED(normDiffL1_32f)(data1, data2, 0, &result, (int)len, 1);
	r = np.sum(np.abs(src1.flat))
	return r

def pow(src, power, dst=None):
	"""
	"""
	assert dst is not None
	assert src.dtype == dst.dtype and src.shape == dst.shape
	assert power==2
	np.power(src, power, out=dst)
	return dst

def sqrt(src, dst=None):
	"""
	"""
	assert dst is not None
	assert src.dtype == dst.dtype and src.shape == dst.shape
	np.sqrt(src, dst)
	return dst

#############################################

def namedWindow(s):
	""
	print('namedWindow',s)

import matplotlib.image as mpimg
IMREAD_UNCHANGED, IMREAD_GRAYSCALE, IMREAD_COLOR = -1, 0, 1
def imread(fn, flags = IMREAD_COLOR):
	""
	assert flags == IMREAD_UNCHANGED
	image = mpimg.imread(fn)
	return image


####################################
# modules/imgproc/src/histogram.cpp
####################################

_h = np.empty((256,), dtype=np.uint32)
_cumul_scaled = np.empty((256,), dtype=np.float32)
_lut = np.empty((256,), dtype=np.uint32)

def equalizeHist(image, new_image, h=None, cumul_scaled=None, lut=None):
	"returns scale"
	assert image.ndim == 2 and image.shape == new_image.shape, (image.shape , new_image.shape)
	if h is None:
		h = _h
	if cumul_scaled is None:
		cumul_scaled = _cumul_scaled
	if lut is None:
		lut = _lut
	assert h.shape == cumul_scaled.shape == lut.shape == (256,)
	sz = np.prod(image.shape)
	h[:],_ = np.histogram(image, bins=range(257)) # ... including the rightmost edge
	assert h.shape == (256,) and sum(h) == np.prod(image.shape)

	for i0,n0 in enumerate(h):
		if n0:
			break
	lut[:i0] = 0
	dirac = n0 == sz 
	lut[i0] = 0 if not dirac else i0
	cumul = 0
	for i,x in enumerate(h[i0+1:], start=i0+1):
		cumul += h[i]
		lut[i] = cumul
	scale = np.float32(1) if dirac else np.divide(255 , (sz - n0), dtype=np.float32)
	#lut[:] = np.round(np.multiply(lut, scale, dtype=np.float32), decimals=0)
	cumul_scaled[:] = np.multiply(lut, scale, dtype=np.float32)
	# For values exactly halfway between rounded decimal values, NumPy rounds to the nearest even value.
	# Thus 1.5 and 2.5 round to 2.0, -0.5 and 0.5 round to 0.0, etc.
	# np.round(x, decimals=0) == np.rint(x)
	lut[:] = np.rint(cumul_scaled) # np.round(cumul_scaled, decimals=0)
	assert all(0<=x<=255 for x in lut)
	new_image[:] = lut[image]
	return scale

#################################
# modules/imgproc/src/filter.cpp
#################################

# enum BorderTypes { # base.hpp
BORDER_CONSTANT, BORDER_REPLICATE, BORDER_REFLECT, BORDER_WRAP, BORDER_REFLECT_101, BORDER_TRANSPARENT = range(6)
BORDER_ISOLATED = 16
BORDER_DEFAULT = BORDER_REFLECT_101 # gfedcb|abcdefgh|gfedcba
_borderMap = [ "BORDER_CONSTANT", "BORDER_REPLICATE", "BORDER_REFLECT", "BORDER_WRAP", "BORDER_REFLECT_101" ]
assert BORDER_DEFAULT == cv_true.BORDER_DEFAULT

def _normalizeAnchor(anchor, WH):
	"filterengine.hpp"
	x,y = anchor
	if x == -1:
		x = W//2
	if y == -1:
		y = H//2
	return (x,y)

def filter2D(src, ddepth, kernel, dst=None, anchor=(-1,-1), delta=0, borderType=BORDER_DEFAULT, _OpenCL=False): # -> dst
	"""
	"""
	assert ddepth == -1 and anchor==(-1,-1) and delta==0 and borderType == BORDER_DEFAULT
	assert dst is not None
	assert src.shape == dst.shape and src.dtype == dst.dtype
	assert len(src.shape) == 2
	assert src.dtype == np.float32
	assert kernel.shape == (3,3) and kernel.dtype == src.dtype
	#cv_true.filter2D(src, ddepth, kernel, dst, anchor, delta, borderType)
	if ddepth < 0:
		ddepth = src.dtype
	else:
		assert False
	# anchor = _normalizeAnchor(anchor, WH) # filterengine.hpp"
	KH,KW = kernel.shape
	x,y = anchor
	if x == -1:
		x = KW//2
	if y == -1:
		y = KH//2
	anchor = x,y
	cn = 1
	if _OpenCL:
		# ocl_filter2D(_src, _dst, ddepth, _kernel, anchor0, delta, borderType)
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
		"convertToWT": 'float',
		"convertToDstT": 'float',
		}
		build_options = ' '.join([])
	else:
		pass
		
	
	return dst

#################################
# modules/imgproc/src/filter.cpp
#################################

INTER_LINEAR = 1
assert INTER_LINEAR == cv_true.INTER_LINEAR

def resize(src, dsize, dst=None, fx=0.0, fy=0.0, interpolation=INTER_LINEAR): # -> dst
	"""
	"""
	assert fx==0.0 and fy==0.0 and interpolation==INTER_LINEAR
	assert dst is not None
	cv_true.resize(src, dsize, dst, fx, fy, interpolation)
	return dst


##################################

_rng = np.random.default_rng(12345)
def rand_mat(image):
	""
	sh = image.shape
	assert len(sh)==2
	if image.dtype == np.uint8:
		offset1, offset2 = _rng.integers(low=0, high=4, size=(2,), dtype=np.uint8)
		image[:] = _rng.integers(low=offset1, high=256-offset2, size=sh, dtype=np.uint8)
	elif image.dtype == np.float32:
		image[:] = _rng.uniform(size=sh) # 0 .. 1
	else:
		assert False

if __name__ == "__main__":
	import cv2 as cv_true
	
	Nruns = 10
	
	assert CV_32S == cv_true.CV_32S
	assert CV_32SC3 == cv_true.CV_32SC3
	assert NORM_L1 == cv_true.NORM_L1
	
	print('********** add ************')
	
	f1 = np.empty((500,500), dtype=np.float32)
	f2 = np.empty((500,500), dtype=np.float32)
	f3 = np.empty((500,500), dtype=np.float32)
	f4 = np.empty((500,500), dtype=np.float32)
	for i in range(Nruns):
		rand_mat(f1)
		rand_mat(f2)
		add(f1,f2,f3)
		cv_true.add(f1,f2,f4)
		x = sum(sum(f3 != f4))
		if x:
			print('PB',x)
	
	print('********** countNonZero ************')
	
	assert countNonZero(f4) == cv_true.countNonZero(f4)
	
	print('********** max ************')
	
	f3 = max(f1, 0.1)
	f4 = cv_true.max(f1,0.1)
	x = sum(sum(f3 != f4))
	if x:
		print('PB',x)
	
	print('********** norm ************')
	
	e_r_max = 0
	for i in range(Nruns):
		rand_mat(f1)
		r1 = norm(f1, NORM_L1, None)
		r2 = cv_true.norm(f1, NORM_L1, None)
		e_r = 2*np.abs(r1-r2)/(r1+r2)
		if e_r > e_r_max:
			e_r_max = e_r
	print(e_r_max)
	
	print('********** pow ************')

	pow(f1,2,dst=f3)
	cv_true.pow(f1,2,dst=f4)
	print(np.max(np.abs((f3-f4).flat)))
	
	print('********** sqrt************')

	sqrt(f1,dst=f3)
	cv_true.sqrt(f1,dst=f4)
	print(np.max(np.abs((f3-f4).flat)))
	
	print('****** equalizeHist *******')
	
	sh = (500,600)
	sh = (720, 1080)
	#
	sz = np.prod(sh)
	image = np.empty(sh, dtype=np.uint8)
	new_image = np.empty(sh, dtype=np.uint8)
	ref_image = np.empty(sh, dtype=np.uint8)
	h = np.empty((256,), dtype=np.uint32)
	lut = np.empty((256,), dtype=np.uint32)
	#rng = np.random.default_rng(12345)
	for i in range(Nruns):
		rand_mat(image)
		equalizeHist(image, new_image, h=h, lut=lut)
		cv_true.equalizeHist(image, ref_image)
		x = sum(sum(new_image != ref_image))
		if x:
			print('PB',x)
	
	print('****** filter2D *******')
	
	kernel= np.array([[1.0, 2.0, 1.0],
				[2.0, 4.0, 2.0],
				[1.0, 2.0, 1.0]], dtype = np.float32) * (1/16)
	for i in range(Nruns):
		rand_mat(f1)
		filter2D(f1, -1, kernel, dst=f3)
		cv_true.filter2D(f1, -1, kernel, dst=f4)
		x = sum(sum(f3!= f4))
		if x:
			print('PB',x)
	
	
	