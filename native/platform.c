#include "platform.h"
#include <math.h>

static HWND     g_hwnd = NULL;
static HDC      g_hdc  = NULL;
static HDC      g_memDC = NULL;
static HBITMAP  g_memBmp = NULL;
static int      g_w = 800, g_h = 600;

static float    g_rx = 0, g_ry = 0, g_hw = 0, g_hh = 0, g_ang = 0;
static int      g_r = 255, g_g = 165, g_b = 0;

LRESULT CALLBACK WndProc(HWND hWnd, UINT msg, WPARAM w, LPARAM l) {
    if (msg == WM_CLOSE) PostQuitMessage(0);
    return DefWindowProcW(hWnd, msg, w, l);
}

void Vulkan_Init(int w, int h) {
    g_w = w;
    g_h = h;
    HINSTANCE inst = GetModuleHandleW(NULL);

    WNDCLASSEXW wc = {0};
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = inst;
    wc.lpszClassName = L"ManimClass";
    wc.hbrBackground = CreateSolidBrush(RGB(12, 18, 35));
    RegisterClassExW(&wc);

    g_hwnd = CreateWindowExW(0, L"ManimClass", L"Manim Live", WS_OVERLAPPEDWINDOW, 100, 100, w, h, NULL, NULL, inst, NULL);
    g_hdc = GetDC(g_hwnd);

    g_memDC = CreateCompatibleDC(g_hdc);
    g_memBmp = CreateCompatibleBitmap(g_hdc, w, h);
    SelectObject(g_memDC, g_memBmp);

    ShowWindow(g_hwnd, SW_SHOW);
    UpdateWindow(g_hwnd);
}

void DrawRect(float cx, float cy, float hw, float hh, float ang, int r, int g, int b) {
    g_rx = cx;
    g_ry = cy;
    g_hw = hw;
    g_hh = hh;
    g_ang = ang;
    g_r = r;
    g_g = g;
    g_b = b;
}

int Vulkan_Tick(void) {
    MSG msg;
    while (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
        if (msg.message == WM_QUIT) return 0;
    }

    RECT rc = {0, 0, g_w, g_h};
    HBRUSH bg_brush = CreateSolidBrush(RGB(12, 18, 35));
    FillRect(g_memDC, &rc, bg_brush);
    DeleteObject(bg_brush);

    float c = cosf(g_ang);
    float s = sinf(g_ang);
    POINT pts[4];

    pts[0].x = g_w/2 + (int)(((g_rx + (-g_hw*c - -g_hh*s)) * 100.0f));
    pts[0].y = g_h/2 - (int)(((g_ry + (-g_hw*s + -g_hh*c)) * 100.0f));
    pts[1].x = g_w/2 + (int)(((g_rx + ( g_hw*c - -g_hh*s)) * 100.0f));
    pts[1].y = g_h/2 - (int)(((g_ry + ( g_hw*s + -g_hh*c)) * 100.0f));
    pts[2].x = g_w/2 + (int)(((g_rx + ( g_hw*c -  g_hh*s)) * 100.0f));
    pts[2].y = g_h/2 - (int)(((g_ry + ( g_hw*s +  g_hh*c)) * 100.0f));
    pts[3].x = g_w/2 + (int)(((g_rx + (-g_hw*c -  g_hh*s)) * 100.0f));
    pts[3].y = g_h/2 - (int)(((g_ry + (-g_hw*s +  g_hh*c)) * 100.0f));

    HBRUSH br = CreateSolidBrush(RGB(g_r, g_g, g_b));
    HPEN pen = CreatePen(PS_SOLID, 2, RGB(255, 255, 255));

    HGDIOBJ old_br = SelectObject(g_memDC, br);
    HGDIOBJ old_pen = SelectObject(g_memDC, pen);

    Polygon(g_memDC, pts, 4);

    SelectObject(g_memDC, old_br);
    SelectObject(g_memDC, old_pen);
    DeleteObject(br);
    DeleteObject(pen);

    BitBlt(g_hdc, 0, 0, g_w, g_h, g_memDC, 0, 0, SRCCOPY);
    return 1;
}

void Vulkan_Shutdown(void) {
    DeleteDC(g_memDC);
    DeleteObject(g_memBmp);
    ReleaseDC(g_hwnd, g_hdc);
    DestroyWindow(g_hwnd);
}