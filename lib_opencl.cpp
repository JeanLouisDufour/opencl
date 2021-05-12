/*
 * Copyright (C) 2019 Kalray SA. All rights reserved.
 */
 /***
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <sys/time.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <math.h>
***/
//#include "common.h"
#define Fc 800
#define FILTER_LEN   11  
#define NSAMPLE 1024*8*16*5
#define Freq 800
#define Pi 3.14159265359
#define SCALE 100
#define Te  0.000125
/***
#include <CL/cl.h>
*******/

#include "lib_opencl.h"

#include <iostream>
#include <fstream>
#include <sstream>

/* Inspired from:
 * https://github.com/victusfate/opencl-book-examples/blob/master/src/Chapter_6/HelloBinaryWorld/HelloBinaryWorld.cpp
 */

#define WG_SIZE 1
const int ARRAY_SIZE = WG_SIZE*64; // reajour define

int16_t result[NSAMPLE];
int16_t a[FILTER_LEN];
int16_t b[NSAMPLE];

char buildLog[16384];

#define POCL_DEBUG 1

cl_context CreateContext()
{
	cl_int errNum;
	cl_uint numPlatforms;
	cl_platform_id firstPlatformId;
	cl_context context = NULL;

	// First, select an OpenCL platform to run on.  For this example, we
	// simply choose the first available platform.  Normally, you would
	// query for all available platforms and select the most appropriate one.
	errNum = clGetPlatformIDs(1, &firstPlatformId, &numPlatforms);
	if (errNum != CL_SUCCESS || numPlatforms <= 0)
	{
		std::cerr << "Failed to find any OpenCL platforms." << std::endl;
		return NULL;
	}

	// Next, create an OpenCL context on the platform.  Attempt to
	// create a GPU-based context, and if that fails, try to create
	// a CPU-based context.
	cl_context_properties contextProperties[] =
	{
		CL_CONTEXT_PLATFORM,
		(cl_context_properties)firstPlatformId,
		0
	};
	context = clCreateContextFromType(contextProperties, CL_DEVICE_TYPE_ACCELERATOR | CL_DEVICE_TYPE_GPU,
			NULL, NULL, &errNum);
	if (errNum != CL_SUCCESS)
	{
		std::cout << "Could not create MPPA context : " << errNum << std::endl;
		return NULL;
	}

	return context;
}
cl_command_queue CreateCommandQueue(cl_context context, cl_device_id *device)
{
	cl_int errNum;
	cl_device_id *devices;
	cl_command_queue commandQueue = NULL;
	size_t deviceBufferSize = -1;

	// First get the size of the devices buffer
	errNum = clGetContextInfo(context, CL_CONTEXT_DEVICES, 0, NULL, &deviceBufferSize);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Failed call to clGetContextInfo(...,GL_CONTEXT_DEVICES,...)";
		return NULL;
	}

	if (deviceBufferSize <= 0)
	{
		std::cerr << "No devices available.";
		return NULL;
	}

	// Allocate memory for the devices buffer
	devices = new cl_device_id[deviceBufferSize / sizeof(cl_device_id)];
	errNum = clGetContextInfo(context, CL_CONTEXT_DEVICES, deviceBufferSize, devices, NULL);
	if (errNum != CL_SUCCESS)
	{
		delete [] devices;
		std::cerr << "Failed to get device IDs";
		return NULL;
	}

	// In this example, we just choose the first available device.  In a
	// real program, you would likely use all available devices or choose
	// the highest performance device based on OpenCL device queries
	commandQueue = clCreateCommandQueue(context, devices[0], 0, NULL);
	if (commandQueue == NULL)
	{
		delete [] devices;
		std::cerr << "Failed to create commandQueue for device 0";
		return NULL;
	}

	*device = devices[0];
	delete [] devices;
	return commandQueue;
}

