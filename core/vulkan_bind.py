import ctypes
import os
import math
from manim import (
    Mobject, Square, Circle, Line, Rectangle, Polygon,
    Arrow, Dot, DashedLine, RegularPolygon, Triangle,
    Arc, Ellipse, Point
)


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
            raise FileNotFoundError(f"vulkan_core.dll not found")

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

        if self.dll.Vulkan_Init(w, h) != 1:
            raise RuntimeError("Vulkan_Init failed")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        for mob in scene.mobjects:
            self.draw(mob, angle)

    def draw(self, mob, angle=0.0):
        if isinstance(mob, Square):
            self._draw_square(mob, angle)
        elif isinstance(mob, Rectangle):
            self._draw_rectangle(mob, angle)
        elif isinstance(mob, Circle):
            self._draw_circle(mob)
        elif isinstance(mob, Ellipse):
            self._draw_ellipse(mob)
        elif isinstance(mob, Line):
            self._draw_line(mob)
        elif isinstance(mob, Arrow):
            self._draw_arrow(mob)
        elif isinstance(mob, Dot):
            self._draw_dot(mob)
        elif isinstance(mob, Polygon):
            self._draw_polygon(mob)
        elif isinstance(mob, RegularPolygon):
            self._draw_polygon(mob)
        elif isinstance(mob, Triangle):
            self._draw_polygon(mob)
        elif isinstance(mob, DashedLine):
            self._draw_dashed_line(mob)
        elif isinstance(mob, Arc):
            self._draw_arc(mob)
        elif isinstance(mob, Point):
            self._draw_point(mob)
        else:
            self._draw_generic(mob)

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

    def _get_stroke_color_rgb(self, mob):
        try:
            rgbas = mob.get_stroke_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                return int(r * 255), int(g * 255), int(b * 255)
        except Exception:
            pass
        return 255, 255, 255

    def _get_stroke_width(self, mob):
        try:
            sw = mob.get_stroke_width()
            if isinstance(sw, (int, float)):
                return float(sw)
            elif hasattr(sw, '__len__') and len(sw) > 0:
                return float(sw[0])
        except Exception:
            pass
        return 0.0

    def _draw_square(self, sq, angle):
        cx, cy, _ = sq.get_center()
        half = sq.side_length / 2.0
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sh = half * 200.0
        r, g, b = self._get_color_rgb(sq)
        self.dll.AddRect(sx, sy, sh, sh, angle, r, g, b)

    def _draw_rectangle(self, rect, angle):
        cx, cy, _ = rect.get_center()
        hw = rect.width / 2.0
        hh = rect.height / 2.0
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        shw = hw * 200.0
        shh = hh * 200.0
        r, g, b = self._get_color_rgb(rect)
        self.dll.AddRect(sx, sy, shw, shh, angle, r, g, b)

    def _draw_circle(self, cr):
        cx, cy, _ = cr.get_center()
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sr = cr.radius * 200.0
        fill_r, fill_g, fill_b = self._get_color_rgb(cr)
        border_width = self._get_stroke_width(cr)
        border_r, border_g, border_b = self._get_stroke_color_rgb(cr)

        animation_duration = 72
        stroke_progress = min(1.0, self.frame_count / animation_duration)
        self.dll.AddCircle(
            sx, sy, sr,
            fill_r, fill_g, fill_b,
            border_r, border_g, border_b,
            border_width, stroke_progress
        )

    def _draw_ellipse(self, ell):
        cx, cy, _ = ell.get_center()
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        a = ell.width / 2.0 * 200.0
        b = ell.height / 2.0 * 200.0
        r, g, b_val = self._get_color_rgb(ell)
        border_width = self._get_stroke_width(ell)
        border_r, border_g, border_b = self._get_stroke_color_rgb(ell)

        segments = 36
        for i in range(segments):
            a1 = 2.0 * math.pi * i / segments
            a2 = 2.0 * math.pi * (i + 1) / segments
            x1 = sx + math.cos(a1) * a
            y1 = sy + math.sin(a1) * b
            x2 = sx + math.cos(a2) * a
            y2 = sy + math.sin(a2) * b
            self.dll.AddLine(
                ctypes.c_float(x1), ctypes.c_float(y1),
                ctypes.c_float(x2), ctypes.c_float(y2),
                ctypes.c_int(max(1, int(border_width))),
                ctypes.c_int(border_r), ctypes.c_int(border_g), ctypes.c_int(border_b)
            )

    def _draw_line(self, line):
        s = line.get_start()
        e = line.get_end()
        sx1, sy1 = manim_to_screen(s[0], s[1], self.win_w, self.win_h)
        sx2, sy2 = manim_to_screen(e[0], e[1], self.win_w, self.win_h)
        r, g, b = self._get_stroke_color_rgb(line)
        sw = max(1, int(self._get_stroke_width(line)))
        self.dll.AddLine(
            ctypes.c_float(sx1), ctypes.c_float(sy1),
            ctypes.c_float(sx2), ctypes.c_float(sy2),
            ctypes.c_int(sw), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
        )

    def _draw_arrow(self, arrow):
        self._draw_line(arrow)
        tip = arrow.get_tip()
        if tip is not None:
            try:
                vertices = tip.get_vertices()
                if len(vertices) >= 3:
                    for i in range(len(vertices) - 2):
                        s = vertices[i]
                        e = vertices[i + 2]
                        sx1, sy1 = manim_to_screen(s[0], s[1], self.win_w, self.win_h)
                        sx2, sy2 = manim_to_screen(e[0], e[1], self.win_w, self.win_h)
                        r, g, b = self._get_stroke_color_rgb(arrow)
                        self.dll.AddLine(
                            ctypes.c_float(sx1), ctypes.c_float(sy1),
                            ctypes.c_float(sx2), ctypes.c_float(sy2),
                            ctypes.c_int(2), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
                        )
            except Exception:
                pass

    def _draw_dot(self, dot):
        cx, cy, _ = dot.get_center()
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        radius = dot.radius * 200.0 if hasattr(dot, 'radius') else 6.0
        r, g, b = self._get_color_rgb(dot)
        self.dll.AddCircle(
            sx, sy, radius,
            r, g, b,
            0, 0, 0,
            0.0, 1.0
        )

    def _draw_polygon(self, poly):
        try:
            vertices = poly.get_vertices()
        except Exception:
            return
        if len(vertices) < 2:
            return

        r, g, b = self._get_stroke_color_rgb(poly)
        sw = max(1, int(self._get_stroke_width(poly)))

        for i in range(len(vertices)):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % len(vertices)]
            sx1, sy1 = manim_to_screen(v1[0], v1[1], self.win_w, self.win_h)
            sx2, sy2 = manim_to_screen(v2[0], v2[1], self.win_w, self.win_h)
            self.dll.AddLine(
                ctypes.c_float(sx1), ctypes.c_float(sy1),
                ctypes.c_float(sx2), ctypes.c_float(sy2),
                ctypes.c_int(sw), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
            )

        fill_r, fill_g, fill_b = self._get_color_rgb(poly)
        if fill_r != 255 or fill_g != 255 or fill_b != 255:
            self._fill_polygon_triangle_fan(vertices, fill_r, fill_g, fill_b)

    def _fill_polygon_triangle_fan(self, vertices, r, g, b):
        if len(vertices) < 3:
            return
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        scx, scy = manim_to_screen(cx, cy, self.win_w, self.win_h)

        for i in range(len(vertices)):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % len(vertices)]
            sx1, sy1 = manim_to_screen(v1[0], v1[1], self.win_w, self.win_h)
            sx2, sy2 = manim_to_screen(v2[0], v2[1], self.win_w, self.win_h)

            self.dll.AddLine(
                ctypes.c_float(scx), ctypes.c_float(scy),
                ctypes.c_float(sx1), ctypes.c_float(sy1),
                ctypes.c_int(1), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
            )
            self.dll.AddLine(
                ctypes.c_float(scx), ctypes.c_float(scy),
                ctypes.c_float(sx2), ctypes.c_float(sy2),
                ctypes.c_int(1), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
            )
            self.dll.AddLine(
                ctypes.c_float(sx1), ctypes.c_float(sy1),
                ctypes.c_float(sx2), ctypes.c_float(sy2),
                ctypes.c_int(1), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
            )

    def _draw_dashed_line(self, line):
        s = line.get_start()
        e = line.get_end()
        dx = e[0] - s[0]
        dy = e[1] - s[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length < 0.0001:
            return

        dash_length = getattr(line, 'dash_length', 0.1)
        if dash_length <= 0:
            dash_length = 0.1
        gap_length = getattr(line, 'gap_length', 0.05)
        if gap_length <= 0:
            gap_length = 0.05

        nx, ny = dx / length, dy / length
        pos = 0.0
        drawing = True

        r, g, b = self._get_stroke_color_rgb(line)
        sw = max(1, int(self._get_stroke_width(line)))

        while pos < length:
            seg_len = dash_length if drawing else gap_length
            end_pos = min(pos + seg_len, length)

            if drawing:
                x1 = s[0] + nx * pos
                y1 = s[1] + ny * pos
                x2 = s[0] + nx * end_pos
                y2 = s[1] + ny * end_pos
                sx1, sy1 = manim_to_screen(x1, y1, self.win_w, self.win_h)
                sx2, sy2 = manim_to_screen(x2, y2, self.win_w, self.win_h)
                self.dll.AddLine(
                    ctypes.c_float(sx1), ctypes.c_float(sy1),
                    ctypes.c_float(sx2), ctypes.c_float(sy2),
                    ctypes.c_int(sw), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
                )

            pos = end_pos
            drawing = not drawing

    def _draw_arc(self, arc):
        cx, cy, _ = arc.get_center()
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        radius = arc.radius * 200.0 if hasattr(arc, 'radius') else 100.0

        start_angle = arc.start_angle if hasattr(arc, 'start_angle') else 0
        angle_range = arc.angle if hasattr(arc, 'angle') else math.pi

        r, g, b = self._get_stroke_color_rgb(arc)
        sw = max(1, int(self._get_stroke_width(arc)))

        segments = 36
        for i in range(segments):
            a1 = start_angle + angle_range * i / segments
            a2 = start_angle + angle_range * (i + 1) / segments
            x1 = sx + math.cos(a1) * radius
            y1 = sy + math.sin(a1) * radius
            x2 = sx + math.cos(a2) * radius
            y2 = sy + math.sin(a2) * radius
            self.dll.AddLine(
                ctypes.c_float(x1), ctypes.c_float(y1),
                ctypes.c_float(x2), ctypes.c_float(y2),
                ctypes.c_int(sw), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
            )

    def _draw_point(self, point):
        pos = point.get_location()
        sx, sy = manim_to_screen(pos[0], pos[1], self.win_w, self.win_h)
        r, g, b = self._get_color_rgb(point)
        self.dll.AddCircle(
            sx, sy, 4.0,
            r, g, b,
            0, 0, 0, 0.0, 1.0
        )

    def _draw_generic(self, mob):
        try:
            points = mob.get_points()
            if points is not None and len(points) > 0:
                r, g, b = self._get_color_rgb(mob)
                for i in range(0, len(points) - 1, 1):
                    sx1, sy1 = manim_to_screen(points[i][0], points[i][1], self.win_w, self.win_h)
                    sx2, sy2 = manim_to_screen(points[i+1][0], points[i+1][1], self.win_w, self.win_h)
                    self.dll.AddLine(
                        ctypes.c_float(sx1), ctypes.c_float(sy1),
                        ctypes.c_float(sx2), ctypes.c_float(sy2),
                        ctypes.c_int(1), ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
                    )
        except Exception:
            pass

    def tick(self):
        self.frame_count += 1
        return self.dll.Vulkan_Tick() != 0

    def close(self):
        self.dll.Vulkan_Shutdown()
