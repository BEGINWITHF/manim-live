#ifndef VULKAN_RENDER_H
#define VULKAN_RENDER_H

#include <windows.h>
#include <vulkan/vulkan.h>

void Render_Init(HWND hwnd, int width, int height);
void Render_Frame(void);
void Render_SetClear(float r, float g, float b);
void Render_Cleanup(void);

#endif