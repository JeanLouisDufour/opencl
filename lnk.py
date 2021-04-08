import ctypes, sys

"""
/cygdrive/c/ProgramData/Anaconda3/Library/bin/OpenCL.dll
/cygdrive/c/ProgramData/Anaconda3/pkgs/khronos-opencl-icd-loader-2020.12.18-h8d14728_0/Library/bin/OpenCL.dll
/cygdrive/c/Users/F074018/.conda/pkgs/khronos-opencl-icd-loader-2020.12.18-h8d14728_0/Library/bin/OpenCL.dll
/cygdrive/c/Windows/servicing/LCU/Package_for_RollupFix~31bf3856ad364e35~amd64~~17763.1577.1.5/amd64_dual_rdvgwddmdx11.inf_31bf3856ad364e35_10.0.17763.134_none_79f739fa0dcd1ce8/f/opencl.dll
/cygdrive/c/Windows/servicing/LCU/Package_for_RollupFix~31bf3856ad364e35~amd64~~17763.1577.1.5/amd64_dual_rdvgwddmdx11.inf_31bf3856ad364e35_10.0.17763.134_none_79f739fa0dcd1ce8/r/opencl.dll
/cygdrive/c/Windows/servicing/LCU/Package_for_RollupFix~31bf3856ad364e35~amd64~~17763.1697.1.9/amd64_dual_rdvgwddmdx11.inf_31bf3856ad364e35_10.0.17763.134_none_79f739fa0dcd1ce8/f/opencl.dll
/cygdrive/c/Windows/servicing/LCU/Package_for_RollupFix~31bf3856ad364e35~amd64~~17763.1697.1.9/amd64_dual_rdvgwddmdx11.inf_31bf3856ad364e35_10.0.17763.134_none_79f739fa0dcd1ce8/r/opencl.dll
/cygdrive/c/Windows/System32/DriverStore/FileRepository/rdvgwddmdx11.inf_amd64_2a04ea66c78bd1a9/opencl.dll
/cygdrive/c/Windows/System32/OpenCL.DLL
/cygdrive/c/Windows/SysWOW64/opencl.dll
/cygdrive/c/Windows/WinSxS/amd64_dual_rdvgwddmdx11.inf_31bf3856ad364e35_10.0.17763.1_none_f5eacb26e053cd47/opencl.dll
/cygdrive/c/Windows/WinSxS/wow64_microsoft-windows-r..xwddmdriver-wow64-c_31bf3856ad364e35_10.0.17763.1_none_a1ee56d8046354ed/opencl.dll
/cygdrive/c/Windows/WinSxS/amd64_dual_rdvgwddmdx11.inf_31bf3856ad364e35_10.0.17763.134_none_79f739fa0dcd1ce8/opencl.dll
"""

dll = r'C:\Users\F074018\Anaconda3\Library\bin\OpenCL.dll'
dll = r'c:\Windows\System32\OpenCL.DLL'
#dll = r'c:\Windows\SysWOW64\OpenCL.DLL' # OSError: [WinError 193] %1 n’est pas une application Win32 valide

######################

def b2_cl_bool(b):
	""
	assert b in (b'',b'\x00',b'\x01'), b ## b'\x00' normalement n'arrive pas
	return b == b'\x01'
def b2_cl_command_queue_properties(b):
	""
	assert len(b) > 0, len(b)
	return b
def b2_cl_device_affinity_domain(b):
	""
	assert len(b) in (0,), len(b)
	return b
def b2_cl_device_exec_capabilities(b):
	""
	assert len(b) > 0, len(b)
	return b
def b2_cl_device_fp_config(b):
	""
	assert len(b) in (0,1), len(b)
	return b
def b2_cl_device_id(b):
	""
	assert len(b) in (0,), len(b)
	return b
def b2_cl_device_local_mem_type(b):
	""
	assert len(b) > 0, len(b)
	return b
def b2_cl_device_mem_cache_type(b):
	""
	assert len(b) > 0, len(b)
	return b
def b2_cl_device_partition_property_ARRAY(b):
	""
	assert len(b) in (0,2), len(b)
	return b
def b2_cl_device_type(b):
	""
	assert len(b) <= 1, len(b)
	dt = 0 if len(b)== 0 else b[0]
	assert dt < (1<<5), dt
	l = []
	for dtn_i, dtn in enumerate(cl_device_type_TAGS):
		if dt & (1<<dtn_i):
			l.append(dtn)
	return l
