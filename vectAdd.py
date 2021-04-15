import ctypes
from lnk import *

from math import sin, cos

print("test EXTERNE")

ksrc = """
#define FLOAT float                                     
__kernel void vecAdd(  __global FLOAT *a,  
                       __global FLOAT *b, 
                       __global FLOAT *c,       
                       const unsigned int n)    
{                                               
    //Get our global thread ID                  
    int id = get_global_id(0);                  
                                                
    //Make sure we do not go out of bounds      
    if (id < 10)                               
        c[id] = a[id] + b[id];                 
    else c[id] = id;                        
}                                            
"""

n = 21
d = kernel_initiate(ksrc, [(ctypes.c_float * n), (ctypes.c_float * n), (ctypes.c_float * n), cl_uint],"RRWC")

for j in range(10):
	x_a = [sin(i)*sin(i)+j for i in range(n)]
	x_b = [cos(i)*cos(i) for i in range(n)]
	x_c = [None]*n
	kernel_run(d,n,[x_a,x_b,x_c,n])
	delta = [a+b-c for a,b,c in zip(x_a,x_b,x_c)]
	print(delta)

kernel_terminate(d)
