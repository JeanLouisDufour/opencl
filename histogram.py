import ctypes
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

kfile = "histogram.cl"
kfd = open(kfile)
ksrc = kfd.read()
kfd.close()

# 1iere ligne : // macros : NCOL NLIN NWI

NWI = 16
assert sz % NWI == 0 and 256 % NWI == 0
kmacros = "-DNLIN=720 -DNCOL=1080 "
kmacros = {'NLIN':image.shape[0], 'NCOL':image.shape[1], 'NWI':NWI}

if True:
	
	d = kernel_initiate(ksrc,
					 [ (ctypes.c_uint8 * sz), (ctypes.c_uint32 * 256), (ctypes.c_uint8 * NWI)],
					 "RWW",
					 kmacros
	)

	assert 'error' not in d, d['error']

	
	data, hist, diag = params = \
		[image1D, [None]*256, [None]*NWI]
			
	for j in range(10):
		print(j)
		kernel_run(d, NWI, params)
		assert all(di == 3 for di in diag), diag
		print(sum(hist),sz)
		assert sum(hist) == sz, f"{j} : {sum(hist)} {sz}"

	kernel_terminate(d)

	print(sum(hist),sz)
	