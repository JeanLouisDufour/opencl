# //////////////////////////////////////////////////////////////////////////////////////////////         
# // animateMan1.cpp
# // 
# // This program draws a man with movable parts who can be animated. The program has two modes:
# // (a) develop mode in which key frames are created.
# // (b) animate mode in which animation is shown.
# //
# // At the end of the develop mode configurations data is written to the file animateManDataOut.txt. 
# //
# // Interaction:
# // Press a to toggle between develop and animate modes.
# //
# // In develop mode:
# // Press the space bar to select a part.
# // Press the page up/page down keys to rotate the selected part.
# // Press the left/right/up/down arrow keys to move the whole configuration.
# // Press r/R to rotate the viewpoint.
# // Press z/Z to zoom in/out.
# // Press n to create a new configuration - other configurations are ghosted
# // (the new configuration is a copy of the current one so it must be moved to be visible).
# // Press tab to choose a configuration - it is highlighted, others ghosted.
# // Press backspace to reset current configuration.
# // Press delete to delete current configuration.
# //
# // In animate mode:
# // Press the up/down arrow keys to speed up/slow down animation.
# //
# // Sumanta Guha.
# //////////////////////////////////////////////////////////////////////////////////////////////

from math import pi as PI, sin, cos
from dll_glfw3 import *
from OpenGL.GL import *
from OpenGL.GLU import gluLookAt
from glut_stub import *
#from OpenGL.GLUT import *

# PI = math.pi

# Globals.
highlightColor = [ 0.0, 0.0, 0.0 ] # Emphasize color.
lowlightColor = [ 0.7, 0.7, 0.7 ] # De-emphasize color.
partSelectColor = [ 1.0, 0.0, 0.0 ] # Selection indicate color.
font = GLUT_BITMAP_8_BY_13 # Font selection.
animateMode = 0 # In animation mode?
animationPeriod = 1000 # Time interval between frames.
#static std::ofstream outFile; // File to write configurations data.

class Camera:
	"""
{
public:
	Camera();
	void incrementViewDirection();
	void decrementViewDirection();
	void incrementZoomDistance() { zoomDistance += 1.0; }
	void decrementZoomDistance() { zoomDistance -= 1.0; }

	float getViewDirection() const { return viewDirection; }
	float getZoomDistance() const { return zoomDistance; }

private:
	float viewDirection;
	float zoomDistance;
};
"""
	def __init__(self):
		self.viewDirection = 0.0
		self.zoomDistance = 30.0
	
	def incrementViewDirection(self):
		self.viewDirection += 5.0
		if self.viewDirection > 360.0: self.viewDirection -= 360.0
	def decrementViewDirection(self):
		self.viewDirection -= 5.0;
		if self.viewDirection < 0.0: self.viewDirection += 360.0
	def incrementZoomDistance(self):
		self.zoomDistance += 1.0
	def decrementZoomDistance(self):
		self.zoomDistance -= 1.0
	
# Global camera.
camera = Camera()

# Routine to draw a bitmap character string.
def writeBitmapString(font, string):
	""
	for c in string:
		glutBitmapCharacter(font, c)

