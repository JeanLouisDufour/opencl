#define WI 16
#define WG 1

#include <assert.h>

#define __kernel inline
#define __global

#include "histogramme.cl"


void algo() {
	// WG == get_num_groups(0)
	// WI == get_global_size(0)
	int gid = 0;
	for(int wg = 0; wg < WG; wg++) { // get_group_id(0)
		for(int wi = 0; wi < WI/WG; wi++) { // get_local_id(0)
			// gid == get_global_id(0)
		
			gid++;
		}
	}
}

int main() {
	return 0;
}