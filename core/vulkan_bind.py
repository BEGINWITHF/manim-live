import ctypes
import os
import math
import time
from manim import (
    Square, Circle, Line, Rectangle, Polygon,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group
)


def manim_to_screen(x, y, w=800, h=600):
    sx = w / 14.0
    sy = h / 8.0
    cx, cy = w / 2.0, h / 2.0
    return float(cx + x * sx), float(cy - y * sy)


_anim_opacity = {}


def set_anim_opacity(mob, val):
    _anim_opacity[id(mob)] = val


def get_anim_opacity(mob):
    return _anim_opacity.get(id(mob), 1.0)


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def _smooth(t, inflection=10.0):
    error = _sigmoid(-inflection / 2)
    val = (_sigmoid(inflection * (t - 0.5)) - error) / (1 - 2 * error)
    return max(0.0, min(1.0, val))


def _linear(t):
    return t


def _rush_into(t, inflection=10.0):
    return 2.0 * _smooth(t / 2.0, inflection)


def _rush_from(t, inflection=10.0):
    return 2.0 * _smooth(t / 2.0 + 0.5, inflection) - 1.0


def _there_and_back(t, inflection=10.0):
    if t < 0.5:
        new_t = 2.0 * t
    else:
        new_t = 2.0 * (1.0 - t)
    return _smooth(new_t, inflection)


def _slow_into(t):
    return math.sqrt(1.0 - (1.0 - t) * (1.0 - t))


def _double_smooth(t):
    if t < 0.5:
        return 0.5 * _smooth(2.0 * t)
    else:
        return 0.5 * (1.0 + _smooth(2.0 * t - 1.0))


def _wiggle(t, wiggles=2):
    val = math.sin(wiggles * math.pi * t)
    return _there_and_back(t) * val


def _lingering(t):
    return _squish_rate_func(lambda x: x, 0, 0.8)(t)


def _exponential_decay(t, half_life=0.1):
    return 1.0 - math.exp(-t / half_life)


def _squish_rate_func(func, a, b):
    def result(t):
        return func((t - a) / (b - a))
    return result


DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0.0
TARGET_FPS = 60
FRAME_DURATION = 1.0 / TARGET_FPS


class Animation:
    def __init__(
        self,
        mobject=None,
        lag_ratio=DEFAULT_ANIMATION_LAG_RATIO,
        run_time=DEFAULT_ANIMATION_RUN_TIME,
        rate_func=None,
        reverse_rate_function=False,
        name=None,
        remover=False,
        suspend_mobject_updating=True,
        introducer=False,
        **kwargs,
    ):
        self.mobject = mobject
        self.lag_ratio = lag_ratio
        self._run_time = run_time
        self.rate_func = rate_func if rate_func is not None else _smooth
        self.reverse_rate_function = reverse_rate_function
        self.name = name
        self.remover = remover
        self.suspend_mobject_updating = suspend_mobject_updating
        self.introducer = introducer
        self.start_time = 0.0
        self.finished = False
        self._original_starting_mobject = None

    @property
    def run_time(self):
        return self._run_time

    @run_time.setter
    def run_time(self, value):
        self._run_time = value

    def __str__(self):
        return self.name or f"{type(self).__name__}({self.mobject})"

    def __repr__(self):
        return self.__str__()

    def begin(self, t):
        self.start_time = t
        if self.mobject is not None:
            self._original_starting_mobject = self.create_starting_mobject()

    def finish(self):
        self.finished = True

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        self.interpolate_mobject(alpha)

    def interpolate_mobject(self, alpha):
        pass

    def interpolate_submobject(self, submobject, starting_submobject, alpha):
        pass

    def get_sub_alpha(self, alpha, index, num_submobjects):
        if num_submobjects <= 1:
            return alpha
        lag_ratio = self.lag_ratio
        if lag_ratio == 0:
            return alpha
        start = alpha * lag_ratio * index
        end = alpha + alpha * lag_ratio * (index - num_submobjects + 1)
        return max(0.0, min(1.0, (end + start) / 2.0 if lag_ratio < 1 else start))

    def clean_up_from_scene(self, scene):
        pass

    def create_starting_mobject(self):
        return self.mobject

    def get_all_mobjects(self):
        if self.mobject is not None:
            return [self.mobject]
        return []

    def get_all_families_zipped(self):
        return []

    def update_mobjects(self, dt):
        pass

    def get_all_mobjects_to_update(self):
        return []

    def copy(self):
        return type(self)(
            self.mobject,
            lag_ratio=self.lag_ratio,
            run_time=self._run_time,
            rate_func=self.rate_func,
            reverse_rate_function=self.reverse_rate_function,
            name=self.name,
            remover=self.remover,
            introducer=self.introducer,
        )

    def set_run_time(self, run_time):
        self._run_time = run_time
        return self

    def get_run_time(self):
        return self._run_time

    def set_rate_func(self, rate_func):
        self.rate_func = rate_func
        return self

    def get_rate_func(self):
        return self.rate_func

    def set_name(self, name):
        self.name = name
        return self

    def is_remover(self):
        return self.remover

    def is_introducer(self):
        return self.introducer

    @classmethod
    def set_default(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)


