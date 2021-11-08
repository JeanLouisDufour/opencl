import ctypes, re, os, sys
_PyCArrayType = type(ctypes.c_float*36) # dans _ctypes, mais inaccessible autrement

Kalray = False
if sys.platform == 'linux':
	if os.path.exists(r'/opt/kalray'):
		Kalray = True
		dll = r'/opt/kalray/accesscore/lib/libOpenCL.so.2.5.0' # SI OSError: ... , passer de Anaconda a Python basique
	else:
		dll = r'/usr/lib/x86_64-linux-gnu/libOpenCL.so.1.0.0'
	# dll = r'/usr/lib/x86_64-linux-gnu/hwloc/hwloc_opencl.so' # OSError: /usr/lib/x86_64-linux-gnu/hwloc/hwloc_opencl.so: undefined symbol: hwloc_obj_add_info
else:
	dll = r'C:\Users\F074018\Anaconda3\Library\bin\OpenCL.dll'
	dll = r'c:\Windows\System32\OpenCL.DLL'
	# dll = r'c:\Windows\SysWOW64\OpenCL.DLL' # OSError: [WinError 193] %1 n’est pas une application Win32 valide

######## types de base ##############

def b2_cl_uint(b):
	""
	assert len(b) == 4, len(b)
	return int.from_bytes(b, 'little') # unsigned

def b2_cl_ulong(b):
	""
	assert len(b) == 8, len(b)
	return int.from_bytes(b, 'little') # unsigned

####### types derives #######

def b2_cl_bool(b):
	""
	booleen = b2_cl_uint(b)
	assert 0 <= booleen <= 1, booleen
	return booleen
