import ctypes
import os

class VulkanRender:
    def __init__(self, w=800, h=600):
        self.dll = ctypes.CDLL(os.path.abspath("vulkan_core.dll"))
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Init(w, h)

        self.dll.DrawRect.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]

    def tick(self):
        return self.dll.Vulkan_Tick() != 0

    def draw_rect(self, cx, cy, hw, hh, angle, r, g, b):
        self.dll.DrawRect(cx, cy, hw, hh, angle, r, g, b)

    def close(self):
        self.dll.Vulkan_Shutdown()