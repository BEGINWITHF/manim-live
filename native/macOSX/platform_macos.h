#ifndef PLATFORM_MACOS_H
#define PLATFORM_MACOS_H

#include "platform_common.h"

#ifdef __cplusplus
extern "C" {
#endif

// macOS-specific implementations
PLATFORM_EXPORT int Vulkan_Init(int w, int h);
PLATFORM_EXPORT int Vulkan_Tick(void);
PLATFORM_EXPORT void Vulkan_Shutdown(void);

PLATFORM_EXPORT void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b);
PLATFORM_EXPORT void AddCircle(float x, float y, float radius, int r, int g, int b);
PLATFORM_EXPORT void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b);
PLATFORM_EXPORT void AddText(const char* text, float x, float y, int size, int r, int g, int b);

PLATFORM_EXPORT void ClearShapes(void);

#ifdef __cplusplus
}
#endif

#endif
