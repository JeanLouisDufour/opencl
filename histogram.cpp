#include "pgm.h"
#include "lib_opencl.h"
#include <iostream>

int main(void) {
	//
	uint32_t width;
    uint32_t  height;
    uint8_t bpp;
	parsePGM("cat.pgm", &width, &height, &bpp); // bpp == 1 ou 2
	std::cout  <<  "w : " << width << "  h : " <<  height  << "  bpp : " <<  bpp  << std::endl;
	char *pt = new char[width * height];
	uint32_t pitch = width;
	loadPGM("cat.pgm", pt, width, height, pitch, bpp);
	
	
	
	
	//
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
	
	kernel_initiate(&kd);
//					 [ (ctypes.c_uint8 * sz), (ctypes.c_uint32 * 256), (ctypes.c_uint8 * NWI)],
					

	return 0;
}