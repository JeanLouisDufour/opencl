# https://stackabuse.com/brief-introduction-to-opengl-in-python-with-pyopengl/

import OpenGL.GL as gl, time
from dll_glfw3 import *

w,h= 500,500
def square():
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(100, 100)
    gl.glVertex2f(200, 100)
    gl.glVertex2f(200, 200)
    gl.glVertex2f(100, 200)
    gl.glEnd()

def iterate():
    gl.glViewport(0, 0, 500, 500)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    gl.glMatrixMode (gl.GL_MODELVIEW)
    gl.glLoadIdentity()

def showScreen():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glLoadIdentity()
    iterate()
    gl.glColor3f(1.0, 0.0, 3.0)
    square()
    # glutSwapBuffers()

if True:
	r = glfwInit()
	assert r == 1, "Init failed"
	
	window = glfwCreateWindow(w, h, "Hello World".encode('cp1250'), None, None)
	assert window > 0, "CreateWindow failed"
	
	code = glfwGetError(None)
	assert code == 0, code
	
	glfwSetErrorCallback(DFLT_errorfun)
	glfwSetFramebufferSizeCallback(window, GLFWframebuffersizefun(lambda _win,w,h: gl.glViewport(0, 0, w, h)))
	
	glfwMakeContextCurrent(window)
	glfwSwapInterval(1)
	code = glfwGetError(None)
	assert code == 0, code
	
	while not glfwWindowShouldClose(window):
		showScreen()
		glfwSwapBuffers(window); glfwPollEvents()
		time.sleep(1)
	
	glfwTerminate()
	
if False:
	
	# OpenGL : https://www.labri.fr/perso/nrougier/python-opengl/#modern-opengl
	
	gl.glClearColor(1.0,0.0,0.0,1.0) # rouge
	gl.glClear(gl.GL_COLOR_BUFFER_BIT)
	glfwSwapBuffers(window); glfwPollEvents()
	
	gl.glClearColor(0.0,1.0,0.0,1.0) # vert
	gl.glClear(gl.GL_COLOR_BUFFER_BIT)
	glfwSwapBuffers(window); glfwPollEvents()
	
	

	glfwTerminate()