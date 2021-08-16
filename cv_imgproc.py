import numpy as np
import cv2 as cv_true

CV_8U, CV_8S, CV_16U, CV_16S, CV_32S, CV_32F, CV_64F = range(7)
assert CV_32S == cv_true.CV_32S

CV_8UC3, CV_8SC3, CV_16UC3, CV_16SC3, CV_32SC3, CV_32FC3, CV_64FC3 = range(16,16+7)
assert CV_32SC3 == cv_true.CV_32SC3

NORM_INF, NORM_L1, NORM_L2 = 1,2,4
assert NORM_L1 == cv_true.NORM_L1

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
	assert dst is not None
	assert src1.dtype == src2.dtype == dst.dtype
	np.maximum(src1,src2,out=dst)
	return dst

def norm(src1, normType=NORM_L2, mask=None):
	"""
	cv.norm(	src1      [, normType[, mask]]	) ->	retval
	cv.norm(	src1, src2[, normType[, mask]]	) ->	retval

	"""
	r = cv_true.norm(src1, normType, mask)
	return r

def pow(src, power, dst=None):
	"""
	"""
	assert dst is not None
	assert src.dtype == dst.dtype and src.shape == dst.shape
	assert power==2
	dst[:] = src*src
	return dst

def sqrt(src, dst=None):
	"""
	"""
	assert dst is not None
	assert src.dtype == dst.dtype and src.shape == dst.shape
	np.sqrt(src, dst)
	return dst

###

def namedWindow(s):
	""
	print('namedWindow',s)

####################################
# modules/imgproc/src/histogram.cpp
####################################

_h = np.empty((256,), dtype=np.uint32)
_cumul_scaled = np.empty((256,), dtype=np.float32)
_lut = np.empty((256,), dtype=np.uint32)

def hist_ctrl(image, new_image, h=None, cumul_scaled=None, lut=None):
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

BORDER_DEFAULT = BORDER_REFLECT_101 = 4 # gfedcb|abcdefgh|gfedcba
assert BORDER_DEFAULT == cv_true.BORDER_DEFAULT

def filter2D(src, ddepth, kernel, dst=None, anchor=(-1,-1), delta=0, borderType=BORDER_DEFAULT): # -> dst
	"""
	"""
	assert ddepth == -1 and anchor==(-1,-1) and delta==0 and borderType == BORDER_DEFAULT
	assert dst is not None
	assert src.shape == dst.shape and src.dtype == dst.dtype
	assert kernel.shape == (3,3) and kernel.dtype == src.dtype
	cv_true.filter2D(src, ddepth, kernel, dst, anchor, delta, borderType)
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
def rand_image(image):
	""
	sh = image.shape
	assert len(sh)==2
	offset1, offset2 = _rng.integers(low=0, high=4, size=(2,), dtype=np.uint8)
	image[:] = _rng.integers(low=offset1, high=256-offset2, size=sh, dtype=np.uint8)

if __name__ == "__main__":
	import cv2 as cv
	sh = (500,600)
	sh = (720, 1080)
	#
	sz = np.prod(sh)
	image = np.empty(sh, dtype=np.uint8)
	new_image = np.empty(sh, dtype=np.uint8)
	ref_image = np.empty(sh, dtype=np.uint8)
	h = np.empty((256,), dtype=np.uint32)
	lut = np.empty((256,), dtype=np.uint32)
	rng = np.random.default_rng(12345)
	for i in range(1000):
		rand_image(image)
		hist_ctrl(image, new_image, h=h, lut=lut)
		cv.equalizeHist(image, ref_image)
		x = sum(sum(new_image != ref_image))
		if x:
			print('PB',x)