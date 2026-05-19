#include "vulkan_bind.h"
#include "vulkan_render.h"
#include <windows.h>

extern "C" {
    HWND CreateMainWindow(int w, int h);
    void ProcessWindowMsg(void);
}

static HWND s_win_handle = nullptr;

extern "C" __declspec(dllexport) int __stdcall SceneInit(int w, int h)
{
    s_win_handle = CreateMainWindow(w, h);
    for(int i=0; i<10; i++) ProcessWindowMsg();
    VK_Init(s_win_handle, w, h);
    return 0;
}

extern "C" __declspec(dllexport) void __stdcall SceneRender(void)
{
    ProcessWindowMsg();
    VK_Draw();
}

extern "C" __declspec(dllexport) void __stdcall SceneExit(void)
{
    VK_Cleanup();
}

extern "C" __declspec(dllexport) void __stdcall SceneSetBgColor(float r, float g, float b)
{
    VK_SetClearColor(r, g, b);
}   