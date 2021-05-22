"""
BARRIER :
Kalray = 0,0023
Intel = 0,0013
GPU Intel = 0,016
"""
import ctypes, time
from lnk import *

import numpy as np
import matplotlib.pyplot as plt
"%matplotlib inline"
import imageio
from math import prod

file = 'cat.bmp'
file = 'cat.pgm' # g = grey, p =color, b = binary

image = imageio.imread(file)
assert image.ndim == 2 and image.dtype == np.dtype('uint8')
assert image.shape == (720, 1080) 

h,_ = np.histogram(image, bins=range(257)) # ... including the rightmost edge
assert h.shape == (256,) and sum(h) == prod(image.shape)

#plt.plot(h)
#plt.plot(h[:16])

########### xx ########

sz = prod(image.shape)
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

if True:
	
	d = kernel_initiate("histogram.cl",
					 [ uint8_t * sz, uint32_t * 256, uint8_t * NWI],
					 "RWW",
					 f"-DNLIN={image.shape[0]} -DNCOL={image.shape[1]} -DNWI={NWI}"
					 #,dev_kind="CPU"
	)

	assert 'error' not in d, d['error']

	
	#data, hist, diag = \
	params = \
		[image1D, [None]*256, [None]*NWI]
	[[h1,_],[h2,_],[h3,_]] = d['params']
	h1[:] = image.reshape((sz,))  ### dans la vraie vie, une nouvelle image a chaque cycle
	
	nb_iter = 100
	print('start',nb_iter)
	tic = time.perf_counter()
	for j in range(nb_iter):
		#print(j)
		kernel_run(d, NWI, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=NWI)
		assert all(di == 3 for di in h3), list(h3)
		assert sum(h2)==sz and all(h2==h) # h2[0]==h[0]
		#print(sum(h2),sz, h2[0], h[0])
		# assert sum(hist) == sz, f"{j} : {sum(hist)} {sz}"
	toc = time.perf_counter()
	print('stop', (toc-tic)/nb_iter)
	
	kernel_terminate(d)

	# print(sum(h2),sz)
	