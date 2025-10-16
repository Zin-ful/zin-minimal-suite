#ifndef PIXEL_H
#define PIXEL_H

#include <stdint.h>

extern signed int screen_res_y;
extern signed int screen_res_x;

int init_framebuffer();
void close_framebuffer();
void clear_screen();
void draw_pixel(int x, int y, uint32_t color);
void erase_pixel(int x, int y, uint32_t color);
void draw_rect(int x, int y, int w, int h, uint32_t color);
void erase_rect(int x, int y, int w, int h);
#endif