class Man:
	"""
{
public:
	Man();
	void incrementSelectedPart();

	void incrementPartAngle();
	void decrementPartAngle();
	void setPartAngle(float angle) { partAngles[selectedPart] = angle; }

	void incrementUpMove() { upMove += 0.1; }
	void decrementUpMove() { upMove -= 0.1; }
	void setUpMove(float move) { upMove = move; }

	void incrementForwardMove() { forwardMove += 0.1; }
	void decrementForwardMove() { forwardMove -= 0.1; }
	void setForwardMove(float move) { forwardMove = move; }

	void setHighlight(int inputHighlight) { highlight = inputHighlight; }

	void draw();
	void outputData();
	void writeData();

private:
	// Man configuration values.
	float partAngles[9]; // Angles from 0 to 360 of 9 body parts - torso, left and right
						 // upper arms, left and right lower arms, left and right upper
						 // legs, left and right lower legs. 
						 // All parts move parallel to the same plane.

	float upMove, forwardMove; // Up and forward translation components - both lie
							   // on the plane parallel to which parts rotate -
							   // therefore all translations and part rotations
							   // are along one fixed plane.

	int selectedPart; // Selected part number - this part can be interactively rotated
					  // in the develop mode.

	int highlight; // If man is currently selected.
};
"""
	NBPARTS = 9
	
	def __init__(self):
		self.partAngles = [0.0] * self.NBPARTS
		self.upMove = 0.0
		self.forwardMove = 0.0
		self.selectedPart = 0
		self.highlight = 1

	def incrementSelectedPart(self):
		if self.selectedPart < self.NBPARTS-1:
			self.selectedPart += 1
		else:
			self.selectedPart = 0

	def incrementPartAngle(self):
		self.partAngles[self.selectedPart] += 5.0
		if self.partAngles[self.selectedPart] >= 360.0:
			self.partAngles[self.selectedPart] -= 360.0
	def decrementPartAngle(self):
		self.partAngles[self.selectedPart] -= 5.0
		if self.partAngles[self.selectedPart] < 0.0:
			self.partAngles[self.selectedPart] += 360.0
	def setPartAngle(self, angle): self.partAngles[self.selectedPart] = angle
	
	def incrementUpMove(self): self.upMove += 0.1
	def decrementUpMove(self): self.upMove -= 0.1
	def setUpMove(self, move): self.upMove = move

	def incrementForwardMove(self): self.forwardMove += 0.1
	def decrementForwardMove(self): self.forwardMove -= 0.1
	def setForwardMove(self, move): self.forwardMove = move

	def setHighlight(self, inputHighlight): self.highlight = inputHighlight
	
	def draw(self):
		""
		if self.highlight or self.animateMode:	glColor3fv(highlightColor)
		else: 									glColor3fv(lowlightColor)

		glPushMatrix()

		# Up and forward translations.
		glTranslatef(0.0, self.upMove, self.forwardMove);

		# Torso begin.
		if self.highlight and (not animateMode) and self.selectedPart == 0:
			glColor3fv(partSelectColor)

		glRotatef(self.partAngles[0], 1.0, 0.0, 0.0)

		glPushMatrix()
		glScalef(4.0, 16.0, 4.0)
		glutWireCube(1.0)
		glPopMatrix()
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Torso end.
	
		# Head begin.
		glPushMatrix()
	
		glTranslatef(0.0, 11.5, 0.0)
		glPushMatrix()
		glScalef(2.0, 3.0, 2.0)
		glutWireSphere(1.0, 10, 8)
		glPopMatrix()
	
		glPopMatrix()
		# Head end.
	
		# Left upper and lower arm begin.
		glPushMatrix()
	
		# Left upper arm begin.
		if self.highlight and (not animateMode) and self.selectedPart == 1: glColor3fv(partSelectColor)
		glTranslatef(3.0, 8.0, 0.0)
		glRotatef(180.0 + self.partAngles[1], 1.0, 0.0, 0.0)
		glTranslatef(0.0, 4.0, 0.0)
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix()
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Left upper arm end.
	
		# Left lower arm begin.
		if self.highlight and (not animateMode) and self.selectedPart == 2: glColor3fv(partSelectColor)
		glTranslatef(0.0, 4.0, 0.0)
		glRotatef(self.partAngles[2], 1.0, 0.0, 0.0)
		glTranslatef(0.0, 4.0, 0.0)
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix()
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Left lower arm end.
	
		glPopMatrix()
		# Left upper and lower arm end.
	
		# Right upper and lower arm begin.
		glPushMatrix()
	
		# Right upper arm begin.
		if self.highlight and (not animateMode) and self.selectedPart == 3: glColor3fv(partSelectColor)
		glTranslatef(-3.0, 8.0, 0.0)
		glRotatef(180.0 + self.partAngles[3], 1.0, 0.0, 0.0)
		glTranslatef(0.0, 4.0, 0.0)
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix();
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Right upper arm end.
	
		# Right lower arm begin.
		if self.highlight and (not animateMode) and self.selectedPart == 4: glColor3fv(partSelectColor)
		glTranslatef(0.0, 4.0, 0.0)
		glRotatef(self.partAngles[4], 1.0, 0.0, 0.0)
		glTranslatef(0.0, 4.0, 0.0)
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix()
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Right lower arm end.
	
		glPopMatrix()
		# Right upper and lower arm end.
	
		# Left upper and lower leg with foot begin.
		glPushMatrix()
	
		# Left upper leg begin.
		if self.highlight and (not animateMode) and self.selectedPart == 5: glColor3fv(partSelectColor)
		glTranslatef(1.5, -8.0, 0.0)
		glRotatef(self.partAngles[5], 1.0, 0.0, 0.0)
		glTranslatef(0.0, -4.0, 0.0)
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix()
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Left upper leg end.
	
		# Left lower leg with foot begin.
		if self.highlight and (not animateMode) and self.selectedPart == 6: glColor3fv(partSelectColor)
		glTranslatef(0.0, -4.0, 0.0)
		glRotatef(self.partAngles[6], 1.0, 0.0, 0.0)
		glTranslatef(0.0, -4.0, 0.0)
	
		# Lower leg.
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix()
	
		# Foot.
		glTranslatef(0.0, -5.0, 0.5)
		glPushMatrix()
		glScalef(2.0, 1.0, 3.0)
		glutWireCube(1.0)
		glPopMatrix()
	
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Left lower leg with foot end.
	
		glPopMatrix()
		# Left upper and lower leg with foot end.
	
		# Right upper and lower leg with foot begin.
		glPushMatrix()
	
		# Right upper leg begin.
		if self.highlight and (not animateMode) and self.selectedPart == 7: glColor3fv(partSelectColor)
		glTranslatef(-1.5, -8.0, 0.0)
		glRotatef(self.partAngles[7], 1.0, 0.0, 0.0)
		glTranslatef(0.0, -4.0, 0.0)
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix()
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Right upper leg end.
	
		# Right lower leg with foot begin.
		if self.highlight and (not animateMode) and self.selectedPart == 8: glColor3fv(partSelectColor)
		glTranslatef(0.0, -4.0, 0.0)
		glRotatef(self.partAngles[8], 1.0, 0.0, 0.0)
		glTranslatef(0.0, -4.0, 0.0)
	
		# Lower leg.
		glPushMatrix()
		glScalef(2.0, 8.0, 2.0)
		glutWireCube(1.0)
		glPopMatrix()
	
		# Foot.
		glTranslatef(0.0, -5.0, 0.5)
		glPushMatrix()
		glScalef(2.0, 1.0, 3.0)
		glutWireCube(1.0)
		glPopMatrix()
	
		if self.highlight and (not animateMode): glColor3fv(highlightColor)
		# Right lower leg with foot end.
	
		glPopMatrix()
		# Right upper and lower leg with foot end.
	
		glPopMatrix()


	def outputData(self):
		""
