// macros : NCOL NLIN NWI
#define HIST_BINS 256
//#define numDataPerWorkItem (NLIN * NCOL / NWI)
//#define numHistPerWorkItem (HIST_BINS / NWI)

#define LOCALHIST

__kernel 
void histogram(__global uchar *data,
               __global int   *histogram,
			   __global float *scale,
			   __global uint *cumul_and_then_lut,
			   __global uchar *new_data,
			   __global uchar *diag)
{
                         // int numDataPerWorkItem, // beaucoup (1M/64 = 16384)
						// int numHistPerWorkItem,  // 256/64 = 4
#ifdef LOCALHIST
	__local int localHistogram[HIST_BINS];
#endif
   /*__private*/ int privateHistogram[HIST_BINS];  ///// utile dans tous les cas
   int lid = get_local_id(0), lsz = get_local_size(0);
   int gid = get_global_id(0), gsz = get_global_size(0);
   int ng = get_num_groups(0), gr_id = get_group_id(0);
   uchar ok = 0;
   if (gid==lid+gr_id*lsz) ok |= 1;
   // on ne veut qu'un seul groupe
   if (ng==1 && gr_id==0) ok |= 2;
   diag[gid] = ok;
   
	int im_sz = NLIN * NCOL;
	int numDataPerWorkItem = (im_sz / NWI);
	int numHistPerWorkItem = (HIST_BINS / NWI);

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

/***************************************/
	barrier(CLK_GLOBAL_MEM_FENCE | CLK_LOCAL_MEM_FENCE);
	
	if (gid == 0) { ///////// BEGIN UN SEUL WORKER
	
	int i0;
	for (i0 = 0; i0 < HIST_BINS; i0++) if (histogram[i0]) break;
	int n0 = histogram[i0];
	for(int i=0; i < i0; i++) cumul_and_then_lut[i] = 0;
	cumul_and_then_lut[i0] = n0!=im_sz ? 0 : i0;
	uint cumul = 0;
	for(int i=i0+1; i < HIST_BINS; i++) {
		cumul += histogram[i];
		cumul_and_then_lut[i] = cumul;
	}
	if (n0 == im_sz) {
		*scale = 1.0f; /// cumul = 0 ... 0 i0 0 ... 0
	} else {
		*scale = 255.0f / (float)(im_sz - n0);
	}
	
	} // END UN SEUL WORKER
	
	barrier(CLK_GLOBAL_MEM_FENCE | CLK_LOCAL_MEM_FENCE);
	
	for (int i = 0; i < numHistPerWorkItem; i++) {
		cumul_and_then_lut[i+hist_offset] = (uint)rint((float)(cumul_and_then_lut[i+hist_offset]) * *scale);
	}
	
	barrier(CLK_GLOBAL_MEM_FENCE | CLK_LOCAL_MEM_FENCE);
	/* __global uchar * */ p = data + data_offset;
	__global uchar *q = new_data + data_offset;
	
   for (int i = 0; i < numDataPerWorkItem; i++) q[i] = cumul_and_then_lut[p[i]];

}