def b2_cl_platform_id(b):
	""
	assert len(b) > 0, len(b)
	return b
def b2_cl_ulong(b):
	""
	assert len(b) <= 8, len(b)
	return int.from_bytes(b, 'little')
def b2_cl_uint(b):
	""
	assert len(b) <= 4, len(b)
	return int.from_bytes(b, 'little')
def b2_size_t(b):
	""
	assert len(b) <= 8, len(b)
	return int.from_bytes(b, 'little')
def b2_size_t_ARRAY(b):
	""
	assert len(b) in (0,), len(b)
	return b
def b2_str(b):
	""
	return b.decode('cp1250')

#### BEGIN cl.h ######

CL_FALSE = 0
CL_TRUE  = 1

cl_platform_info_START = 0x0900
cl_platform_info_TAGS = [
"PROFILE"    , #                     0x0900,
"VERSION"    , #                     0x0901,
"NAME"       , #                     0x0902,
"VENDOR"     , #                     0x0903,
"EXTENSIONS" , #                     0x0904,
]

## cl_device_type - bitfield */
CL_DEVICE_TYPE_DEFAULT     =                (1 << 0)
CL_DEVICE_TYPE_CPU         =                (1 << 1)
CL_DEVICE_TYPE_GPU         =                (1 << 2)
CL_DEVICE_TYPE_ACCELERATOR =                (1 << 3)
CL_DEVICE_TYPE_CUSTOM      =                (1 << 4)
CL_DEVICE_TYPE_ALL         =                0xFFFFFFFF

cl_device_type_TAGS = ['DEFAULT','CPU','GPU','ACCELERATOR','CUSTOM']


