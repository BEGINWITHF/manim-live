#ifndef PLATFORM_H
#define PLATFORM_H

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) int Vulkan_Init(int w, int h);
__declspec(dllexport) int Vulkan_Tick(void);
__declspec(dllexport) void Vulkan_Shutdown(void);

__declspec(dllexport) void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b);
__declspec(dllexport) void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress);
__declspec(dllexport) void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b);
__declspec(dllexport) void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b);
__declspec(dllexport) void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts);
__declspec(dllexport) void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length);
__declspec(dllexport) void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width);
__declspec(dllexport) void AddPoint(float x, float y, int r, int g, int b);
__declspec(dllexport) void AddText(float x, float y, int r, int g, int b, float font_size, const char* text);
__declspec(dllexport) int Text_LoadFont(const unsigned char *data, int data_len);

__declspec(dllexport) void ClearShapes(void);

#ifdef __cplusplus
}
#endif

#endif