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

image0 = imageio.imread(file)
assert image0.shape == (720, 1080) and image0.dtype == np.dtype('uint8')
l0 = 190; c0 = 256
image = image0[l0:l0+512,c0:c0+512]
sz = image.size

h,_ = np.histogram(image, bins=range(257)) # ... including the rightmost edge
assert h.shape == (256,) and sum(h) == image.size

image1D = image.reshape((image.size,)) # flatten() fait une copie, alors que reshape() partage les donnees
# le plus grand diviseur de sz <= 64
for div in range(64,1,-1):
	q,r = divmod(sz,div)
	if r == 0:
		break
assert sz == div*q
assert div >= 16



# 1iere ligne : // macros : NCOL NLIN NWI

version = 1

if version == 1:
	kname = "histogram_GOOD"
	GSZ = [512,512] # 8192 # 8193 -> erreur -54
	LSZ = [64,64] # CPU : max 8192
	LSZ = [16,16] # GPU : max 512
	LSZ = [4,4] # GPU : max 512
	NWI = prod(GSZ)
	d = kernel_initiate("histogram_ERTS.cl",
					 [ uint8_t * sz, uint32_t * 256],
					 "RX",
					 f"-DNLIN={image.shape[0]} -DNCOL={image.shape[1]} -DNWI={NWI}"
					 , dev_kind="CPU"
					 , kname=kname
	)

else:
	kname = "histogram"
	GSZ = [16]
	LSZ = None
	NWI = prod(GSZ)
	assert image.size % NWI == 0 and 256 % NWI == 0	
	d = kernel_initiate("histogram_ERTS.cl",
					 [ uint8_t * sz, uint32_t * 256, uint8_t * NWI],
					 "RWW",
					 f"-DNLIN={image.shape[0]} -DNCOL={image.shape[1]} -DNWI={NWI}"
					 #, dev_kind="CPU"
					 , kname=kname
	)

if True:
	assert 'error' not in d, d['error']
	
	if len(d['params']) == 2:
		params = [image1D, [None]*256]
		[[h1,_],[h2,_]] = d['params']
		h3 = None
	else:
		params = [image1D, [None]*256, [None]*NWI]
		[[h1,_],[h2,_],[h3,_]] = d['params']
	h1[:] = image.reshape((sz,))  ### dans la vraie vie, une nouvelle image a chaque cycle
	h2_init = np.zeros((256,), dtype="uint8")
	nb_iter = 1
	print('start',nb_iter)
	tic = time.perf_counter()
	for j in range(nb_iter):
		#print(j)
		h2[:] = h2_init
		kernel_run(d, GSZ, params, blocking_writes=False, blocking_reads=False, finish=True, local_work_size=LSZ)
		assert h3 is None or all(di == 3 for di in h3), list(h3)
		if sum(h2)==image.size:
			assert all(h2==h) # h2[0]==h[0]
			print('OK')
		else:
			print('! ',sz-sum(h2))
		# assert sum(hist) == sz, f"{j} : {sum(hist)} {sz}"
	toc = time.perf_counter()
	print('stop', (toc-tic)/nb_iter)
	
	kernel_terminate(d)

	# print(sum(h2),sz)
	