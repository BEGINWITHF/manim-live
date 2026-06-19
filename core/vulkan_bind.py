import ctypes
import os
import math
from manim import (
    Mobject, Square, Circle, Line, Rectangle, Polygon,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point
)


def manim_to_screen(x, y, w=800, h=600, scale=200):
    cx, cy = w / 2.0, h / 2.0
    return float(cx + x * scale), float(cy - y * scale)


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
            raise FileNotFoundError("vulkan_core.dll not found")

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
            ctypes.c_float, ctypes.c_float
        ]
        self.dll.AddLine.restype = None
        self.dll.AddLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int
        ]
        self.dll.AddEllipse.restype = None
        self.dll.AddEllipse.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        self.dll.AddPolygon.restype = None
        self.dll.AddPolygon.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float)
        ]
        self.dll.AddDashedLine.restype = None
        self.dll.AddDashedLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float
        ]
        self.dll.AddArc.restype = None
        self.dll.AddArc.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float
        ]
        self.dll.AddPoint.restype = None
        self.dll.AddPoint.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]

        if self.dll.Vulkan_Init(w, h) != 1:
            raise RuntimeError("Vulkan_Init failed")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        for mob in scene.mobjects:
            self._send(mob, angle)

    def _send(self, mob, angle=0.0):
        w, h = self.win_w, self.win_h

        if isinstance(mob, Square):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            half = mob.side_length / 2.0 * 200
            r, g, b = self._color(mob)
            self.dll.AddRect(sx, sy, half, half, angle, r, g, b)

        elif isinstance(mob, Rectangle):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            hw = mob.width / 2.0 * 200
            hh = mob.height / 2.0 * 200
            r, g, b = self._color(mob)
            self.dll.AddRect(sx, sy, hw, hh, angle, r, g, b)

        elif isinstance(mob, Circle):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            sr = mob.radius * 200
            fr, fg, fb = self._color(mob)
            br, bg, bb = self._stroke_color(mob)
            bw = self._stroke_width(mob)
            sp = min(1.0, self.frame_count / 72.0)
            self.dll.AddCircle(sx, sy, sr, fr, fg, fb, br, bg, bb, bw, sp)

        elif isinstance(mob, Ellipse):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            rx = mob.width / 2.0 * 200
            ry = mob.height / 2.0 * 200
            r, g, b = self._color(mob)
            self.dll.AddEllipse(sx, sy, rx, ry, r, g, b)

        elif isinstance(mob, Line):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            sw = max(1, int(self._stroke_width(mob)))
            self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b)

        elif isinstance(mob, Arrow):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            sw = max(1, int(self._stroke_width(mob)))
            self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b)

        elif isinstance(mob, Dot):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            rad = mob.radius * 200 if hasattr(mob, 'radius') else 6.0
            r, g, b = self._color(mob)
            self.dll.AddCircle(sx, sy, rad, r, g, b, 0, 0, 0, 0.0, 1.0)

        elif isinstance(mob, DashedLine):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            sw = max(1, int(self._stroke_width(mob)))
            dl = getattr(mob, 'dash_length', 0.1)
            gl = getattr(mob, 'gap_length', 0.05)
            if dl <= 0: dl = 0.1
            if gl <= 0: gl = 0.05
            self.dll.AddDashedLine(sx1, sy1, sx2, sy2, sw, r, g, b, dl, gl)

        elif isinstance(mob, Arc):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            rad = mob.radius * 200 if hasattr(mob, 'radius') else 100.0
            sa = mob.start_angle if hasattr(mob, 'start_angle') else 0
            ang = mob.angle if hasattr(mob, 'angle') else math.pi
            r, g, b = self._stroke_color(mob)
            sw = self._stroke_width(mob)
            self.dll.AddArc(sx, sy, rad, sa, ang, r, g, b, sw)

        elif isinstance(mob, Polygon):
            verts = mob.get_vertices()
            self._send_polygon(mob, verts)

        elif isinstance(mob, Point):
            pos = mob.get_location()
            sx, sy = manim_to_screen(pos[0], pos[1], w, h)
            r, g, b = self._color(mob)
            self.dll.AddPoint(sx, sy, r, g, b)

    def _send_polygon(self, mob, verts):
        w, h = self.win_w, self.win_h
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        fr, fg, fb = self._color(mob)
        br, bg, bb = self._stroke_color(mob)
        bw = self._stroke_width(mob)

        flat = []
        for v in verts:
            vx, vy = manim_to_screen(v[0], v[1], w, h)
            flat.append(vx)
            flat.append(vy)

        arr = (ctypes.c_float * len(flat))(*flat)
        self.dll.AddPolygon(
            sx, sy, fr, fg, fb, br, bg, bb, bw,
            len(verts), arr
        )

    def _color(self, mob):
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

    def _stroke_color(self, mob):
        try:
            rgbas = mob.get_stroke_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                return int(r * 255), int(g * 255), int(b * 255)
        except Exception:
            pass
        return 255, 255, 255

    def _stroke_width(self, mob):
        try:
            sw = mob.get_stroke_width()
            if isinstance(sw, (int, float)):
                return float(sw)
            elif hasattr(sw, '__len__') and len(sw) > 0:
                return float(sw[0])
        except Exception:
            pass
        return 0.0

    def tick(self):
        self.frame_count += 1
        return self.dll.Vulkan_Tick() != 0

    def close(self):
        self.dll.Vulkan_Shutdown()