cl_program CreateProgram(cl_context context, cl_device_id device, const char* fileName, char *dcc_args)
{
	cl_int errNum;
	cl_program program;

	std::ifstream kernelFile(fileName, std::ios::in);
	if (!kernelFile.is_open())
	{
		std::cerr << "Failed to open file for reading: " << fileName << std::endl;
		return NULL;
	}

	std::ostringstream oss;
	oss << kernelFile.rdbuf();

	std::string srcStdStr = oss.str();
	const char *srcStr = srcStdStr.c_str();
	program = clCreateProgramWithSource(context, 1,
			(const char**)&srcStr,
			NULL, NULL);
	if (program == NULL)
	{
		std::cerr << "Failed to create CL program from source." << std::endl;
		return NULL;
	}

	errNum = clBuildProgram(program, 0, NULL, dcc_args, NULL, NULL);
	if (errNum != CL_SUCCESS)
	{
		// Determine the reason for the error
		clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG,
				sizeof(buildLog), buildLog, NULL);

		std::cerr << "Error in kernel: " << std::endl;
		std::cerr << buildLog;
		clReleaseProgram(program);
		return NULL;
	}

	return program;
}

cl_program CreateProgramFromBinary(cl_context context, cl_device_id device, const char* fileName)
{
	FILE *fp = fopen(fileName, "rb");
	if (fp == NULL)
	{
		fprintf(stderr, "Failed opening %s\n", fileName);
		return NULL;
	}
	printf("File opened %s\n", fileName);

	// Determine the size of the binary
	size_t binarySize;
	fseek(fp, 0, SEEK_END);
	binarySize = ftell(fp);
	rewind(fp);

	unsigned char *programBinary = new unsigned char[binarySize];
	fread(programBinary, 1, binarySize, fp);
	fclose(fp);

	cl_int errNum = 0;
	cl_program program;
	cl_int binaryStatus;

	program = clCreateProgramWithBinary(context,
			1,
			&device,
			&binarySize,
			(const unsigned char**)&programBinary,
			&binaryStatus,
			&errNum);
	delete [] programBinary;
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error loading program binary." << std::endl;
		return NULL;
	}

	if (binaryStatus != CL_SUCCESS)
	{
		std::cerr << "Invalid binary for device" << std::endl;
		return NULL;
	}

	errNum = clBuildProgram(program, 0, NULL, NULL, NULL, NULL);
	if (errNum != CL_SUCCESS)
	{
		// Determine the reason for the error
		clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG,
				sizeof(buildLog), buildLog, NULL);

		std::cerr << "Error in program: " << std::endl;
		std::cerr << buildLog << std::endl;
		clReleaseProgram(program);
		return NULL;
	}

	return program;
}

bool SaveProgramBinary(cl_program program, cl_device_id device, const char* fileName)
{
	cl_uint numDevices = 0;
	cl_int errNum;

	// 1 - Query for number of devices attached to program
	errNum = clGetProgramInfo(program, CL_PROGRAM_NUM_DEVICES, sizeof(cl_uint),
			&numDevices, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error querying for number of devices." << std::endl;
		return false;
	}

	// 2 - Get all of the Device IDs
	cl_device_id *devices = new cl_device_id[numDevices];
	errNum = clGetProgramInfo(program, CL_PROGRAM_DEVICES,
			sizeof(cl_device_id) * numDevices,
			devices, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error querying for devices." << std::endl;
		delete [] devices;
		return false;
	}

	// 3 - Determine the size of each program binary
	size_t *programBinarySizes = new size_t [numDevices];
	errNum = clGetProgramInfo(program, CL_PROGRAM_BINARY_SIZES,
			sizeof(size_t) * numDevices,
			programBinarySizes, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error querying for program binary sizes." << std::endl;
		delete [] devices;
		delete [] programBinarySizes;
		return false;
	}

	unsigned char **programBinaries = new unsigned char*[numDevices];
	for (cl_uint i = 0; i < numDevices; i++)
	{
		programBinaries[i] = new unsigned char[programBinarySizes[i]];
	}

	// 4 - Get all of the program binaries
	errNum = clGetProgramInfo(program, CL_PROGRAM_BINARIES, sizeof(unsigned char*) * numDevices,
			programBinaries, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error querying for program binaries" << std::endl;

		delete [] devices;
		delete [] programBinarySizes;
		for (cl_uint i = 0; i < numDevices; i++)
		{
			delete [] programBinaries[i];
		}
		delete [] programBinaries;
		return false;
	}

	// 5 - Finally store the binaries for the device requested out to disk for future reading.
	for (cl_uint i = 0; i < numDevices; i++)
	{
		// Store the binary just for the device requested.  In a scenario where
		// multiple devices were being used you would save all of the binaries out here.
		if (devices[i] == device)
		{
			FILE *fp = fopen(fileName, "wb");
			fwrite(programBinaries[i], 1, programBinarySizes[i], fp);
			fclose(fp);
			break;
		}
	}

	// Cleanup
	delete [] devices;
	delete [] programBinarySizes;
	for (cl_uint i = 0; i < numDevices; i++)
	{
		delete [] programBinaries[i];
	}
	delete [] programBinaries;
	return true;
}

