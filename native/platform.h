#ifndef PLATFORM_H
#define PLATFORM_H

#include "shared_types.h"

#ifdef __cplusplus
extern "C" {
#endif

PLATFORM_EXPORT int Vulkan_Init(int w, int h);
PLATFORM_EXPORT int Vulkan_Tick(void);
PLATFORM_EXPORT void Vulkan_Shutdown(void);

PLATFORM_EXPORT void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha);
PLATFORM_EXPORT void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha);
PLATFORM_EXPORT void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float alpha);
PLATFORM_EXPORT void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha);
PLATFORM_EXPORT void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts, float stroke_progress, float alpha, int close_path);
PLATFORM_EXPORT void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length, float alpha);
PLATFORM_EXPORT void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width, float alpha);
PLATFORM_EXPORT void AddPoint(float x, float y, int r, int g, int b, float alpha);
PLATFORM_EXPORT void AddText(float x, float y, int r, int g, int b, float font_size, float opacity, const char* text, float alpha);
PLATFORM_EXPORT int Text_LoadFont(const unsigned char *data, int data_len);
PLATFORM_EXPORT void AddLineStrip(const float *points, const float *alphas, int count, int width, int r, int g, int b, float alpha);
PLATFORM_EXPORT void AddBezierPath(const float *points, int num_points, int sr, int sg, int sb, float stroke_width, int fr, int fg, int fb, float fill_opacity, float progress, int show_stroke, int show_fill, float alpha);

PLATFORM_EXPORT void ClearShapes(void);
PLATFORM_EXPORT int SaveScreenshot(const char *path);

#ifdef __cplusplus
}
#endif

#endif
