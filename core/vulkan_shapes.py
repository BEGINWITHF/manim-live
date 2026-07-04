import ctypes
import math
from core.vulkan_util import manim_to_screen, rotate_point, get_fill_rgb, get_stroke_rgb, get_stroke_w
from core.animations import get_anim_rotation


class ShapeMixin:
    def _color(self, mob, alpha=1.0):
        return get_fill_rgb(mob, alpha)

    def _stroke_color(self, mob):
        return get_stroke_rgb(mob)

    def _stroke_width(self, mob):
        return get_stroke_w(mob)

    def _rotate_point(self, x, y, cx, cy, angle):
        return rotate_point(x, y, cx, cy, angle)

    def _send_square(self, mob, a, w, h, rot):
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale_x = w / 14.0
        half = mob.side_length / 2.0 * scale_x
        fo = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0
        so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if fo <= 0:
            if a < 1.0:
                return
            sr, sg, sb = self._stroke_color(mob)
            sr = int(sr * so)
            sg = int(sg * so)
            sb = int(sb * so)
            sw = max(1, round(self._stroke_width(mob)))
            tl = self._rotate_point(sx - half, sy - half, sx, sy, rot)
            tr = self._rotate_point(sx + half, sy - half, sx, sy, rot)
            br = self._rotate_point(sx + half, sy + half, sx, sy, rot)
            bl = self._rotate_point(sx - half, sy + half, sx, sy, rot)
            perimeter = 2.0 * (2.0 * half + 2.0 * half)
            drawn = perimeter * progress
            edges = [
                (tr, tl, 2.0 * half),
                (tl, bl, 2.0 * half),
                (bl, br, 2.0 * half),
                (br, tr, 2.0 * half),
            ]
            remaining = drawn
            for (x0, y0), (x1, y1), length in edges:
                if remaining <= 0:
                    break
                if remaining >= length:
                    self.dll.AddLine(x0, y0, x1, y1, sw, sr, sg, sb, a)
                    remaining -= length
                else:
                    frac = remaining / length
                    ex = x0 + (x1 - x0) * frac
                    ey = y0 + (y1 - y0) * frac
                    self.dll.AddLine(x0, y0, ex, ey, sw, sr, sg, sb, a)
                    remaining = 0
        else:
            if progress >= 1.0:
                r, g, b = self._color(mob, a)
                self.dll.AddRect(sx, sy, half, half, rot, r, g, b, a)
                if so > 0 and a >= 1.0:
                    sr, sg, sb = self._stroke_color(mob)
                    sr = int(sr * so)
                    sg = int(sg * so)
                    sb = int(sb * so)
                    sw = max(1, round(self._stroke_width(mob)))
                    tl = self._rotate_point(sx - half, sy - half, sx, sy, rot)
                    tr = self._rotate_point(sx + half, sy - half, sx, sy, rot)
                    br = self._rotate_point(sx + half, sy + half, sx, sy, rot)
                    bl = self._rotate_point(sx - half, sy + half, sx, sy, rot)
                    self.dll.AddLine(tr[0], tr[1], tl[0], tl[1], sw, sr, sg, sb, a)
                    self.dll.AddLine(tl[0], tl[1], bl[0], bl[1], sw, sr, sg, sb, a)
                    self.dll.AddLine(bl[0], bl[1], br[0], br[1], sw, sr, sg, sb, a)
                    self.dll.AddLine(br[0], br[1], tr[0], tr[1], sw, sr, sg, sb, a)
            else:
                stroke_progress = min(1.0, progress * 2.0)
                if stroke_progress > 0 and a >= 1.0:
                    sr, sg, sb = self._stroke_color(mob)
                    sr = int(sr * so)
                    sg = int(sg * so)
                    sb = int(sb * so)
                    sw = max(1, round(self._stroke_width(mob)))
                    tl = self._rotate_point(sx - half, sy - half, sx, sy, rot)
                    tr = self._rotate_point(sx + half, sy - half, sx, sy, rot)
                    br = self._rotate_point(sx + half, sy + half, sx, sy, rot)
                    bl = self._rotate_point(sx - half, sy + half, sx, sy, rot)
                    perimeter = 2.0 * (2.0 * half + 2.0 * half)
                    drawn = perimeter * stroke_progress
                    edges = [
                        (tr, tl, 2.0 * half),
                        (tl, bl, 2.0 * half),
                        (bl, br, 2.0 * half),
                        (br, tr, 2.0 * half),
                    ]
                    remaining = drawn
                    for (x0, y0), (x1, y1), length in edges:
                        if remaining <= 0:
                            break
                        if remaining >= length:
                            self.dll.AddLine(x0, y0, x1, y1, sw, sr, sg, sb, a)
                            remaining -= length
                        else:
                            frac = remaining / length
                            ex = x0 + (x1 - x0) * frac
                            ey = y0 + (y1 - y0) * frac
                            self.dll.AddLine(x0, y0, ex, ey, sw, sr, sg, sb, a)
                            remaining = 0
                if progress > 0.5:
                    fill_alpha = (progress - 0.5) * 2.0
                    r, g, b = self._color(mob, a)
                    fr = int(r * fill_alpha)
                    fg = int(g * fill_alpha)
                    fb = int(b * fill_alpha)
                    self.dll.AddRect(sx, sy, half, half, rot, fr, fg, fb, a)

    def _send_rectangle(self, mob, a, w, h, rot):
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale_x = w / 14.0
        scale_y = h / 8.0
        hw = mob.width / 2.0 * scale_x
        hh = mob.height / 2.0 * scale_y
        fo = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0
        so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if fo <= 0:
            if a < 1.0:
                return
            sr, sg, sb = self._stroke_color(mob)
            sr = int(sr * so)
            sg = int(sg * so)
            sb = int(sb * so)
            sw = max(1, round(self._stroke_width(mob)))
            tl = self._rotate_point(sx - hw, sy - hh, sx, sy, rot)
            tr = self._rotate_point(sx + hw, sy - hh, sx, sy, rot)
            br = self._rotate_point(sx + hw, sy + hh, sx, sy, rot)
            bl = self._rotate_point(sx - hw, sy + hh, sx, sy, rot)
            perimeter = 2.0 * (2.0 * hw + 2.0 * hh)
            drawn = perimeter * progress
            edges = [
                (tr, tl, 2.0 * hw),
                (tl, bl, 2.0 * hh),
                (bl, br, 2.0 * hw),
                (br, tr, 2.0 * hh),
            ]
            remaining = drawn
            for (x0, y0), (x1, y1), length in edges:
                if remaining <= 0:
                    break
                if remaining >= length:
                    self.dll.AddLine(x0, y0, x1, y1, sw, sr, sg, sb, a)
                    remaining -= length
                else:
                    frac = remaining / length
                    ex = x0 + (x1 - x0) * frac
                    ey = y0 + (y1 - y0) * frac
                    self.dll.AddLine(x0, y0, ex, ey, sw, sr, sg, sb, a)
                    remaining = 0
        else:
            if progress >= 1.0:
                r, g, b = self._color(mob, a)
                self.dll.AddRect(sx, sy, hw, hh, rot, r, g, b, a)
            else:
                stroke_progress = min(1.0, progress * 2.0)
                if stroke_progress > 0 and a >= 1.0:
                    sr, sg, sb = self._stroke_color(mob)
                    sr = int(sr * so)
                    sg = int(sg * so)
                    sb = int(sb * so)
                    sw = max(1, round(self._stroke_width(mob)))
                    tl = self._rotate_point(sx - hw, sy - hh, sx, sy, rot)
                    tr = self._rotate_point(sx + hw, sy - hh, sx, sy, rot)
                    br = self._rotate_point(sx + hw, sy + hh, sx, sy, rot)
                    bl = self._rotate_point(sx - hw, sy + hh, sx, sy, rot)
                    perimeter = 2.0 * (2.0 * hw + 2.0 * hh)
                    drawn = perimeter * stroke_progress
                    edges = [
                        (tr, tl, 2.0 * hw),
                        (tl, bl, 2.0 * hh),
                        (bl, br, 2.0 * hw),
                        (br, tr, 2.0 * hh),
                    ]
                    remaining = drawn
                    for (x0, y0), (x1, y1), length in edges:
                        if remaining <= 0:
                            break
                        if remaining >= length:
                            self.dll.AddLine(x0, y0, x1, y1, sw, sr, sg, sb, a)
                            remaining -= length
                        else:
                            frac = remaining / length
                            ex = x0 + (x1 - x0) * frac
                            ey = y0 + (y1 - y0) * frac
                            self.dll.AddLine(x0, y0, ex, ey, sw, sr, sg, sb, a)
                            remaining = 0
                if progress > 0.5:
                    fill_opacity = (progress - 0.5) * 2.0
                    r, g, b = self._color(mob, a)
                    r = int(r * fill_opacity)
                    g = int(g * fill_opacity)
                    b = int(b * fill_opacity)
                    self.dll.AddRect(sx, sy, hw, hh, rot, r, g, b, a)

    def _send_ellipse(self, mob, a, w, h, rot):
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale = w / 14.0
        rx = mob.width / 2.0 * scale
        ry = mob.height / 2.0 * scale
        fo = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0
        so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if fo <= 0:
            if a < 1.0:
                return
            sr, sg, sb = self._stroke_color(mob)
            sr = int(sr * so)
            sg = int(sg * so)
            sb = int(sb * so)
            sw = max(1, round(self._stroke_width(mob)))
            segs = 48
            circumference = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
            drawn = circumference * progress
            accumulated = 0.0
            prev_angle_rad = rot
            prev_px = sx + math.cos(prev_angle_rad) * rx
            prev_py = sy - math.sin(prev_angle_rad) * ry
            for j in range(1, segs + 1):
                if accumulated >= drawn:
                    break
                cur_angle_rad = rot - 2.0 * math.pi * j / segs
                px = sx + math.cos(cur_angle_rad) * rx
                py = sy - math.sin(cur_angle_rad) * ry
                seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                if accumulated + seg_len <= drawn:
                    self.dll.AddLine(prev_px, prev_py, px, py, sw, sr, sg, sb, a)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    ex = prev_px + (px - prev_px) * frac
                    ey = prev_py + (py - prev_py) * frac
                    self.dll.AddLine(prev_px, prev_py, ex, ey, sw, sr, sg, sb, a)
                    accumulated = drawn
                prev_px, prev_py = px, py
        else:
            if progress >= 1.0:
                r, g, b = self._color(mob, a)
                self.dll.AddEllipse(sx, sy, rx, ry, r, g, b, a)
            else:
                stroke_progress = min(1.0, progress * 2.0)
                if stroke_progress > 0 and a >= 1.0:
                    sr2, sg2, sb2 = self._stroke_color(mob)
                    sr2 = int(sr2 * so)
                    sg2 = int(sg2 * so)
                    sb2 = int(sb2 * so)
                    sw2 = max(1, round(self._stroke_width(mob)))
                    segs = 48
                    circumference = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
                    drawn = circumference * stroke_progress
                    accumulated = 0.0
                    prev_angle_rad = rot
                    prev_px = sx + math.cos(prev_angle_rad) * rx
                    prev_py = sy - math.sin(prev_angle_rad) * ry
                    for j in range(1, segs + 1):
                        if accumulated >= drawn:
                            break
                        cur_angle_rad = rot - 2.0 * math.pi * j / segs
                        px = sx + math.cos(cur_angle_rad) * rx
                        py = sy - math.sin(cur_angle_rad) * ry
                        seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                        if accumulated + seg_len <= drawn:
                            self.dll.AddLine(prev_px, prev_py, px, py, sw2, sr2, sg2, sb2, a)
                            accumulated += seg_len
                        else:
                            frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                            ex = prev_px + (px - prev_px) * frac
                            ey = prev_py + (py - prev_py) * frac
                            self.dll.AddLine(prev_px, prev_py, ex, ey, sw2, sr2, sg2, sb2, a)
                            accumulated = drawn
                        prev_px, prev_py = px, py
                if progress > 0.5:
                    fill_opacity = (progress - 0.5) * 2.0
                    r, g, b = self._color(mob, a)
                    r = int(r * fill_opacity)
                    g = int(g * fill_opacity)
                    b = int(b * fill_opacity)
                    self.dll.AddEllipse(sx, sy, rx, ry, r, g, b, a)

    def _send_circle(self, mob, a, w, h, rot):
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale_y = h / 8.0
        sr = mob.radius * scale_y
        fo = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0
        so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if fo <= 0:
            if a < 1.0:
                return
            cr, cg, cb = self._stroke_color(mob)
            cr = int(cr * so)
            cg = int(cg * so)
            cb = int(cb * so)
            sw = max(1, round(self._stroke_width(mob)))
            segs = 48
            circumference = 2.0 * math.pi * sr
            drawn = circumference * progress
            accumulated = 0.0
            prev_angle_rad = rot
            prev_px = sx + math.cos(prev_angle_rad) * sr
            prev_py = sy - math.sin(prev_angle_rad) * sr
            for j in range(1, segs + 1):
                if accumulated >= drawn:
                    break
                cur_angle_rad = rot - 2.0 * math.pi * j / segs
                px = sx + math.cos(cur_angle_rad) * sr
                py = sy - math.sin(cur_angle_rad) * sr
                seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                if accumulated + seg_len <= drawn:
                    self.dll.AddLine(prev_px, prev_py, px, py, sw, cr, cg, cb, a)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    ex = prev_px + (px - prev_px) * frac
                    ey = prev_py + (py - prev_py) * frac
                    self.dll.AddLine(prev_px, prev_py, ex, ey, sw, cr, cg, cb, a)
                    accumulated = drawn
                prev_px, prev_py = px, py
        else:
            if progress >= 1.0:
                fr, fg, fb = self._color(mob, a)
                br, bg, bb = self._stroke_color(mob)
                bw = self._stroke_width(mob)
                self.dll.AddCircle(sx, sy, sr, fr, fg, fb, br, bg, bb, bw, 1.0, a)
            else:
                stroke_progress = min(1.0, progress * 2.0)
                if stroke_progress > 0 and a >= 1.0:
                    cr2, cg2, cb2 = self._stroke_color(mob)
                    cr2 = int(cr2 * so)
                    cg2 = int(cg2 * so)
                    cb2 = int(cb2 * so)
                    sw2 = max(1, round(self._stroke_width(mob)))
                    segs = 48
                    circumference = 2.0 * math.pi * sr
                    drawn = circumference * stroke_progress
                    accumulated = 0.0
                    prev_angle_rad = rot
                    prev_px = sx + math.cos(prev_angle_rad) * sr
                    prev_py = sy - math.sin(prev_angle_rad) * sr
                    for j in range(1, segs + 1):
                        if accumulated >= drawn:
                            break
                        cur_angle_rad = rot - 2.0 * math.pi * j / segs
                        px = sx + math.cos(cur_angle_rad) * sr
                        py = sy - math.sin(cur_angle_rad) * sr
                        seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                        if accumulated + seg_len <= drawn:
                            self.dll.AddLine(prev_px, prev_py, px, py, sw2, cr2, cg2, cb2, a)
                            accumulated += seg_len
                        else:
                            frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                            ex = prev_px + (px - prev_px) * frac
                            ey = prev_py + (py - prev_py) * frac
                            self.dll.AddLine(prev_px, prev_py, ex, ey, sw2, cr2, cg2, cb2, a)
                            accumulated = drawn
                        prev_px, prev_py = px, py
                if progress > 0.5:
                    fill_opacity = (progress - 0.5) * 2.0
                    fr, fg, fb = self._color(mob, a)
                    br2, bg2, bb2 = self._stroke_color(mob)
                    bw2 = self._stroke_width(mob) * (h / 8.0)
                    self.dll.AddCircle(sx, sy, sr, fr, fg, fb, br2, bg2, bb2, bw2, fill_opacity, a)

    def _send_arrow(self, mob, a, w, h, rot):
        s = mob.get_start()
        e = mob.get_end()
        cx, cy, _ = mob.get_center()
        sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
        sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
        scx, scy = manim_to_screen(cx, cy, w, h)
        sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
        sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        r, g, b = self._stroke_color(mob)
        sw = max(1, round(self._stroke_width(mob)))
        self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b, a)
        dx = sx2 - sx1
        dy = sy2 - sy1
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            ux = dx / length
            uy = dy / length
            head_len = min(20.0, length * 0.15)
            head_w = head_len * 0.5
            px = -uy
            py = ux
            hx1 = sx2 - ux * head_len + px * head_w
            hy1 = sy2 - uy * head_len + py * head_w
            hx2 = sx2 - ux * head_len - px * head_w
            hy2 = sy2 - uy * head_len - py * head_w
            self.dll.AddLine(sx2, sy2, hx1, hy1, sw, r, g, b, a)
            self.dll.AddLine(sx2, sy2, hx2, hy2, sw, r, g, b, a)
            head_pts = [
                sx2, sy2, 0.0, sx2, sy2, 0.0,
                hx1, hy1, 0.0, hx1, hy1, 0.0,
                hx1, hy1, 0.0, hx1, hy1, 0.0,
                hx2, hy2, 0.0, hx2, hy2, 0.0,
                hx2, hy2, 0.0, hx2, hy2, 0.0,
                sx2, sy2, 0.0, sx2, sy2, 0.0,
            ]
            head_arr = (ctypes.c_float * len(head_pts))(*head_pts)
            self.dll.AddBezierPath(
                head_arr, 12,
                r, g, b, float(sw),
                r, g, b, 1.0,
                1.0, 1, 1, a,
            )

    def _send_line(self, mob, a, w, h, rot):
        s = mob.get_start()
        e = mob.get_end()
        cx, cy, _ = mob.get_center()
        sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
        sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
        scx, scy = manim_to_screen(cx, cy, w, h)
        sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
        sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        r, g, b = self._stroke_color(mob)
        sw = max(1, round(self._stroke_width(mob)))
        self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b, a)

    def _send_dot(self, mob, a, w, h):
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale_y = h / 8.0
        rad = mob.radius * scale_y if hasattr(mob, 'radius') else 6.0
        r, g, b = self._color(mob, a)
        self.dll.AddCircle(sx, sy, rad, r, g, b, 0, 0, 0, 0.0, 1.0, a)

    def _send_dashed_line(self, mob, a, w, h):
        s = mob.get_start()
        e = mob.get_end()
        sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
        sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
        r, g, b = self._stroke_color(mob)
        scale_x = w / 14.0
        sw = max(1, round(self._stroke_width(mob)))
        dl_manim = getattr(mob, 'dash_length', 0.05)
        ratio = getattr(mob, 'dashed_ratio', 0.5)
        if ratio <= 0 or ratio >= 1:
            ratio = 0.5
        gl_manim = dl_manim * (1.0 - ratio) / ratio
        dl = max(1.0, dl_manim * scale_x)
        gl = max(1.0, gl_manim * scale_x)
        self.dll.AddDashedLine(sx1, sy1, sx2, sy2, sw, r, g, b, dl, gl, a)

    def _send_arc(self, mob, a, w, h):
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale_y = h / 8.0
        rad = mob.radius * scale_y if hasattr(mob, 'radius') else 100.0
        sa = mob.start_angle if hasattr(mob, 'start_angle') else 0
        ang = mob.angle if hasattr(mob, 'angle') else math.pi
        r, g, b = self._stroke_color(mob)
        sw = max(1, round(self._stroke_width(mob)))
        self.dll.AddArc(sx, sy, rad, sa, ang, r, g, b, sw, a)

    def _send_polygon(self, mob, verts, alpha=1.0):
        w, h = self.win_w, self.win_h
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        fr, fg, fb = self._color(mob, alpha)
        br, bg, bb = self._stroke_color(mob)
        bw = self._stroke_width(mob)
        rot = get_anim_rotation(mob)

        flat = []
        for v in verts:
            vx, vy = manim_to_screen(v[0], v[1], w, h)
            vx, vy = self._rotate_point(vx, vy, sx, sy, rot)
            flat.append(vx)
            flat.append(vy)

        arr = (ctypes.c_float * len(flat))(*flat)
        self.dll.AddPolygon(
            sx, sy, fr, fg, fb, br, bg, bb, bw,
            len(verts), arr, alpha
        )

    def _send_point(self, mob, a, w, h):
        pos = mob.get_location()
        sx, sy = manim_to_screen(pos[0], pos[1], w, h)
        r, g, b = self._color(mob, a)
        self.dll.AddPoint(sx, sy, r, g, b, a)
