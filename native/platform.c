#include "platform.h"
#include <math.h>
#include <stdlib.h>

static int screenW = 800, screenH = 600;
static HWND hwnd;
static HDC hdc;
static HDC memDC;
static HBITMAP memBmp;

typedef struct {
    float x, y, hw, hh, rot;
    int r, g, b;
} Rect;

static Rect* shapes = NULL;
static int shapeCount = 0;
static int capacity = 0;

static void resizeIfNeeded() {
    if (shapeCount < capacity) return;
    capacity = (capacity == 0) ? 64 : capacity * 2;
    shapes = realloc(shapes, capacity * sizeof(Rect));
}

LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l) {
    if (m == WM_CLOSE) PostQuitMessage(0);
    return DefWindowProcA(h, m, w, l);
}

void Vulkan_Init(int w, int h) {
    screenW = w;
    screenH = h;
    HINSTANCE inst = GetModuleHandleA(NULL);

    WNDCLASSEXA wc = {0};
    wc.cbSize = sizeof(wc);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = inst;
    wc.lpszClassName = "ManimVK";
    wc.hbrBackground = (HBRUSH)(COLOR_BACKGROUND);
    RegisterClassExA(&wc);

    hwnd = CreateWindowExA(0, "ManimVK", "Manim Live", WS_OVERLAPPEDWINDOW,
        100, 100, w, h, NULL, NULL, inst, NULL);
    hdc = GetDC(hwnd);
    memDC = CreateCompatibleDC(hdc);
    memBmp = CreateCompatibleBitmap(hdc, w, h);
    SelectObject(memDC, memBmp);
    ShowWindow(hwnd, 1);
}

void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b) {
    resizeIfNeeded();
    shapes[shapeCount].x = x;
    shapes[shapeCount].y = y;
    shapes[shapeCount].hw = hw;
    shapes[shapeCount].hh = hh;
    shapes[shapeCount].rot = rot;
    shapes[shapeCount].r = r;
    shapes[shapeCount].g = g;
    shapes[shapeCount].b = b;
    shapeCount++;
}

void ClearShapes() {
    shapeCount = 0;
}

int Vulkan_Tick() {
    MSG msg;
    while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    if (!IsWindow(hwnd)) return 0;

    RECT rc = {0, 0, screenW, screenH};
    HBRUSH bg = CreateSolidBrush(RGB(12, 18, 35));
    FillRect(memDC, &rc, bg);
    DeleteObject(bg);

    for (int i = 0; i < shapeCount; i++) {
        Rect s = shapes[i];
        float c = cosf(s.rot);
        float sr = sinf(s.rot);

        POINT pts[4];
        pts[0].x = (long)(screenW/2 + (s.x + (-s.hw*c - -s.hh*sr)) * screenW/2);
        pts[0].y = (long)(screenH/2 + (s.y + (-s.hw*sr + -s.hh*c)) * screenH/2);
        pts[1].x = (long)(screenW/2 + (s.x + ( s.hw*c - -s.hh*sr)) * screenW/2);
        pts[1].y = (long)(screenH/2 + (s.y + ( s.hw*sr + -s.hh*c)) * screenH/2);
        pts[2].x = (long)(screenW/2 + (s.x + ( s.hw*c -  s.hh*sr)) * screenW/2);
        pts[2].y = (long)(screenH/2 + (s.y + ( s.hw*sr +  s.hh*c)) * screenH/2);
        pts[3].x = (long)(screenW/2 + (s.x + (-s.hw*c -  s.hh*sr)) * screenW/2);
        pts[3].y = (long)(screenH/2 + (s.y + (-s.hw*sr +  s.hh*c)) * screenH/2);

        HBRUSH br = CreateSolidBrush(RGB(s.r, s.g, s.b));
        HPEN pen = CreatePen(PS_SOLID, 2, RGB(255,255,255));
        HGDIOBJ oldb = SelectObject(memDC, br);
        HGDIOBJ oldp = SelectObject(memDC, pen);
        Polygon(memDC, pts, 4);
        SelectObject(memDC, oldb);
        SelectObject(memDC, oldp);
        DeleteObject(pen);
        DeleteObject(br);
    }

    BitBlt(hdc, 0,0,screenW,screenH, memDC,0,0,SRCCOPY);
    ClearShapes();
    return 1;
}

void Vulkan_Shutdown() {
    if (shapes) free(shapes);
    DeleteDC(memDC);
    DeleteObject(memBmp);
    ReleaseDC(hwnd, hdc);
    DestroyWindow(hwnd);
}