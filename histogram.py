import ctypes
from lnk import *

import numpy as np
import matplotlib.pyplot as plt
"%matplotlib inline"
import imageio
from math import prod

file = 'cat.bmp'

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





NWI = 32
assert sz % NWI == 0 and 256 % NWI == 0
ksrc = \
"""#define NWI {NWI}
#define HIST_BINS 256
#define numDataPerWorkItem (720 * 1080 / NWI)
#define numHistPerWorkItem (HIST_BINS / NWI)

#define LOCALHIST

__kernel 
void histogram(__global uchar *data,
               __global int *histogram,
			   __global uchar *diag)
{
                         // int numDataPerWorkItem, // beaucoup (1M/64 = 16384)
						// int numHistPerWorkItem,  // 256/64 = 4
#ifdef LOCALHIST
	__local int localHistogram[HIST_BINS];
#endif
   /*__private*/ int privateHistogram[HIST_BINS];
   int lid = get_local_id(0), lsz = get_local_size(0);
   int gid = get_global_id(0), gsz = get_global_size(0);
   
   uchar ok = 0;
   if (lid==gid) ok |= 1;
   int ng = get_num_groups(0), gr_id = get_group_id(0);
   if (ng==1 && gr_id==0) ok |= 2;
   diag[gid] = ok;
   
   
   int data_offset = gid*numDataPerWorkItem;
   int hist_offset = gid*numHistPerWorkItem;
   
   for (int i = 0; i < numHistPerWorkItem; i++) {
#ifdef LOCALHIST
			localHistogram[i+hist_offset] = 0;
#else
			histogram[i+hist_offset] = 0;
#endif
	}
   
   /* Initialize local histogram to zero */
   for (int i = 0; i < HIST_BINS; i++) privateHistogram[i] = 0;
   
   /* Wait until all work-items within 
    * the work-group have completed */
   // barrier(CLK_LOCAL_MEM_FENCE);
   
   /* Compute local histogram */
   __global uchar *p = data + data_offset;
   for (int i = 0; i < numDataPerWorkItem; i++) privateHistogram[p[i]]++;
   
   
   /* Wait until all work-items within 
    * the work-group have completed */
   //barrier(CLK_GLOBAL_MEM_FENCE | CLK_LOCAL_MEM_FENCE);
   //mem_fence(CLK_GLOBAL_MEM_FENCE | CLK_LOCAL_MEM_FENCE);
   
   /* Write the local histogram out to the global histogram */
	
	for (int i = 0; i < HIST_BINS; i++) {
			int j = (i + hist_offset) & 255;
			//if (j >= HIST_BINS) j -= HIST_BINS;
			//j -= j >= HIST_BINS ? HIST_BINS : 0;
#ifdef LOCALHIST
#if 0 
			localHistogram[j] += privateHistogram[j];
			barrier(CLK_LOCAL_MEM_FENCE); 
#else
			atomic_add(&localHistogram[j], privateHistogram[j]); // erreur des le debut !!!!!
#endif
#else
#if 1
			histogram[j] += privateHistogram[j];
			barrier(CLK_GLOBAL_MEM_FENCE);
#else
			atomic_add(&histogram[j], privateHistogram[j]);
#endif
#endif
	}
#ifdef LOCALHIST
	for (int i = 0; i < numHistPerWorkItem; i++) {
			histogram[i+hist_offset] = localHistogram[i+hist_offset];
	}
#endif
}
"""
# pb entre la fstring et les '//'
ksrc = ksrc.replace('{NWI}', f'{NWI}')


if True:
	
	d = kernel_initiate(ksrc,
					 [ (ctypes.c_uint8 * sz), (ctypes.c_uint32 * 256), (ctypes.c_uint8 * NWI)],
					 "RWW"
	)

	assert 'error' not in d, d['error']

	
	data, hist, diag = params = \
		[image1D, [None]*256, [None]*NWI]
			
	for j in range(1000):
		kernel_run(d, NWI, params)
		assert all(di == 3 for di in diag)
		assert sum(hist) == sz, f"{j} : {sum(hist)} {sz}"

	kernel_terminate(d)

	print(sum(hist),sz)
	