cl_device_info_START = 0x1000
cl_device_info_TAGS = [
["TYPE"                             , b2_cl_device_type],
["VENDOR_ID"                        , b2_cl_uint],
["MAX_COMPUTE_UNITS"                , b2_cl_uint],
["MAX_WORK_ITEM_DIMENSIONS"         , b2_cl_uint],
["MAX_WORK_GROUP_SIZE"              , b2_size_t],
["MAX_WORK_ITEM_SIZES"              , b2_size_t_ARRAY],
["PREFERRED_VECTOR_WIDTH_CHAR"      , b2_cl_uint],
["PREFERRED_VECTOR_WIDTH_SHORT"     , b2_cl_uint],
["PREFERRED_VECTOR_WIDTH_INT"       , b2_cl_uint],
["PREFERRED_VECTOR_WIDTH_LONG"      , b2_cl_uint],
["PREFERRED_VECTOR_WIDTH_FLOAT"     , b2_cl_uint],
["PREFERRED_VECTOR_WIDTH_DOUBLE"    , b2_cl_uint],
["MAX_CLOCK_FREQUENCY"              , b2_cl_uint],
["ADDRESS_BITS"                     , b2_cl_uint],
["MAX_READ_IMAGE_ARGS"              , b2_cl_uint],
["MAX_WRITE_IMAGE_ARGS"             , b2_cl_uint],
["MAX_MEM_ALLOC_SIZE"               , b2_cl_ulong],
["IMAGE2D_MAX_WIDTH"                , b2_size_t],
["IMAGE2D_MAX_HEIGHT"               , b2_size_t],
["IMAGE3D_MAX_WIDTH"                , b2_size_t],
["IMAGE3D_MAX_HEIGHT"               , b2_size_t],
["IMAGE3D_MAX_DEPTH"                , b2_size_t],
["IMAGE_SUPPORT"                    , b2_cl_bool],
["MAX_PARAMETER_SIZE"               , b2_size_t],
["MAX_SAMPLERS"                     , b2_cl_uint],
["MEM_BASE_ADDR_ALIGN"              , b2_cl_uint],
["MIN_DATA_TYPE_ALIGN_SIZE"         , b2_cl_uint],  ### DEPRECATED
["SINGLE_FP_CONFIG"                 , b2_cl_device_fp_config],
["GLOBAL_MEM_CACHE_TYPE"            , b2_cl_device_mem_cache_type],
["GLOBAL_MEM_CACHELINE_SIZE"        , b2_cl_uint],
["GLOBAL_MEM_CACHE_SIZE"            , b2_cl_ulong],
["GLOBAL_MEM_SIZE"                  , b2_cl_ulong],
["MAX_CONSTANT_BUFFER_SIZE"         , b2_cl_ulong],
["MAX_CONSTANT_ARGS"                , b2_cl_uint],
["LOCAL_MEM_TYPE"                   , b2_cl_device_local_mem_type],
["LOCAL_MEM_SIZE"                   , b2_cl_ulong],
["ERROR_CORRECTION_SUPPORT"         , b2_cl_bool],
["PROFILING_TIMER_RESOLUTION"       , b2_size_t],
["ENDIAN_LITTLE"                    , b2_cl_bool],
["AVAILABLE"                        , b2_cl_bool],
["COMPILER_AVAILABLE"               , b2_cl_bool],
["EXECUTION_CAPABILITIES"           , b2_cl_device_exec_capabilities],
["QUEUE_PROPERTIES"                 , b2_cl_command_queue_properties],
["NAME"                             , b2_str],
["VENDOR"                           , b2_str],
["DRIVER_VERSION"                   , b2_str],  ## special
["PROFILE"                          , b2_str],
["VERSION"                          , b2_str],
["EXTENSIONS"                       , b2_str],
["PLATFORM"                         , b2_cl_platform_id],
["DOUBLE_FP_CONFIG"                 , b2_cl_device_fp_config],
['reserved for CL_DEVICE_HALF_FP_CONFIG', None],
["PREFERRED_VECTOR_WIDTH_HALF"      , b2_cl_uint],
["HOST_UNIFIED_MEMORY"              , b2_cl_bool],
["NATIVE_VECTOR_WIDTH_CHAR"         , b2_cl_uint],
["NATIVE_VECTOR_WIDTH_SHORT"        , b2_cl_uint],
["NATIVE_VECTOR_WIDTH_INT"          , b2_cl_uint],
["NATIVE_VECTOR_WIDTH_LONG"         , b2_cl_uint],
["NATIVE_VECTOR_WIDTH_FLOAT"        , b2_cl_uint],
["NATIVE_VECTOR_WIDTH_DOUBLE"       , b2_cl_uint],
["NATIVE_VECTOR_WIDTH_HALF"         , b2_cl_uint],
["OPENCL_C_VERSION"                 , b2_str],
["LINKER_AVAILABLE"                 , b2_cl_bool],
["BUILT_IN_KERNELS"                 , b2_str],
["IMAGE_MAX_BUFFER_SIZE"            , b2_size_t],
["IMAGE_MAX_ARRAY_SIZE"             , b2_size_t],
["PARENT_DEVICE"                    , b2_cl_device_id],
["PARTITION_MAX_SUB_DEVICES"        , b2_cl_uint],
["PARTITION_PROPERTIES"             , b2_cl_device_partition_property_ARRAY],
["PARTITION_AFFINITY_DOMAIN"        , b2_cl_device_affinity_domain],
["PARTITION_TYPE"                   , b2_cl_device_partition_property_ARRAY],
["REFERENCE_COUNT"                  , b2_cl_uint],
["PREFERRED_INTEROP_USER_SYNC"      , b2_cl_bool],
["PRINTF_BUFFER_SIZE"               , b2_size_t],
["IMAGE_PITCH_ALIGNMENT"            , None],  # hors spec 1.2
["IMAGE_BASE_ADDRESS_ALIGNMENT"     , None],  # hors spec 1.2
]

## cl_mem_flags - bitfield */
CL_MEM_READ_WRITE      =                     (1 << 0)
CL_MEM_WRITE_ONLY      =                     (1 << 1)
CL_MEM_READ_ONLY       =                     (1 << 2)
CL_MEM_USE_HOST_PTR    =                     (1 << 3)
CL_MEM_ALLOC_HOST_PTR  =                     (1 << 4)
CL_MEM_COPY_HOST_PTR   =                     (1 << 5)
## reserved                                  (1 << 6)    
CL_MEM_HOST_WRITE_ONLY =                     (1 << 7)
CL_MEM_HOST_READ_ONLY  =                     (1 << 8)
CL_MEM_HOST_NO_ACCESS  =                     (1 << 9)

#### END cl.h ######

if True: # mylib is None or mylib._name != dll:
	mylib = ctypes.CDLL(dll)
	
