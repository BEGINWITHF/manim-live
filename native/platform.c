#include "platform.h"
#include "vulkan_render.h"
#include "vulkan_core.h"
#include "shared_types.h"
#include <stdio.h>
#include <string.h>
#include <windows.h>

static Rect g_rects[MAX_SHAPES];
static int g_rect_count = 0;
static Circle g_circles[MAX_SHAPES];
static int g_circle_count = 0;
static LineObj g_lines[MAX_SHAPES];
static int g_line_count = 0;
static EllipseObj g_ellipses[MAX_SHAPES];
static int g_ellipse_count = 0;
static PolygonObj g_polygons[MAX_SHAPES];
static int g_polygon_count = 0;
static DashedLineObj g_dashed_lines[MAX_SHAPES];
static int g_dashed_line_count = 0;
static ArcObj g_arcs[MAX_SHAPES];
static int g_arc_count = 0;
static PointObj g_points[MAX_SHAPES];
static int g_point_count = 0;

static double g_aspect_ratio = 16.0 / 9.0;
static int g_min_width = 320;
static int g_min_height = 240;

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    (void)lpvReserved;
    (void)hinstDLL;
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
        case WM_SIZE:
            if (wParam != SIZE_MINIMIZED && g_is_ready) {
                g_framebuffer_resized = true;
            }
            return DefWindowProcW(hwnd, msg, wParam, lParam);
        case WM_SIZING: {
            RECT *r = (RECT *)lParam;
            int w = r->right - r->left;
            int h = r->bottom - r->top;
            int border = (int)(GetSystemMetrics(SM_CXEDGE) * 2);
            int caption = (int)(GetSystemMetrics(SM_CYCAPTION) + GetSystemMetrics(SM_CYEDGE) * 2);
            int inner_w = w - border;
            int inner_h = h - caption;
            if (inner_w <= 0 || inner_h <= 0) return 0;
            int d = wParam;
            if (d == WMSZ_LEFT || d == WMSZ_RIGHT) {
                int new_h = (int)(inner_w / g_aspect_ratio + 0.5);
                if (d == WMSZ_LEFT) r->top = r->bottom - new_h - caption;
                else r->bottom = r->top + new_h + caption;
            } else if (d == WMSZ_TOP || d == WMSZ_BOTTOM) {
                int new_w = (int)(inner_h * g_aspect_ratio + 0.5);
                if (d == WMSZ_TOP) r->left = r->right - new_w - border;
                else r->right = r->left + new_w + border;
            } else {
                int new_h = (int)(inner_w / g_aspect_ratio + 0.5);
                r->bottom = r->top + new_h + caption;
            }
            return 0;
        }
        case WM_GETMINMAXINFO: {
            MINMAXINFO *mmi = (MINMAXINFO *)lParam;
            int border = (int)(GetSystemMetrics(SM_CXEDGE) * 2);
            int caption = (int)(GetSystemMetrics(SM_CYCAPTION) + GetSystemMetrics(SM_CYEDGE) * 2);
            mmi->ptMinTrackSize.x = g_min_width + border;
            mmi->ptMinTrackSize.y = (LONG)(g_min_width / g_aspect_ratio + 0.5) + caption;
            return 0;
        }
        default:
            return DefWindowProcW(hwnd, msg, wParam, lParam);
    }
}

__declspec(dllexport) int Vulkan_Init(int w, int h) {
    SetProcessDPIAware();
    g_hinst = GetModuleHandleW(NULL);
    g_aspect_ratio = (double)w / (double)h;
    g_min_width = w / 4;
    if (g_min_width < 320) g_min_width = 320;
    WNDCLASSW wc = {
        .lpfnWndProc = WndProc,
        .hInstance = g_hinst,
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
        NULL, NULL, g_hinst, NULL
    );

    if (!g_hwnd) {
        fprintf(stderr, "[FATAL] CreateWindowExW failed\n");
        return 0;
    }

    Render_Init(g_hwnd, w, h, g_hinst);

    if (!Render_IsReady()) {
        fprintf(stderr, "[ERROR] Vulkan renderer failed to initialize\n");
        return 0;
    }

    ShowWindow(g_hwnd, SW_SHOW);
    UpdateWindow(g_hwnd);
    return 1;
}