bool CreateMemObjects(struct kdata *kdp)
{
	cl_kernel kernel = kdp->kernel;
	cl_context context = kdp->context;
	int no = kdp->arg_num;
	cl_mem *memObjects = kdp->d_objs = (cl_mem *)malloc(sizeof(cl_mem)*no);
	size_t *sizes = kdp->arg_sizes;
	cl_mem_flags *flags = kdp->d_obj_flags = (cl_mem_flags *)malloc(sizeof(cl_mem_flags)*no);
	cl_int err;
	if (kdp->h_objs == NULL)
		kdp->h_objs = (void **)calloc(no,sizeof(void *));
	for (int i = 0; i < no; i++) {
		// host
		if (kdp->h_objs[i] == NULL)
			kdp->h_objs[i] = (void *)malloc(sizes[i]);
		// device
		char k = kdp->arg_kinds[i];
		flags[i] = k=='R' ? CL_MEM_READ_ONLY : k=='W' ? CL_MEM_WRITE_ONLY : CL_MEM_READ_WRITE;
		memObjects[i] = clCreateBuffer(context, flags[i], sizes[i], NULL, &err);
		if (err) {
			std::cout << "FAIL : clCreateBuffer : " << i << " : " << err << std::endl;
			return false;
		} else if (memObjects[i] == NULL) {
			std::cout << "FAIL : clCreateBuffer : " << i << " : " << "STRANGE : NULL pt returned" << std::endl;
			return false;
		}
		err = clSetKernelArg(kernel, i, sizeof(cl_mem), &memObjects[i]);
		if (err) {
			std::cout << "FAIL : clSetKernelArg : " << i << " : " << err << std::endl;
			return false;
		}
	}
	return true;
}

///
//Cleanup any created OpenCL resources
//
void Cleanup(cl_context context, cl_command_queue commandQueue,
		cl_program program, cl_kernel kernel, cl_mem memObjects[3])
{
	for (int i = 0; i < 3; i++)
	{
		if (memObjects[i] != 0)
			clReleaseMemObject(memObjects[i]);
	}
	if (commandQueue != 0)
		clReleaseCommandQueue(commandQueue);

	if (kernel != 0)
		clReleaseKernel(kernel);

	if (program != 0)
		clReleaseProgram(program);

	if (context != 0)
		clReleaseContext(context);

}

extern uint64_t pocl_debug_messages_filter;

static inline void
mppa_cos_configure_count_cycle(void)
{
#ifdef __CLUSTER_OS__
	/* config pmc for cycle count */
	uint64_t pmc_value = __builtin_k1_get(COS_SFR_PMC);

	pmc_value &= ~(0xfULL);
	__builtin_k1_set(COS_SFR_PMC, pmc_value);
#endif
}

static inline uint64_t
mppa_cos_get_count_cycle(void)
{
#ifdef __CLUSTER_OS__
	return __builtin_k1_get(COS_SFR_PM0);
#else
	uint64_t a, d;
	__asm__ volatile ("rdtsc" : "=a" (a), "=d" (d));
	return (d<<32) | a;
#endif
}


////////////////////////////////////
//      FIR COEFFICIENTS           //
////////////////////////////////////
void fircoef( int16_t *coefficient, int filterLength , int fc) {
        int16_t *coeffp; // pointer to coefficients
        int n;
        int k;
        for ( n = 0; n < filterLength; n++ ) {
                k= n- (int)( filterLength/2 );
                // For design a high pass; multiply coeff with (-1)^k : pow(-1,k)
                if (k!=0)
                        coefficient[n]=sin(2*Pi*fc*Te*(k))/(Pi*k)*3000;
                else
                        coefficient[n]=2*fc*Te*3000;
                //printf("coeff_FIR[%d]=%f \n",n,(double)coefficient[n]);
        }
}

