#include <windows.h>
#include <stdio.h>

static HWND hWnd = NULL;

LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l)
{
    if (m == WM_CLOSE) PostQuitMessage(0);
    return DefWindowProc(h, m, w, l);
}

__declspec(dllexport) int InitManimWindow()
{
    HINSTANCE hInst = GetModuleHandle(NULL);
    WNDCLASSEXA wc = {0};
    wc.cbSize = sizeof(WNDCLASSEXA);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInst;
    wc.lpszClassName = "ManimWin";

    RegisterClassExA(&wc);

    hWnd = CreateWindowExA(
        0, "ManimWin", "Manim C+Python Vulkan Renderer",
        WS_OVERLAPPEDWINDOW, 100, 100, 800, 600,
        NULL, NULL, hInst, NULL
    );

    ShowWindow(hWnd, SW_SHOW);
    UpdateWindow(hWnd);
    return 1;
}

__declspec(dllexport) void ClearWindow(int r, int g, int b)
{
    HDC hdc = GetDC(hWnd);
    RECT rc;
    GetClientRect(hWnd, &rc);
    HBRUSH brush = CreateSolidBrush(RGB(r,g,b));
    FillRect(hdc, &rc, brush);
    DeleteObject(brush);
    ReleaseDC(hWnd, hdc);
}

__declspec(dllexport) void DrawLine(int x1, int y1, int x2, int y2, int r, int g, int b, int w)
{
    HDC hdc = GetDC(hWnd);
    HPEN pen = CreatePen(PS_SOLID, w, RGB(r,g,b));
    SelectObject(hdc, pen);
    MoveToEx(hdc, x1, y1, NULL);
    LineTo(hdc, x2, y2);
    DeleteObject(pen);
    ReleaseDC(hWnd, hdc);
}

__declspec(dllexport) void DrawCircle(int cx, int cy, int rad, int r, int g, int b)
{
    HDC hdc = GetDC(hWnd);
    HPEN pen = CreatePen(PS_SOLID, 2, RGB(r,g,b));
    SelectObject(hdc, pen);
    Ellipse(hdc, cx-rad, cy-rad, cx+rad, cy+rad);
    DeleteObject(pen);
    ReleaseDC(hWnd, hdc);
}

__declspec(dllexport) void DrawRect(int x1, int y1, int x2, int y2, int r, int g, int b, int w)
{
    HDC hdc = GetDC(hWnd);
    HPEN pen = CreatePen(PS_SOLID, w, RGB(r,g,b));
    SelectObject(hdc, pen);
    Rectangle(hdc, x1, y1, x2, y2);
    DeleteObject(pen);
    ReleaseDC(hWnd, hdc);
}

__declspec(dllexport) void RenderText(const char* text, int x, int y, int r, int g, int b, int fontSize)
{
    HDC hdc = GetDC(hWnd);
    SetTextColor(hdc, RGB(r,g,b));
    SetBkMode(hdc, TRANSPARENT);

    HFONT hFont = CreateFontA(
        fontSize, 0,0,0, FW_BOLD, 0,0,0,
        ANSI_CHARSET, OUT_DEFAULT_PRECIS,
        CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY,
        DEFAULT_PITCH | FF_SWISS, "Arial"
    );

    SelectObject(hdc, hFont);
    TextOutA(hdc, x, y, text, lstrlenA(text));
    DeleteObject(hFont);
    ReleaseDC(hWnd, hdc);
}

__declspec(dllexport) int WindowTick()
{
    MSG msg;
    while (PeekMessageA(&msg, NULL, 0,0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
        if (msg.message == WM_QUIT) return 0;
    }
    return 1;
}