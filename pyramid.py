import numpy as np
#import cv2 as cv
import cv_stub as cv

from tim import *

from linearExpansion import Settings as LinearExpansion_Settings, Intf as LinearExpansion

class Settings(GeneSettings):
	
	VarianceLimitMode = "VarianceOffset", "VarianceMinimum"
	VarianceOffset, VarianceMinimum = range(2)
	
	def __init__(self):
		self.enable_finalLinearExpansion = ParamScalar(False, True)
		self.force_singlePrecision = ParamScalar(True, False)
		self.GCE_onConstantVariance = LinearExpansion_Settings()
		self.local_EstimatedNoise_alphaFilter = ParamScalar(True, 0.95, range_min=0.0, range_max=1.0, rangePrecision=2)
		self.local_gainBoost = ParamScalar(True, 0.2, range_min=0.0, range_max=1.0, rangePrecision=3)
		self.local_maxScaleNumber = ParamScalar(False, 20, range_min=2, range_max=30, rangePrecision=0)
		self.local_varianceLimit_kSigma = ParamScalar(True, 3.0, range_min=0.01, range_max=10.0, rangePrecision=2)
		self.local_varianceLimit_mode = ParamEnum(True, self.VarianceLimitMode, self.VarianceOffset)
		
	
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
		self.propagate_updateSettings()
		self.filter = np.array([[1.0, 2.0, 1.0],
						  [2.0, 4.0, 2.0],
						  [1.0, 2.0, 1.0]], dtype = np.float32) * (1/16)
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
		if self.GCE_onConstantVariance:
			namedInputsInfo = []
			for name, (HW,depth,regular) in i_namedInputsInfo.items():
				namedInputsInfo.append((name, (HW, (cv.CV_32F if name=='imgSrc' else depth),regular)))
			self.GCE_onConstantVariance.algo.set_inputInfos(namedInputsInfo)
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
		self.hsvImage_split = [nan_array(self.allocatedSize, np.float32) for _ in range(3)]
		self.internalBufferType = cv.CV_32F
		if ((False == self.settings.force_singlePrecision and \
	        (cv.CV_16U == self.inputDepthType or cv.CV_32F == self.inputDepthType or 255.0 != self.inputDynamicRange))):
			self.internalBufferType = cv.CV_64F
			assert False
		for n in range(self.theoretical_pyramidSize):
			self.imagePyramid[n] = nan_array(self.pyramidSizes[n], type_cv2np(self.internalBufferType))
			self.scales_constantVariance[n] = nan_array(self.pyramidSizes[n], np.float32)
		self.constantVarianceImage_expanded = nan_array(self.allocatedSize, np.float32)
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
		assert type_np2cv(self.imagePyramid[0].dtype) == self.internalBufferType
		self.imagePyramid[0][...] = self.luminanceImage ; self.imagePyramid[0] *= 1.0 / self.inputDynamicRange
		# Loop over each scale
		for n in range(self.effective_scalesNumber):
			I_upscaled_squared = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
			I_upscaled         = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
			if True: # I_convolved 
				I_convolved  = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
				cv.filter2D(self.imagePyramid[n], -1, self.filter, dst=I_convolved, borderType=cv.BORDER_REFLECT_101)
				isfinite(I_convolved)
				cv.resize(I_convolved, swap(self.pyramidSizes[n+1]), dst=self.imagePyramid[n+1]) # 0, 0, cv::INTER_LINEAR
				isfinite(self.imagePyramid[n+1]) #### !!!!! NaN
				cv.resize(self.imagePyramid[n+1], swap(self.pyramidSizes[n]), dst=I_upscaled) # 0, 0, cv::INTER_LINEAR     
				isfinite(I_upscaled)
				cv.pow(I_upscaled, 2, dst=I_upscaled_squared)
				self.bufferPool.release(I_convolved)
			I_squared_upscaled = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
			if True: # I_squared... 
				I_squared = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
				I_squared_convolved = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
				I_squared_convolved_downscaled = self.bufferPool.request(self.pyramidSizes[n+1], self.internalBufferType)
				cv.pow(self.imagePyramid[n], 2, dst=I_squared)
				cv.filter2D(I_squared, -1, self.filter, dst=I_squared_convolved, borderType=cv.BORDER_REFLECT_101)
				cv.resize(I_squared_convolved, swap(self.pyramidSizes[n+1]), dst=I_squared_convolved_downscaled) # 0, 0, cv::INTER_LINEAR
				cv.resize(I_squared_convolved_downscaled, swap(self.pyramidSizes[n]), dst=I_squared_upscaled) # 0, 0, cv::INTER_LINEAR)
				self.bufferPool.release(I_squared)
				self.bufferPool.release(I_squared_convolved)
				self.bufferPool.release(I_squared_convolved_downscaled)
			I_HF = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
			I_HF[:] = self.imagePyramid[n] - I_upscaled
			isfinite(I_HF)
			self.bufferPool.release(I_upscaled)
			if 0 == n:
				cnz = cv.countNonZero(i_mask)
				if cnz == 0: # i_mask.empty()
					self.estimatedNoise = cv.norm(np.abs(I_HF), cv.NORM_L1) * (1.0/I_HF.size)
				else:
					self.estimatedNoise = cv.norm(np.abs(I_HF), cv.NORM_L1, i_mask) * (1.0/cnz)
				self.filtered_estimatedNoise = self.filterVal(self.estimatedNoise, self.settings.local_EstimatedNoise_alphaFilter, self.filtered_estimatedNoise)
			varOff = 8.0*np.power(self.settings.local_varianceLimit_kSigma.val, 2)*np.power(self.filtered_estimatedNoise, 2)
			variance = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
			if Settings.VarianceOffset == self.settings.local_varianceLimit_mode.val:
				variance[:] = cv.max(I_squared_upscaled - I_upscaled_squared, 0) + varOff
			else:
				variance[:] = cv.max(I_squared_upscaled - I_upscaled_squared, varOff)
			self.bufferPool.release(I_upscaled_squared)
			self.bufferPool.release(I_squared_upscaled)
			sqrt_var = self.bufferPool.request(self.pyramidSizes[n], self.internalBufferType)
			cv.sqrt(variance, dst=sqrt_var)
			self.bufferPool.release(variance)
			if cv.CV_64F == self.internalBufferType:
				assert False
			else:
				self.scales_constantVariance[n] = self.gains[n] * I_HF/sqrt_var
			self.bufferPool.release(I_HF)
			self.bufferPool.release(sqrt_var)
		#
		constantVarianceImage = self.bufferPool.request(self.allocatedSize, cv.CV_32F)
		scale_constantVariance_resized = None # cv::Mat
		for n in reversed(range(self.effective_scalesNumber)):
			index = n
			if 0 == index:
				cv.add(self.scales_constantVariance[index], scale_constantVariance_resized, dst=constantVarianceImage)
				self.bufferPool.release(scale_constantVariance_resized)
			elif self.effective_scalesNumber-1 == index: # First iteration
				scale_constantVariance_resized = self.bufferPool.request(self.pyramidSizes[index-1], cv.CV_32F)
				cv.resize(self.scales_constantVariance[index], swap(self.pyramidSizes[index-1]), dst=scale_constantVariance_resized)
			else:
				scales_constantVariance_upscaled = self.bufferPool.request(self.pyramidSizes[index], cv.CV_32F)
				cv.add(self.scales_constantVariance[index], scale_constantVariance_resized, dst=scales_constantVariance_upscaled)
				isfinite(scales_constantVariance_upscaled)
				self.bufferPool.release(scale_constantVariance_resized)
				scale_constantVariance_resized = self.bufferPool.request(self.pyramidSizes[index-1], cv.CV_32F)
				cv.resize(scales_constantVariance_upscaled, swap(self.pyramidSizes[index-1]), dst=scale_constantVariance_resized)
				self.bufferPool.release(scales_constantVariance_upscaled)
		#
		isfinite(constantVarianceImage)
		if self.settings.enable_finalLinearExpansion.val:
			assert 0 <= self.GCE_onConstantVariance.run([["imgSrc", constantVarianceImage],
                                              ["imgMsk", i_mask]],
                                             [["imgDst", self.constantVarianceImage_expanded]],
                                             Standard)
		else:
			self.constantVarianceImage_expanded[...] = constantVarianceImage
		self.bufferPool.release(constantVarianceImage)
		return 0

	def postProcessing(self, o_dst):
		""
		if self.inputType in (cv.CV_8UC3, cv.CV_16UC3, cv.CV_32FC3):
			assert False
		elif self.inputType in (cv.CV_8U, cv.CV_16U, cv.CV_32F):
			alpha = self.outputDynamicRange if self.settings.enable_finalLinearExpansion.val else 1.0
			assert type_np2cv(o_dst.dtype) == self.outputType
			o_dst[...] = self.constantVarianceImage_expanded * alpha
		else:
			assert False
		return 0

	def filterVal(self, i_newVal, i_alphaFilter, io_filteredVal):
		""
		if not np.isfinite(io_filteredVal):
			assert np.isnan(io_filteredVal)
			if not np.isfinite(i_newVal):
				assert np.isnan(i_newVal)
				print(f'filterVal: i_newVal = {i_newVal}')
				i_newVal = 0.0
			io_filteredVal = i_newVal
		elif (1.0 - i_alphaFilter) > FLT_EPSILON and not np.isnan(i_newVal):
			io_filteredVal = i_alphaFilter * io_filteredVal + (1 - i_alphaFilter) * i_newVal
		return io_filteredVal
	
