#ifndef RENDERER_H
#define RENDERER_H

#include <windows.h>

void renderer_init(HWND hwnd, int w, int h);
void renderer_frame(void);
void renderer_set_clear(float r, float g, float b);
void renderer_cleanup(void);

#endif