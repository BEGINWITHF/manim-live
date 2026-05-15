#define VK_USE_PLATFORM_WIN32_KHR
#include <windows.h>
#include <vulkan/vulkan.h>
#include "renderer.h"

static int g_ready = 0;

void renderer_init(HWND hwnd, int w, int h) {
    g_ready = 1;
}

void renderer_frame(void) {
    if (!g_ready) return;
}

void renderer_set_clear(float r, float g, float b) {
}

void renderer_cleanup(void) {
}