###########################################
		
class Intf(GeneIntf):
	def __init__(self, settings, outputType = cv.CV_8U, inputDynamicRange = np.NaN, outputDynamicRange = np.NaN):
		name = "le nom de l'algo"
		super().__init__(name)
		self.algo = Algo(settings, name, outputType, inputDynamicRange, outputDynamicRange)


if __name__ == "__main__":
	"non_regression_test.cpp, AlgorithmExecution.cpp"
	cv.namedWindow('image')
	test_dir = r'C:\users\F074018\Documents\cah\cah\cahlocale\test\int\data' + '\\'
	settings = Settings()
	m = Intf(settings, cv.CV_8U, 65535.0, 255.0)
	assert m.algo.isInitialized
	algo = m.algo
	image = input_img = cv.imread(test_dir+"test_image_L14_1.tif", cv.IMREAD_UNCHANGED)
	# (480, 640) uint16
	imageSize = image.shape
	imageType = type_np2cv(image)
	inputInfos = {"imgSrc": (imageSize, imageType, RegularArray), \
			   "imgMsk" : (imageSize, cv.CV_8U, RegularArray)}
	assert 0 <= m.algo.set_inputInfos(inputInfos)
	
	output_img = np.zeros(input_img.shape, np.uint8)
	mask = np.zeros(input_img.shape, np.uint8)
	m.run([['imgSrc',input_img], ['imgMsk',mask]], [['imgDst',output_img]], Cpu)
	
	