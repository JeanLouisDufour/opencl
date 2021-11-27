import ctypes, re, os, sys

dll = r"C:\Users\F074018\Anaconda3\Library\bin\glfw3.dll"

mylib = ctypes.CDLL(dll)

_P = ctypes.POINTER
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

GLFWmonitor_Ptr = ctypes.c_void_p
GLFWwindow_Ptr = ctypes.c_void_p

GLFWerrorfun = ctypes.CFUNCTYPE(None, int32_t, ctypes.c_char_p)
def _DFLT_errorfun(a,b):
	print(f"*******\nerror : {a}\n{b}\n*********")
DFLT_errorfun = GLFWerrorfun(_DFLT_errorfun)
NULL_errorfun = GLFWerrorfun(0)

GLFWframebuffersizefun = ctypes.CFUNCTYPE(None, GLFWwindow_Ptr, int32_t, int32_t)
def _DFLT_framebuffersizefun(w,a,b):
	print(f"** framebuffersize : {a} {b} **")
DFLT_framebuffersizefun = GLFWframebuffersizefun(_DFLT_framebuffersizefun)
NULL_framebuffersizefun = GLFWframebuffersizefun(0)

GLFWkeyfun = ctypes.CFUNCTYPE(None, int32_t, int32_t, int32_t, int32_t)
def _DFLT_keyfun(a,b,c,d):
	print(f"** key : {a} {b} {c} {d} **")
DFLT_keyfun = GLFWkeyfun(_DFLT_keyfun)
NULL_keyfun = GLFWkeyfun(0)

GLFWwindowclosefun = ctypes.CFUNCTYPE(None, GLFWwindow_Ptr)
def _DFLT_windowclosefun(w):
	print(f"** windowclose **")
DFLT_windowclosefun = GLFWwindowclosefun(_DFLT_windowclosefun)
NULL_windowclosefun = GLFWwindowclosefun(0)

api = [
["glfwCreateWindow", GLFWwindow_Ptr, int32_t, int32_t, ctypes.c_char_p, GLFWmonitor_Ptr, GLFWwindow_Ptr],
["glfwDestroyWindow", None, GLFWwindow_Ptr],
["glfwGetError", int32_t, _P(ctypes.c_char_p)],
["glfwGetFramebufferSize", None, GLFWwindow_Ptr, _P(int32_t), _P(int32_t)],
["glfwGetTime", double_t],
["glfwInit", int32_t],
["glfwMakeContextCurrent", None, GLFWwindow_Ptr],
["glfwPollEvents"],
["glfwSetErrorCallback", GLFWerrorfun, GLFWerrorfun],
["glfwSetFramebufferSizeCallback", GLFWframebuffersizefun, GLFWwindow_Ptr, GLFWframebuffersizefun],
["glfwSetKeyCallback", GLFWkeyfun, GLFWwindow_Ptr, GLFWkeyfun],
["glfwSetWindowCloseCallback", GLFWwindowclosefun, GLFWwindow_Ptr, GLFWwindowclosefun],
["glfwSwapBuffers", None, GLFWwindow_Ptr],
["glfwSwapInterval", None, int32_t],
["glfwTerminate"],
["glfwVulkanSupported", int32_t],
["glfwWindowHint", None, int32_t, int32_t],
["glfwWindowShouldClose", int32_t, GLFWwindow_Ptr],
]

_m = sys.modules[__name__]
for _l in api:
	_fn = _l[0]
	_fd = getattr(mylib, _fn, None)
	if _fd is None:
		print(f"WARNING : {_fn} not in {mylib}")
	else:
		_fd.restype = _l[1] if len(_l) > 1 else None
		if len(_l) > 2:
			_fd.argtypes = _l[2:]
	setattr(_m, _fn, _fd)

#  patch des fonctions avec parametres char*
_glfwCreateWindow = glfwCreateWindow
def glfwCreateWindow(width, height, title, monitor, share):
	""
	return _glfwCreateWindow(width, height, title.encode('cp1250'), monitor, share)

GLFW_CONTEXT_VERSION_MAJOR = 0x00022002
GLFW_CONTEXT_VERSION_MINOR = 0x00022003

GLFW_NO_ERROR               = 0
GLFW_NOT_INITIALIZED        = 0x00010001
GLFW_NO_CURRENT_CONTEXT     = 0x00010002
GLFW_INVALID_ENUM           = 0x00010003
GLFW_INVALID_VALUE          = 0x00010004
GLFW_OUT_OF_MEMORY          = 0x00010005
GLFW_API_UNAVAILABLE        = 0x00010006
GLFW_VERSION_UNAVAILABLE    = 0x00010007
GLFW_PLATFORM_ERROR         = 0x00010008
GLFW_FORMAT_UNAVAILABLE     = 0x00010009
GLFW_NO_WINDOW_CONTEXT      = 0x0001000A

GLFW_error_START            = 0x00010001
GLFW_error_TAGS = [
	"NOT_INITIALIZED",
	"NO_CURRENT_CONTEXT",
	"INVALID_ENUM",
	"INVALID_VALUE",
	"OUT_OF_MEMORY",
	"API_UNAVAILABLE",
	"VERSION_UNAVAILABLE",
	"PLATFORM_ERROR",
	"FORMAT_UNAVAILABLE",
	"NO_WINDOW_CONTEXT",
]

if __name__ == "__main__":
	r = glfwInit()
	assert r == 1, "Init failed"
	
	print('Vulkan : ', glfwVulkanSupported())
	
	window = glfwCreateWindow(640, 480, "Hello World", None, None)
	assert window > 0, "CreateWindow failed"
	
	code = glfwGetError(None)
	assert code == 0, code
	
	prev_error_cb = glfwSetErrorCallback(DFLT_errorfun)
	prev_framebuffersize_cb = glfwSetFramebufferSizeCallback(window, DFLT_framebuffersizefun)
	
	glfwMakeContextCurrent(window)
	glfwSwapInterval(1)
	code = glfwGetError(None)
	assert code == 0
	
	while not glfwWindowShouldClose(window):
		# rendering
		glfwSwapBuffers(window); glfwPollEvents()
	
	glfwTerminate()
	