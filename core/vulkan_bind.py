import ctypes
import os

def manim_to_ndc(x: float, y: float):
    return x / 4.0, -y / 3.0

class VulkanRender:
    def __init__(self, w=800, h=600):
        self.dll = ctypes.CDLL(os.path.abspath("vulkan_core.dll"))
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Init(w, h)

        self.dll.AddRect.argtypes = [ctypes.c_float]*5 + [ctypes.c_int]*3
        self.dll.AddCircle.argtypes = [ctypes.c_float]*3 + [ctypes.c_int]*3
        self.dll.AddLine.argtypes = [ctypes.c_float]*4 + [ctypes.c_int]*4
        self.dll.AddArrow.argtypes = [ctypes.c_float]*4 + [ctypes.c_int]*4
        self.dll.AddText.argtypes = [ctypes.c_char_p, ctypes.c_float, ctypes.c_float, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

    def add_rect(self, x, y, hw, hh, rot, r, g, b):
        self.dll.AddRect(x, y, hw, hh, rot, r, g, b)
    def add_circle(self, x, y, radius, r, g, b):
        self.dll.AddCircle(x, y, radius, r, g, b)
    def add_line(self, x1, y1, x2, y2, width, r, g, b):
        self.dll.AddLine(x1, y1, x2, y2, width, r, g, b)
    def add_arrow(self, x1, y1, x2, y2, width, r, g, b):
        self.dll.AddArrow(x1, y1, x2, y2, width, r, g, b)
    def add_text(self, text, x, y, size, r, g, b):
        self.dll.AddText(text.encode('utf-8'), x, y, size, r, g, b)

    def tick(self):
        return self.dll.Vulkan_Tick() != 0
    def close(self):
        self.dll.Vulkan_Shutdown()