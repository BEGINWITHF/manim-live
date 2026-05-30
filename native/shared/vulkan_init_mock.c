#include "vulkan_render.h"
#include <stdio.h>

// Mock Vulkan implementation for testing cross-platform structure
static int g_ready = 0;

void Render_Init(RenderWindow window, int width, int height, RenderInstance instance) {
    printf("[MOCK] Render_Init called: window=%p, size=%dx%d\n", window, width, height);
    g_ready = 1;
}

int Render_IsReady(void) {
    return g_ready;
}

void Render_DrawScene(const ShapeRect* rects, int rect_count, 
                      const ShapeCircle* circles, int circle_count, 
                      const ShapeLine* lines, int line_count) {
    printf("[MOCK] Render_DrawScene: rects=%d, circles=%d, lines=%d\n", 
           rect_count, circle_count, line_count);
}

void Render_Cleanup(void) {
    printf("[MOCK] Render_Cleanup called\n");
    g_ready = 0;
}
