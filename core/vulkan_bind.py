import ctypes
import os
from manim import Mobject, Square, Circle, Line, Text

def manim_to_screen(x: float, y: float, w=800, h=600):
    scale = 200
    cx = w / 2
    cy = h / 2
    sx = int(cx + x * scale)
    sy = int(cy - y * scale)
    return sx, sy

class VulkanRender:
    def __init__(self, w=800, h=600):
        self.win_w = w
        self.win_h = h
        self.dll = ctypes.CDLL(os.path.abspath("vulkan_core.dll"))
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Init(w, h)

        self.dll.AddRect.argtypes = [ctypes.c_float] * 5 + [ctypes.c_int] * 3
        self.dll.AddCircle.argtypes = [ctypes.c_float] * 3 + [ctypes.c_int] * 3
        self.dll.AddLine.argtypes = [ctypes.c_float] * 4 + [ctypes.c_int] * 2
        self.dll.AddText.argtypes = [ctypes.c_char_p, ctypes.c_float, ctypes.c_float, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

    def sync(self, scene, angle=0.0):
        for mob in scene.mobjects:
            self.draw(mob, angle)

    def draw(self, mob: Mobject, angle=0.0):
        try:
            if isinstance(mob, Square):
                self.draw_square(mob, angle)
            elif isinstance(mob, Circle):
                self.draw_circle(mob)
            elif isinstance(mob, Line):
                self.draw_line(mob)
            elif isinstance(mob, Text):
                self.draw_text(mob)
        except Exception:
            pass

    def draw_square(self, sq: Square, angle):
        cx, cy, _ = sq.get_center()
        half = sq.side_length / 2
        self.dll.AddRect(cx, cy, half, half, angle, 255, 130, 80)

    def draw_circle(self, cr: Circle):
        cx, cy, _ = cr.get_center()
        r = cr.radius
        self.dll.AddCircle(cx, cy, r, 80, 180, 255)

    def draw_line(self, line: Line):
        s = line.get_start()
        e = line.get_end()
        self.dll.AddLine(s[0], s[1], e[0], e[1], 3, 220, 220, 220)

    def draw_text(self, text: Text):
        cx, cy, _ = text.get_center()
        self.dll.AddText(text.text.encode("utf-8"), cx, cy, 22, 255, 255, 255)

    def tick(self):
        return self.dll.Vulkan_Tick() != 0

    def close(self):
        self.dll.Vulkan_Shutdown()