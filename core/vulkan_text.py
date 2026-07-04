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
            if len(pts) < 4:
                return
        except Exception:
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
