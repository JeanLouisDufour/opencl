"""
BARRIER :
Kalray = 0,0023
Intel = 0,0013
GPU Intel = 0,016
"""
import ctypes, time
#from lnk import *

import numpy as np
import matplotlib.pyplot as plt
"%matplotlib inline"
import imageio
from math import prod, ceil
import cv2 as cv

source = 0
#source = r'E:\webgl-examples-gh-pages\tutorial\sample8\Firefox.mp4'

# BEGIN prechauffage
cap = cv.VideoCapture(source)
assert cap.isOpened()
ok, image_color = cap.read()
assert ok
id_color = id(image_color)
print(image_color.shape, image_color.dtype) # (480, 640, 3) uint8
image_gray = cv.cvtColor(image_color, cv.COLOR_BGR2GRAY)
print(image_gray.shape, image_gray.dtype) # 
image_gray_sz = prod(image_gray.shape)
id_gray = id(image_gray)
cv.namedWindow('image')
image_fps = np.empty((76,160), dtype=np.uint8) # 160 mini pour pouvoir la dragger
cv.namedWindow('fps')
image_cah = image_gray.copy()
cv.namedWindow('image_cah')
image_equ = image_gray.copy()
cv.namedWindow('image_equ')
hist_gray = np.empty((256,1), dtype=np.float32) # uint32 non supporte par calcHist
hist_gray_cumsum = np.empty((256,), dtype=np.float32) 
hist_int32 = np.empty((256,), dtype=np.int32)
lut = np.empty((256,), dtype=np.int32)
cv.namedWindow('histogram')
hist_img = np.empty((256,256), dtype=np.uint8)
# https://docs.opencv.org/master/dc/da5/tutorial_py_drawing_functions.html
hist_pts = np.empty((256,1,2), dtype = np.int32)
hist_pts[:,0,0] = range(256)
# END prechauffage

txt_orig = (20, 70)
txt_font = cv.FONT_HERSHEY_SIMPLEX
txt_scale = 3
txt_color = 0 # (0,0,0) # (100, 255, 0)
txt_thick = 3

fps = 0; fps_str = "00"
tic = ceil(time.perf_counter())
while ok:
	fps += 1
	if True:
		cv.calcHist([image_gray], [0], None, [256], [0,256], hist_gray)
		hist_img[:] = 0  # ou .fill(0)
		hist_int32[:] = hist_gray[:,0] # conversion float32 -> int32
		assert sum(hist_int32) == image_gray_sz
		hist_pts[:,0,1] = 256 - (hist_int32 >> 5) # 8192 / 256 = 32
		cv.polylines(hist_img, [hist_pts], False, 255)
		cv.imshow('histogram', hist_img)
	if time.perf_counter() > tic:
		tic += 1
		image_fps[:] = 255
		cv.putText(image_fps, str(fps), txt_orig, txt_font, txt_scale, txt_color, txt_thick)
		cv.imshow('fps',image_fps)
		fps = 0
	# image cah
	for i,n in enumerate(hist_int32):
		if n:
			break
	if n == image_gray_sz: # Dirac
		lut[i] = i # les autres : rien a faire
	else:
		lut[i] = 0
		scale = np.divide(255.0, image_gray_sz - n, dtype=np.float32)
		lut[i+1:] = np.round(np.multiply(np.cumsum(hist_int32[i+1:]), scale, dtype=np.float32), decimals=0)
		assert all(0 <= lut[i:]) and all(lut[i:] <= 255)
	#np.cumsum(hist_gray, out=hist_gray_cumsum)
	image_cah[:] = lut[image_gray]
	cv.imshow('image_cah',image_cah)
	# image equ
	cv.equalizeHist(image_gray, image_equ)
	cv.imshow('image_equ',image_equ)
	x = sum(sum(image_cah != image_equ))
	if x:
		print(x)
	#
	cv.imshow('image',image_gray)
	ok, image_color = cap.read(image_color)
	assert id_color == id(image_color)
	image_gray = cv.cvtColor(image_color, cv.COLOR_BGR2GRAY, image_gray)
	assert id_gray == id(image_gray)
	ok &= cv.waitKey(1) & 0xFF != ord('q') ## vivement pollKey

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

if False:
	
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

cap.release()
cv.destroyAllWindows()
