from glut_geometry import fghCube, fghSphere
import ctypes
import OpenGL
from dll_glfw3 import *

GLUT_BITMAP_8_BY_13 = ctypes.c_void_p(3)
GLUT_COMPATIBILITY_PROFILE = 2
GLUT_DOUBLE = OpenGL.constant.IntConstant('GLUT_DOUBLE',2)
GLUT_KEY_PAGE_DOWN = OpenGL.constant.IntConstant('GLUT_KEY_PAGE_DOWN',105)
GLUT_KEY_PAGE_UP = OpenGL.constant.IntConstant('GLUT_KEY_PAGE_UP',104)
GLUT_KEY_LEFT = OpenGL.constant.IntConstant('GLUT_KEY_LEFT',100)
GLUT_KEY_RIGHT = OpenGL.constant.IntConstant('GLUT_KEY_RIGHT',102)
GLUT_KEY_DOWN = OpenGL.constant.IntConstant('GLUT_KEY_DOWN',103)
GLUT_KEY_UP = OpenGL.constant.IntConstant('GLUT_KEY_UP',101)
GLUT_RGBA = OpenGL.constant.IntConstant('GLUT_RGBA',0)

window = window_w = window_h = None
drawing_cb = None

def glutBitmapCharacter(fontID, character): ### fg_font.c
	pass
def glutCreateWindow(title): ### fg_window.c
	""
	global window
	window = glfwCreateWindow(window_w, window_h, title, None, None)
	assert window > 0, "CreateWindow failed"
	glfwMakeContextCurrent(window)
	glfwSwapInterval(1)
	code = glfwGetError(None)
	assert code == 0, code
def glutDisplayFunc(callback): ### include/GL/freeglut_std.h ????
	""
	global drawing_cb
	drawing_cb = callback
def glutInit(argv = ()): ### fg_init.c
	""
	assert len(argv) == 0
	r = glfwInit()
	assert r == 1, "Init failed"
def glutInitContextProfile(profile): ### fg_init.c
	""
	assert profile == GLUT_COMPATIBILITY_PROFILE
def glutInitContextVersion(majorVersion, minorVersion): ### fg_init.c
	""
	assert (majorVersion, minorVersion) == (4,3)
def glutInitDisplayMode(displayMode): ### fg_init.c
	""
	assert displayMode == GLUT_DOUBLE | GLUT_RGBA
def glutInitWindowPosition(x,y): ### fg_init.c
	""
	pass
def glutInitWindowSize(width, height): ### fg_init.c
	""
	global window_w, window_h
	window_w, window_h = width, height
def glutKeyboardFunc(keyInput):
	""
	pass
def glutMainLoop():
	""
	try:
		while not glfwWindowShouldClose(window):
			drawing_cb()
			glfwSwapBuffers(window); glfwPollEvents()
	except:
		print('something bad happened ...')
	glfwTerminate()
def glutPostRedisplay():
	""
	pass
def glutReshapeFunc(callback):
	"cb(w,h)"
	def cb1(_win,w,h):
		callback(w,h)
	_cb = glfwSetFramebufferSizeCallback(window, GLFWframebuffersizefun(cb1))
def glutSpecialFunc(specialKeyInput):
	""
	pass
def glutSwapBuffers():
	""
	glfwSwapBuffers(window)
def glutTimerFunc(msecs, func, value):
	"func(value)"
	pass

################# Cube : fg_geometry.c #########

def glutWireCube(dSize): ### fg_geometry.c
	""
	assert isinstance(dSize, float) and dSize >= 0.0
	fghCube(dSize, True)

def glutWireSphere(radius, slices, stacks): ### fg_geometry.c
	""
	assert isinstance(radius, float) and radius >= 0.0 \
	  and  isinstance(slices, int) and slices >= 1 \
	  and  isinstance(stacks, int) and stacks >= 2
	fghSphere(radius, slices, stacks, True)

if __name__ == '__main__':
	from dll_glfw3 import *
	from math import fabs, sin
	assert 1 == glfwInit()
	window = glfwCreateWindow(640, 480, "Hello World", None, None)
	assert window > 0, "CreateWindow failed"
	glfwMakeContextCurrent(window)
	glfwSwapInterval(1)
	code = glfwGetError(None)
	assert code == 0
	while not glfwWindowShouldClose(window):
		# begin rendering
		t = glfwGetTime()
		dSize = fabs(sin(t))+1.0
		glutWireCube(dSize)
		# end rendering
		glfwSwapBuffers(window); glfwPollEvents()
	glfwTerminate()
