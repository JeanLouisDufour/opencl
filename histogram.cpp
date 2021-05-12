#include "pgm.h"
#include "lib_opencl.h"

int main(void) {
	d = kernel_initiate(ksrc,
					 [ (ctypes.c_uint8 * sz), (ctypes.c_uint32 * 256), (ctypes.c_uint8 * NWI)],
					 "RWW",
					 kmacros
	)

	assert 'error' not in d, d['error']
}