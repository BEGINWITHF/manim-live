#ifndef VULKAN_RENDER_H
#define VULKAN_RENDER_H

#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif

void VK_Init(HWND hwnd, int w, int h);
void VK_Draw(void);
void VK_SetClearColor(float r, float g, float b);
void VK_Cleanup(void);

#ifdef __cplusplus
}
#endif

#endif