#
intptr_t = ctypes.c_int64
_P = ctypes.POINTER
# base types
cl_int = ctypes.c_int32
cl_long = ctypes.c_int64
cl_uint = ctypes.c_uint32
cl_ulong = ctypes.c_uint64
size_t = ctypes.c_size_t
void = ctypes.c_char
### voir https://stackoverflow.com/questions/33484591/callbacks-with-ctypes-how-to-call-a-python-function-from-c
CL_CALLBACK = ctypes.POINTER(void) ## car jamais utilise : None
# other types
cl_bitfield = cl_ulong
cl_bool = cl_uint
cl_command_queue = ctypes.c_void_p
cl_command_queue_properties = cl_bitfield
cl_context = ctypes.c_void_p # ctypes.POINTER(void)
cl_context_properties = intptr_t
cl_device_id = ctypes.c_void_p # ctypes.POINTER(void)
cl_device_info = cl_uint
cl_device_type = cl_bitfield
cl_event = ctypes.c_void_p
cl_kernel = ctypes.c_void_p
cl_mem = ctypes.c_void_p
cl_mem_flags = cl_bitfield
cl_platform_id = ctypes.c_void_p # ctypes.POINTER(void)
cl_platform_info = cl_uint
cl_program = ctypes.c_void_p

## bug ? None not accepted as a CFUNCTYPE

CL_CALLBACK_context = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p)
def DFLT_CALLBACK_context(a,b,c,d): print("default CALLBACK context\n")
DFLT_CALLBACK_context = CL_CALLBACK_context(DFLT_CALLBACK_context)
NULL_CALLBACK_context = ctypes.cast(None, CL_CALLBACK_context)
assert bytes(memoryview(NULL_CALLBACK_context)) == b'\x00\x00\x00\x00\x00\x00\x00\x00'

CL_CALLBACK_program = ctypes.CFUNCTYPE(None, cl_program, ctypes.c_void_p)
def DFLT_CALLBACK_program(a,b): print("default CALLBACK program\n")
DFLT_CALLBACK_program = CL_CALLBACK_program(DFLT_CALLBACK_program)
NULL_CALLBACK_program = ctypes.cast(None, CL_CALLBACK_program)
assert bytes(memoryview(NULL_CALLBACK_program)) == b'\x00\x00\x00\x00\x00\x00\x00\x00'

###### https://stackoverflow.com/questions/2962281/what-is-the-pythonic-way-to-setattr-for-a-module

