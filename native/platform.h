#ifndef PLATFORM_H
#define PLATFORM_H

#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) int Vulkan_Init(int w, int h);
__declspec(dllexport) int Vulkan_Tick(void);
__declspec(dllexport) void Vulkan_Shutdown(void);

__declspec(dllexport) void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b);
__declspec(dllexport) void AddCircle(float x, float y, float radius, int r, int g, int b);
__declspec(dllexport) void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b);
__declspec(dllexport) void AddText(const char* text, float x, float y, int size, int r, int g, int b);

__declspec(dllexport) void ClearShapes(void);

#ifdef __cplusplus
}
#endif

#endif