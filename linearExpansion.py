import numpy as np
import cv2 as cv

from tim import *

class Settings(GeneSettings):
	pass

class Algo(GeneAlgo):
	def __init__(self, i_settings, name, i_outputType, i_inputDynamic, i_outputDynamic):
		self.isInitialized = True
		
	def allocate(self, i_hardwareType):
		""
		pass
		return 0

class Intf(GeneIntf):
	def __init__(self, i_settings, i_outputType, i_inputDynamic, i_outputDynamic):
		name = "le nom de l'algo"
		super().__init__(name)
		self.algo = Algo(i_settings, name, i_outputType, i_inputDynamic, i_outputDynamic)
