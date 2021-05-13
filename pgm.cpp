#include "pgm.h"

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <iostream>

void savePGM8b(const char * path,
              void * pt,
              uint32_t width,
              uint32_t height,
              uint32_t pitch)
{
    FILE * fp = fopen(path, "wb");
    if(fp == 0){
        printf("[%s %d] Cannot open file for writing %s\n", __FUNCTION__, __LINE__, path);
        return;
    }
    printf("[%s %d] %p %d %d %d\n", __FUNCTION__, __LINE__, pt,width, height, pitch);

    fprintf(fp, "P5\n%d %d\n255\n", width, height);
    uint32_t j;
    uint8_t * ptr = (uint8_t *) pt;
    for(j = 0; j < height; j++){
        fwrite(ptr, 1 , width, fp);
        ptr += pitch;
    }
    fclose(fp);

}

void savePGM16b(const char * path,
              void * pt,
              uint32_t width,
              uint32_t height,
              uint32_t pitch)
{
    FILE * fp = fopen(path, "wb");
    if(fp == 0){
        printf("[%s %d] Cannot open file for writing %s\n", __FUNCTION__, __LINE__, path);
        return;
    }

    fprintf(fp, "P5\n%d %d\n65535\n", width, height);
    uint32_t j;
    uint8_t * ptr = (uint8_t *) pt;
    for(j = 0; j < height; j++){
        fwrite(ptr, 1 , width*2, fp);
        ptr += pitch;
    }

    fclose(fp);
}

void  parsePGM(const char * path,
                  uint32_t * width,
                  uint32_t * height,
                  uint8_t * bpp)
{
    FILE * fp = fopen(path, "rb");
    if(fp == 0){
        printf("[%s %d] Cannot open file for reading %s\n", __FUNCTION__, __LINE__, path);
        return;
    }

    uint32_t read;
    uint32_t maxValue = 0;
    uint8_t buffer[128];

    read = fscanf(fp,"%s", buffer);
    printf("[%s %d] %d %s\n", __FUNCTION__, __LINE__, read,buffer);
    read = fscanf(fp,"%d %d", width, height);
    printf("[%s %d] %d %d %d\n", __FUNCTION__, __LINE__, read,*width,*height);
    read = fscanf(fp,"%d", &maxValue);
    printf("[%s %d] %d %d\n", __FUNCTION__, __LINE__, read,maxValue);

    if(maxValue== 255){
        *bpp = 1;
    } else if(maxValue == 65535){
        *bpp = 2;
    }
    fclose(fp);

}
void  loadPGM(const char * path,
              void * pt,
              uint32_t width,
              uint32_t height,
              uint32_t pitch,
              uint8_t bpp)
{
    FILE * fp = fopen(path, "rb");
    if(fp == 0){
        printf("[%s %d] Cannot open file for reading %s\n", __FUNCTION__, __LINE__, path);
        return;
    }

	int _;
    uint32_t maxValue = 0;
    uint8_t buffer[128];

    _ = fscanf(fp,"%s", buffer);
    _ = fscanf(fp,"%d %d", &width, &height);
    _ = fscanf(fp,"%d", &maxValue);
	std::cout << "whm " << width << " " << height << " " << maxValue  << std::endl;
	
    _ = fread(buffer, 1, 1, fp);

	uint8_t * npt = (uint8_t*)pt;
#ifdef FOO
    uint32_t lineSize = width * bpp;

    uint32_t j ;
    for(j = 0; j < height; j++){
        fread(npt + j*pitch, lineSize, 1, fp);
    }
#else
	int sz = width * height;
	int lu = fread(npt, 1, sz, fp);
	std::cout << "sz " << sz << " lu " << lu << " " << (int)npt[0] << " ... " <<  (int)npt[sz-1] << std::endl;
#endif
    fclose(fp);

}

void  readPGM(const char * path,
	void **pt,
    uint32_t * width,
    uint32_t  * height,
    uint8_t * bpp) {

    FILE * fp = fopen(path, "rb");
    assert(fp);

    uint32_t read;
    uint32_t maxValue = 0;
    uint8_t buffer[128];

    read = fscanf(fp,"%s", buffer);
    //printf("[%s %d] %d %s\n", __FUNCTION__, __LINE__, read,buffer);
	assert(read == 1 && buffer[0]=='P' && buffer[1]=='5');
    read = fscanf(fp,"%d %d", width, height);
    //printf("[%s %d] %d %d %d\n", __FUNCTION__, __LINE__, read,*width,*height);
	assert(read == 2 && *width <= 65536 && *height <= 65536);
    read = fscanf(fp,"%d", &maxValue);
    //printf("[%s %d] %d %d\n", __FUNCTION__, __LINE__, read,maxValue);
	assert(read == 1);

    if(maxValue== 255){
        *bpp = 1;
    } else if(maxValue == 65535){
        *bpp = 2;
    } else {
		assert(false);
	}

	read = fread(buffer, 1, 1, fp);
	assert(read==1);
	
	uint32_t sz = *width * *height *  *bpp;
	*pt = malloc(sz);
	assert(*pt);
	read = fread(*pt, 1, sz, fp);
    fclose(fp);
	assert(read==sz);
}
