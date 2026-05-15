import ctypes
import os

class VulkanRender:
    def __init__(self, w=800, h=600):
        self.dll = ctypes.CDLL(os.path.abspath("vulkan_core.dll"))
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Init(w, h)

        self.dll.AddRect.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]

    def add_rect(self, x, y, hw, hh, rot, r, g, b):
        self.dll.AddRect(x, y, hw, hh, rot, r, g, b)

    def tick(self):
        return self.dll.Vulkan_Tick() != 0

    def close(self):
        self.dll.Vulkan_Shutdown()