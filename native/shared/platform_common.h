#ifndef PLATFORM_COMMON_H
#define PLATFORM_COMMON_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Common shape definitions
#define MAX_SHAPES 1024

typedef struct {
    float x, y, hw, hh, rot;
    int r, g, b;
} ShapeRect;

typedef struct {
    float x, y, radius;
    int r, g, b;
} ShapeCircle;

typedef struct {
    float x1, y1, x2, y2;
    int width;
    int r, g, b;
} ShapeLine;

// Platform-agnostic API
#ifdef _WIN32
    #define PLATFORM_EXPORT __declspec(dllexport)
#elif defined(__APPLE__)
    #define PLATFORM_EXPORT __attribute__((visibility("default")))
#else
    #define PLATFORM_EXPORT
#endif

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
