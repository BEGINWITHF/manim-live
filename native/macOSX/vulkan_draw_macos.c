#include "vulkan_render.h"
#include <stdio.h>

// macOS-specific drawing implementation
// This would contain the actual Vulkan rendering commands for macOS

// Placeholder implementation - the actual drawing is handled in Render_DrawScene
// This file could contain macOS-specific Vulkan setup if needed

void Render_DrawScene(const ShapeRect* rects, int rect_count,
                      const ShapeCircle* circles, int circle_count,
                      const ShapeLine* lines, int line_count) {
    printf("[MACOS] Render_DrawScene: rects=%d, circles=%d, lines=%d\n",
           rect_count, circle_count, line_count);
}

void Render_Cleanup(void) {
    printf("[MACOS] Render_Cleanup called\n");
}
