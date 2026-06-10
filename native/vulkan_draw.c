#include "vulkan_core.h"
#include "vulkan_render.h"
#include "draw_common.h"

float g_vertices[MAX_VERTICES * 5];
uint32_t g_vertex_count = 0;

void BuildVerticesFromRects(const Rect *rects, int count);
void BuildVerticesFromCircles(const Circle *circles, int count);
void BuildVerticesFromLines(const LineObj *lines, int count);


void Render_DrawScene(const Rect* rects, int rect_count,
                      const Circle* circles, int circle_count,
                      const LineObj* lines, int line_count) {

    g_vertex_count = 0;

    if (rects && rect_count > 0) {
        BuildVerticesFromRects(rects, rect_count);
    }

    if (circles && circle_count > 0) {
        BuildVerticesFromCircles(circles, circle_count);
    }

    if (lines && line_count > 0) {
        BuildVerticesFromLines(lines, line_count);
    }

    if (g_vertex_count > 0) {
        update_vertex_buffer(g_vertices, g_vertex_count * 5 * sizeof(float));
    }
}