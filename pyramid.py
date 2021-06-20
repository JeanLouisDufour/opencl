import numpy as np
import cv2 as cv

from tim import *

from linearExpansion import Settings as LinearExpansion_Settings, Intf as LinearExpansion

class Settings(GeneSettings):
	def __init__(self):
		self.enable_finalLinearExpansion = ParamScalar(False, True)
		self.force_singlePrecision = ParamScalar(True, False)
		self.GCE_onConstantVariance = LinearExpansion_Settings()
		self.local_gainBoost = ParamScalar(True, 0.2, range_min=0.0, range_max=1.0, rangePrecision=3)
		self.local_maxScaleNumber = ParamScalar(False, 20, range_min=2, range_max=30, rangePrecision=0)
		
	
class Algo(GeneAlgo):
	def __init__(self, settings, name, outputType, inputDynamicRange, outputDynamicRange):
		super().__init__(settings, name, \
		   [], \
		   [], \
		   [])
		self.settings = settings
		self.outputType = outputType
		self.inputDynamicRange = inputDynamicRange
		self.outputDynamicRange = outputDynamicRange
		#
		self.current_inputInfoMap = {}
		self.imagePyramid = [] # liste d'images
		self.luminanceImage = None
		#
		self.estimatedNoise = np.NaN
		self.filtered_estimatedNoise = np.NaN
		if False == self.settings.enable_finalLinearExpansion.val and cv.CV_32F != self.outputType:
			assert False, "enable_finalLinearExpansion can only be false when m_outputType=CV_32F"
		if self.settings.enable_finalLinearExpansion.val:
			self.GCE_onConstantVariance = LinearExpansion(settings.GCE_onConstantVariance, cv.CV_32F, 1.0, 1.0)
			assert self.GCE_onConstantVariance.algo.isInitialized
			self.subModules_list = [self.GCE_onConstantVariance]
		
		self.isInitialized = True
		
	def propagate_updateSettings(self):
		""
		pass
	
	def update_outputInfoMap(self):
		""
		self.inputType = self.current_inputInfoMap["imgSrc"][1]
		pass
		return 0
	
	def has_backend(i_backendType):
		""
		pass
	
	def checkSizeRestriction(i_imageSize):
		""
		pass
	
	def compute_theoretical_maxScale(i_imageSize):
		""
		pass
	
	def compute_effective_maxScale():
		""
		pass
	
	def initPyramidSize():
		""
		pass
	
	def initGainValue():
		""
		pass
	
	def propagate_inputInfos(self, i_namedInputsInfo): # const std::vector<NamedImageInfo>
		""
		pass
		return 0
	
	def allocate(self, i_hardwareType):
		""
		assert not self.isAllocated(i_hardwareType)
		for sm in self.subModules_list:
			assert 0 <= sm.algo.allocate(i_hardwareType)
		### compute_theoretical_maxScale
		[H,W] = self.current_inputInfoMap["imgSrc"][0] # (sh,ty,kd)
		smallerDim = min(W,H)
		# std::round: <<rounding halfway cases away from zero>> : 0.5 -> 1, 1.5 -> 2
		image_maxScales = int(round_halfway_away0(np.log(smallerDim)/np.log(2)))
		image_maxScales = max(image_maxScales - 1, 1)
		settings_maxScale = self.settings.local_maxScaleNumber.range_max
		self.theoretical_maxScale = min(image_maxScales, settings_maxScale)
		### compute_effective_maxScale
		self.effective_scalesNumber = min(self.theoretical_maxScale, self.settings.local_maxScaleNumber.val)
		### initGainValue
		self.gains = [max(36, 0) for i in range(self.theoretical_maxScale)]
		self.gains = [max((self.settings.local_gainBoost.val*(7 - 2*i) + i/4)/4, 0) for i in range(self.theoretical_maxScale)]
		### initPyramidSize
		self.theoretical_pyramidSize = self.theoretical_maxScale + 1
		self.pyramidSizes = [None] * self.theoretical_pyramidSize
		self.pyramidSizes[0] = self.current_inputInfoMap["imgSrc"][0] # shape
		for i in range(1,self.theoretical_pyramidSize):
			H,W = self.pyramidSizes[i-1]
			self.pyramidSizes[i] = (H//2,W//2)
		#
		self.allocatedSize, self.allocatedType, _ = self.current_inputInfoMap["imgSrc"]
		### allocate_cpu
		self.imagePyramid = [None]*self.theoretical_pyramidSize
		self.scales_constantVariance = [None]*self.theoretical_pyramidSize
		self.allocatedType
		self.allocatedSize
		self.hsvImage_split = [np.empty(self.allocatedSize, np.float32) for _ in range(3)]
		self.internalBufferType = cv.CV_32F
		if ((False == self.settings.force_singlePrecision and \
	        (cv.CV_16U == self.inputDepthType or cv.CV_32F == self.inputDepthType or 255.0 != self.inputDynamicRange))):
			self.internalBufferType = cv.CV_64F
			assert False
		for n in range(self.theoretical_pyramidSize):
			self.imagePyramid[n] = np.empty(self.pyramidSizes[n], type_cv2np(self.internalBufferType))
			self.scales_constantVariance[n] = np.empty(self.pyramidSizes[n], np.float32)
		self.constantVarianceImage_expanded = np.empty(self.allocatedSize, np.float32)
		#
		self.update_allocationInfo(i_hardwareType)
		return 0
	
	def allocate_cpu():
		""
		pass
	
	def run(self, i_inputMats,io_outputMats):
		""
		i_src = i_inputMats["imgSrc"]
		i_mask = i_inputMats["imgMsk"]
		o_dst = io_outputMats["imgDst"]
		assert 0 <= self.preProcessing(i_src), "preProcessing() failed"
		assert 0 <= self.constantVarianceProcessing(i_mask), "constantVarianceProcessing() failed"
		assert 0 <= self.postProcessing(o_dst), "postProcessing() failed"
		return 0
	
	def preProcessing(self, i_src):
		""
		if self.inputType in (cv.CV_8UC3, cv.CV_16UC3, cv.CV_32FC3):
			assert False
		elif self.inputType in (cv.CV_8U, cv.CV_16U, cv.CV_32F):
			self.luminanceImage = i_src
		else:
			assert False
		return 0
	
	def constantVarianceProcessing(self, i_mask):
		""
		# Convert m_luminanceImage to float-32/64bit, in range [0;1]
		self.imagePyramid[0]
		self.internalBufferType
		self.inputDynamicRange
		# Loop over each scale
		for n in range(self.effective_scalesNumber):
			I_upscaled_squared = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
	
		return 0

	def postProcessing(self, o_dst):
		""
		pass
		return 0

###########################################
		
class Intf(GeneIntf):
	def __init__(self, settings, outputType = cv.CV_8U, inputDynamicRange = np.NaN, outputDynamicRange = np.NaN):
		name = "le nom de l'algo"
		super().__init__(name)
		self.algo = Algo(settings, name, outputType, inputDynamicRange, outputDynamicRange)

m = None # Algo()
"""
m.current_inputInfoMap = {}
m.imagePyramid = [] # liste d'images
m.luminanceImage = None
m.settings = Settings()
m.settings.enable_finalLinearExpansion = ParamScalar()
m.settings.local_gainBoost = ParamScalar()
m.settings.local_maxScaleNumber = ParamScalar()
m.settings.local_maxScaleNumber.maxV = 30
"""

def PyramidalConstantVariance_INH(settings, outputType = cv.CV_8U, \
							  inputDynamicRange = None, outputDynamicRange = None):
	""
	m.settings = settings
	obj['m_outputType']

def round_halfway_away0(x):
	"0.5 -> 1, 1.5 -> 2, ..."
	f = np.floor(x)
	return f if x - f < 0.5 else f+1


def allocate_INH():
	""
	### compute_theoretical_maxScale
	[H,W] = m.current_inputInfoMap["imgSrc"].shape
	smallerDim = min(W,H)
	# std::round: <<rounding halfway cases away from zero>> : 0.5 -> 1, 1.5 -> 2
	image_maxScales = round_halfway_away0(np.log(smallerDim)/np.log(2))
	image_maxScales = max(image_maxScales - 1, 1)
	settings_maxScale = m.settings.local_maxScaleNumber.range_max
	m.theoretical_maxScale = min(image_maxScales, settings_maxScale)
	### compute_effective_maxScale
	m.effective_scalesNumber = min(m.theoretical_maxScale, m.settings.local_maxScaleNumber.val)
	### initGainValue
	m.gains = [max(36, 0) for i in range(m.theoretical_maxScale)]
	#m_gains = [max((m.settings.local_gainBoost.val*(7 - 2*i) + i/4)/4, 0) for i in range(m.theoretical_maxScale)]
	### initPyramidSize
	m.theoretical_pyramidSize = m.theoretical_maxScale + 1
	m.pyramidSizes = [None] * m.theoretical_pyramidSize
	m.pyramidSizes[0] = m.current_inputInfoMap["imgSrc"].shape
	for i in range(1,m.theoretical_pyramidSize):
		H,W = m.pyramidSizes[i-1]
		m.pyramidSizes[i] = (H//2,W//2)
	### allocate_cpu
	pass



def preProcessing_INH(i_src):
	""
	if m.inputType in (cv.CV_8UC3, cv.CV_16UC3, cv.CV_32FC3):
		assert False
	elif m.inputType in (cv.CV_8U, CV_16U, cv.CV_32F):
		m.luminanceImage = i_src
	else:
		assert False


def run_INH(i_src, i_mask, o_dst):
	"..._Algo"
	err = preProcessing(i_src)
	err = constantVarianceProcessing(i_mask)
	err = postProcessing(o_dst)

if __name__ == "__main__":
	"non_regression_test.cpp, AlgorithmExecution.cpp"
	test_dir = r'C:\users\F074018\Documents\cah\cah\cahlocale\test\int\data' + '\\'
	settings = Settings()
	m = Intf(settings, cv.CV_8U, 65535.0, 255.0)
	assert m.algo.isInitialized
	image = input_img = cv.imread(test_dir+"test_image_L14_1.tif", cv.IMREAD_UNCHANGED)
	# (480, 640) uint16
	imageSize = image.shape
	imageType = type_np2cv(image)
	inputInfos = {"imgSrc": (imageSize, imageType, RegularArray), \
			   "imgMsk" : (imageSize, cv.CV_8U, RegularArray)}
	assert 0 <= m.algo.set_inputInfos(inputInfos)
	
	output_img = np.empty(input_img.shape, np.uint8)
	mask = np.empty(input_img.shape, np.uint8)
	m.run([['imgSrc',input_img], ['imgMsk',mask]], [['imgDst',output_img]], Cpu)
	
	