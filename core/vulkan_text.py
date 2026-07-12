import ctypes
from core.vulkan_util import manim_to_screen, get_fill_rgb
from core.animations import get_anim_opacity


class TextMixin:
    def _send_transformed_text(self, mob, w, h, alpha=1.0):
        try:
            c = mob.get_color()
            base_r, base_g, base_b = round(float(c[0]) * 255), round(float(c[1]) * 255), round(float(c[2]) * 255)
        except Exception:
            base_r, base_g, base_b = 255, 255, 255
        if base_r == 0 and base_g == 0 and base_b == 0:
            base_r, base_g, base_b = 255, 255, 255

        for sub in mob.submobjects:
            sub_a = get_anim_opacity(sub)
            if sub_a <= 0:
                continue
            try:
                pts = sub.get_points() if hasattr(sub, 'get_points') else sub.points
                if len(pts) < 4:
                    continue
                num_segs = len(pts) // 4
                if num_segs == 0:
                    continue
                sr = int(base_r * sub_a * alpha)
                sg = int(base_g * sub_a * alpha)
                sb = int(base_b * sub_a * alpha)
                flat = []
                for seg_i in range(num_segs):
                    for pt_i in range(4):
                        p = pts[seg_i * 4 + pt_i]
                        vx, vy = manim_to_screen(p[0], p[1], w, h)
                        flat.append(vx)
                        flat.append(vy)
                        flat.append(0.0)
                arr = (ctypes.c_float * len(flat))(*flat)
                self.dll.AddBezierPath(
                    arr, num_segs * 4,
                    sr, sg, sb, 0.7,
                    sr, sg, sb, 1.0,
                    1.0, 1, 1, alpha,
                )
            except Exception:
                pass

    def _send_text_write(self, mob, letter_alphas, w, h, alpha=1.0):
        try:
            c = mob.get_color()
            base_r, base_g, base_b = round(float(c[0]) * 255), round(float(c[1]) * 255), round(float(c[2]) * 255)
        except Exception:
            base_r, base_g, base_b = 255, 255, 255
        if base_r == 0 and base_g == 0 and base_b == 0:
            base_r, base_g, base_b = 255, 255, 255

        for i, sub in enumerate(mob.submobjects):
            sub_alpha = letter_alphas.get(i, 0.0)
            if sub_alpha <= 0.001:
                continue

            pts = sub.get_points()
            if len(pts) < 8:
                continue

            flat = []
            for p in pts:
                sx, sy = manim_to_screen(p[0], p[1], w, h)
                flat.append(sx)
                flat.append(sy)
                flat.append(0.0)

            n = len(flat) // 3
            arr = (ctypes.c_float * len(flat))(*flat)

            stroke_progress = min(1.0, sub_alpha * 2.5)
            stroke_fade = max(0.0, 1.0 - max(0.0, (sub_alpha - 0.4) * 2.5))
            fill_alpha = max(0.0, (sub_alpha - 0.3) * 2.0)

            sr = int(base_r * stroke_fade)
            sg = int(base_g * stroke_fade)
            sb = int(base_b * stroke_fade)

            self.dll.AddBezierPath(
                arr, n,
                sr, sg, sb, 0.7,
                base_r, base_g, base_b, fill_alpha,
                stroke_progress, 1, 1 if fill_alpha > 0 else 0, alpha,
            )

    def _send_text_bitmap(self, mob, w, h, alpha=1.0):
        try:
            c = mob.get_color()
            base_r, base_g, base_b = int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)
        except Exception:
            base_r, base_g, base_b = 255, 255, 255
        if base_r == 0 and base_g == 0 and base_b == 0:
            base_r, base_g, base_b = 255, 255, 255
        fo = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0
        if fo <= 0:
            return
        progress = getattr(mob, '_vulkan_progress', 1.0)
        for sub in mob.submobjects:
            try:
                pts = sub.get_points()
            except Exception:
                continue
            if len(pts) < 8:
                continue
            num_segs = len(pts) // 4
            if num_segs == 0:
                continue
            flat = []
            for p in pts:
                sx, sy = manim_to_screen(p[0], p[1], w, h)
                flat.append(sx)
                flat.append(sy)
                flat.append(0.0)
            arr = (ctypes.c_float * len(flat))(*flat)
            n = len(flat) // 3
            self.dll.AddBezierPath(
                arr, n,
                base_r, base_g, base_b, 0.7,
                base_r, base_g, base_b, 1.0,
                progress, 1, 1, alpha,
            )

    def _send_vmobject(self, mob, a, w, h, parent_offset=None):
        try:
            pts = mob.get_points()
        except Exception:
            return

        from manim.animation.changing import TracedPath
        is_polyline = isinstance(mob, TracedPath)

        if is_polyline and len(pts) >= 2:
            sr, sg, sb, sa = 1, 1, 1, 1
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    sr, sg, sb, sa = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2]), float(srgbas[0][3])
            except Exception:
                sr, sg, sb = 1, 1, 1
                sa = 1.0
            so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
            sw_manim = 2.0
            try:
                raw = mob.get_stroke_width()
                if isinstance(raw, (int, float)):
                    sw_manim = float(raw)
                elif hasattr(raw, '__len__') and len(raw) > 0:
                    sw_manim = float(raw[0])
            except Exception:
                pass
            sw = max(1, int(round(sw_manim * 0.01 * (h / 8.0))))

            raw_pts = []
            for i in range(len(pts)):
                raw_pts.append((float(pts[i][0]), float(pts[i][1])))

            so_attr = getattr(mob, 'stroke_opacity', 1.0)
            if isinstance(so_attr, (list, tuple)) and len(so_attr) == 2:
                sri = round(sr * 255 * a)
                sgi = round(sg * 255 * a)
                sbi = round(sb * 255 * a)
                so_start, so_end = float(so_attr[0]), float(so_attr[1])
                so_arr = []
                n_raw = len(raw_pts)
                for i in range(n_raw):
                    t = i / max(1, n_raw - 1)
                    so_arr.append(so_start + (so_end - so_start) * t)
            else:
                sri = round(sr * 255 * sa * a)
                sgi = round(sg * 255 * sa * a)
                sbi = round(sb * 255 * sa * a)
                so_arr = None

            if len(raw_pts) >= 2:
                smooth_pts = [raw_pts[0]]
                smooth_so = [so_arr[0]] if so_arr else None
                for i in range(len(raw_pts) - 1):
                    x0, y0 = raw_pts[i]
                    x1, y1 = raw_pts[i + 1]
                    dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
                    steps = max(1, int(dist / 0.15))
                    for j in range(1, steps + 1):
                        t = j / steps
                        smooth_pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
                        if smooth_so is not None:
                            so0 = so_arr[i]
                            so1 = so_arr[i + 1]
                            smooth_so.append(so0 + (so1 - so0) * t)
                raw_pts = smooth_pts
                so_arr = smooth_so

            coords = (ctypes.c_float * (len(raw_pts) * 2))()
            for i in range(len(raw_pts)):
                x0, y0 = raw_pts[i]
                if parent_offset is not None:
                    x0 += parent_offset[0]; y0 += parent_offset[1]
                sx, sy = manim_to_screen(x0, y0, w, h)
                coords[i * 2] = sx
                coords[i * 2 + 1] = sy

            alphas = (ctypes.c_float * len(raw_pts))()
            if so_arr is not None:
                for i in range(len(raw_pts)):
                    alphas[i] = max(0.0, min(1.0, so_arr[i] * a))
            else:
                for i in range(len(raw_pts)):
                    alphas[i] = a
            self.dll.AddLineStrip(coords, alphas, len(raw_pts), sw, sri, sgi, sbi, 1.0)
            return
        else:
            if len(pts) < 4:
                return
            flat = []
            for p in pts:
                px, py = p[0], p[1]
                if parent_offset is not None:
                    px += parent_offset[0]
                    py += parent_offset[1]
                sx, sy = manim_to_screen(px, py, w, h)
                flat.append(sx)
                flat.append(sy)
                flat.append(0.0)

        n = len(flat) // 3
        if n < 8:
            return
        arr = (ctypes.c_float * len(flat))(*flat)

        fr, fg, fb, fa = 0, 0, 0, 0
        try:
            frgbas = mob.get_fill_rgbas()
            if len(frgbas) > 0:
                fr, fg, fb, fa = float(frgbas[0][0]), float(frgbas[0][1]), float(frgbas[0][2]), float(frgbas[0][3])
        except Exception:
            pass
        if fr == 0 and fg == 0 and fb == 0:
            try:
                c = mob.get_color()
                fr, fg, fb = float(c[0]), float(c[1]), float(c[2])
                fa = 1.0
            except Exception:
                fr, fg, fb = 1.0, 1.0, 1.0
                fa = 1.0

        sr, sg, sb, sa = 1, 1, 1, 1
        try:
            srgbas = mob.get_stroke_rgbas()
            if len(srgbas) > 0:
                sr, sg, sb, sa = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2]), float(srgbas[0][3])
        except Exception:
            sr, sg, sb = fr, fg, fb
            sa = 1.0

        so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
        sw = self._stroke_width(mob)
        fill_alpha = min(1.0, fa * a)
        stroke_alpha = min(1.0, sa * so * a)
        stroke_w = max(1.0, sw)

        sri = round(sr * 255 * stroke_alpha)
        sgi = round(sg * 255 * stroke_alpha)
        sbi = round(sb * 255 * stroke_alpha)
        fri = round(fr * 255)
        fgi = round(fg * 255)
        fbi = round(fb * 255)

        show_fill = 1 if fill_alpha > 0.01 else 0
        show_stroke = 1 if (stroke_alpha > 0.01 and stroke_w > 0) else 0

        self.dll.AddBezierPath(
            arr, n,
            sri, sgi, sbi, stroke_w,
            fri, fgi, fbi, fill_alpha,
            1.0, show_stroke, show_fill, a,
        )

    def _send_text_stroke(self, mob, a, w, h, parent_offset=None):
        if not hasattr(mob, 'family_members_with_points'):
            return
        for fm in mob.family_members_with_points():
            sw_attr = fm.get_stroke_width() if hasattr(fm, 'get_stroke_width') else 0
            if sw_attr <= 0:
                continue
            self._send_vmobject(fm, a, w, h, parent_offset)
