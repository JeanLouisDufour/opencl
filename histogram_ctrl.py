"""
BARRIER :
Kalray =    0,0023 
Intel =     0,0013 0.0023
GPU Intel = 0,016  0.030
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

h = np.empty((256,), np.uint32)
lut = np.empty((256,), np.uint32)
hist_ctrl(image, h, lut, image_ref)

# 1iere ligne : // macros : NCOL NLIN NWI

NWI = 16
assert sz % NWI == 0 and 256 % NWI == 0
kmacros = "-DNLIN=720 -DNCOL=1080 "
kmacros = {'NLIN':image.shape[0], 'NCOL':image.shape[1], 'NWI':NWI}
	
rand_test = False

def k_hist_init(im_in, im_out):
	""
	sh = im_in.shape
	assert sh == im_out.shape
	sz = np.prod(sh)
	d = kernel_initiate("histogram_ctrl.cl",
					 [ uint8_t*sz, uint32_t*256, float_t*1, uint32_t*256, uint8_t*sz,\
						   uint8_t * NWI],
					 "RWWWWW",
					 f"-DNLIN={sh[0]} -DNCOL={sh[1]} -DNWI={NWI}"
					 #,dev_kind="CPU"
					 ,params = [im_in, None, None, None, im_out]
	)
	assert 'error' not in d, d['error']
	d['host_params'] = [h for h,_ in d['params']]
	return d

def k_hist_run(d, im_in, im_out):
	""
	h1,h2,h3,h4,h5,h6 = d['host_params']
	#h1[:] = im_in.flatten()
	kernel_run(d, NWI, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=NWI)
	#im_out.flat[:] = h5

if __name__ == "__main__":
	d = k_hist_init(image, image_new)

	#data, hist, diag = \
	params = \
		[image.flatten(), [None]*256, [None]*NWI, [None]*1, [None]*256, image_new.flatten()]
	# [[h1,_],[h2,_],[h3,_],[h4,_],[h5,_],[h6,_]] = d['params']
	h1,h2,h3,h4,h5,h6 = d['host_params']
	#h1[:] = image.flatten()  ### dans la vraie vie, une nouvelle image a chaque cycle
	
	nb_iter = 1
	print('start',nb_iter)
	tic = time.perf_counter()
	for j in range(nb_iter):
		if rand_test:
			rand_image(image)
			scale = hist_ctrl(image, h, lut, image_ref)
			#h1[:] = image.flatten()
		kernel_run(d, NWI, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=NWI)
		if True:
			assert all(di == 3 for di in h6), list(h6)
			assert all(h2==h)
			assert h3[0] == scale
			assert all(h4 == lut)
			assert all(h5 == image_ref.flatten())
	toc = time.perf_counter()
	print('stop', (toc-tic)/nb_iter)
	
	kernel_terminate(d)
