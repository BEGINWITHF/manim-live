import ctypes
import os
from manim import *

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

    def color(self, c):
        try:
            r, g, b = c.to_rgb()
            return int(r * 255), int(g * 255), int(b * 255)
        except:
            return 255, 255, 255

    def draw(self, mob, angle=0):
        r, g, b = self.color(mob.get_color())

        if isinstance(mob, Square):
            cx, cy, _ = mob.get_center()
            hw = mob.width / 2
            hh = mob.height / 2
            nx, ny = manim_to_ndc(cx, cy)
            self.add_rect(nx, ny, hw/4, hh/3, angle, r, g, b)

        elif isinstance(mob, Circle):
            cx, cy, _ = mob.get_center()
            rad = mob.width / 2
            nx, ny = manim_to_ndc(cx, cy)
            self.add_circle(nx, ny, rad/4, r, g, b)

        elif isinstance(mob, Arrow):
            # 强制走箭头逻辑，不进Line分支
            s = mob.get_start()
            e = mob.get_end()
            # 放大坐标，保证箭头头可见
            sx = s[0] * 0.5
            sy = s[1] * 0.5
            ex = e[0] * 0.5
            ey = e[1] * 0.5
            sx, sy = manim_to_ndc(sx, sy)
            ex, ey = manim_to_ndc(ex, ey)
            self.add_arrow(sx, sy, ex, ey, int(mob.stroke_width), r, g, b)

        elif isinstance(mob, Line):
            s = mob.get_start()
            e = mob.get_end()
            sx, sy = manim_to_ndc(s[0], s[1])
            ex, ey = manim_to_ndc(e[0], e[1])
            self.add_line(sx, sy, ex, ey, int(mob.stroke_width), r, g, b)

    def sync(self, scene, angle=0):
        for obj in scene.mobjects:
            self.draw(obj, angle)

    def tick(self):
        return self.dll.Vulkan_Tick() != 0

    def shutdown(self):
        self.dll.Vulkan_Shutdown()