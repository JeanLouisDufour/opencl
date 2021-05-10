#ifndef __PGM__C__
#define __PGM__C__
#include <stdint.h>
void savePGM8b(const char * path,
              void * pt,
              uint32_t width,
              uint32_t height,
              uint32_t pitch);

void savePGM16b(const char * path,
              void * pt,
              uint32_t width,
              uint32_t height,
              uint32_t pitch);

void  parsePGM(const char * path,
                  uint32_t * width,
                  uint32_t  * height,
                  uint8_t * bpp);
void  loadPGM(const char * path,
              void * pt,
              uint32_t width,
              uint32_t height,
              uint32_t pitch,
              uint8_t bpp);
#endif // __PGM__C__