api = [
["clBuildProgram",			cl_int,		cl_program, cl_uint, _P(cl_device_id), ctypes.c_char_p, CL_CALLBACK_program, ctypes.c_void_p],
["clCompileProgram"],
["clCreateBuffer",			cl_mem,		cl_context, cl_mem_flags, size_t, ctypes.c_void_p, _P(cl_int)],
["clCreateCommandQueue",	cl_command_queue, cl_context, cl_device_id, cl_command_queue_properties, _P(cl_int)],
["clCreateCommandQueueWithProperties"],
["clCreateContext",			cl_context,	_P(cl_context_properties), cl_uint, _P(cl_device_id), CL_CALLBACK_context, ctypes.c_void_p, _P(cl_int)],
["clCreateContextFromType"],
["clCreateFromGLBuffer"],
["clCreateFromGLRenderbuffer"],
["clCreateFromGLTexture"],
["clCreateFromGLTexture2D"],
["clCreateFromGLTexture3D"],
["clCreateImage"],
["clCreateImage2D"],
["clCreateImage3D"],
["clCreateKernel",			cl_kernel,	cl_program, ctypes.c_char_p, _P(cl_int)],
["clCreateKernelsInProgram"],
["clCreatePipe"],
["clCreateProgramWithBinary"],
["clCreateProgramWithBuiltInKernels"],
["clCreateProgramWithSource", cl_program, cl_context, cl_uint, _P(ctypes.c_char_p), _P(size_t), _P(cl_int)],
# clCreateSampler
# clCreateSamplerWithProperties
# clCreateSubBuffer
# clCreateSubDevices
# clCreateUserEvent
# clEnqueueAcquireGLObjects
# clEnqueueBarrier
# clEnqueueBarrierWithWaitList
# clEnqueueCopyBuffer
# clEnqueueCopyBufferRect
# clEnqueueCopyBufferToImage
# clEnqueueCopyImage
# clEnqueueCopyImageToBuffer
# clEnqueueFillBuffer
# clEnqueueFillImage
# clEnqueueMapBuffer
# clEnqueueMapImage
# clEnqueueMarker
# clEnqueueMarkerWithWaitList
# clEnqueueMigrateMemObjects
["clEnqueueNDRangeKernel",	cl_int,		cl_command_queue, cl_kernel, cl_uint, _P(size_t), _P(size_t), _P(size_t), cl_uint, _P(cl_event), _P(cl_event)],
# clEnqueueNativeKernel
["clEnqueueReadBuffer",		cl_int,		cl_command_queue, cl_mem, cl_bool, size_t, size_t, ctypes.c_void_p, cl_uint, _P(cl_event), _P(cl_event)],
# clEnqueueReadBufferRect
# clEnqueueReadImage
# clEnqueueReleaseGLObjects
# clEnqueueSVMFree
# clEnqueueSVMMap
# clEnqueueSVMMemFill
# clEnqueueSVMMemcpy
# clEnqueueSVMUnmap
# clEnqueueTask
# clEnqueueUnmapMemObject
# clEnqueueWaitForEvents
["clEnqueueWriteBuffer",	cl_int,		cl_command_queue, cl_mem, cl_bool, size_t, size_t, ctypes.c_void_p, cl_uint, _P(cl_event), _P(cl_event)],
# clEnqueueWriteBufferRect
# clEnqueueWriteImage
["clFinish",				cl_int,	cl_command_queue],
# clFlush
# clGetCommandQueueInfo
# clGetContextInfo
["clGetDeviceIDs",			cl_int,		cl_platform_id, cl_device_type, cl_uint, _P(cl_device_id), _P(cl_uint)],
["clGetDeviceInfo",			cl_int,		cl_device_id, cl_device_info, size_t, ctypes.c_void_p, _P(size_t)],
# clGetEventInfo
# clGetEventProfilingInfo
# clGetExtensionFunctionAddress
# clGetExtensionFunctionAddressForPlatform
# clGetGLObjectInfo
# clGetGLTextureInfo
# clGetImageInfo
# clGetKernelArgInfo
# clGetKernelInfo
# clGetKernelWorkGroupInfo
# clGetMemObjectInfo
# clGetPipeInfo
["clGetPlatformIDs", 		cl_int,		cl_uint, _P(cl_platform_id), _P(cl_uint)],
["clGetPlatformInfo",		cl_int,		cl_platform_id, cl_platform_info, size_t, ctypes.c_void_p, _P(size_t)],
# clGetProgramBuildInfo
# clGetProgramInfo
# clGetSamplerInfo
# clGetSupportedImageFormats
# clLinkProgram
["clReleaseCommandQueue",	cl_int,		cl_command_queue],
["clReleaseContext",		cl_int,		cl_context],
# clReleaseDevice
# clReleaseEvent
["clReleaseKernel",			cl_int,		cl_kernel],
["clReleaseMemObject",		cl_int,		cl_mem],
["clReleaseProgram",		cl_int,		cl_program],
# clReleaseSampler
# clRetainCommandQueue
# clRetainContext
# clRetainDevice
# clRetainEvent
# clRetainKernel
# clRetainMemObject
# clRetainProgram
# clRetainSampler
# clSVMAlloc
# clSVMFree
# clSetCommandQueueProperty
# clSetEventCallback
["clSetKernelArg",			cl_int,		cl_kernel, cl_uint, size_t, ctypes.c_void_p],
# clSetKernelArgSVMPointer
# clSetKernelExecInfo
# clSetMemObjectDestructorCallback
# clSetUserEventStatus
# clUnloadCompiler
# clUnloadPlatformCompiler
# clWaitForEvents
]

_m = sys.modules[__name__]
for _l in api:
	_fn = _l[0]
	_fd = getattr(mylib, _fn, None)
	if _fd is None:
		print(f"OpenCL WARNING : {fn} not in {mylib}")
	elif len(_l) > 1:
		_fd.restype = _l[1]
		_fd.argtypes = _l[2:]
	setattr(_m, _fn, _fd)

