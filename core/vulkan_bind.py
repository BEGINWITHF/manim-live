import ctypes
import os
import math
from manim import (
    Square, Circle, Line, Rectangle, Polygon,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text
)


def manim_to_screen(x, y, w=800, h=600):
    sx = w / 14.0
    sy = h / 8.0
    cx, cy = w / 2.0, h / 2.0
    return float(cx + x * sx), float(cy - y * sy)


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
        self.dll.AddText.restype = None
        self.dll.AddText.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_char_p
        ]
        self.dll.Text_LoadFont.restype = ctypes.c_int
        self.dll.Text_LoadFont.argtypes = [ctypes.c_char_p, ctypes.c_int]

        if self.dll.Vulkan_Init(w, h) != 1:
            raise RuntimeError("Vulkan_Init failed")

        self._load_font()

    def _load_font(self):
        font_paths = []
        if os.name == 'nt':
            windir = os.environ.get('WINDIR', r'C:\Windows')
            font_paths = [
                os.path.join(windir, 'Fonts', 'arial.ttf'),
                os.path.join(windir, 'Fonts', 'segoeui.ttf'),
                os.path.join(windir, 'Fonts', 'tahoma.ttf'),
            ]
        else:
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/TTF/DejaVuSans.ttf',
                '/usr/share/fonts/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf',
            ]
        for fp in font_paths:
            if os.path.exists(fp):
                with open(fp, 'rb') as f:
                    data = f.read()
                buf = ctypes.create_string_buffer(data)
                if self.dll.Text_LoadFont(buf, len(data)):
                    return
        print("[WARNING] No system font found, text will not render")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        for mob in scene.mobjects:
            self._send(mob, angle)

    def _send(self, mob, angle=0.0):
        w, h = self.win_w, self.win_h

        if isinstance(mob, Square):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_x = w / 14.0
            half = mob.side_length / 2.0 * scale_x
            r, g, b = self._color(mob)
            self.dll.AddRect(sx, sy, half, half, angle, r, g, b)

        elif isinstance(mob, Rectangle):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_x = w / 14.0
            scale_y = h / 8.0
            hw = mob.width / 2.0 * scale_x
            hh = mob.height / 2.0 * scale_y
            r, g, b = self._color(mob)
            self.dll.AddRect(sx, sy, hw, hh, angle, r, g, b)

        elif isinstance(mob, Circle):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_y = h / 8.0
            sr = mob.radius * scale_y
            fr, fg, fb = self._color(mob)
            br, bg, bb = self._stroke_color(mob)
            bw = self._stroke_width(mob) * (h / 8.0)
            sp = min(1.0, self.frame_count / 72.0)
            self.dll.AddCircle(sx, sy, sr, fr, fg, fb, br, bg, bb, bw, sp)

        elif isinstance(mob, Ellipse):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            rx = mob.width / 2.0 * (w / 14.0)
            ry = mob.height / 2.0 * (h / 8.0)
            r, g, b = self._color(mob)
            self.dll.AddEllipse(sx, sy, rx, ry, r, g, b)

        elif isinstance(mob, Line):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            sw = max(1, round(self._stroke_width(mob) * (w / 14.0)))
            self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b)

        elif isinstance(mob, Arrow):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            sw = max(1, round(self._stroke_width(mob) * (w / 14.0)))
            self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b)

        elif isinstance(mob, Dot):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_y = h / 8.0
            rad = mob.radius * scale_y if hasattr(mob, 'radius') else 6.0
            r, g, b = self._color(mob)
            self.dll.AddCircle(sx, sy, rad, r, g, b, 0, 0, 0, 0.0, 1.0)

        elif isinstance(mob, DashedLine):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            scale_x = w / 14.0
            sw = max(1, round(self._stroke_width(mob) * scale_x))
            dl = getattr(mob, 'dash_length', 0.1) * scale_x
            gl = getattr(mob, 'gap_length', 0.05) * scale_x
            if dl <= 0: dl = 0.1 * scale_x
            if gl <= 0: gl = 0.05 * scale_x
            self.dll.AddDashedLine(sx1, sy1, sx2, sy2, sw, r, g, b, dl, gl)

        elif isinstance(mob, Arc):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_y = h / 8.0
            rad = mob.radius * scale_y if hasattr(mob, 'radius') else 100.0
            sa = mob.start_angle if hasattr(mob, 'start_angle') else 0
            ang = mob.angle if hasattr(mob, 'angle') else math.pi
            r, g, b = self._stroke_color(mob)
            sw = self._stroke_width(mob) * scale_y
            self.dll.AddArc(sx, sy, rad, sa, ang, r, g, b, sw)

        elif isinstance(mob, Polygon):
            verts = mob.get_vertices()
            self._send_polygon(mob, verts)

        elif isinstance(mob, Point):
            pos = mob.get_location()
            sx, sy = manim_to_screen(pos[0], pos[1], w, h)
            r, g, b = self._color(mob)
            self.dll.AddPoint(sx, sy, r, g, b)

        elif isinstance(mob, Text):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            try:
                c = mob.get_color()
                r, g, b = int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)
            except Exception:
                r, g, b = 255, 255, 255
            if r == 0 and g == 0 and b == 0:
                r, g, b = 255, 255, 255
            fs = mob.font_size if hasattr(mob, 'font_size') else 48
            txt = mob.text if hasattr(mob, 'text') else ""
            self.dll.AddText(sx, sy, r, g, b, float(fs), txt.encode('utf-8'))

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
        result = self.dll.Vulkan_Tick()
        if result == 0:
            return False
        self.win_w = (result >> 16) & 0xFFFF
        self.win_h = result & 0xFFFF
        return True

    def close(self):
        self.dll.Vulkan_Shutdown()