/*******************************************/

void kernel_initiate(struct kdata *kd, char *src) {
	
}

/*******************************************/

int main(void)
{

	mppa_cos_configure_count_cycle();
	printf("Master OpenCL : a %p b %p result %p\n", a, b, result);

	struct kdata kd;
	kd = {0};
	kd.src = "histogram.cl";
	kd.name = "histogram";
	kd.compile_options = "-g -DNLIN=720 -DNCOL=1080 -DNWI=16";
	
	size_t sizes[] = {720*1080, 256,16};
	// cl_mem_flags flags[] = {CL_MEM_READ_ONLY, CL_MEM_WRITE_ONLY, CL_MEM_WRITE_ONLY};
	
	kd.arg_num = 3;
	kd.arg_kinds = "RWW";
	kd.arg_sizes = sizes;
	// kd.d_obj_flags = flags;
	
	
	cl_context context = 0;
	cl_command_queue commandQueue = 0;
	cl_program program = 0;
	cl_device_id device = 0;
	cl_kernel kernel = 0;
	cl_mem memObjects[3] = { 0, 0, 0 };
	cl_int errNum;

	// Create an OpenCL context on first available platform
	kd.context = context = CreateContext();
	if (context == NULL)
	{
		std::cerr << "Failed to create OpenCL context." << std::endl;
		return 1;
	}

	// Create a command-queue on the first device available
	// on the created context
	kd.queue = commandQueue = CreateCommandQueue(context, &device);
	if (commandQueue == NULL)
	{
		Cleanup(context, commandQueue, program, kernel, memObjects);
		return 1;
	}
	kd.device = device;

	// Create OpenCL program - first attempt to load cached binary.
	//  If that is not available, then create the program from source
	//  and store the binary for future use.
	std::cout << "Attempting to create program from binary..." << std::endl;
	
	program = CreateProgramFromBinary(context, device, "HelloWorld.cl.pocl");

	if (program == NULL)
	{
		std::cout << "Binary not loaded, create from source..." << std::endl;
#ifdef ORIGINAL
		program = CreateProgram(context, device, kd.src, kd.compile_options);
#else
		std::ifstream sourceFile(kd.src);
		std::string sourceCode(std::istreambuf_iterator<char>{sourceFile}, {});
		const char* ksrc = sourceCode.c_str();
		kd.program = program = clCreateProgramWithSource( context, 1, &ksrc, 0, &errNum );
		if (errNum) {
			std::cout << "FAIL : clCreateProgramWithSource : " << errNum << std::endl;
			Cleanup(context, commandQueue, program, kernel, memObjects);
			return 1;
		}
		errNum = clBuildProgram( program, 0, NULL, kd.compile_options, NULL, NULL);
		if (errNum) {
			std::cout << "FAIL : clBuildProgram : " << errNum << std::endl;
			size_t log_size;
			errNum = clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, 0, NULL, &log_size);
			std::cout << errNum << std::endl;
			char *log = new char[log_size+1];
			errNum = clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, log_size, log, NULL);
			std::cout << errNum << std::endl;
			std::cout << log << std::endl; 
			
			Cleanup(context, commandQueue, program, kernel, memObjects);
			return 1;
		}
		std::cout << "OK OK OK" << std::endl;
		//Cleanup(context, commandQueue, program, kernel, memObjects);
		//return 1;
#endif
		if (program == NULL)
		{
			Cleanup(context, commandQueue, program, kernel, memObjects);
			return 1;
		}
#ifdef ORIGINAL
		std::cout << "Save program binary for future run..." << std::endl;
		if (SaveProgramBinary(program, device, "HelloWorld.cl.bin") == false)
		{
			std::cerr << "Failed to write program binary" << std::endl;
			Cleanup(context, commandQueue, program, kernel, memObjects);
			return 1;
		}