__declspec(dllexport) void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b) {
    if (g_rect_count < MAX_SHAPES) {
        g_rects[g_rect_count++] = (Rect){ x, y, hw, hh, rot, r, g, b };
    }
}

__declspec(dllexport) void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress) {
    if (g_circle_count < MAX_SHAPES) {
        g_circles[g_circle_count++] = (Circle){ x, y, radius, r, g, b, border_r, border_g, border_b, border_width, stroke_progress };
    }
}

__declspec(dllexport) void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b) {
    if (g_line_count < MAX_SHAPES) {
        g_lines[g_line_count++] = (LineObj){ x1, y1, x2, y2, width, r, g, b };
    }
}

__declspec(dllexport) void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b) {
    if (g_ellipse_count < MAX_SHAPES) {
        g_ellipses[g_ellipse_count++] = (EllipseObj){ x, y, rx, ry, r, g, b };
    }
}

__declspec(dllexport) void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts) {
    if (g_polygon_count < MAX_SHAPES && vert_count <= MAX_POLYGON_VERTS) {
        PolygonObj* p = &g_polygons[g_polygon_count++];
        p->x = x; p->y = y;
        p->r = r; p->g = g; p->b = b;
        p->border_r = border_r; p->border_g = border_g; p->border_b = border_b;
        p->border_width = border_width;
        p->vert_count = vert_count;
        memcpy(p->verts, verts, sizeof(float) * vert_count * 2);
    }
}

__declspec(dllexport) void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length) {
    if (g_dashed_line_count < MAX_SHAPES) {
        g_dashed_lines[g_dashed_line_count++] = (DashedLineObj){ x1, y1, x2, y2, width, r, g, b, dash_length, gap_length };
    }
}

__declspec(dllexport) void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width) {
    if (g_arc_count < MAX_SHAPES) {
        g_arcs[g_arc_count++] = (ArcObj){ x, y, radius, start_angle, angle, r, g, b, stroke_width };
    }
}

__declspec(dllexport) void AddPoint(float x, float y, int r, int g, int b) {
    if (g_point_count < MAX_SHAPES) {
        g_points[g_point_count++] = (PointObj){ x, y, r, g, b };
    }
}

__declspec(dllexport) void ClearShapes(void) {
    g_rect_count = 0;
    g_circle_count = 0;
    g_line_count = 0;
    g_ellipse_count = 0;
    g_polygon_count = 0;
    g_dashed_line_count = 0;
    g_arc_count = 0;
    g_point_count = 0;
}

__declspec(dllexport) int Vulkan_Tick(void) {
    MSG msg;
    while (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) return 0;
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    if (g_hwnd && IsWindow(g_hwnd)) {
        if (g_framebuffer_resized) {
            g_framebuffer_resized = false;
            RecreateSwapchain();
        }
        Render_DrawScene(
            g_rects, g_rect_count,
            g_circles, g_circle_count,
            g_lines, g_line_count,
            g_ellipses, g_ellipse_count,
            g_polygons, g_polygon_count,
            g_dashed_lines, g_dashed_line_count,
            g_arcs, g_arc_count,
            g_points, g_point_count
        );
        extern uint32_t g_vertex_count;
        Render_DrawFrame(g_vertex_count);
        RECT rc;
        GetClientRect(g_hwnd, &rc);
        int cw = rc.right - rc.left;
        int ch = rc.bottom - rc.top;
        return (cw << 16) | (ch & 0xFFFF);
    }
    return 0;
}

__declspec(dllexport) void Vulkan_Shutdown(void) {
    Render_Cleanup();
    if (g_hwnd && IsWindow(g_hwnd)) {
        DestroyWindow(g_hwnd);
        g_hwnd = NULL;
    }
    UnregisterClassW(L"ManimVulkanClass", g_hinst);
}
