#ifndef DRAW_COMMON_H
#define DRAW_COMMON_H

#include "vulkan_core.h"
#include <math.h>

extern float g_vertices[];
extern uint32_t g_vertex_count;
extern VkExtent2D g_swapchain_ext;

#define MAX_VERTICES 1048576

static inline void ToNDC(float px, float py, float *nx, float *ny) {
    *nx = (px / (float)g_swapchain_ext.width) * 2.0f - 1.0f;
    *ny = (py / (float)g_swapchain_ext.height) * 2.0f - 1.0f;
}

static inline int PushVertex(float px, float py, float r, float g, float b, float a) {
    if (g_vertex_count >= MAX_VERTICES) return 0;

    float nx, ny;
    ToNDC(px, py, &nx, &ny);

    uint32_t idx = g_vertex_count * 6;
    g_vertices[idx + 0] = nx;
    g_vertices[idx + 1] = ny;
    g_vertices[idx + 2] = r;
    g_vertices[idx + 3] = g;
    g_vertices[idx + 4] = b;
    g_vertices[idx + 5] = a;

    g_vertex_count++;
    return 1;
}

#endif