"""
clGetPlatformIDs = mylib.clGetPlatformIDs
clGetPlatformIDs.restype = cl_int
clGetPlatformIDs.argtypes = [cl_uint, ctypes.POINTER(cl_platform_id), ctypes.POINTER(cl_uint)]

clGetPlatformInfo = mylib.clGetPlatformInfo
clGetPlatformInfo.restype = cl_int
clGetPlatformInfo.argtypes = [cl_platform_id, cl_platform_info, size_t, ctypes.POINTER(void), ctypes.POINTER(size_t)]

clGetDeviceIDs = mylib.clGetDeviceIDs
clGetDeviceIDs.restype = cl_int
clGetDeviceIDs.argtypes = [cl_platform_id, cl_device_type, cl_uint, ctypes.POINTER(cl_device_id), ctypes.POINTER(cl_uint)]

clGetDeviceInfo = mylib.clGetDeviceInfo
clGetDeviceInfo.restype = cl_int
clGetDeviceInfo.argtypes = [cl_device_id, cl_device_info, size_t, ctypes.c_void_p, ctypes.POINTER(size_t)]

CL_CALLBACK_context = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p)
def DFLT_CALLBACK_context(a,b,c,d): print("default CALLBACK context\n")
DFLT_CALLBACK_context = CL_CALLBACK_context(DFLT_CALLBACK_context)
NULL_CALLBACK_context = ctypes.cast(None, CL_CALLBACK_context)
assert bytes(memoryview(NULL_CALLBACK_context)) == b'\x00\x00\x00\x00\x00\x00\x00\x00'
	
clCreateContext = mylib.clCreateContext
clCreateContext.restype = cl_context
clCreateContext.argtypes = [ctypes.POINTER(cl_context_properties), cl_uint, ctypes.POINTER(cl_device_id), CL_CALLBACK_context, ctypes.c_void_p, ctypes.POINTER(cl_int)]

clReleaseContext = mylib.clReleaseContext
clReleaseContext.restype = cl_int
clReleaseContext.argtypes = [cl_context]

clCreateCommandQueue = mylib.clCreateCommandQueue
clCreateCommandQueue.restype = cl_command_queue
clCreateCommandQueue.argtypes = [cl_context, cl_device_id, cl_command_queue_properties, ctypes.POINTER(cl_int)]

clReleaseCommandQueue = mylib.clReleaseCommandQueue
clReleaseCommandQueue.restype = cl_int
clReleaseCommandQueue.argtypes = [cl_command_queue]

clCreateProgramWithSource = mylib.clCreateProgramWithSource
clCreateProgramWithSource.restype = cl_program
clCreateProgramWithSource.argtypes = [cl_context, cl_uint, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(size_t), ctypes.POINTER(cl_int)]

clReleaseProgram = mylib.clReleaseProgram
clReleaseProgram.restype = cl_int
clReleaseProgram.argtypes = [cl_program]

CL_CALLBACK_program = ctypes.CFUNCTYPE(None, cl_program, ctypes.c_void_p)
def DFLT_CALLBACK_program(a,b): print("default CALLBACK program\n")
DFLT_CALLBACK_program = CL_CALLBACK_program(DFLT_CALLBACK_program)
NULL_CALLBACK_program = ctypes.cast(None, CL_CALLBACK_program)
assert bytes(memoryview(NULL_CALLBACK_program)) == b'\x00\x00\x00\x00\x00\x00\x00\x00'

clBuildProgram = mylib.clBuildProgram
clBuildProgram.restype = cl_int
clBuildProgram.argtypes = [cl_program, cl_uint, _P(cl_device_id), ctypes.c_char_p, CL_CALLBACK_program, ctypes.c_void_p]

clCreateKernel = mylib.clCreateKernel
clCreateKernel.restype = cl_kernel
clCreateKernel.argtypes = [cl_program, ctypes.c_char_p, _P(cl_int)]

clReleaseKernel = mylib.clReleaseKernel
clReleaseKernel.restype = cl_int
clReleaseKernel.argtypes = [cl_kernel]

clCreateBuffer = mylib.clCreateBuffer
clCreateBuffer.restype = cl_mem
clCreateBuffer.argtypes = [cl_context, cl_mem_flags, size_t, ctypes.c_void_p, _P(cl_int)]

clReleaseMemObject = mylib.clReleaseMemObject
clReleaseMemObject.restype = cl_int
clReleaseMemObject.argtypes = [cl_mem]
"""
_R = ctypes.byref

buf1024 = ctypes.create_string_buffer(1024)
buf_sz = size_t()
buf_sz_REF = _R(buf_sz)
ndevs = ctypes.c_uint()
ndevs_REF = _R(ndevs)

