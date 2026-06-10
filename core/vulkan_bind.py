import ctypes
import os
from manim import Mobject, Square, Circle, Line

def manim_to_screen(x, y, w=800, h=600, scale=200):
    cx, cy = w / 2.0, h / 2.0
    sx = cx + x * scale
    sy = cy - y * scale
    return float(sx), float(sy)

class VulkanRender:
    def __init__(self, w=800, h=600):
        self.win_w = w
        self.win_h = h
        self.frame_count = 0
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dll"))

        if not os.path.exists(dll_path):

            dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dll"))
        if not os.path.exists(dll_path):

            raise FileNotFoundError(f"找不到 vulkan_core.dll")

        self.dll = ctypes.CDLL(dll_path)
        self.dll.Vulkan_Init.restype = ctypes.c_int
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Tick.restype = ctypes.c_int
        self.dll.Vulkan_Tick.argtypes = []
        self.dll.Vulkan_Shutdown.restype = None
        self.dll.Vulkan_Shutdown.argtypes = []
        self.dll.ClearShapes.restype = None
        self.dll.ClearShapes.argtypes = []
        self.dll.AddRect.restype = None
        self.dll.AddRect.argtypes = [

            ctypes.c_float, ctypes.c_float, ctypes.c_float,

            ctypes.c_float, ctypes.c_float,

            ctypes.c_int, ctypes.c_int, ctypes.c_int

        ]
        self.dll.AddCircle.restype = None
        self.dll.AddCircle.argtypes = [

            ctypes.c_float, ctypes.c_float, ctypes.c_float,

            ctypes.c_int, ctypes.c_int, ctypes.c_int,

            ctypes.c_int, ctypes.c_int, ctypes.c_int,

            ctypes.c_float,

            ctypes.c_float

        ]
        self.dll.AddLine.restype = None
        self.dll.AddLine.argtypes = [

            ctypes.c_float, ctypes.c_float,

            ctypes.c_float, ctypes.c_float,

            ctypes.c_int, ctypes.c_int,

            ctypes.c_int, ctypes.c_int

        ]
        if self.dll.Vulkan_Init(w, h) != 1:

            raise RuntimeError("Vulkan_Init 失败")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        count = 0
        for mob in scene.mobjects:

            self.draw(mob, angle)

            count += 1
            
    def draw(self, mob, angle=0.0):

        if isinstance(mob, Square):

            self._draw_square(mob, angle)

        elif isinstance(mob, Circle):

            self._draw_circle(mob)

        elif isinstance(mob, Line):

            self._draw_line(mob)

    def _get_color_rgb(self, mob):
        try:
            rgbas = mob.get_fill_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                return int(r * 255), int(g * 255), int(b * 255)
        except Exception:
            pass
        try:
            rgbas = mob.get_stroke_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                return int(r * 255), int(g * 255), int(b * 255)
        except Exception:
            pass
        return 255, 255, 255

    def _draw_square(self, sq, angle):
        cx, cy, _ = sq.get_center()
        half = sq.side_length / 2.0
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sh = half * 200.0
        r, g, b = self._get_color_rgb(sq)
        self.dll.AddRect(sx, sy, sh, sh, angle, r, g, b)
        
    def _draw_circle(self, cr):
        cx, cy, _ = cr.get_center()
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sr = cr.radius * 200.0
        fill_r, fill_g, fill_b = self._get_color_rgb(cr)
        border_width = 0.0
        border_r, border_g, border_b = 0, 0, 0
        try:
            stroke_widths = cr.get_stroke_width()
            if isinstance(stroke_widths, (int, float)):
                border_width = float(stroke_widths)
            elif hasattr(stroke_widths, '__len__') and len(stroke_widths) > 0:
                border_width = float(stroke_widths[0])
            stroke_rgbas = cr.get_stroke_rgbas()
            if len(stroke_rgbas) > 0:
                border_r = int(stroke_rgbas[0][0] * 255)
                border_g = int(stroke_rgbas[0][1] * 255)
                border_b = int(stroke_rgbas[0][2] * 255)
        except Exception:
            pass

        animation_duration = 72
        stroke_progress = min(1.0, self.frame_count / animation_duration)
        self.dll.AddCircle(
            sx, sy, sr,
            fill_r, fill_g, fill_b,
            border_r, border_g, border_b,
            border_width,
            stroke_progress
        )

    def _draw_line(self, line):
        s = line.get_start()
        e = line.get_end()
        sx1, sy1 = manim_to_screen(s[0], s[1], self.win_w, self.win_h)
        sx2, sy2 = manim_to_screen(e[0], e[1], self.win_w, self.win_h)
        try:
            rgbas = line.get_stroke_rgbas()
            r, g, b = int(rgbas[0][0]*255), int(rgbas[0][1]*255), int(rgbas[0][2]*255)
        except:
            r, g, b = 255, 255, 255

        self.dll.AddLine(sx1, sy1, sx2, sy2, 3, r, g, b)
        
    def tick(self):
        self.frame_count += 1
        return self.dll.Vulkan_Tick() != 0

    def close(self):
        self.dll.Vulkan_Shutdown()