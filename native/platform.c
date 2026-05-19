#include <windows.h>

LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l) {
    if (m == WM_DESTROY) PostQuitMessage(0);
    return DefWindowProc(h,m,w,l);
}

__declspec(dllexport) HWND CreateMainWindow(int w, int h) {
    WNDCLASSEX wc = {0};
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = "SafeWindow";
    wc.hbrBackground = CreateSolidBrush(RGB(40, 80, 160));

    RegisterClassEx(&wc);

    HWND hwnd = CreateWindowExA(0,
        "SafeWindow",
        "Vulkan Window",
        WS_OVERLAPPEDWINDOW,
        100, 100, w, h,
        NULL, NULL,
        wc.hInstance, NULL
    );

    ShowWindow(hwnd, 1);
    UpdateWindow(hwnd);
    return hwnd;
}

__declspec(dllexport) void ProcessWindowMsg(void) {
    MSG msg;
    while (PeekMessageA(&msg, NULL, 0,0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
}