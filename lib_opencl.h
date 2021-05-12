#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <sys/time.h>
#include <math.h>

#include <CL/cl.h>

struct kdata {
	/// INPUTS
	const char *src;				// "histogram.cl"
	const char *name;				// "histogram"
	int arg_num;					// 3    (les args alloues)
	size_t *arg_sizes;				// en octets
	const char *arg_kinds;			// "RWX"
	const char *compile_options;	// "-g -DFOO=BAR"
	void **h_objs;					// NULL ou tableau de pointeurs
	cl_platform_id platform;
	cl_device_id device;
	cl_device_type device_type;
	cl_context	context;
	cl_command_queue queue;
	cl_program program;
	cl_kernel kernel;
	int *params;
	cl_mem *d_objs;
	cl_mem_flags *d_obj_flags;
};

void kernel_initiate(struct kdata *kd, char *src);
