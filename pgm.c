#include "pgm.h"

#include <stdio.h>
#include <stdlib.h>

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


    uint32_t maxValue = 0;
    uint8_t buffer[128];

    fscanf(fp,"%s", buffer);
    fscanf(fp,"%d %d", &width, &height);
    fscanf(fp,"%d", &maxValue);

    fread(buffer, 1, 1, fp);

    uint32_t lineSize = width * bpp;
    uint8_t * npt = (uint8_t*)pt;

    uint32_t j ;
    for(j = 0; j < height; j++){
        fread(npt + j*pitch, lineSize, 1, fp);
    }

    fclose(fp);

}
