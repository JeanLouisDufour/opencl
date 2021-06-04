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

}
