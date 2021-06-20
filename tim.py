import numpy as np
import cv2 as cv

_ty_d = { # ne pas mettre directement np.uint16 ...
	np.dtype('uint16'): cv.CV_16U
	}

def type_np2cv(npt):
	""
	if isinstance(npt, np.ndarray):
		sh = npt.shape
		ty = npt.dtype
	else:
		ty = npt
	if ty not in _ty_d:
		r = None
	else:
		r = _ty_d[ty]
	return r

def type_cv2np(cvt):
	""
	if cvt == cv.CV_32F:
		r = np.float32
	else:
		assert False, cvt
	return r

class DynamicPool:
	def request(self, cv_size, cv_type):
		""
		a = np.empty(cv_size, type_cv2np(cv_type))
		return a


class ParamScalar:
	def __init__(self, isUpdateAllowed, default, range_min=None, range_max=None, rangePrecision=None):
		"name, help, isUpdateAllowed, default, ... sauf dans certains cas"
		self.isUpdateAllowed, self.default = isUpdateAllowed, default
		self.val = self.default  ### surveillance de l'update non implementee
		if range_min is not None:
			self.range_min = range_min
		if range_max is not None:
			self.range_max = range_max
		if rangePrecision is not None:
			self.rangePrecision = rangePrecision

class GeneSettings:
	pass


class GeneAlgo:
	def __init__(self, settings, name, supportedInputs, supportedOutputs, relatedIO):
		self.subModules_list = []
		self.isAllocated_cpu = self.isAllocated_cuda = self.isAllocated_ocl = False
		self.allocated_inputInfoMap = {}
		self.current_inputInfoMap = self.current_outputInfoMap = None
		self.bufferPool = DynamicPool()
		
	def isAllocated(self, i_hardwareType):
		""
		if self.current_inputInfoMap != self.allocated_inputInfoMap:
			return False
		return  self.isAllocated_ocl  if i_hardwareType==OpenCL else \
				self.isAllocated_cuda if i_hardwareType==Cuda   else \
				self.isAllocated_cpu

	def update_allocationInfo(self, i_hardwareType):
		""
		self.isAllocated_cpu = self.isAllocated_ocl = self.isAllocated_cuda = False
		if i_hardwareType == cpu:
			self.isAllocated_cpu = True
		else:
			assert False
		self.allocatedBackend = i_hardwareType
		self.allocated_inputInfoMap = self.current_inputInfoMap

	def set_inputInfos(self, i_namedInputsInfo):
		""
		self.current_inputInfoMap = dict(i_namedInputsInfo)
		assert 0 <= self.update_outputInfoMap()
		assert 0 <= self.propagate_inputInfos(i_namedInputsInfo)
		self.hasInfoForCurrentInput = True
		return 0
	
	
###########################################

Standard, OpenCL, Cuda = range(3)
standard = Cpu = cpu = Standard
opencl = OpenCL
cuda = CUDA = Cuda

UndefinedArray, RegularArray, PyramidArray, ArrayOfArrays = range(4)
		
class GeneIntf:
	def __init__(self,name):
		self.name = name
	
	def check_inputs(self, i_inputs):
		""
		for name, arr in i_inputs:
			assert isinstance(name, str) and isinstance(arr,(list, np.ndarray))
		assert isinstance(self.algo.current_inputInfoMap, dict)
		for i_name, i_arr in i_inputs:
			sh, ty, kd = self.algo.current_inputInfoMap[i_name]
			pass
		
		#self.algo.current_inputInfoMap = dict(i_inputs)
		return 0
	
	def check_outputs(self, i_outputs):
		""
		for name, arr in i_outputs:
			assert isinstance(name, str) and isinstance(arr,(list, np.ndarray))
		assert self.algo.current_outputInfoMap is None
		self.algo.current_outputInfoMap = dict(i_outputs)
		return 0
	
	def check_IO(self, i_inputs, i_outputs):
		""
		self.check_inputs(i_inputs)
		self.check_outputs(i_outputs)
		return 0
	
	def run_standard_regular(self, i_inputs, io_outputs):
		""
		assert 0 <= self.algo.run(dict(i_inputs), dict(io_outputs))
		return 0
		
	def run(self, i_inputs, io_outputs, i_hardwareType):
		""
		if not self.algo.isInitialized:
			assert False, f"({self.name}) This instance was not correctly initialized."
		if 0 > self.check_IO(i_inputs, io_outputs):
			assert False, f"({self.name}) An error occured while checking the validity of the inputs and outputs."
		if not self.algo.isAllocated(i_hardwareType):
			print('WARNING', f"({self.name}) The method allocate() should have been called before run() to avoid dynamic allocations.")
			if 0 > self.algo.allocate(i_hardwareType):
				assert False,  f"({self.name}) m_super_algo->allocate() failed."
		has_regular = any(isinstance(v[1], np.ndarray) for v in i_inputs)
		has_array = any(isinstance(v[1], list) for v in i_inputs)
		if i_hardwareType == Standard:
			if has_regular and has_array:
				if 0 > self.run_standard_regularAndArray(i_inputs,io_outputs):
					assert False
			elif has_regular:
				if 0 > self.run_standard_regular(i_inputs, io_outputs):
					assert False
			else:
				if 0 > self.run_standard_pyramid(i_inputs, io_outputs):
					assert False
		elif i_hardwareType == OpenCL:
			pass
		elif i_hardwareType == Cuda:
			assert False
		else:
			assert False
		return 0
