#ifndef VULKAN_RENDER_H
#define VULKAN_RENDER_H

#ifdef _WIN32
    #include <windows.h>
    #define VK_USE_PLATFORM_WIN32_KHR
    typedef HWND RenderWindow;
    typedef HINSTANCE RenderInstance;
#elif defined(__APPLE__)
    #ifdef MOCK_VULKAN
        // Mock Vulkan types for testing
        typedef void* VkInstance;
        typedef void* VkDevice;
        typedef void* VkQueue;
        typedef void* VkCommandBuffer;
        typedef void* VkRenderPass;
        typedef void* VkPipeline;
        typedef void* VkFramebuffer;
        typedef void* VkSurfaceKHR;
        typedef void* VkSwapchainKHR;
        #define VK_NULL_HANDLE NULL
    #else
        #include <vulkan/vulkan.h>
        #define VK_USE_PLATFORM_MACOS_MVK
    #endif
    typedef void* RenderWindow;
    typedef void* RenderInstance;
#else
    #include <vulkan/vulkan.h>
    typedef void* RenderWindow;
    typedef void* RenderInstance;
#endif

#include "platform_common.h"

void Render_Init(RenderWindow window, int width, int height, RenderInstance instance);

int Render_IsReady(void);

void Render_DrawScene(const ShapeRect* rects, int rect_count, 
                      const ShapeCircle* circles, int circle_count, 
                      const ShapeLine* lines, int line_count);

void Render_Cleanup(void);

#endif