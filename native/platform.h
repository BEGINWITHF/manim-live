#ifndef PLATFORM_H
#define PLATFORM_H

#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) void Vulkan_Init(int w, int h);
__declspec(dllexport) int  Vulkan_Tick(void);
__declspec(dllexport) void Vulkan_Shutdown(void);
__declspec(dllexport) void DrawRect(float cx, float cy, float hw, float hh, float ang, int r, int g, int b);

#ifdef __cplusplus
}
#endif

#endif