# 	int i;
# 	for (i = 0; i < 9; i++) outFile << partAngles[i] << " ";
# 	outFile << upMove << " " << forwardMove << std::endl;
		pass

# # Routine to convert floating point to char string.
# void floatToString(char * destStr, int precision, float val)
# {
# 	sprintf(destStr, "%f", val);
# 	destStr[precision] = '\0';
# }

# Routine to write configurations data.
	def writeData(self):
		"""
{
	char buffer[33];

	floatToString(buffer, 4, partAngles[0]);
	glRasterPos3f(-28.0, 10.0, 0.0);
	writeBitmapString((void*)font, "torso = ");
	glRasterPos3f(-11.0, 10.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[1]);
	glRasterPos3f(-28.0, 8.0, 0.0);
	writeBitmapString((void*)font, "left upper arm = ");
	glRasterPos3f(-11.0, 8.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[2]);
	glRasterPos3f(-28.0, 6.0, 0.0);
	writeBitmapString((void*)font, "left lower arm = ");
	glRasterPos3f(-11.0, 6.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[3]);
	glRasterPos3f(-28.0, 4.0, 0.0);
	writeBitmapString((void*)font, "right upper arm = ");
	glRasterPos3f(-11.0, 4.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[4]);
	glRasterPos3f(-28.0, 2.0, 0.0);
	writeBitmapString((void*)font, "right lower arm = ");
	glRasterPos3f(-11.0, 2.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[5]);
	glRasterPos3f(-28.0, 0.0, 0.0);
	writeBitmapString((void*)font, "left uppper leg = ");
	glRasterPos3f(-11.0, 0.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[6]);
	glRasterPos3f(-28.0, -2.0, 0.0);
	writeBitmapString((void*)font, "left lower leg = ");
	glRasterPos3f(-11.0, -2.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[7]);
	glRasterPos3f(-28.0, -4.0, 0.0);
	writeBitmapString((void*)font, "right upper leg = ");
	glRasterPos3f(-11.0, -4.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, partAngles[8]);
	glRasterPos3f(-28.0, -6.0, 0.0);
	writeBitmapString((void*)font, "right lower leg = ");
	glRasterPos3f(-11.0, -6.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, upMove);
	glRasterPos3f(-28.0, -8.0, 0.0);
	writeBitmapString((void*)font, "upMove = ");
	glRasterPos3f(-11.0, -8.0, 0.0);
	writeBitmapString((void*)font, buffer);

	floatToString(buffer, 4, forwardMove);
	glRasterPos3f(-28.0, -10.0, 0.0);
	writeBitmapString((void*)font, "forwardMove = ");
	glRasterPos3f(-11.0, -10.0, 0.0);
	writeBitmapString((void*)font, buffer);
}"""
		pass


