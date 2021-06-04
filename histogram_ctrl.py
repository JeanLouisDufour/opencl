"""
BARRIER :
Kalray    = 
CPU Intel = 0.00041  0.00282
GPU Intel = 0.00374  0.03129
"""
import ctypes, time
from lnk import *

import numpy as np
import matplotlib.pyplot as plt
"%matplotlib inline"
import imageio
from math import prod

from histogram_ctrl_ref import hist_ctrl, rand_image

file = 'cat.bmp'
file = 'cat.pgm' # g = grey, p =color, b = binary

image = imageio.imread(file)
assert image.ndim == 2 and image.dtype == np.dtype('uint8')
assert image.shape == (720, 1080) 
sz = prod(image.shape)
image_new = np.empty(image.shape, image.dtype)
image_ref = np.empty(image.shape, image.dtype)
image_ref2 = np.empty(image.shape, image.dtype)

h = np.empty((256,), np.uint32)
lut = np.empty((256,), np.uint32)
scale = hist_ctrl(image, image_ref, h=h, lut=lut)

# 1iere ligne : // macros : NCOL NLIN NWI

NWI = 16
assert sz % NWI == 0 and 256 % NWI == 0
kmacros = "-DNLIN=720 -DNCOL=1080 "
kmacros = {'NLIN':image.shape[0], 'NCOL':image.shape[1], 'NWI':NWI}

def k_hist_init(im_in, im_out, kernel_file="histogram_ctrl.cl"):
	""
	sh = im_in.shape
	assert sh == im_out.shape
	sz = np.prod(sh)
	d = kernel_initiate(kernel_file,
					 [ uint8_t*sz, uint32_t*256, float_t*1, uint32_t*256, uint8_t*sz,\
						   uint8_t * NWI],
					 "RWWWWW",
					 f"-DNLIN={sh[0]} -DNCOL={sh[1]} -DNWI={NWI}"
					 #,dev_kind="CPU"
					 #,params = [im_in, None, None, None, im_out]
	)
	assert 'error' not in d, d['error']
	d['host_params'] = [h for h,_ in d['params']]
	return d

def k_hist_run(d, im_in, im_out):
	""
	params = [None]*6
	h1,h2,h3,h4,h5,h6 = d['host_params']
	#h1[:] = im_in.flat[:]
	kernel_run(d, NWI, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=NWI)
	#im_out.flat[:] = h5

if __name__ == "__main__":
	
	rand_test = False
	chk_test = False
	nb_iter = 1000

	try:
		import cv2 as cv
		cv_ok = True
	except ModuleNotFoundError:
		cv_ok = False
	
	d = k_hist_init(image, image_new \
				 #, kernel_file="histogram_ctrl_EMPTY.cl"
				 )

	#data, hist, diag = \
	params = \
		[image.flatten(), [None]*256, [None]*NWI, [None]*1, [None]*256, image_new.flatten()]
	# [[h1,_],[h2,_],[h3,_],[h4,_],[h5,_],[h6,_]] = d['params']
	h1,h2,h3,h4,h5,h6 = d['host_params']
	h1_flat = np.ctypeslib.as_array(h1)
	h1_2d = h1_flat.reshape((720,1080))
	h5_flat = np.ctypeslib.as_array(h5)
	h5_2d = h5_flat.reshape((720,1080))
	
	h1_2d[:,:] = image
	
	print('start',nb_iter)
	tic = time.perf_counter()
	for j in range(nb_iter):
		if rand_test:
			rand_image(h1_2d)
			if chk_test:
				scale = hist_ctrl(h1_2d, image_ref, h=h, lut=lut)
				if cv_ok:
					cv.equalizeHist(h1_2d, image_ref2)
					assert all(image_ref.flat == image_ref2.flat)
			#h1[:] = image.flatten()
		#kernel_run(d, NWI, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=NWI)
		k_hist_run(d, image, image_new)
		if chk_test:
			assert all(di == 3 for di in h6), list(h6)
			assert all(h2==h), j
			if h3[0] != scale:
				print("!!!! ", j, "h3[0] != scale", h3[0], scale, (h3[0] - scale)/(h3[0] + scale))
			if not all(h4 == lut):
				deltas = [(i,h,l) for i,(h,l) in enumerate(zip(h4,lut)) if h!=l]
				print("!!!! ", j, "not all(h4 == lut)", deltas)
			if not all(h5 == image_ref.flat):
				print("!!!! ", j, "not all(h5 == image_ref.flat)")
			#assert all(h5_2d.flat == image_ref.flat)
	toc = time.perf_counter()
	print('stop', (toc-tic)/nb_iter)
	
	kernel_terminate(d)
