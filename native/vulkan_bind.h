#ifndef VULKAN_BIND_H
#define VULKAN_BIND_H

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) int __stdcall SceneInit(int w,int h);
__declspec(dllexport) void __stdcall SceneRender(void);
__declspec(dllexport) void __stdcall SceneExit(void);
__declspec(dllexport) void __stdcall SceneSetBgColor(float r,float g,float b);

#ifdef __cplusplus
}
#endif

#endif