# Global vector of man configurations.
manVector = [] # std::vector<Man>

#  Global iterators to traverse manVector.
manVectorIterator = 0 # std::vector<Man>::iterator
manVectorAnimationIterator = 0 # std::vector<Man>::iterator

# Drawing routine.
def drawScene():
	""
	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()

	# Write text in isolated (i.e., before gluLookAt) translate block.
	glPushMatrix()
	glTranslatef(0.0, 0.0, -30.0)
	glColor3fv(highlightColor)
	glRasterPos3f(-28.0, 25.0, 0.0)
	if not animateMode:
		writeBitmapString(font, "DEVELOP MODE")
		manVector[manVectorIterator].writeData()
	else:
		writeBitmapString(font, "ANIMATE MODE")
	glPopMatrix()

	# Place camera.
	gluLookAt(camera.zoomDistance * sin(camera.viewDirection*PI / 180.0), 0.0,
		camera.zoomDistance * cos(camera.viewDirection*PI / 180.0), 0.0,
		0.0, 0.0, 0.0, 1.0, 0.0)

	# Move man right 10 units because of data text on left of screen.
	glTranslatef(10.0, 0.0, 0.0)

	if not animateMode: # Develop mode.
		# Draw all the configurations in manVector.
		for man in manVector: man.draw()
	else: # Animated mode - 
		# use separate iterator so as to leave develop mode iterator unchanged.
		manVector[manVectorAnimationIterator].draw()

	# Other (fixed) objects in scene are drawn below starting here.

	# Black floor.
	glColor3f(0.0, 0.0, 0.0)
	glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
	for zi in range(-5,20): ### for (float z = -25.0; z<100.0; z += 5.0)
		z = zi * 5.0
		glBegin(GL_TRIANGLE_STRIP)
		for xi in range(-10,10): ### for (float x = -50.0; x<50.0; x += 5.0)
			x = xi * 5.0
			glVertex3f(x, -25.0, z)
			glVertex3f(x, -25.0, z + 5.0)
		glEnd()

	# Green sphere.
	glColor3f(0.0, 1.0, 0.0)
	glTranslatef(0.0, -20.0, 10.0)
	glPushMatrix()
	glScalef(5.0, 5.0, 5.0)
	glutWireSphere(1.0, 10, 8)
	glPopMatrix()

	glutSwapBuffers()

# Timer function.
def animate(value):
	""
	global manVectorAnimationIterator
	if animateMode:
		manVectorAnimationIterator += 1
		if manVectorAnimationIterator == len(manVector):
			manVectorAnimationIterator = 0
		glutPostRedisplay()
		glutTimerFunc(animationPeriod, animate, 1)

# Function to write configurations to file.
def outputConfigurations():
	"""
	outFile.open("animateManDataOut.txt");
	for (auto man : manVector) { man.outputData(); }
	outFile.close();
"""
	pass

# Initialization routine.
def setup():
	""
	global manVectorIterator, manVectorAnimationIterator, camera
	glClearColor(1.0, 1.0, 1.0, 0.0)

	# Initialize global manVector with single configuration.
	manVector.append(Man())

	# Initialize global iterators for manVector.
	manVectorIterator = 0
	manVectorAnimationIterator = 0

	# Initialize camera.
	camera = Camera()


# OpenGL window reshape routine.
def resize(w, h):
	""
	glViewport(0, 0, w, h)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glFrustum(-5.0, 5.0, -5.0, 5.0, 5.0, 100.0)
	glMatrixMode(GL_MODELVIEW)

