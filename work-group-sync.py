import ctypes
from lnk import *

"""
https://software.intel.com/content/www/us/en/develop/documentation/iocl-opg/top/optimizing-opencl-usage-with-intel-processor-graphics/optimizing-utilization-of-execution-units.html
keep in mind that compiler may pack up to 32 work items per thread (with SIMD-32).
"""


ksrc = \
"""__kernel void kinfos(  __global uchar *Aok, __global uint *Aok2,
                       __global int *pn)    
{					 
	int n = *pn; 
                   
    int id = get_global_id(0), sz = get_global_size(0);
	int lid = get_local_id(0), lsz = get_local_size(0);                    
	int num_groups = get_num_groups(0), gid = get_group_id(0);
	// printf("%d %d\\n",gid,num_groups); // sur quel stdout ???
	
	uchar ok = 0;
	if (sz == n) ok |= 1;
	if (lsz <= n && n % lsz == 0) ok |= 2; // et egal jusqu'a 512 inclus
	if (lid == id % lsz) ok |= 4;
	if (gid == id / lsz) ok |= 8;
	if (Aok[id] == 157) ok |= 16;
	Aok[id] = ok;
	
	// phase 2
	
	uint cnt = 0;
	for(int i = n-1; i >= 0; i--) {
		if (Aok[i] == 31) {
			cnt++;
		};
	};
	Aok2[id] = cnt;
	
       
      
}                                            
"""
repetitions = 1

for n in range(1,71):
	# AssertionError: 65 : Aok2 KO 1179 ***********************
	print(f'****** {n} ***********')
	sz = n
	d = kernel_initiate(ksrc,
					 [ (ctypes.c_uint8 * n), (ctypes.c_uint32 * n)] + [(cl_int * 1)],
					 "X"+"W"*1+"R"
	)

	assert 'error' not in d, d['error']

	ref_Aok, ref_Aok2 = [[157]*n, [None]*n]
	Aok, Aok2, An = params = \
		[[157]*n] + [[None]*n for i in range(1)] + [[n]]
			
	for j in range(repetitions):
		Aok[:] = ref_Aok
		Aok2[:] = ref_Aok2
		kernel_run(d,n,params)
		assert all(ok ==31 for ok in Aok)
		assert all(ok2 ==n for ok2 in Aok2), f'{n} : Aok2 KO {j} ***********************'

	kernel_terminate(d)
	
	assert all(ok ==31 for ok in Aok)

	if all(ok2 ==n for ok2 in Aok2):
		2+2 # print(f'{n} : Aok2 OK')
	else:
		print(f'{n} : Aok2 KO ***********************')
		assert False
		