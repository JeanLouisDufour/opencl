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
new_image = image.copy()

h,_ = np.histogram(image, bins=range(257)) # ... including the rightmost edge
assert h.shape == (256,) and sum(h) == prod(image.shape)

for i0,n0 in enumerate(h):
	if n0:
		break
cumul_and_then_lut = np.zeros(h.shape, dtype=h.dtype)
dirac = n0 == sz 
cumul_and_then_lut[i0] = 0 if not dirac else i0
cumul = 0;
for i,x in enumerate(h[i0+1:], start=i0+1):
	cumul += h[i]
	cumul_and_then_lut[i] = cumul
scale = np.float32(1) if dirac else np.divide(255 , (sz - n0), dtype=np.float32)
cumul_and_then_lut[:] = np.round(np.multiply(cumul_and_then_lut, scale, dtype=np.float32), decimals=0)
assert all(0<=x<=255 for x in cumul_and_then_lut)
new_image[:] = cumul_and_then_lut[image]
lut = cumul_and_then_lut
"""
if n == image_gray_sz: # Dirac
	lut[i] = i # les autres : rien a faire
	else:
		scale = np.divide(255.0, image_gray_sz - n, dtype=np.float32)
		if False: # opencv
			lut[i] = 0
			lut[i+1:] = np.round(np.multiply(np.cumsum(hist_int32[i+1:]), scale, dtype=np.float32), decimals=0)
		else: # opencl
			hist_int32[i] = 0
			np.cumsum(hist_int32, out=hist_int32_cumsum)
			lut[:] = np.round(np.multiply(hist_int32_cumsum, scale, dtype=np.float32), decimals=0)
		assert all(0 <= lut[i:]) and all(lut[i:] <= 255)
"""





#plt.plot(h)
#plt.plot(h[:16])

########### xx ########

image1D = image.reshape((sz,))
# le plus grand diviseur de sz <= 64
for div in range(64,1,-1):
	q,r = divmod(sz,div)
	if r == 0:
		break
assert sz == div*q
assert div >= 16



# 1iere ligne : // macros : NCOL NLIN NWI

NWI = 16
assert sz % NWI == 0 and 256 % NWI == 0
kmacros = "-DNLIN=720 -DNCOL=1080 "
kmacros = {'NLIN':image.shape[0], 'NCOL':image.shape[1], 'NWI':NWI}


	
rand_test = False

def k_hist_init(sh):
	""
	sz = np.prod(sh)
	d = kernel_initiate("histogram_ctrl.cl",
					 [ uint8_t*sz, uint32_t*256, float_t*1, uint32_t*256, uint8_t*sz,\
						   uint8_t * NWI],
					 "RWWWWW",
					 f"-DNLIN={sh[0]} -DNCOL={sh[1]} -DNWI={NWI}"
					 #,dev_kind="CPU"
					 ,params = [image]
	)
	assert 'error' not in d, d['error']
	d['host_params'] = [h for h,_ in d['params']]
	return d

def k_hist_run(d, im_in, im_out):
	""
	h1,h2,h3,h4,h5,h6 = d['host_params']
	h1[:] = im_in.flatten()
	kernel_run(d, NWI, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=NWI)
	im_out.flat[:] = h5

if __name__ == "__main__":
	d = k_hist_init(image.shape)
	new_image1D = image1D.copy()
	#data, hist, diag = \
	params = \
		[image1D, [None]*256, [None]*NWI, [None]*1, [None]*256, new_image1D]
	# [[h1,_],[h2,_],[h3,_],[h4,_],[h5,_],[h6,_]] = d['params']
	h1,h2,h3,h4,h5,h6 = d['host_params']
	h1[:] = image.flatten()  ### dans la vraie vie, une nouvelle image a chaque cycle
	
	nb_iter = 100
	print('start',nb_iter)
	tic = time.perf_counter()
	for j in range(nb_iter):
		if rand_test:
			rand_image(image)
			scale = hist_ctrl(image, h, lut, new_image)
			h1[:] = image.flatten()
		kernel_run(d, NWI, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=NWI)
		if rand_test:
			assert all(di == 3 for di in h6), list(h6)
			assert all(h2==h)
			assert h3[0] == scale
			assert all(h4 == lut)
			assert all(h5 == new_image.flatten())
	toc = time.perf_counter()
	print('stop', (toc-tic)/nb_iter)
	
	kernel_terminate(d)

	# print(sum(h2),sz)
	