import OpenGL.GL as gl, time
from dll_glfw3 import *

W,H = 640, 480

if True:
	r = glfwInit()
	assert r == 1, "Init failed"
	
	window = glfwCreateWindow(W, H, "Hello World".encode('cp1250'), None, None)
	assert window > 0, "CreateWindow failed"
	
	code = glfwGetError(None)
	assert code == 0
	
	glfwSetErrorCallback(DFLT_errorfun)
	glfwSetFramebufferSizeCallback(window, GLFWframebuffersizefun(lambda _win,w,h: gl.glViewport(0, 0, w, h)))
	
	glfwMakeContextCurrent(window)
	glfwSwapInterval(1)
	code = glfwGetError(None)
	assert code == 0
	
	
	
	
	
	# OpenGL : https://www.labri.fr/perso/nrougier/python-opengl/#modern-opengl
	
	gl.glClearColor(1.0,0.0,0.0,1.0) # rouge
	gl.glClear(gl.GL_COLOR_BUFFER_BIT)
	glfwSwapBuffers(window); glfwPollEvents()
	
	gl.glClearColor(0.0,1.0,0.0,1.0) # vert
	gl.glClear(gl.GL_COLOR_BUFFER_BIT)
	glfwSwapBuffers(window); glfwPollEvents()
	
	program  = gl.glCreateProgram()
	vertex   = gl.glCreateShader(gl.GL_VERTEX_SHADER)
	fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
	
	vertex_code = """
attribute vec2 position;
void main() { gl_Position = vec4(position, 0.0, 1.0); }
"""
	fragment_code = """
void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }
"""
	gl.glShaderSource(vertex, vertex_code)
	gl.glShaderSource(fragment, fragment_code)
	gl.glCompileShader(vertex)
	if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
		error = gl.glGetShaderInfoLog(vertex).decode()
		print(error)
		raise RuntimeError("Vertex shader compilation error")
	gl.glCompileShader(fragment)
	if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
		error = gl.glGetShaderInfoLog(fragment).decode()
		print(error)
		raise RuntimeError("Fragment shader compilation error")

	gl.glAttachShader(program, vertex)
	gl.glAttachShader(program, fragment)
	gl.glLinkProgram(program)

	if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
		print(gl.glGetProgramInfoLog(program))
		raise RuntimeError('Linking error')


	glfwTerminate()