# Keyboard input processing routine.
def keyInput(key, x, y):
	""
	localManVectorIterator = 0 # std::vector<Man>::iterator
	okey = ord(key)
	if okey == 27:
		assert False # exit(0)
	elif key == 'a': # Toggle between develop and animate modes.
		if animateMode == 0:
			manVectorAnimationIterator = 0
			outputConfigurations() # Write configurations data to file at end of develop mode.
			animateMode = 1
			animate(1)
		else:
			animateMode = 0
	elif key == 'r': # Rotate camera.
		camera.incrementViewDirection()
	elif key == 'R': # Rotate camera.
		camera.decrementViewDirection()
	elif key == 'z': # Zoom in.
		camera.decrementZoomDistance()
	elif key == 'Z': # Zoom out.
		camera.incrementZoomDistance()
	elif key == 'n': # Create new man configuration.
			  # Turn highlight off current configuration.
		manVector[manVectorIterator].setHighlight(0)

		localManVectorIterator = manVectorIterator
		manVectorIterator += 1

		# Insert copy of current configuration and highlight.
		print(""" ???????????????
		manVectorIterator =
			manVector.insert(manVectorIterator, Man(*localManVectorIterator));
			""")
		manVector[manVectorIterator].setHighlight(1)
		
	elif key == ' ': # Select next body part.
		manVector[manVectorIterator].incrementSelectedPart()

		# Tab - select next man configuration.
	elif okey == 9:
		# Turn highlight off current configuration.
		manVector[manVectorIterator].setHighlight(0)

		# Increment iterator - go to start if at end already.
		manVectorIterator += 1
		if manVectorIterator == len(manVector):
			manVectorIterator = 0

		# Highlight current configuration.
		manVector[manVectorIterator].setHighlight(1)

		# Backspace - reset current man configuration,
	elif okey == 8:
		"""
		if (manVectorIterator != manVector.begin()) # Not first configuration. 
		{
			# Make copy of the previous configuration and highlight.
			localManVectorIterator = manVectorIterator;
			localManVectorIterator--;
			manVectorIterator =
				manVector.insert(manVectorIterator, Man(*localManVectorIterator));
			manVectorIterator->setHighlight(1);

			# Delete current configuration.
			manVectorIterator++;
			manVectorIterator = manVector.erase(manVectorIterator);

			# Return iterator.
			manVectorIterator--;
		}
		else # First configuration
		{
			# Delete the current configuration.
			manVectorIterator = manVector.erase(manVectorIterator);

			# Create new configuration.
			manVector.insert(manVectorIterator, Man());
		}
		"""

		# Delete - delete current man configuration.
	elif okey == 127:
		"""
		if (manVector.size() > 1)
		{
			manVectorIterator = manVector.erase(manVectorIterator);
			if (manVectorIterator != manVector.begin())
				manVectorIterator--;

			# Highlight current configuration.
			manVectorIterator->setHighlight(1);
		}
		"""

	glutPostRedisplay()

# Callback routine for non-ASCII key entry.
def specialKeyInput(key, x, y):
	""
	if (key == GLUT_KEY_PAGE_DOWN): manVector[manVectorIterator].decrementPartAngle()
	elif (key == GLUT_KEY_PAGE_UP): manVector[manVectorIterator].incrementPartAngle()
	elif (key == GLUT_KEY_LEFT): manVector[manVectorIterator].decrementForwardMove()
	elif (key == GLUT_KEY_RIGHT): manVector[manVectorIterator].incrementForwardMove()
	elif (key == GLUT_KEY_DOWN):
		if (not animateMode): manVector[manVectorIterator].decrementUpMove()
		else: animationPeriod += 10
	elif (key == GLUT_KEY_UP):
		if (not animateMode): manVector[manVectorIterator].incrementUpMove()
		else:
			if (animationPeriod > 10): animationPeriod -= 10
	glutPostRedisplay()

# Routine to output interaction instructions to the C++ window.
def printInteraction():
	""
	s = """Interaction:
Press a to toggle between develop and animate modes.

In develop mode:
Press the space bar to select a part.
Press the page up/page down keys to rotate the selected part.
Press the left/right/up/down arrow keys to move the whole configuration.
Press r/R to rotate the viewpoint.
Press z/Z to zoom in/out.
Press n to create a new configuration - other configurations are ghosted
(the new configuration is a copy of the current one so it must be moved to be visible).
Press tab to choose a configuration - it is highlighted, others ghosted.
Press backspace to reset current configuration.
Press delete to delete current configuration.

In animate mode:
Press the up/down arrow keys to speed up/slow down animation.
"""
	print(s)

# Main routine.
#int main(int argc, char **argv)
if True:
	printInteraction()
	glutInit([])

	glutInitContextVersion(4, 3)
	glutInitContextProfile(GLUT_COMPATIBILITY_PROFILE)

	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
	glutInitWindowSize(500, 500)
	glutInitWindowPosition(100, 100)
	glutCreateWindow("animateMan1.cpp")
	glutDisplayFunc(drawScene)
	glutReshapeFunc(resize)
	glutKeyboardFunc(keyInput)
	glutSpecialFunc(specialKeyInput)

	#glewExperimental = GL_TRUE
	#glewInit()

	setup()

	glutMainLoop()
