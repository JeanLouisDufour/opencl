import ctypes
from lnk import *

"""
https://software.intel.com/content/www/us/en/develop/documentation/iocl-opg/top/optimizing-opencl-usage-with-intel-processor-graphics/optimizing-utilization-of-execution-units.html
keep in mind that compiler may pack up to 32 work items per thread (with SIMD-32).

"""


ksrc = """
#define TY size_t          
__kernel void kinfos(  __global TY *Aid,
					    __global TY *Asz,
						__global TY *Alid, __global TY *Alsz,
						__global TY *Anum_groups, __global TY *Agroup_id, 
                       __global int *pn)    
{					 
	int n = *pn; 
    //Get our global thread ID                  
    TY id = get_global_id(0), sz = get_global_size(0);
	TY lid = get_local_id(0), lsz = get_local_size(0);                    
	TY num_groups = get_num_groups(0), group_id = get_group_id(0);
                        
    //Make sure we do not go out of bounds      
    if (id < n) {                             
        Aid[id] = id;
		Asz[id] = sz;
		Alid[id] = lid; Alsz[id] = lsz;
		Anum_groups[id] = num_groups; Agroup_id[id] = group_id;
    } else {
		// c[id] = id;
	}                        
}                                            
"""

n = sz = 10000
TY = ctypes.c_size_t
d = kernel_initiate(ksrc,
	[ (TY * n) for _ in range(6)] + [(cl_int * 1)],
	"W"*6+"R"
	)

if 'error' in d:
	assert False, d['error']

for j in range(1):
	Aid, Asz, Alid, Alsz, Anum_groups, Agroup_id, An = params = \
		[[None]*n for i in range(6)] + [[n]]
	kernel_run(d,n,params)
	#kernel_run(d,n,[Aid, Asz, Alid, Alsz, Anum_groups, Agroup_id, n])
	assert all(Aid[i]==i for i in range(len(Aid)))
	print(Aid[:16])
	assert all(Asz[i]==sz for i in range(len(Asz)))
	print(Asz[:16])
	lsz = Alsz[0]
	assert all(Alid[i]==(i%lsz) for i in range(len(Alid)))
	print(Alid[:16])
	assert all(Alsz[i]==lsz for i in range(len(Alsz)))
	print(Alsz[:16])
	assert all(Anum_groups[i]==(sz//lsz) for i in range(len(Anum_groups)))
	print(Anum_groups[:16])
	assert all(Agroup_id[i]==(i//lsz) for i in range(len(Agroup_id)))
	print(Agroup_id[:16])
	assert all(Aid[i] == Agroup_id[i]*Alsz[i]+Alid[i] for i in range(len(Aid)))

kernel_terminate(d)

lsz_array = [0]
for n in range(1,1000):
	sz = n
	d = kernel_initiate(ksrc,
					 [ (TY * n) for _ in range(6)] + [(cl_int * 1)],
					 "W"*6+"R"
	)
	assert 'error' not in d

	Aid, Asz, Alid, Alsz, Anum_groups, Agroup_id, An = params = \
		[[None]*n for i in range(6)] + [[n]]
	kernel_run(d,n,params)
	#kernel_run(d,n,[Aid, Asz, Alid, Alsz, Anum_groups, Agroup_id, n])
	assert all(Aid[i]==i for i in range(len(Aid)))
	#print(Aid[:16])
	assert all(Asz[i]==sz for i in range(len(Asz)))
	#print(Asz[:16])
	lsz = Alsz[0]
	assert all(Alid[i]==(i%lsz) for i in range(len(Alid)))
	#print(Alid[:16])
	assert all(Alsz[i]==lsz for i in range(len(Alsz)))
	#print(Alsz[:16])
	assert all(Anum_groups[i]==(sz//lsz) for i in range(len(Anum_groups)))
	#print(Anum_groups[:16])
	assert all(Agroup_id[i]==(i//lsz) for i in range(len(Agroup_id)))
	#print(Agroup_id[:16])
	assert all(Aid[i] == Agroup_id[i]*Alsz[i]+Alid[i] for i in range(len(Aid)))
	lsz_array.append(lsz)
	print((n,lsz))

	kernel_terminate(d)

assert lsz_array[:513] == list(range(513)) # et apres, lsz divise i
