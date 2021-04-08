import ctypes
from lnk import *

from math import sin, cos

print("test EXTERNE")

if True: # vecAdd
	ksrc = (
"#define FLOAT float                                             \n"
"__kernel void vecAdd(  __global FLOAT *a,                       \n"
"                       __global FLOAT *b,                       \n"
"                       __global FLOAT *c,                       \n"
"                       const unsigned int n)                    \n"
"{                                                               \n"
"    //Get our global thread ID                                  \n"
"    int id = get_global_id(0);                                  \n"
"                                                                \n"
"    //Make sure we do not go out of bounds                      \n"
"    if (id < n)                                                 \n"
"        c[id] = a[id] + b[id];                                  \n"
"}                                                               \n"
)
	n = 8
	nb_bytes = n * 4
	e = cl_int(-1000)
	e_REF = ctypes.byref(e)
	kernelSource = (ctypes.c_char_p * 1)(ksrc.encode('cp1250'))
	cpPlatform = (cl_platform_id * 1)()
	err = clGetPlatformIDs(1, cpPlatform, None)
	assert err == 0
	device_id = (cl_device_id * 1)()
	err = clGetDeviceIDs(cpPlatform[0], CL_DEVICE_TYPE_GPU, 1, device_id, None)
	assert err == 0
	context = clCreateContext(None, 1, device_id, NULL_CALLBACK_context, None, e_REF)
	assert e.value == 0
	queue = clCreateCommandQueue(context, device_id[0], 0, e_REF);
	assert e.value == 0
	program = clCreateProgramWithSource(context, 1, kernelSource, None, e_REF)
	assert e.value == 0
	err = clBuildProgram(program, 0, None, None, NULL_CALLBACK_program, None)
	assert err == 0
	kernel = clCreateKernel(program, b"vecAdd", e_REF)
	assert e.value == 0
	d_a = clCreateBuffer(context, CL_MEM_READ_ONLY, nb_bytes, None, e_REF)
	assert e.value == 0
	d_b = clCreateBuffer(context, CL_MEM_READ_ONLY, nb_bytes, None, e_REF)
	assert e.value == 0
	d_c = clCreateBuffer(context, CL_MEM_WRITE_ONLY, nb_bytes, None, e_REF)
	assert e.value == 0
	
	
	
	err = clReleaseMemObject(d_a)
	err |= clReleaseMemObject(d_b)
	err |= clReleaseMemObject(d_c)
	assert err == 0
	err = clReleaseKernel(kernel)
	assert err == 0
	err = clReleaseProgram(program)
	assert err == 0
	err = clReleaseCommandQueue(queue)
	assert err == 0
	err = clReleaseContext(context)
	assert err == 0
	