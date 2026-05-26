#include "platform.h"
#include "vulkan_render.h"
#include "shared_types.h"
#include <stdio.h>
#include <string.h>

static HWND g_hwnd = NULL;
static HINSTANCE g_main_hinst = NULL;

static Rect g_rects[MAX_SHAPES];
static int g_rect_count = 0;

static Circle g_circles[MAX_SHAPES];
static int g_circle_count = 0;

static LineObj g_lines[MAX_SHAPES];
static int g_line_count = 0;

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    (void)lpvReserved;
    if (fdwReason == DLL_PROCESS_ATTACH) {
        g_main_hinst = GetModuleHandleW(NULL);
    }
    return TRUE;
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CLOSE:
            DestroyWindow(hwnd);
            return 0;
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
        default:
            return DefWindowProcW(hwnd, msg, wParam, lParam);
    }
}

__declspec(dllexport) int Vulkan_Init(int w, int h) {
    printf("[DEBUG] Vulkan_Init enter w=%d h=%d hinst=%p\n", w, h, (void*)g_main_hinst);
    fflush(stdout);

    WNDCLASSW wc = {
        .lpfnWndProc = WndProc,
        .hInstance = g_main_hinst,
        .lpszClassName = L"ManimVulkanClass",
        .hCursor = LoadCursor(NULL, IDC_ARROW),
        .hbrBackground = (HBRUSH)(COLOR_WINDOW + 1)
    };
    RegisterClassW(&wc);

    RECT rect = { 0, 0, w, h };
    AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);

    g_hwnd = CreateWindowExW(
        0, L"ManimVulkanClass", L"Manim Vulkan",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT,
        rect.right - rect.left, rect.bottom - rect.top,
        NULL, NULL, g_main_hinst, NULL
    );

    if (!g_hwnd) {
        fprintf(stderr, "[FATAL] CreateWindowExW failed\n");
        return 0;
    }
    printf("[DEBUG] Window created hwnd=%p\n", (void*)g_hwnd);
    fflush(stdout);

    Render_Init(g_hwnd, w, h, g_main_hinst);

    if (!Render_IsReady()) {
        fprintf(stderr, "[ERROR] Vulkan renderer failed to initialize\n");
        return 0;
    }

    ShowWindow(g_hwnd, SW_SHOW);
    UpdateWindow(g_hwnd);
    printf("[INFO] Vulkan_Init succeeded (%dx%d)\n", w, h);
    fflush(stdout);
    return 1;
}

__declspec(dllexport) void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b) {
    if (g_rect_count < MAX_SHAPES) {
        g_rects[g_rect_count++] = (Rect){ x, y, hw, hh, rot, r, g, b };
        printf("[C] AddRect #%d: pos=(%.2f,%.2f) size=(%.2f,%.2f) rgba=(%d,%d,%d)\n",
               g_rect_count - 1, x, y, hw, hh, r, g, b);
        fflush(stdout);
    }
}

__declspec(dllexport) void AddCircle(float x, float y, float radius, int r, int g, int b) {
    if (g_circle_count < MAX_SHAPES) {
        g_circles[g_circle_count++] = (Circle){ x, y, radius, r, g, b };
    }
}

__declspec(dllexport) void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b) {
    if (g_line_count < MAX_SHAPES) {
        g_lines[g_line_count++] = (LineObj){ x1, y1, x2, y2, width, r, g, b };
    }
}

__declspec(dllexport) void AddText(const char* text, float x, float y, int size, int r, int g, int b) {
    // TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
}

__declspec(dllexport) void ClearShapes(void) {
    g_rect_count = 0;
    g_circle_count = 0;
    g_line_count = 0;
}

__declspec(dllexport) int Vulkan_Tick(void) {
    MSG msg;
    while (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) return 0;
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    if (g_hwnd && IsWindow(g_hwnd)) {
        printf("[C] Vulkan_Tick: rects=%d circles=%d lines=%d\n",
               g_rect_count, g_circle_count, g_line_count);
        fflush(stdout);

        Render_DrawScene(g_rects, g_rect_count,
                         g_circles, g_circle_count,
                         g_lines, g_line_count);
        return 1;
    }
    return 0;
}

__declspec(dllexport) void Vulkan_Shutdown(void) {
    Render_Cleanup();
    if (g_hwnd && IsWindow(g_hwnd)) {
        DestroyWindow(g_hwnd);
        g_hwnd = NULL;
    }
    UnregisterClassW(L"ManimVulkanClass", g_main_hinst);
}