#endif
	}
	else
	{
		std::cout << "Read program from binary." << std::endl;
	}

	// Create OpenCL kernel
	kd.kernel = kernel = clCreateKernel(program, kd.name, &errNum);
	if (kernel == NULL || errNum)
	{
		std::cerr << "FAIL : clCreateKernel : " << errNum << std::endl;
		Cleanup(context, commandQueue, program, kernel, memObjects);
		return 1;
	}

#ifdef ORIGINAL
	// Create memory objects that will be used as arguments to
	// kernel.  First create host memory arrays that will be
	// used to store the arguments to the kernel
	for (int i = 0; i < ARRAY_SIZE; i++)
	{
		result[i] = 0;
	}


	// Sample initialisation
        for(int i=0; i<NSAMPLE; i++) {
                b[i] = (int16_t) (sin(2*Pi*Freq*(i*Te))+(1.6)*sin(2*Pi*Freq*4*(i*Te))+4)*SCALE;
        }


        fircoef( a, FILTER_LEN , Fc);
#endif
	
	if (!CreateMemObjects(&kd))
	{
		Cleanup(context, commandQueue, program, kernel, memObjects);
		return 1;
	}

	size_t globalWorkSize[1] = { 1 }; // use the define
	size_t localWorkSize[1] = { WG_SIZE }; // same
/***
	errNum = clSetKernelArg(kernel, 0, sizeof(cl_mem), &memObjects[0]);
	errNum |= clSetKernelArg(kernel, 1, sizeof(cl_mem), &memObjects[1]);
	errNum |= clSetKernelArg(kernel, 2, sizeof(cl_mem), &memObjects[2]);

	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error setting kernel_vector_add arguments." << std::endl;
		Cleanup(context, commandQueue, program, kernel, memObjects);
		return 1;
	}
***/
	struct timeval time_before, time_after;

	gettimeofday (&time_before, NULL);

	// Enqueue a and b
	for(int i=0; i < kd.arg_num; i++) {
		char k = kd.arg_kinds[i];
		if (k == 'R' || k == 'X') {
			errNum = clEnqueueWriteBuffer(kd.queue, kd.d_objs[i], CL_TRUE,
				0, kd.arg_sizes[i], kd.h_objs[i], 0, NULL, NULL);
			if (errNum) {
				std::cerr << "FAIL : clEnqueueWriteBuffer " << i << " : " << errNum << std::endl;
				Cleanup(context, commandQueue, program, kernel, memObjects);
				return 1;
			}
		}
	}

	// Queue the kernel up for execution across the array
	uint64_t start = mppa_cos_get_count_cycle();

	errNum = clEnqueueNDRangeKernel(kd.queue, kd.kernel, 1, NULL, globalWorkSize, localWorkSize,
			0, NULL, NULL);
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error queuing kernel for execution. Error code is " << errNum << "." << std::endl;
		Cleanup(context, commandQueue, program, kernel, memObjects);
		return 1;
	}

	// Read the output buffer back to the Host
	uint64_t start_read = mppa_cos_get_count_cycle();
	errNum = clEnqueueReadBuffer(commandQueue, memObjects[2], CL_TRUE, 0, NSAMPLE * sizeof(int16_t), result,
			0, NULL, NULL);

	clFinish(commandQueue);

	gettimeofday (&time_after, NULL);

        printf("[Coolidge] Total Processing time in us: %ld us\n",((time_after.tv_sec - time_before.tv_sec) * 1000000 + time_after.tv_usec) - time_before.tv_usec);


	uint64_t end_read = mppa_cos_get_count_cycle();
	if (errNum != CL_SUCCESS)
	{
		std::cerr << "Error reading result buffer." << std::endl;
		Cleanup(context, commandQueue, program, kernel, memObjects);
		return 1;
	}


	 // printf some values to ckech the results
        for (int i=0; i < 5; i ++) {
                 //printf("c[%d]=%f \n",NSAMPLE/2+i,(double) result[NSAMPLE/2+i]);
        }


	std::cout << "Executed program succesfully." << std::endl;

	Cleanup(context, commandQueue, program, kernel, memObjects);

	std::cout << "Goodbye." << std::endl;
	return 0;
}
