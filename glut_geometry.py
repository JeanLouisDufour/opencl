import numpy as np
from OpenGL.GL import *

def fghDrawGeometryWire(vertices, normals, numVertices,
                       vertIdxs, numParts, numVertPerPart, vertexMode,
                       vertIdxs2, numParts2, numVertPerPart2):
	""
	attribute_v_coord  = -1 # fgStructure.CurrentWindow->Window.attribute_v_coord;
	attribute_v_normal = -1 # fgStructure.CurrentWindow->Window.attribute_v_normal;

	if False: #(fgState.HasOpenGL20 && (attribute_v_coord != -1 || attribute_v_normal != -1))
		#/* User requested a 2.0 draw */
		pass # fghDrawGeometryWire20(vertices, normals, numVertices,
		#				vertIdxs, numParts, numVertPerPart, vertexMode,
		#                      vertIdxs2, numParts2, numVertPerPart2,
		#                      attribute_v_coord, attribute_v_normal);
	else:
		fghDrawGeometryWire11(vertices, normals,
                              vertIdxs, numParts, numVertPerPart, vertexMode,
                              vertIdxs2, numParts2, numVertPerPart2)

def fghDrawGeometryWire11(vertices, normals,
                         vertIdxs, numParts, numVertPerPart, vertexMode,
                         vertIdxs2, numParts2, numVertPerPart2):
	""
	glEnableClientState(GL_VERTEX_ARRAY)
	glEnableClientState(GL_NORMAL_ARRAY)

	glVertexPointer(3, GL_FLOAT, 0, vertices)
	glNormalPointer(GL_FLOAT, 0, normals)

	if vertIdxs is None or len(vertIdxs) == 0:
		# Draw per face (TODO: could use glMultiDrawArrays if available) */
		for i in range(numParts):
			glDrawArrays(vertexMode, i*numVertPerPart, numVertPerPart)
	else:
		for i in range(numParts):
			glDrawElements(vertexMode,numVertPerPart,GL_UNSIGNED_SHORT, \
				  vertIdxs[i*numVertPerPart:(i+1)*numVertPerPart])

	if vertIdxs2 is not None and len(vertIdxs2) > 0:
		for i in range(numParts2):
			glDrawElements(GL_LINE_LOOP,numVertPerPart2,GL_UNSIGNED_SHORT, \
				  vertIdxs2[i*numVertPerPart2:(i+1)*numVertPerPart2])

	glDisableClientState(GL_VERTEX_ARRAY);
	glDisableClientState(GL_NORMAL_ARRAY);

def fghDrawGeometrySolid11(vertices, normals,
						   textcs, numVertices,
						   vertIdxs, numParts, numVertIdxsPerPart):
	""
	pass

def fghDrawGeometryWire20(vertices, normals, numVertices,
                          vertIdxs, numParts, numVertPerPart, vertexMode,
                          vertIdxs2, numParts2, numVertPerPart2,
                          attribute_v_coord = -1, attribute_v_normal = -1):
	""
	vbo_coords = vbo_normals = ibo_elements = ibo_elements2 = 0
	numVertIdxs = numParts * numVertPerPart
	numVertIdxs2 = numParts2 * numVertPerPart2
	
	if numVertices > 0 and attribute_v_coord != -1:
		assert False
	if numVertices > 0 and attribute_v_normal != -1:
		assert False
	if vertIdxs:
		assert False
	if vertIdxs2:
		assert False
	"TBC"
	

class Shape:
	@classmethod
	def Generate(cls):
		""
		if cls.NUM_EDGE_PER_FACE == 3:
			vertSamps = ()             # nothing to do here, we'll draw with glDrawArrays
		elif cls.NUM_EDGE_PER_FACE == 4:
			vertSamps = (0,1,2, 0,2,3) # quad    : 4 input vertices, 6 output (2 triangles)
		elif cls.NUM_EDGE_PER_FACE == 5:
			vertSamps = (0,1,2, 0,2,4, 4,2,3) # pentagon: 5 input vertices, 9 output (3 triangles)
		else:
			assert False, cls.NUM_EDGE_PER_FACE
		for i in range(cls.NUM_FACES):
			normIdx         = i*3
			faceIdxVertIdx  = i*cls.NUM_EDGE_PER_FACE
			for j in range(cls.NUM_EDGE_PER_FACE):
				outIdx  = i*cls.NUM_EDGE_PER_FACE*3+j*3
				vertIdx = cls.vi[faceIdxVertIdx+j]*3
				cls.verts[outIdx:outIdx+3] = cls.v[vertIdx:vertIdx+3]
				cls.norms[outIdx:outIdx+3] = cls.n[normIdx:normIdx+3]
			for j,vs in enumerate(vertSamps):
				cls.vertIdxs[i*len(vertSamps)+j] = faceIdxVertIdx + vs
				
	
