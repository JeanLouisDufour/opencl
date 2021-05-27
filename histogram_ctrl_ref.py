"""
reference du kernel histogram_ctrl.cl
"""

import numpy as np

def hist_ctrl(image, h, lut, new_image):
	"returns scale"
	assert image.ndim == 2 and image.shape == new_image.shape and \
		h.shape == lut.shape == (256,)
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
	lut[:] = np.round(np.multiply(lut, scale, dtype=np.float32), decimals=0)
	assert all(0<=x<=255 for x in lut)
	new_image[:] = lut[image]
	return scale

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
	for i in range(100):
		rand_image(image)
		hist_ctrl(image, h, lut, new_image)
		cv.equalizeHist(image, ref_image)
		x = sum(sum(new_image != ref_image))
		if x:
			print('PB',x)