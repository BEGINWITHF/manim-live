#ifndef PLATFORM_H
#define PLATFORM_H

#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif

void Vulkan_Init(int w, int h);
int Vulkan_Tick();
void Vulkan_Shutdown();

void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b);
void AddCircle(float x, float y, float radius, int r, int g, int b);
void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b);
void AddArrow(float x1, float y1, float x2, float y2, int width, int r, int g, int b);
void AddText(const char* text, float x, float y, int size, int r, int g, int b);

void AddRectSeparate(float x, float y, float hw, float hh, float rot, int fr, int fg, int fb, int sr, int sg, int sb, int sw);
void AddCircleSeparate(float x, float y, float radius, int fr, int fg, int fb, int sr, int sg, int sb, int sw);

void AddPolygonSeparate(float* points, int count, int fr, int fg, int fb, int sr, int sg, int sb, int strokeWidth);

#ifdef __cplusplus
}
#endif

#endif