class Create(Animation):
    def __init__(self, mobject, run_time=1.0, **kwargs):
        super().__init__(mobject, run_time=run_time, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        self.mobject._vulkan_progress = alpha


class Succession(Animation):
    def __init__(self, *animations, rate_func=None, **kwargs):
        self.animations = list(animations)
        total = sum(a.run_time for a in self.animations)
        super().__init__(run_time=total, rate_func=rate_func, **kwargs)

    def begin(self, t):
        super().begin(t)
        cumulative = 0.0
        for a in self.animations:
            a.begin(t + cumulative)
            cumulative += a.run_time

    def interpolate(self, t):
        elapsed = t - self.start_time
        cumulative = 0.0
        for a in self.animations:
            if elapsed < cumulative + a.run_time:
                a.interpolate(t)
                return
            cumulative += a.run_time
        if self.animations:
            self.animations[-1].interpolate(t)

    def finish(self):
        super().finish()
        for a in self.animations:
            a.finish()

    def get_all_mobjects(self):
        mobs = []
        for a in self.animations:
            mobs.extend(a.get_all_mobjects())
        return mobs

    def get_all_families_zipped(self):
        families = []
        for a in self.animations:
            families.extend(a.get_all_families_zipped())
        return families


class Wait(Animation):
    def __init__(
        self,
        run_time=1.0,
        stop_condition=None,
        frozen_frame=None,
        rate_func=None,
        **kwargs,
    ):
        super().__init__(None, run_time=run_time, rate_func=rate_func or _linear, **kwargs)
        self.stop_condition = stop_condition
        self.frozen_frame = frozen_frame

    def begin(self, t):
        super().begin(t)

    def finish(self):
        super().finish()

    def clean_up_from_scene(self, scene):
        pass

    def update_mobjects(self, dt):
        pass

    def interpolate(self, alpha):
        pass


class Add(Animation):
    def __init__(self, *mobjects, run_time=0.0, **kwargs):
        self.mobjects = list(mobjects)
        super().__init__(mobjects[0] if mobjects else None, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)

    def finish(self):
        super().finish()

    def clean_up_from_scene(self, scene):
        pass

    def update_mobjects(self, dt):
        pass

    def interpolate(self, t):
        elapsed = t - self.start_time
        if elapsed >= 0:
            for mob in self.mobjects:
                set_anim_opacity(mob, 1.0)

    def get_all_mobjects(self):
        return list(self.mobjects)


def prepare_animation(anim):
    if isinstance(anim, Animation):
        return anim
    raise TypeError(f"Expected Animation, got {type(anim)}")


class VulkanRender:
    def __init__(self, w=1920, h=1080):
        self.win_w = w
        self.win_h = h
        self.frame_count = 0
        self.scene = None
        self._active_anims = []
        self.init_w = w
        self.init_h = h

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
        custom = os.environ.get('MANIM_FONT', '')
        if custom and os.path.exists(custom):
            with open(custom, 'rb') as f:
                data = f.read()
            buf = ctypes.create_string_buffer(data)
            self.dll.Text_LoadFont(buf, len(data))

        font_paths = []
        if os.name == 'nt':
            windir = os.environ.get('WINDIR', r'C:\Windows')
            font_paths = [
                os.path.join(windir, 'Fonts', 'malgun.ttf'),
                os.path.join(windir, 'Fonts', 'NotoSansSC-VF.ttf'),
                os.path.join(windir, 'Fonts', 'NotoSansJP-VF.ttf'),
                os.path.join(windir, 'Fonts', 'msyh.ttc'),
                os.path.join(windir, 'Fonts', 'simhei.ttf'),
                os.path.join(windir, 'Fonts', 'msgothic.ttc'),
                os.path.join(windir, 'Fonts', 'segoeui.ttf'),
                os.path.join(windir, 'Fonts', 'arial.ttf'),
            ]
        else:
            font_paths = [
                '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttf',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/TTF/DejaVuSans.ttf',
            ]
        for fp in font_paths:
            if os.path.exists(fp):
                with open(fp, 'rb') as f:
                    data = f.read()
                buf = ctypes.create_string_buffer(data)
                self.dll.Text_LoadFont(buf, len(data))

        if self.dll.Text_LoadFont.argtypes is None:
            print("[WARNING] No system font found, text will not render")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        for mob in scene.mobjects:
            self._send(mob, angle)

    def _send(self, mob, angle=0.0):
        w, h = self.win_w, self.win_h
        a = get_anim_opacity(mob)
        if a <= 0:
            return

        if isinstance(mob, (VGroup, Group)):
            for sub in mob:
                self._send(sub, angle)
            return

        if isinstance(mob, Square):
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
                sr, sg, sb = self._stroke_color(mob)
                sr = int(sr * so * a)
                sg = int(sg * so * a)
                sb = int(sb * so * a)
                sw = max(1, round(self._stroke_width(mob)))
                tl = (sx - half, sy - half)
                tr = (sx + half, sy - half)
                br = (sx + half, sy + half)
                bl = (sx - half, sy + half)
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
                        self.dll.AddLine(x0, y0, x1, y1, sw, sr, sg, sb)
                        remaining -= length
                    else:
                        frac = remaining / length
                        ex = x0 + (x1 - x0) * frac
                        ey = y0 + (y1 - y0) * frac
                        self.dll.AddLine(x0, y0, ex, ey, sw, sr, sg, sb)
                        remaining = 0
            else:
                r, g, b = self._color(mob)
                self.dll.AddRect(sx, sy, half, half, angle, r, g, b)

        elif isinstance(mob, Rectangle):
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
                sr, sg, sb = self._stroke_color(mob)
                sr = int(sr * so * a)
                sg = int(sg * so * a)
                sb = int(sb * so * a)
                sw = max(1, round(self._stroke_width(mob)))
                tl = (sx - hw, sy - hh)
                tr = (sx + hw, sy - hh)
                br = (sx + hw, sy + hh)
                bl = (sx - hw, sy + hh)
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
                        self.dll.AddLine(x0, y0, x1, y1, sw, sr, sg, sb)
                        remaining -= length
                    else:
                        frac = remaining / length
                        ex = x0 + (x1 - x0) * frac
                        ey = y0 + (y1 - y0) * frac
                        self.dll.AddLine(x0, y0, ex, ey, sw, sr, sg, sb)
                        remaining = 0
            else:
                r, g, b = self._color(mob)
                self.dll.AddRect(sx, sy, hw, hh, angle, r, g, b)

        elif isinstance(mob, Ellipse):
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
                sr, sg, sb = self._stroke_color(mob)
                sr = int(sr * so * a)
                sg = int(sg * so * a)
                sb = int(sb * so * a)
                sw = max(1, round(self._stroke_width(mob)))
                segs = 48
                circumference = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
                drawn = circumference * progress
                accumulated = 0.0
                prev_px = sx + rx
                prev_py = sy
                for j in range(1, segs + 1):
                    if accumulated >= drawn:
                        break
                    angle = -2.0 * math.pi * j / segs
                    px = sx + math.cos(angle) * rx
                    py = sy + math.sin(angle) * ry
                    seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                    if accumulated + seg_len <= drawn:
                        self.dll.AddLine(prev_px, prev_py, px, py, sw, sr, sg, sb)
                        accumulated += seg_len
                    else:
                        frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                        ex = prev_px + (px - prev_px) * frac
                        ey = prev_py + (py - prev_py) * frac
                        self.dll.AddLine(prev_px, prev_py, ex, ey, sw, sr, sg, sb)
                        accumulated = drawn
                    prev_px, prev_py = px, py
            else:
                r, g, b = self._color(mob)
                self.dll.AddEllipse(sx, sy, rx, ry, r, g, b)

        elif isinstance(mob, Circle):
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
                cr, cg, cb = self._stroke_color(mob)
                cr = int(cr * so * a)
                cg = int(cg * so * a)
                cb = int(cb * so * a)
                sw = max(1, round(self._stroke_width(mob)))
                segs = 48
                circumference = 2.0 * math.pi * sr
                drawn = circumference * progress
                accumulated = 0.0
                prev_px = sx + sr
                prev_py = sy
                for j in range(1, segs + 1):
                    if accumulated >= drawn:
                        break
                    angle = -2.0 * math.pi * j / segs
                    px = sx + math.cos(angle) * sr
                    py = sy + math.sin(angle) * sr
                    seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                    if accumulated + seg_len <= drawn:
                        self.dll.AddLine(prev_px, prev_py, px, py, sw, cr, cg, cb)
                        accumulated += seg_len
                    else:
                        frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                        ex = prev_px + (px - prev_px) * frac
                        ey = prev_py + (py - prev_py) * frac
                        self.dll.AddLine(prev_px, prev_py, ex, ey, sw, cr, cg, cb)
                        accumulated = drawn
                    prev_px, prev_py = px, py
            else:
                fr, fg, fb = self._color(mob)
                br, bg, bb = self._stroke_color(mob)
                bw = self._stroke_width(mob) * (h / 8.0)
                sp = min(1.0, self.frame_count / 72.0)
                self.dll.AddCircle(sx, sy, sr, fr, fg, fb, br, bg, bb, bw, sp)

        elif isinstance(mob, Arrow):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            sw = max(1, round(self._stroke_width(mob)))
            self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b)
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
                self.dll.AddLine(sx2, sy2, hx1, hy1, sw, r, g, b)
                self.dll.AddLine(sx2, sy2, hx2, hy2, sw, r, g, b)

        elif isinstance(mob, Line):
            s = mob.get_start()
            e = mob.get_end()
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h)
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h)
            r, g, b = self._stroke_color(mob)
            sw = max(1, round(self._stroke_width(mob)))
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
            sw = max(1, round(self._stroke_width(mob)))
            dl_manim = getattr(mob, 'dash_length', 0.05)
            ratio = getattr(mob, 'dashed_ratio', 0.5)
            if ratio <= 0 or ratio >= 1:
                ratio = 0.5
            gl_manim = dl_manim * (1.0 - ratio) / ratio
            dl = max(1.0, dl_manim * scale_x)
            gl = max(1.0, gl_manim * scale_x)
            self.dll.AddDashedLine(sx1, sy1, sx2, sy2, sw, r, g, b, dl, gl)

        elif isinstance(mob, Arc):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_y = h / 8.0
            rad = mob.radius * scale_y if hasattr(mob, 'radius') else 100.0
            sa = mob.start_angle if hasattr(mob, 'start_angle') else 0
            ang = mob.angle if hasattr(mob, 'angle') else math.pi
            r, g, b = self._stroke_color(mob)
            sw = max(1, round(self._stroke_width(mob)))
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
            fo = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0
            if fo <= 0:
                return
            fs = mob.font_size if hasattr(mob, 'font_size') else 48
            scale = min(w / self.init_w, h / self.init_h) if self.init_w > 0 and self.init_h > 0 else 1.0
            fs = fs * scale
            txt = mob.original_text if hasattr(mob, 'original_text') else (mob.text if hasattr(mob, 'text') else "")
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

    def _extract_add_mobjects(self, anim):
        mobjects = []
        if isinstance(anim, Add):
            mobjects.extend(anim.mobjects)
        elif isinstance(anim, Succession):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub))
        return mobjects

    def play(self, *animations, **kwargs):
        if not self.scene:
            return

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))

        all_mobjects = list(add_mobs)
        for anim in animations:
            if isinstance(anim, Create) and anim.mobject:
                anim.mobject._vulkan_progress = 0.0
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
            elif isinstance(anim, Succession):
                for sub in anim.animations:
                    if isinstance(sub, Create) and sub.mobject:
                        sub.mobject._vulkan_progress = 0.0
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)

        for mob in all_mobjects:
            if mob not in self.scene.mobjects:
                self.scene.add(mob)
        for mob in add_mobs:
            set_anim_opacity(mob, 0.0)

        for a in animations:
            if isinstance(a, Add):
                for mob in a.mobjects:
                    set_anim_opacity(mob, 1.0)

        real_anims = [a for a in animations if not isinstance(a, Add)]

        for a in real_anims:
            a.begin(time.time())

        self._active_anims = real_anims

        while True:
            frame_start = time.time()
            now = frame_start
            all_done = True
            for a in self._active_anims:
                a.interpolate(now)
                if not a.finished and (now - a.start_time) >= a.run_time:
                    a.finish()
                if not a.finished:
                    all_done = False

            if not self.tick():
                break
            self.sync(self.scene)

            if all_done:
                break

            elapsed = time.time() - frame_start
            if elapsed < FRAME_DURATION:
                time.sleep(FRAME_DURATION - elapsed)

    def close(self):
        self.dll.Vulkan_Shutdown()