class Cube(Shape):
	####################################
	### partie specifique a la forme ###
	v = np.array([      # Vertex Coordinates
	 .5, .5, .5,
    -.5, .5, .5,
    -.5,-.5, .5,
     .5,-.5, .5,
     .5,-.5,-.5,
     .5, .5,-.5,
    -.5, .5,-.5,
    -.5,-.5,-.5
	], dtype = np.float32)
	assert len(v) % 3 == 0
	NUM_VERT = len(v) // 3
	#
	n = np.array([       # Normal Vectors
	 0.0, 0.0, 1.0,
     1.0, 0.0, 0.0,
     0.0, 1.0, 0.0,
    -1.0, 0.0, 0.0,
     0.0,-1.0, 0.0,
     0.0, 0.0,-1.0
	], dtype = np.float32)
	assert len(n) % 3 == 0
	NUM_FACES = len(n) // 3
	#
	NUM_EDGE_PER_FACE = 4
	VERT_PER_OBJ = NUM_FACES*NUM_EDGE_PER_FACE
	vi = np.array([     # Vertex indices, as quads, before triangulation
	0,1,2,3,
    0,3,4,5,
    0,5,6,1,
    1,6,7,2,
    7,4,3,2,
    4,7,6,5
	], dtype = np.uint8)
	assert VERT_PER_OBJ == len(vi)
	#
	# DECLARE_SHAPE_CACHE_DECOMPOSE_TO_TRIANGLE
	#
	VERT_ELEM_PER_OBJ = VERT_PER_OBJ*3
	verts = np.zeros(VERT_ELEM_PER_OBJ, dtype = 'float32')
	norms = np.zeros(VERT_ELEM_PER_OBJ, dtype = 'float32')
	VERT_PER_OBJ_TRI = VERT_PER_OBJ+NUM_FACES*2 # 2 extra edges per face when drawing quads as triangles
	vertIdxs = np.zeros(VERT_PER_OBJ_TRI, dtype = 'uint16')
	#################################
	# Generate() # non encore accessible, de meme que Cube
	# a ce niveau, seul __qualname__ existe et vaut la chaine "Cube" (donc inutile)
	# donc on fait l'appel en dehors :
Cube.Generate()

def fghCube(dSize, useWireMode):
	""
# 	if not Cube.Cached:
# 		Cube.Generate()
# 		Cube.Cached = True
	if dSize != 1.0:
		vertices = Cube.verts * dSize
	else:
		vertices = Cube.verts
	if useWireMode:
		fghDrawGeometryWire(vertices, Cube.norms, Cube.VERT_PER_OBJ,
                            None,Cube.NUM_FACES, Cube.NUM_EDGE_PER_FACE,GL_LINE_LOOP,
                            None,0,0)
	else:
		assert False

################# Sphere ####################

def fghCircleTable(n, halfCircle):
	""
	assert n != 0
	size = np.abs(n)
	sint = np.empty(size+1, 'float32')
	cost = np.empty(size+1, 'float32')
	angle = (1.0 if halfCircle else 2.0)*np.pi/n
	for i in range(size+1):
		sint[i] = np.sin(angle*i)
		cost[i] = np.cos(angle*i)
	return (sint, cost)

def fghGenerateSphere(radius, slices, stacks):
	""
	nVert = slices*(stacks-1)+2
	assert nVert <= 65535, nVert
	vertices = np.empty(nVert*3, 'float32')
	normals = np.empty(nVert*3, 'float32')
	sint1, cost1 = fghCircleTable(-slices, False)
	sint2, cost2 = fghCircleTable(stacks, True)
	# top
	vertices[0:3] = normals[0:3] = [0.0, 0.0, 1.0]
	idx = 3
	# each stack
	for i in range(1,stacks):
		for j in range(slices):
			xyz = [cost1[j]*sint2[i], sint1[j]*sint2[i], cost2[i]]
			vertices[idx:idx+3] = normals[idx:idx+3] = xyz
			idx += 3
	# bottom
	vertices[idx:idx+3] = normals[idx:idx+3] = [0.0, 0.0, -1.0]
	#
	return (vertices*radius, normals, nVert)

def fghSphere(radius, slices, stacks, useWireMode):
	""
	vertices, normals, nVert = fghGenerateSphere(radius,slices,stacks)
	if useWireMode:
		sliceIdx = np.zeros(slices*(stacks+1), 'uint16')
		stackIdx = np.zeros(slices*(stacks-1), 'uint16')
		# generate for each stack
		idx = 0
		for i in range(stacks-1):
			offset = 1+i*slices
			for j in range(slices):
				stackIdx[idx] = offset+j ; idx += 1
		# generate for each slice
		idx = 0
		for i in range(slices):
			offset = 1+i
			sliceIdx[idx] = 0 ; idx += 1
			for j in range(stacks-1):
				sliceIdx[idx] = offset+j*slices ; idx += 1
			sliceIdx[idx] = nVert-1 ; idx += 1
		# draw
		fghDrawGeometryWire(vertices,normals,nVert,
            sliceIdx,slices,stacks+1,GL_LINE_STRIP,
            stackIdx,stacks-1,slices)
	else:
		assert False

if __name__ == '__main__':
	from dll_glfw3 import *
	assert 1 == glfwInit()
	window = glfwCreateWindow(640, 480, "Hello World".encode('cp1250'), None, None)
	assert window > 0, "CreateWindow failed"
	glfwMakeContextCurrent(window)
	glfwSwapInterval(1)
	code = glfwGetError(None)
	assert code == 0
	while not glfwWindowShouldClose(window):
		# begin rendering
		#fghCube(1.0, True)
		fghSphere(1.0, 4,4, True)
		# end rendering
		glfwSwapBuffers(window); glfwPollEvents()
	glfwTerminate()
