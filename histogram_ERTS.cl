// macros : NCOL NLIN NWI
#define HIST_BINS 256
#define numDataPerWorkItem (NLIN * NCOL / NWI)
#define numHistPerWorkItem (HIST_BINS / NWI)

__kernel void histogram_1(__global uchar data[512][512], __global int histogram[256]) {
	int gid0 = get_global_id(0), gid1 = get_global_id(1);
#ifdef UNSAFE
	histogram[data[gid0][gid1]] += 1;
#else
	atomic_inc( &histogram[data[gid0][gid1]] );
#endif
}

__kernel void histogram_BAD(__global uchar image[512][512], __global int histogram[256]) {
	int gid0 = get_global_id(0), gid1 = get_global_id(1);
	histogram[image[gid0][gid1]] += 1;
}

__kernel void histogram_GOOD(__global uchar image[512][512], __global int histogram[256]) {
	int gid0 = get_global_id(0), gid1 = get_global_id(1);
	atomic_inc( &histogram[image[gid0][gid1]] );
}

__kernel void resize_22_(__global uchar src[512][512], __global uchar dst[256][256]) {
	uint gid0 = get_global_id(0), gid1 = get_global_id(1), sum = 0;
	for(int i = 0; i <= 1; i++)
		for(int j = 0; j <= 1; i++)
			sum += src[2*gid0+i][2*gid1+j];
	dst[gid0][gid1] = sum/4;
}

__kernel void resize_22(__global uchar src[512][512], __global uchar dst[256][256]) {
	uint gid0 = get_global_id(0), gid1 = get_global_id(1);
	dst[gid0][gid1] = (src[2*gid0  ][2*gid1  ]
					+  src[2*gid0  ][2*gid1+1]
					+  src[2*gid0+1][2*gid1  ]
					+  src[2*gid0+1][2*gid1+1] ) / 4;
}

#define LOCALHIST

__kernel 
void histogram(__global uchar *data,
               __global int *histogram,
			   __global uchar *diag)
{
                         // int numDataPerWorkItem, // beaucoup (1M/64 = 16384)
						// int numHistPerWorkItem,  // 256/64 = 4
#ifdef LOCALHIST
	__local int localHistogram[HIST_BINS];
#endif
   /*__private*/ int privateHistogram[HIST_BINS];
   int lid = get_local_id(0), lsz = get_local_size(0);
   int gid = get_global_id(0), gsz = get_global_size(0);
   int ng = get_num_groups(0), gr_id = get_group_id(0);
   uchar ok = 0;
   if (gid==lid+gr_id*lsz) ok |= 1;
   // on ne veut qu'un seul groupe
   if (ng==1 && gr_id==0) ok |= 2;
   diag[gid] = ok;
   
   
   int data_offset = gid*numDataPerWorkItem;
   int hist_offset = gid*numHistPerWorkItem;
   
   for (int i = 0; i < numHistPerWorkItem; i++) {
#ifdef LOCALHIST
			localHistogram[i+hist_offset] = 0;
#else
			histogram[i+hist_offset] = 0;
#endif
	}
   
   /* Initialize local histogram to zero */
   for (int i = 0; i < HIST_BINS; i++) privateHistogram[i] = 0;
   
   /* Wait until all work-items within 
    * the work-group have completed */
   // barrier(CLK_LOCAL_MEM_FENCE);
   
   /* Compute local histogram */
   __global uchar *p = data + data_offset;
   for (int i = 0; i < numDataPerWorkItem; i++) privateHistogram[p[i]]++;
   
   
   /* Wait until all work-items within 
    * the work-group have completed */
   //barrier(CLK_GLOBAL_MEM_FENCE | CLK_LOCAL_MEM_FENCE);
   //mem_fence(CLK_GLOBAL_MEM_FENCE | CLK_LOCAL_MEM_FENCE);
   
   /* Write the local histogram out to the global histogram */
	
	for (int i = 0; i < HIST_BINS; i++) {
			int j = (i + hist_offset) & 255;
			//if (j >= HIST_BINS) j -= HIST_BINS;
			//j -= j >= HIST_BINS ? HIST_BINS : 0;
#ifdef LOCALHIST
#if 1 
			localHistogram[j] += privateHistogram[j];
			barrier(CLK_LOCAL_MEM_FENCE); 
#else
			atomic_add(&localHistogram[j], privateHistogram[j]); // erreur des le debut !!!!!
#endif
#else
#if 1
			histogram[j] += privateHistogram[j];
			barrier(CLK_GLOBAL_MEM_FENCE);
#else
			atomic_add(&histogram[j], privateHistogram[j]);
#endif
#endif
	}
#ifdef LOCALHIST
	for (int i = 0; i < numHistPerWorkItem; i++) {
			histogram[i+hist_offset] = localHistogram[i+hist_offset];
	}
#endif
}
