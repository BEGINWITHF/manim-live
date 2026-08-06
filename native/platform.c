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
static TextObj g_texts[MAX_SHAPES];
static int g_text_count = 0;

#define CMD_RECT 0
#define CMD_CIRCLE 1
#define CMD_LINE 2
#define CMD_ELLIPSE 3
#define CMD_POLYGON 4
#define CMD_DASHED_LINE 5
#define CMD_ARC 6
#define CMD_POINT 7
#define CMD_TEXT 8

#define MAX_DRAW_CMDS 16384
static DrawCmd g_draw_cmds[MAX_DRAW_CMDS];
static int g_draw_cmd_count = 0;

static double g_aspect_ratio = 16.0 / 9.0;
static int g_min_width = 320;

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
        .hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH)
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

__declspec(dllexport) void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_rect_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_rects[g_rect_count] = (Rect){ x, y, hw, hh, rot, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_RECT, g_rect_count };
        g_rect_count++;
    }
}

__declspec(dllexport) void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_circle_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_circles[g_circle_count] = (Circle){ x, y, radius, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_CIRCLE, g_circle_count };
        g_circle_count++;
    }
}

__declspec(dllexport) void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float alpha) {
    if (g_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_lines[g_line_count] = (LineObj){ x1, y1, x2, y2, width, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_LINE, g_line_count };
        g_line_count++;
    }
}

__declspec(dllexport) void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_ellipse_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_ellipses[g_ellipse_count] = (EllipseObj){ x, y, rx, ry, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ELLIPSE, g_ellipse_count };
        g_ellipse_count++;
    }
}

__declspec(dllexport) void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts, float stroke_progress, float alpha, int close_path) {
    if (g_polygon_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS && vert_count <= MAX_POLYGON_VERTS) {
        PolygonObj* p = &g_polygons[g_polygon_count];
        p->x = x; p->y = y;
        p->r = r; p->g = g; p->b = b;
        p->border_r = border_r; p->border_g = border_g; p->border_b = border_b;
        p->border_width = border_width;
        p->vert_count = vert_count;
        p->stroke_progress = stroke_progress;
        p->alpha = alpha;
        p->close_path = close_path;
        memcpy(p->verts, verts, sizeof(float) * vert_count * 2);
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_POLYGON, g_polygon_count };
        g_polygon_count++;
    }
}

__declspec(dllexport) void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length, float alpha) {
    if (g_dashed_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_dashed_lines[g_dashed_line_count] = (DashedLineObj){ x1, y1, x2, y2, width, r, g, b, dash_length, gap_length, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_DASHED_LINE, g_dashed_line_count };
        g_dashed_line_count++;
    }
}

__declspec(dllexport) void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width, float alpha) {
    if (g_arc_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_arcs[g_arc_count] = (ArcObj){ x, y, radius, start_angle, angle, r, g, b, stroke_width, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ARC, g_arc_count };
        g_arc_count++;
    }
}

__declspec(dllexport) void AddPoint(float x, float y, int r, int g, int b, float alpha) {
    if (g_point_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_points[g_point_count] = (PointObj){ x, y, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_POINT, g_point_count };
        g_point_count++;
    }
}

__declspec(dllexport) void AddText(float x, float y, int r, int g, int b, float font_size, float opacity, const char* text, float alpha) {
    if (g_text_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS && text) {
        TextObj* t = &g_texts[g_text_count];
        t->x = x; t->y = y;
        t->r = r; t->g = g; t->b = b;
        t->font_size = font_size;
        t->opacity = opacity;
        t->alpha = alpha;
        int len = 0;
        while (text[len] && len < MAX_TEXT_LEN - 1) {
            t->text[len] = text[len];
            len++;
        }
        t->text[len] = '\0';
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_TEXT, g_text_count };
        g_text_count++;
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
    g_text_count = 0;
    g_draw_cmd_count = 0;
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
            g_points, g_point_count,
            g_texts, g_text_count,
            g_draw_cmds, g_draw_cmd_count
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

__declspec(dllexport) int SaveScreenshot(const char *path) {
    if (!g_hwnd || !IsWindow(g_hwnd)) return 0;
    HDC hdcWindow = GetDC(g_hwnd);
    if (!hdcWindow) return 0;
    RECT rc;
    GetClientRect(g_hwnd, &rc);
    int w = rc.right - rc.left;
    int h = rc.bottom - rc.top;
    if (w <= 0 || h <= 0) { ReleaseDC(g_hwnd, hdcWindow); return 0; }
    HDC hdcMem = CreateCompatibleDC(hdcWindow);
    HBITMAP hBitmap = CreateCompatibleBitmap(hdcWindow, w, h);
    SelectObject(hdcMem, hBitmap);
    BitBlt(hdcMem, 0, 0, w, h, hdcWindow, 0, 0, SRCCOPY);
    BITMAPINFOHEADER bi = {0};
    bi.biSize = sizeof(BITMAPINFOHEADER);
    bi.biWidth = w;
    bi.biHeight = -h;
    bi.biPlanes = 1;
    bi.biBitCount = 24;
    bi.biCompression = BI_RGB;
    int rowBytes = ((w * 3 + 3) & ~3);
    int imgSize = rowBytes * h;
    char *buf = (char *)malloc(imgSize);
    if (!buf) { DeleteObject(hBitmap); DeleteDC(hdcMem); ReleaseDC(g_hwnd, hdcWindow); return 0; }
    GetDIBits(hdcMem, hBitmap, 0, h, buf, (BITMAPINFO *)&bi, DIB_RGB_COLORS);
    BITMAPFILEHEADER bfh = {0};
    bfh.bfType = 0x4D42;
    bfh.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bfh.bfSize = bfh.bfOffBits + imgSize;
    FILE *fp = fopen(path, "wb");
    if (!fp) { free(buf); DeleteObject(hBitmap); DeleteDC(hdcMem); ReleaseDC(g_hwnd, hdcWindow); return 0; }
    fwrite(&bfh, sizeof(bfh), 1, fp);
    fwrite(&bi, sizeof(bi), 1, fp);
    fwrite(buf, imgSize, 1, fp);
    fclose(fp);
    free(buf);
    DeleteObject(hBitmap);
    DeleteDC(hdcMem);
    ReleaseDC(g_hwnd, hdcWindow);
    return 1;
}
