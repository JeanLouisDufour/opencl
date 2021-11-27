import glfw

if not glfw.init():
	raise Exception('init failed')

glfw.terminate()