b2_cl_command_queue_properties = b2_cl_ulong
b2_cl_device_affinity_domain = b2_cl_ulong
b2_cl_device_exec_capabilities = b2_cl_ulong
b2_cl_device_fp_config = b2_cl_ulong
b2_cl_device_id = b2_cl_ulong
b2_cl_device_local_mem_type = b2_cl_uint
b2_cl_device_mem_cache_type = b2_cl_uint
def b2_cl_device_partition_property_ARRAY(b):
	""
	#assert len(b) in (0,2), len(b)
	elt_sz = 4
	assert len(b) % elt_sz == 0, b
	return [int.from_bytes(b[i*elt_sz:(i+1)*elt_sz], 'little') for i in range(len(b)//elt_sz)]
def b2_cl_device_type(b):
	""
	dt = b2_cl_ulong(b)
	assert dt < (1<<5), dt
	l = []
	for dtn_i, dtn in enumerate(cl_device_type_TAGS):
		if dt & (1<<dtn_i):
			l.append(dtn)
	return l
b2_cl_platform_id = b2_cl_ulong
b2_size_t = b2_cl_ulong
def b2_size_t_ARRAY(b):
	""
	elt_sz = 8
	assert len(b) % elt_sz == 0, len(b)
	return [int.from_bytes(b[i*elt_sz:(i+1)*elt_sz], 'little') for i in range(len(b)//elt_sz)]
def b2_str(b):
	""
	assert b == b'' or b[-1] == 0, b
	return b[:-1].decode('cp1250') if b != b'' else ''

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

## cl_program_build_info */
CL_PROGRAM_BUILD_STATUS                   =  0x1181
CL_PROGRAM_BUILD_OPTIONS                  =  0x1182
CL_PROGRAM_BUILD_LOG                      =  0x1183
CL_PROGRAM_BINARY_TYPE                    =  0x1184

#### END cl.h ######

if True: # mylib is None or mylib._name != dll:
	mylib = ctypes.CDLL(dll)
	
#
intptr_t = ctypes.c_int64
Ptr = _P = ctypes.POINTER
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
cl_program_build_info = cl_uint

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
["clCreateContextFromType",	cl_context,	_P(cl_context_properties), cl_device_type, CL_CALLBACK_context, ctypes.c_void_p, _P(cl_int)],
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
["clGetProgramBuildInfo",	cl_int,		cl_program, cl_device_id, cl_program_build_info, size_t, ctypes.c_void_p, _P(size_t)],
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
		print(f"OpenCL WARNING : {_fn} not in {mylib}")
	elif len(_l) > 1:
		_fd.restype = _l[1]
		_fd.argtypes = _l[2:]
	setattr(_m, _fn, _fd)

Ref = _R = ctypes.byref

buf1024 = ctypes.create_string_buffer(1024)
buf_sz = size_t()
buf_sz_REF = _R(buf_sz)
ndevs = ctypes.c_uint()
ndevs_REF = _R(ndevs)

## Error Codes */
CL_SUCCESS                                =  0
CL_DEVICE_NOT_FOUND                       =  -1
CL_DEVICE_NOT_AVAILABLE                   =  -2
CL_COMPILER_NOT_AVAILABLE                 =  -3
CL_MEM_OBJECT_ALLOCATION_FAILURE          =  -4
CL_OUT_OF_RESOURCES                       =  -5
CL_OUT_OF_HOST_MEMORY                     =  -6
CL_PROFILING_INFO_NOT_AVAILABLE           =  -7
CL_MEM_COPY_OVERLAP                       =  -8
CL_IMAGE_FORMAT_MISMATCH                  =  -9
CL_IMAGE_FORMAT_NOT_SUPPORTED             =  -10
CL_BUILD_PROGRAM_FAILURE 				  =  -11
CL_MAP_FAILURE                               = -12
CL_MISALIGNED_SUB_BUFFER_OFFSET              = -13
CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST = -14
CL_COMPILE_PROGRAM_FAILURE                   = -15
CL_LINKER_NOT_AVAILABLE                      = -16
CL_LINK_PROGRAM_FAILURE                      = -17
CL_DEVICE_PARTITION_FAILED                   = -18
CL_KERNEL_ARG_INFO_NOT_AVAILABLE             = -19
# no man's land
CL_INVALID_VALUE                             = -30
CL_INVALID_DEVICE_TYPE                       = -31
CL_INVALID_PLATFORM                          = -32
#
CL_INVALID_WORK_GROUP_SIZE                   = -54
CL_INVALID_WORK_ITEM_SIZE                    = -55

clErrorCodes = [
"SUCCESS",#                                  0
"DEVICE_NOT_FOUND",#                         -1
"DEVICE_NOT_AVAILABLE",#                     -2
"COMPILER_NOT_AVAILABLE",#                   -3
"MEM_OBJECT_ALLOCATION_FAILURE",#            -4
"OUT_OF_RESOURCES",#                         -5
"OUT_OF_HOST_MEMORY",#                       -6
"PROFILING_INFO_NOT_AVAILABLE",#             -7
"MEM_COPY_OVERLAP",#                         -8
"IMAGE_FORMAT_MISMATCH",#                    -9
"IMAGE_FORMAT_NOT_SUPPORTED",#               -10
"BUILD_PROGRAM_FAILURE",#                    -11
"MAP_FAILURE",#                              -12
"MISALIGNED_SUB_BUFFER_OFFSET",#             -13
"EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST",# -14
"COMPILE_PROGRAM_FAILURE",#                  -15
"LINKER_NOT_AVAILABLE",#                     -16
"LINK_PROGRAM_FAILURE",#                     -17
"DEVICE_PARTITION_FAILED",#                  -18
"KERNEL_ARG_INFO_NOT_AVAILABLE",#            -19
	] + [f"*** UNKNOWN ERROR CODE -{i} ***" for i in range(20,30)] + [
"INVALID_VALUE",#                            -30
"INVALID_DEVICE_TYPE",#                      -31
"INVALID_PLATFORM",#                         -32
	] + [f"*** UNKNOWN ERROR CODE -{i} ***" for i in range(33,54)] + [
"INVALID_WORK_GROUP_SIZE",#                  -54
"INVALID_WORK_ITEM_SIZE",#                   -55
	]
assert clErrorCodes[30] == 'INVALID_VALUE' and clErrorCodes[55] == 'INVALID_WORK_ITEM_SIZE'

def gatherPlatformInfo(p_addr, verbose=True):
	#
	result = {}
	pf_ext = []
	for k_i,k in enumerate(cl_platform_info_TAGS, start=cl_platform_info_START):
		buf_sz.value = 10000000
		r = clGetPlatformInfo(p_addr, k_i, 1024, buf1024, buf_sz_REF)
		if r == 0:
			assert buf_sz.value > 0 and buf_sz.value <= 1024
			# s = buf1024.value[:buf_sz.value].decode('cp1250')
			s = buf1024[:buf_sz.value]
			assert isinstance(s,bytes)
			s = b2_str(s)
			if k == 'EXTENSIONS':
				pf_ext = s.split()
				assert all(e.isidentifier() and e.startswith('cl_') for e in pf_ext)
		elif r == CL_INVALID_VALUE:
			s = '!!! INVALID VALUE !!!'
		elif r == CL_INVALID_PLATFORM:
			print("CL_INVALID_PLATFORM")
			return
		else:
			assert False
		print(f'{k} : {s}')
		result[k] = s
	result['devices'] = devices = []  
	r = clGetDeviceIDs(p_addr, CL_DEVICE_TYPE_ALL, 0, None, ndevs_REF)
	assert r == 0, r
	assert ndevs.value > 0
	devices_vec = (cl_device_id * ndevs.value)() # ctypes.POINTER(ctypes.c_char)
	r = clGetDeviceIDs(p_addr, CL_DEVICE_TYPE_ALL, ndevs.value, devices_vec, None)
	assert r == 0, r
	for i in range(ndevs.value):
		print(f'** device {i} **')
		d_addr = devices_vec[i]
		dev = {}
		for k_i, (k,fn) in enumerate(cl_device_info_TAGS, start=cl_device_info_START):
			if k.startswith('MAX_WORK_'):
				_ = 2+2
			buf_sz.value = 10000000
			r = clGetDeviceInfo(d_addr, k_i, 1024, buf1024, buf_sz_REF)
			if r == 0:
				assert buf_sz.value >= 0 and buf_sz.value <= 1024
			else:
				assert buf_sz.value == 10000000
				buf1024[:32] = b'!!!! clGetDeviceInfo FAILED !!!!'
				buf_sz.value = 32
				fn = None
			#s = buf1024.value[:buf_sz.value]
			#assert s == b'' or s[-1] != 0, s
			s = buf1024[:buf_sz.value]
			assert isinstance(s,bytes)
			if fn is not None:
				s = fn(s)
			if k == 'EXTENSIONS':
				dv_ext = s.split()
				assert all(e.isidentifier() and e.startswith('cl_') for e in dv_ext)
				assert set(pf_ext) <= set(dv_ext)
				s = ' '.join(e for e in dv_ext if e not in pf_ext)
			if verbose or k in {
					'ENDIAN_LITTLE',
					'EXTENSIONS',
					'GLOBAL_MEM_CACHELINE_SIZE',
					'MAX_COMPUTE_UNITS',
					'MAX_WORK_GROUP_SIZE',
					'MAX_WORK_ITEM_SIZES',
					'NAME',
					'TYPE',
					}:
				print(f'{k} : {s}')
			dev[k] = s
		devices.append(dev)
	return result

#mylib = None

# __kernel __attribute__((reqd_work_group_size(LOCAL_SIZE_X,LOCAL_SIZE_Y,1)))
# #define TEMPLATE(name,type) CONCAT(name,type)
# __kernel void TEMPLATE(lrn_full_no_scale,Dtype)(const int nthreads, __global const Dtype* in,

re_kernel = re.compile(r'kernel\s+void\s+')

def get_kernels(ksrc, macros = None):
	""
	kl = []
	#
	i = 0
	ki = ksrc.find('__kernel',i)
	while ki >= 0:
		j = ki+8 # len('__kernel')
		assert ksrc[j].isspace()
		j += 1
		while ksrc[j].isspace(): j+=1
		assert ksrc[j:j+4] == 'void'
		j = j+4
		assert ksrc[j].isspace()
		# j pointe sur les espaces avant le nom
		open_par_i = ksrc.index('(', j+1)
		kname = ksrc[j:open_par_i].strip()
		assert kname.isidentifier()
		#print(kname)
		close_par_i = ksrc.index(')', open_par_i+1)
		open_curpar_i = ksrc.index('{', close_par_i+1)
		assert open_curpar_i == close_par_i+1 or ksrc[close_par_i+1:open_curpar_i].isspace()
		params = ksrc[open_par_i+1:close_par_i].split(',')
		params = [p.strip() for p in params]
		kl.append([kname,ki, params])
		#
		i = open_curpar_i+1
		ki = ksrc.find('__kernel',i)
	return kl

# faciliter l'ecriture de arg_types
int8_t = ctypes.c_int8
int16_t = ctypes.c_int16
int32_t = ctypes.c_int32
int64_t = ctypes.c_int64
uint8_t = ctypes.c_uint8
uint16_t = ctypes.c_uint16
uint32_t = ctypes.c_uint32
uint64_t = ctypes.c_uint64
float_t = ctypes.c_float
double_t = ctypes.c_double


def kernel_initiate(ksrc, arg_types, arg_kinds, macros=None, dev_kind = None, params=None, kname=None):
	""" exemple sur vecadd :
		__kernel void vecAdd(  __global FLOAT *a,  
                       __global FLOAT *b, 
                       __global FLOAT *c,       
                       const unsigned int n)
	ksrc = ...
	n = 21
	d = kernel_initiate(ksrc, [(ctypes.c_float * n), (ctypes.c_float * n), (ctypes.c_float * n), cl_uint],"RRWC")
	"""
	# seuls les types a*b ont un attr _length_
	assert isinstance(ksrc, str)
	if ksrc.endswith("cl"):
		kfile = ksrc
		kfd = open(kfile)
		ksrc = kfd.read()
		kfd.close()
	else:
		kfile = None
	assert len(arg_types) == len(arg_kinds), (len(arg_types), len(arg_kinds))
	assert all(isinstance(x, (_PyCArrayType, int,float)) for x in arg_types)
	assert all(c in "DFILRWX" for c in arg_kinds)
	if params is None:
		params = [None]*len(arg_types)
	if len(params) < len(arg_types):
		params += [None]*(len(arg_types)-len(params))
	kl = get_kernels(ksrc, macros)
	if kname is None:
		[kname,_,kargs] = kl[0]
	else:
		for kn,_,kargs in kl:
			if kn == kname:
				break
		assert kn == kname
	assert len(kargs) == len(arg_types), (len(kargs) , len(arg_types))
	#
	"""
	nb_bytes = n * 4   ## ctypes.sizeof(h_a)
	h_a = (ctypes.c_float * n)(*[sin(i)*sin(i) for i in range(n)])
	h_b = (ctypes.c_float * n)(*[cos(i)*cos(i) for i in range(n)])
	read_arrays = [h_a, h_b]
	h_c = (ctypes.c_float * n_out)() # all 0.0
	write_arrays = [h_c]
	"""
	e = cl_int(-1000)
	e_REF = _R(e)
	kernelSource = (ctypes.c_char_p * 1)(ksrc.encode('cp1250'))
	cpPlatform = (cl_platform_id * 1)()
	err = clGetPlatformIDs(1, cpPlatform, None)
	assert err == 0
	device_id = (cl_device_id * 1)()
	if dev_kind is None:
		dev_ty = CL_DEVICE_TYPE_GPU
		err = clGetDeviceIDs(cpPlatform[0], dev_ty, 1, device_id, None)
		if err == CL_DEVICE_NOT_FOUND:
			dev_ty = CL_DEVICE_TYPE_ACCELERATOR
			err = clGetDeviceIDs(cpPlatform[0], dev_ty, 1, device_id, None)
	elif dev_kind in ("CPU","GPU") or dev_kind.startswith("ACC"):
		dev_ty = CL_DEVICE_TYPE_CPU if dev_kind=="CPU" else \
				 CL_DEVICE_TYPE_GPU if dev_kind=="GPU" else \
				 CL_DEVICE_TYPE_ACCELERATOR
		err = clGetDeviceIDs(cpPlatform[0], dev_ty, 1, device_id, None)
	else:
		assert False, "bad dev_kind"
	assert err == 0, err
	context = clCreateContext(None, 1, device_id, NULL_CALLBACK_context, None, e_REF)
	assert e.value == 0
	queue = clCreateCommandQueue(context, device_id[0], 0, e_REF);
	assert e.value == 0
	program = clCreateProgramWithSource(context, 1, kernelSource, None, e_REF)
	assert e.value == 0
	if macros is not None:
		if isinstance(macros, dict):
			txt = ""
			for mn,mv in macros.items():
				if mv in ("",None):
					txt += "-D"+mn
				elif isinstance(mv,str):
					txt += "-D"+mn+"="+mv
				else:
					txt += "-D"+mn+"="+str(mv)
				txt += " "
			macros = txt
		macros = macros.encode('cp1250')
	err = clBuildProgram(program, 0, None, macros, NULL_CALLBACK_program, None)
	if err == CL_BUILD_PROGRAM_FAILURE:
		"""
		size_t log_size;
    clGetProgramBuildInfo(program, devices_id[0], CL_PROGRAM_BUILD_LOG, 0, NULL, &log_size);

    // Allocate memory for the log
    char *log = (char *) malloc(log_size);

    // Get the log
    clGetProgramBuildInfo(program, devices_id[0], CL_PROGRAM_BUILD_LOG, log_size, log, NULL);

    // Print the log
    printf("%s\n", log);
		"""
		log_size = size_t()
		err = clGetProgramBuildInfo(program, device_id[0], CL_PROGRAM_BUILD_LOG, 0, None, Ref(log_size))
		assert err == 0
		log = ctypes.create_string_buffer(log_size.value)
		err = clGetProgramBuildInfo(program, device_id[0], CL_PROGRAM_BUILD_LOG, log_size, log, None)
		assert err == 0
		d = {
			'src': ksrc, 'arg_types': arg_types, 'arg_kinds': arg_kinds,
			'name': kname, 'args': kargs,
			'platform': cpPlatform[0], 'device': device_id[0], 'device_type': dev_ty,
			'context': context, 'queue': queue,
			'program': program,
			'error': log.value.decode('cp1250')
			}
		kernel_terminate(d)
		return d
	else:
		assert err == 0, err
	kernel = clCreateKernel(program, kname.encode('cp1250'), e_REF) # b"vecAdd"
	assert e.value == 0
	"""
	d_a = clCreateBuffer(context, CL_MEM_READ_ONLY, nb_bytes, None, e_REF)
	assert e.value == 0
	d_b = clCreateBuffer(context, CL_MEM_READ_ONLY, nb_bytes, None, e_REF)
	assert e.value == 0
	read_buffers = [d_a,d_b]
	d_c = clCreateBuffer(context, CL_MEM_WRITE_ONLY, n_out*4, None, e_REF)
	assert e.value == 0
	write_buffers = [d_c]
	if False: # original
		err  = clEnqueueWriteBuffer(queue, d_a, CL_TRUE, 0, nb_bytes, h_a, 0, None, None)
		err |= clEnqueueWriteBuffer(queue, d_b, CL_TRUE, 0, nb_bytes, h_b, 0, None, None)
		assert err == 0
	err   = clSetKernelArg(kernel, 0, ctypes.sizeof(cl_mem), _R(cl_mem(d_a)))
	err  |= clSetKernelArg(kernel, 1, ctypes.sizeof(cl_mem), _R(cl_mem(d_b)))
	err  |= clSetKernelArg(kernel, 2, ctypes.sizeof(cl_mem), _R(cl_mem(d_c)))
	err  |= clSetKernelArg(kernel, 3, ctypes.sizeof(cl_uint), _R(cl_uint(n)))
	assert err == 0 ## -38 == CL_INVALID_MEM_OBJECT
	"""
	err = 0
	eff_params = params
	params = []
	#read_arrays, write_arrays, read_buffers, write_buffers = [],[],[],[]
	for ai, (at,ak,par) in enumerate(zip(arg_types,arg_kinds,eff_params)):
		if hasattr(at, '_length_'): # array
			assert ak in 'RWX'
			d_k = CL_MEM_READ_ONLY  if ak == 'R' else \
				  CL_MEM_WRITE_ONLY if ak == 'W' else \
				  CL_MEM_READ_WRITE
				  
			d_x = clCreateBuffer(context, d_k, ctypes.sizeof(at), None, e_REF)
			assert e.value == 0 and d_x > 0
			d_obj = cl_mem(d_x)
			if par is None:
				h_obj = at() # liaison plus tard par clEnqueueWriteBuffer ou ...Read...
			else:
				assert par.size == at._length_  # ne pas confondre avec par.nbytes
				assert par.dtype.itemsize == ctypes.sizeof(at._type_)
				h_obj = par.ctypes.data_as(ctypes.POINTER(at._type_))
				# accede par p[i*1080+j]
				# h_obj = np.ctypeslib.as_ctypes(par) : <c_ubyte_Array_1080_Array_720 at 0x...>
				# accede par h_obj[i][j]
				# numpy.ctypeslib.as_array(obj, shape=None) : l'inverse
				# ESSAYER : at.from_buffer
		elif ak == 'I':
			assert isinstance(at,int)
			h_obj = d_obj = int32_t(at)
		elif ak == 'F':
			assert isinstance(at,float)
			h_obj = d_obj = float_t(at)
		else:
			assert False, ak
			assert ak == 'C'
			h_obj = d_obj = at()
		err |= clSetKernelArg(kernel, ai, ctypes.sizeof(d_obj), Ref(d_obj))
		if err != 0:
			_ = 2+2
		params.append([h_obj, d_obj])
	assert err == 0, err
	return {
		'src': ksrc, 'arg_types': arg_types, 'arg_kinds': arg_kinds,
		'name': kname, 'args': kargs,
		'platform': cpPlatform[0], 'device': device_id[0], 'device_type': dev_ty,
		'context': context, 'queue': queue,
		'program': program, 'kernel': kernel,
		'params' : params,
		 }

def kernel_write(d,i, value=None, blocking=True):
	""
	p_h, p_d = d['params'][i]
	if value == 0:
		ctypes.memset(p_h,0, )
	if value is not None:
		assert len(value) == p_h._length_
		
		p_h[:] = value
	return clEnqueueWriteBuffer(d['queue'], p_d, blocking, 0, ctypes.sizeof(p_h), p_h, 0, None, None)

_kernel_run_gsz = (size_t * 3)(0)
_kernel_run_lsz = (size_t * 3)(0)
def kernel_run(d,n,eff_params, blocking_writes=CL_TRUE, blocking_reads=CL_TRUE, finish=True, local_work_size=None):
	"""
	from math import sin, cos
	n = 21
	x_a = [sin(i)*sin(i) for i in range(n)]
	x_b = [cos(i)*cos(i) for i in range(n)]
	x_c = [None]*n
	kernel_run(d,21,[x_a,x_b,x_c,n])
	"""
	# global _kernel_run_gsz, _kernel_run_lsz
	params = d['params']
	assert len(params) == len(eff_params)
	arg_kinds = d['arg_kinds']
	queue = d['queue']
	err = 0
	for p_k, (p_h, p_d), p_eff in zip(arg_kinds, params, eff_params):
		if p_k in 'RX':
			if False:
				assert len(p_eff) == p_h._length_
				p_h[:] = p_eff
			err |= clEnqueueWriteBuffer(queue, p_d, blocking_writes, 0, ctypes.sizeof(p_h), p_h, 0, None, None)
		elif p_k == 'C':
			p_h.value = p_eff
	assert err == 0
	kernel = d['kernel']
	global_work_size = [n] if isinstance(n,int) else n
	wkdims = len(global_work_size)
	_kernel_run_gsz[:wkdims] = global_work_size
	if local_work_size is not None:
		local_work_size = [local_work_size] if isinstance(local_work_size,int) else local_work_size
		assert len(local_work_size) == wkdims
		_kernel_run_lsz[:wkdims] = local_work_size
		lws = _kernel_run_lsz
	else:
		lws = None
	err = clEnqueueNDRangeKernel(queue, kernel, wkdims, None, _kernel_run_gsz, lws, 0, None, None)
	if err != 0:
		assert False, err
	assert err == 0, err
	#if d['device_type'] == CL_DEVICE_TYPE_CPU:
	#	err = clFinish(queue)
	#	assert err == 0
	for p_k, (p_h, p_d), p_eff in zip(arg_kinds, params, eff_params):
		if p_k in 'WX':
			err |= clEnqueueReadBuffer(queue, p_d, blocking_reads, 0, ctypes.sizeof(p_h), p_h, 0, None, None)
			if False:
				assert len(p_eff) == p_h._length_
				p_eff[:] = p_h
	assert err == 0
	if finish:
		err = clFinish(queue)
		assert err == 0
	
def kernel_terminate(d):
	""
	err = 0
	for h_x, d_x in d.get('params',[]):
		if h_x != d_x:
			err |= clReleaseMemObject(d_x)
	assert err == 0
	if 'kernel' in d:
		err = clReleaseKernel(d['kernel'])
		assert err == 0
	err = clReleaseProgram(d['program'])
	assert err == 0
	err = clReleaseCommandQueue(d['queue'])
	assert err == 0
	err = clReleaseContext(d['context'])
	assert err == 0

#
num_platforms = cl_uint() # 0
ICD_status = clGetPlatformIDs(0,None, _R(num_platforms)) ## 0 ou -1001 : no ICD
if ICD_status == 0:
	assert num_platforms.value > 0
	platforms_vec = (cl_platform_id * num_platforms.value)() # ctypes.POINTER(ctypes.c_char)
	r = clGetPlatformIDs(num_platforms.value, platforms_vec, None)
	assert r == 0
	platforms_inf = [None] * num_platforms.value
	for p in range(num_platforms.value):
		print(f'************* platform {p} *************')
		p_addr = platforms_vec[p]
		platforms_inf[p] = gatherPlatformInfo(p_addr, verbose=False)
elif ICD_status == -1001:
	printf(f"WARNING : bad return value of clGetPlatformIDs : {ICD_status}")
	platform_inf = gatherPlatformInfo(None)
else:
	printf(f"ERREUR : bad return value of clGetPlatformIDs : {ICD_status}")
	assert False
		
if __name__ == "__main__": # vecAdd
	from math import ceil, cos, prod, sin
	from random import randrange, random
	
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
	ksrc_hist = """
__kernel void histogram(__global uchar data[NLIN][NCOL], __global int histogram[256]) {
	int gid0 = get_global_id(0), gid1 = get_global_id(1);
#ifdef UNSAFE
	histogram[data[gid0][gid1]] += 1;
#else
	atomic_inc( &histogram[data[gid0][gid1]] );
#endif
}
	"""
	print("histogramme")
	nlin = ncol = 512
	sz = nlin * ncol
	d = kernel_initiate(ksrc_hist,
					 [ uint8_t * sz, uint32_t * 256],
					 "RX",
					 f"-DNLIN={nlin} -DNCOL={ncol}"
					 , dev_kind="GPU"
					 , kname="histogram")
	if 'error' in d:
		print('probleme de compilation')
		print(d['error'])
	else:
		GSZ = [nlin,ncol]
		LSZ = [16,16]
		assert all(g%l==0 for (g,l) in zip(GSZ,LSZ)), (GSZ,LSZ)
		[[h1,_],[h2,_]] = d['params']
		for i in range(len(h1)):
			h1[i] = randrange(256)
		for i in range(len(h2)):
			h2[i] = 0
		kernel_run(d, GSZ, [None,None], local_work_size=LSZ)
		if sum(h2) == len(h1):
			print('OK')
		else:
			print('KO')
		
	
	kernel_terminate(d)

if False:
	kl = get_kernels(ksrc)
	
	n = 21
	
	n_out = n+1
	
	work_dim = 1
	## Number of work items in each local work group
	#localSize = 64
	localSize = (size_t * work_dim)(64)
	## Number of total work items - localSize must be devisor
	#globalSize = ceil(n/localSize)*localSize
	globalSize = (size_t * work_dim)(ceil(n/localSize[0])*localSize[0])
	global_size = (size_t * work_dim)(n)
	
	nb_bytes = n * 4   ## ctypes.sizeof(h_a)
	h_a = (ctypes.c_float * n)(*[sin(i)*sin(i) for i in range(n)])
	h_b = (ctypes.c_float * n)(*[cos(i)*cos(i) for i in range(n)])
	read_arrays = [h_a, h_b]
	h_c = (ctypes.c_float * n_out)() # all 0.0
	write_arrays = [h_c]
	e = cl_int(-1000)
	e_REF = _R(e)
	kernelSource = (ctypes.c_char_p * 1)(ksrc.encode('cp1250'))
	cpPlatform = (cl_platform_id * 1)()
	err = clGetPlatformIDs(1, cpPlatform, None)
	assert err == 0
	device_id = (cl_device_id * 1)()
	err = clGetDeviceIDs(cpPlatform[0], CL_DEVICE_TYPE_GPU, 1, device_id, None)
	if err == CL_DEVICE_NOT_FOUND:
		err = clGetDeviceIDs(cpPlatform[0], CL_DEVICE_TYPE_ACCELERATOR, 1, device_id, None)
	assert err == 0, err
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
	read_buffers = [d_a,d_b]
	d_c = clCreateBuffer(context, CL_MEM_WRITE_ONLY, n_out*4, None, e_REF)
	assert e.value == 0
	write_buffers = [d_c]
	if False: # original
		err  = clEnqueueWriteBuffer(queue, d_a, CL_TRUE, 0, nb_bytes, h_a, 0, None, None)
		err |= clEnqueueWriteBuffer(queue, d_b, CL_TRUE, 0, nb_bytes, h_b, 0, None, None)
		assert err == 0
	err   = clSetKernelArg(kernel, 0, ctypes.sizeof(cl_mem), _R(cl_mem(d_a)))
	err  |= clSetKernelArg(kernel, 1, ctypes.sizeof(cl_mem), _R(cl_mem(d_b)))
	err  |= clSetKernelArg(kernel, 2, ctypes.sizeof(cl_mem), _R(cl_mem(d_c)))
	err  |= clSetKernelArg(kernel, 3, ctypes.sizeof(cl_uint), _R(cl_uint(n)))
	assert err == 0 ## -38 == CL_INVALID_MEM_OBJECT
	
	### BEGIN COPRO
	
	if True: # nouveau
		err = 0
		for buf,arr in zip(read_buffers,read_arrays):
			err |= clEnqueueWriteBuffer(queue, buf, CL_TRUE, 0, ctypes.sizeof(arr), arr, 0, None, None)
	else:
		err  = clEnqueueWriteBuffer(queue, d_a, CL_TRUE, 0, nb_bytes, h_a, 0, None, None)
		err |= clEnqueueWriteBuffer(queue, d_b, CL_TRUE, 0, nb_bytes, h_b, 0, None, None)
	assert err == 0
	#err = clEnqueueNDRangeKernel(queue, kernel, 1, None, _R(size_t(globalSize)), _R(size_t(localSize)), 0, None, None)
	#err = clEnqueueNDRangeKernel(queue, kernel, work_dim, None, globalSize, localSize, 0, None, None)
	err = clEnqueueNDRangeKernel(queue, kernel, len(globalSize), None, globalSize, None, 0, None, None)
	assert err == 0
	err = clFinish(queue)
	assert err == 0
	if True:
		err = 0
		for buf,arr in zip(write_buffers,write_arrays):
			err |= clEnqueueReadBuffer(queue, buf, CL_TRUE, 0, ctypes.sizeof(arr), arr, 0, None, None)
	else:
		err = clEnqueueReadBuffer(queue, d_c, CL_TRUE, 0, nb_bytes, h_c, 0, None, None)
	assert err == 0
	
	### END COPRO
	
	delta = [h_c[i]-1 for i in range(n_out)]
	print(delta)
	###
	err = 0
	if False:
		for d_x in read_buffers + write_buffers:
			err |= clReleaseMemObject(d_x)
	elif not Kalray:
		err |= clReleaseMemObject(d_a)
		err |= clReleaseMemObject(d_b)
		err |= clReleaseMemObject(d_c) ### kalray : blocage
	else:
		#err |= clReleaseMemObject(d_c)
		err |= clReleaseMemObject(d_b)
		err |= clReleaseMemObject(d_a)
	assert err == 0
	err = clReleaseKernel(kernel)
	assert err == 0

	#err  = clReleaseMemObject(d_c)
	#assert err == 0

	if not Kalray:
		err = clReleaseProgram(program)
		assert err == 0
	err = clReleaseCommandQueue(queue)
	assert err == 0
	err = clReleaseContext(context)
	assert err == 0
	print('done')
