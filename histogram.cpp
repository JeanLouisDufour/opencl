#include "pgm.h"
#include "lib_opencl.h"
#include <iostream>
#include <assert.h>

int main(void) {
	//
	uint32_t width;
    uint32_t  height;
    uint8_t bpp;
	parsePGM("cat.pgm", &width, &height, &bpp); // bpp == 1 ou 2
	std::cout  <<  "w : " << width << "  h : " <<  height  << "  bpp : " <<  (int)bpp  << std::endl;
	assert(bpp==1);
	int sz = width*height*bpp;
	uint8_t  *pt = new uint8_t [width * height * bpp];
	uint32_t pitch = width;
	loadPGM("cat.pgm", pt, width, height, pitch, bpp);
	
	// histo hote
	uint64_t sum = 0;
	int h[256] = {0};
	for (int i =0; i < sz; i++) {
		sum += pt[i];
		h[pt[i]]++;
	}
	int hs = 0;
	for (int i =0; i < 256; i++) hs += h[i];
	std::cout << hs << " " << sz << std::endl;
	

	//
	int NWI = 16;
	
	struct kdata kd = {0};
	kd.src = "histogram.cl";
	kd.name = "histogram";
	kd.compile_options = "-g -DNLIN=720 -DNCOL=1080 -DNWI=16";
	
	size_t sizes[] = {1*sz, 4*256,1*NWI};
	// cl_mem_flags flags[] = {CL_MEM_READ_ONLY, CL_MEM_WRITE_ONLY, CL_MEM_WRITE_ONLY};
	
	kd.arg_num = 3;
	kd.arg_kinds = "RWW";
	kd.arg_sizes = sizes;
	// kd.d_obj_flags = flags;
	
	kernel_initiate(&kd);

	void *h0 = kd.h_objs[0];
	uint32_t *h1 = (uint32_t *)(kd.h_objs[1]);
	uint8_t *h2 = (uint8_t *)(kd.h_objs[2]);
	memcpy(h0, pt, sz);
	
	struct timeval time_before, time_after;
	int nb_iter = 10;
	bool chk = true;
	std::cout << "Starting " << nb_iter << " iterations" << std::endl;
	gettimeofday (&time_before, NULL);
	
	for(int kiter=0; kiter < nb_iter; kiter++) {
		if (chk) {
			for (int i = 0; i < NWI; i++) h2[i] = 0;
			for (int i = 0; i < 256; i++) h1[i] = 0;
		}
		kernel_run(&kd);
		if (chk) {
			bool h2_ok = true;
			for (int i = 0; i < NWI; i++) if (h2[i] != 3) { h2_ok = false; break; };
			bool h1_ok = true;
			for (int i = 0; i < 256; i++) if (h1[i] != h[i]) { h1_ok = false; break; };
			std::cout << "h2_ok " << h2_ok << " h1_ok " <<  h1_ok << std::endl;
		}
	}
	
	gettimeofday (&time_after, NULL);
	int dt_usec = (time_after.tv_sec - time_before.tv_sec) * 1000000 + time_after.tv_usec - time_before.tv_usec;
    printf("Mean Processing time : %lf s\n",(double)dt_usec / (nb_iter * 1000000.0));

	kernel_terminate(&kd);
	return 0;
}