def gatherPlatformInfo(p_addr):
	#
	for k_i,k in enumerate(cl_platform_info_TAGS, start=cl_platform_info_START):
		r = clGetPlatformInfo(p_addr, k_i, 1024, buf1024, buf_sz_REF)
		assert r == 0 and buf_sz.value > 0
		s = buf1024.value[:buf_sz.value].decode('cp1250')
		print(f'{k} : {s}')
	r = clGetDeviceIDs(p_addr, CL_DEVICE_TYPE_ALL, 0, None, ndevs_REF)
	assert r == 0, r
	assert ndevs.value > 0
	devices_vec = (cl_device_id * ndevs.value)() # ctypes.POINTER(ctypes.c_char)
	r = clGetDeviceIDs(p_addr, CL_DEVICE_TYPE_ALL, ndevs.value, devices_vec, None)
	assert r == 0, r
	for i in range(ndevs.value):
		print(f'** device {i} **')
		d_addr = devices_vec[i]
		for k_i, (k,fn) in enumerate(cl_device_info_TAGS, start=cl_device_info_START):
			buf_sz.value = 10000000
			r = clGetDeviceInfo(d_addr, k_i, 1024, buf1024, buf_sz_REF)
			if r == 0:
				assert buf_sz.value >= 0 and buf_sz.value <= 1024
			else:
				assert buf_sz.value == 10000000
				buf1024[:32] = b'!!!! clGetDeviceInfo FAILED !!!!'
				buf_sz.value = 32
				fn = None
			s = buf1024.value[:buf_sz.value]
			assert s == b'' or s[-1] != 0, s
			if fn is not None:
				s = fn(s)
			print(f'{k} : {s}')

#mylib = None

#def clinfo(dll = r'c:\Windows\System32\OpenCL.DLL'):
	#
#	global mylib
if True:
	

	# None should be used as the NULL pointer


	#
	num_platforms = cl_uint() # 0
	r = clGetPlatformIDs(0,None, _R(num_platforms))
	assert r == 0
	assert num_platforms.value > 0
	platforms_vec = (cl_platform_id * num_platforms.value)() # ctypes.POINTER(ctypes.c_char)
	r = clGetPlatformIDs(num_platforms.value, platforms_vec, None)
	assert r == 0
	platforms_inf = [None] * num_platforms.value
	for p in range(num_platforms.value):
		print(f'************* platform {p} *************')
		p_addr = platforms_vec[p]
		platforms_inf[p] = gatherPlatformInfo(p_addr)
		
		
if __name__ == "__main__": # vecAdd
	from math import sin, cos, ceil
	
	print("\ntest interne")
	
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
	
	## Number of work items in each local work group
	localSize = 64
	## Number of total work items - localSize must be devisor
	globalSize = ceil(n/localSize)*localSize;
	
	nb_bytes = n * 4
	h_a = (ctypes.c_float * n)(*[sin(i)*sin(i) for i in range(n)])
	h_b = (ctypes.c_float * n)(*[cos(i)*cos(i) for i in range(n)])
	h_c = (ctypes.c_float * n)() # all 0.0
	e = cl_int(-1000)
	e_REF = _R(e)
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
	err  = clEnqueueWriteBuffer(queue, d_a, CL_TRUE, 0, nb_bytes, h_a, 0, None, None)
	err |= clEnqueueWriteBuffer(queue, d_b, CL_TRUE, 0, nb_bytes, h_b, 0, None, None)
	assert err == 0
	err   = clSetKernelArg(kernel, 0, ctypes.sizeof(cl_mem), _R(cl_mem(d_a)))
	err  |= clSetKernelArg(kernel, 1, ctypes.sizeof(cl_mem), _R(cl_mem(d_b)))
	err  |= clSetKernelArg(kernel, 2, ctypes.sizeof(cl_mem), _R(cl_mem(d_c)))
	err  |= clSetKernelArg(kernel, 3, ctypes.sizeof(cl_uint), _R(cl_uint(n)))
	assert err == 0 ## -38 == CL_INVALID_MEM_OBJECT
	err = clEnqueueNDRangeKernel(queue, kernel, 1, None, _R(size_t(globalSize)), _R(size_t(localSize)), 0, None, None)
	assert err == 0
	err = clFinish(queue)
	assert err == 0
	###
	err = clEnqueueReadBuffer(queue, d_c, CL_TRUE, 0, nb_bytes, h_c, 0, None, None)
	assert err == 0
	### attendre ou pas ?
	delta = [h_c[i]-1 for i in range(n)]
	print(delta)
	###
	err  = clReleaseMemObject(d_a)
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
	