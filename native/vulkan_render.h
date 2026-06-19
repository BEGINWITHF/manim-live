#ifndef VULKAN_RENDER_H
#define VULKAN_RENDER_H

#include <windows.h>
#define VK_USE_PLATFORM_WIN32_KHR
#include <vulkan/vulkan.h>
#include "shared_types.h"

void Render_Init(HWND hwnd, int width, int height, HINSTANCE hinst);

int Render_IsReady(void);

void Render_DrawScene(const Rect* rects, int rect_count,
                      const Circle* circles, int circle_count,
                      const LineObj* lines, int line_count,
                      const EllipseObj* ellipses, int ellipse_count,
                      const PolygonObj* polygons, int polygon_count,
                      const DashedLineObj* dashed_lines, int dashed_line_count,
                      const ArcObj* arcs, int arc_count,
                      const PointObj* points, int point_count,
                      const TextObj* texts, int text_count);

void Render_Cleanup(void);

#endif
