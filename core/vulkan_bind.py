import ctypes
import os
import math
import time
import numpy as np
from manim import (
    Square, Circle, Line, Rectangle, Polygon, Polygram,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group
)


def manim_to_screen(x, y, w=800, h=600):
    frame_width = w * 8.0 / h
    sx = w / frame_width
    sy = h / 8.0
    cx, cy = w / 2.0, h / 2.0
    return float(cx + x * sx), float(cy - y * sy)


_anim_opacity = {}
_anim_rotation = {}


def set_anim_opacity(mob, val):
    _anim_opacity[id(mob)] = val


def get_anim_opacity(mob):
    return _anim_opacity.get(id(mob), 1.0)


def set_anim_rotation(mob, val):
    _anim_rotation[id(mob)] = val


def get_anim_rotation(mob):
    return _anim_rotation.get(id(mob), 0.0)


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


# ─── Bezier utilities for vector text rendering ────────────────────────
# Community manim uses CUBIC bezier points:
#   [P0, P1, P2, P3, P0', P1', P2', P3', ...]
#   4 points per curve, get_num_curves() = len(points) // 4


def _integer_interpolate(start, end, alpha):
    if alpha >= 1:
        return (end - 1, 1.0)
    if alpha <= 0:
        return (start, 0.0)
    value = int((end - start) * alpha + start)
    value = min(value, end - 1)
    value = max(value, start)
    residue = ((end - start) * alpha) % 1.0
    return (value, residue)


def _partial_bezier_points(points, a, b):
    """Extract a portion [a,b] of a cubic bezier curve using De Casteljau.
    points: 4 points [P0, P1, P2, P3]"""
    if a <= 0 and b >= 1:
        return [list(p) for p in points]
    pts = [list(p[:3]) for p in points]
    a_to_1 = []
    for i in range(len(pts)):
        seg = pts[i:]
        t = a
        for _ in range(len(seg) - 1):
            seg = [[(1 - t) * seg[j][d] + t * seg[j + 1][d] for d in range(len(seg[0]))]
                   for j in range(len(seg) - 1)]
        a_to_1.append(seg[0])
    end_prop = (b - a) / (1.0 - a) if a < 1.0 else 0.0
    result = []
    for i in range(len(a_to_1)):
        seg = a_to_1[:i + 1]
        t = end_prop
        for _ in range(len(seg) - 1):
            seg = [[(1 - t) * seg[j][d] + t * seg[j + 1][d] for d in range(len(seg[0]))]
                   for j in range(len(seg) - 1)]
        result.append(seg[0])
    return result


def _pointwise_become_partial_points(outline_points, a, b):
    """Extract partial curve from cubic bezier points.
    outline_points: numpy array of shape (N, 3) where N = num_curves * 4.
    Returns list of 3D points (cubic bezier points for the DLL)."""
    nppc = 4
    pts = np.array(outline_points)
    if pts.ndim == 1:
        pts = pts.reshape(-1, 3)
    num_curves = len(pts) // nppc
    if num_curves == 0:
        return []
    if a <= 0 and b >= 1:
        return [list(p) for p in pts]
    lower_index, lower_residue = _integer_interpolate(0, num_curves, a)
    upper_index, upper_residue = _integer_interpolate(0, num_curves, b)
    result = []
    if lower_index == upper_index:
        seg = pts[nppc * lower_index:nppc * (lower_index + 1)]
        result.extend(_partial_bezier_points(seg, lower_residue, upper_residue))
    else:
        seg = pts[nppc * lower_index:nppc * (lower_index + 1)]
        result.extend(_partial_bezier_points(seg, lower_residue, 1.0))
        result.extend([list(p) for p in pts[nppc * (lower_index + 1):nppc * upper_index]])
        seg = pts[nppc * upper_index:nppc * (upper_index + 1)]
        result.extend(_partial_bezier_points(seg, 0.0, upper_residue))
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
        self.interpolate_mobject(alpha)

    def interpolate_mobject(self, alpha):
        pass

    def interpolate_submobject(self, submobject, starting_submobject, alpha):
        pass

    def get_sub_alpha(self, alpha, index, num_submobjects):
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        raw_sub_alpha = max(0.0, min(1.0, value - lower))
        if self.reverse_rate_function:
            return self.rate_func(1.0 - raw_sub_alpha)
        else:
            return self.rate_func(raw_sub_alpha)

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


class DrawBorderThenFill(Animation):
    def __init__(self, mobject, run_time=2.0, stroke_width=2, stroke_color=None,
                 rate_func=_double_smooth, introducer=True, **kwargs):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func,
                         introducer=introducer, **kwargs)
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self._starting_mobject = None

    def get_outline(self):
        outline = self.mobject
        return outline

    def begin(self, t):
        super().begin(t)
        self._starting_mobject = self.mobject.copy() if hasattr(self.mobject, 'copy') else self.mobject

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        self._apply_to_submobjects(alpha)

    def _apply_to_submobjects(self, alpha):
        mob = self.mobject
        if not hasattr(mob, 'submobjects') or not mob.submobjects:
            mob._vulkan_progress = self.rate_func(alpha)
            return
        num_subs = len(mob.submobjects)
        letter_alphas = {}
        for i in range(num_subs):
            sub_alpha = self.get_sub_alpha(alpha, i, num_subs)
            letter_alphas[i] = sub_alpha
        mob._letter_alphas = letter_alphas

    def finish(self):
        super().finish()
        mob = self.mobject
        if hasattr(mob, 'submobjects') and mob.submobjects:
            mob._letter_alphas = {i: 1.0 for i in range(len(mob.submobjects))}
        else:
            mob._vulkan_progress = 1.0


class Write(DrawBorderThenFill):
    def __init__(self, mobject, rate_func=_linear, reverse=False, run_time=None,
                 lag_ratio=None, **kwargs):
        self.reverse = reverse
        if "remover" not in kwargs:
            kwargs["remover"] = reverse
        length = 1
        if hasattr(mobject, 'submobjects'):
            length = max(1, len(mobject.submobjects))
        if run_time is None:
            run_time = 1.0 if length < 15 else 2.0
        if lag_ratio is None:
            lag_ratio = min(4.0 / max(1.0, length), 0.2)
        super().__init__(mobject, run_time=run_time, rate_func=rate_func,
                         introducer=not reverse, **kwargs)
        self.lag_ratio = lag_ratio

    def begin(self, t):
        if self.reverse:
            if hasattr(self.mobject, 'invert'):
                self.mobject.invert(recursive=True)
        super().begin(t)

    def finish(self):
        super().finish()
        if self.reverse:
            if hasattr(self.mobject, 'invert'):
                self.mobject.invert(recursive=True)


class Unwrite(Write):
    def __init__(self, mobject, rate_func=_linear, reverse=True, run_time=1.0, **kwargs):
        super().__init__(mobject, rate_func=rate_func, reverse=reverse, run_time=run_time, **kwargs)

    def finish(self):
        Animation.finish(self)
        mob = self.mobject
        if hasattr(mob, 'submobjects') and mob.submobjects:
            mob._letter_alphas = {i: 0.0 for i in range(len(mob.submobjects))}
        else:
            mob._vulkan_progress = 0.0


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


class FadeIn(Animation):
    def __init__(
        self,
        *mobjects,
        shift=None,
        target_position=None,
        scale=1.0,
        run_time=1.0,
        **kwargs,
    ):
        self.fade_shift = shift
        self.target_position = target_position
        self.fade_scale = scale
        self._start_positions = []
        super().__init__(mobjects[0] if mobjects else None, run_time=run_time, **kwargs)
        self.mobjects = list(mobjects)

    def begin(self, t):
        super().begin(t)
        self._start_positions = []
        for mob in self.mobjects:
            set_anim_opacity(mob, 0.0)
            self._start_positions.append(mob.get_center().copy())

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        for i, mob in enumerate(self.mobjects):
            set_anim_opacity(mob, alpha)

            if self.fade_scale != 1.0:
                scale_factor = self.fade_scale + (1.0 - self.fade_scale) * alpha
                mob.scale(scale_factor / getattr(mob, '_last_fade_scale', self.fade_scale))
                mob._last_fade_scale = scale_factor

            if self.fade_shift is not None and alpha < 1.0:
                mob.move_to(self._start_positions[i] + self.fade_shift * (1.0 - alpha))

            if self.target_position is not None and i < len(self._start_positions):
                if hasattr(self.target_position, 'get_center'):
                    target = self.target_position.get_center()
                else:
                    target = np.array(self.target_position, dtype=float)
                original = self._start_positions[i]
                mob.move_to(target + (original - target) * alpha)

    def finish(self):
        super().finish()
        for mob in self.mobjects:
            set_anim_opacity(mob, 1.0)

    def get_all_mobjects(self):
        return list(self.mobjects)


class FadeOut(Animation):
    def __init__(
        self,
        *mobjects,
        shift=None,
        target_position=None,
        scale=1.0,
        run_time=1.0,
        **kwargs,
    ):
        self.fade_shift = shift
        self.target_position = target_position
        self.fade_scale = scale
        super().__init__(mobjects[0] if mobjects else None, run_time=run_time, **kwargs)
        self.mobjects = list(mobjects)
        self.remover = True
        self._start_positions = []

    def begin(self, t):
        super().begin(t)
        self._start_positions = []
        for mob in self.mobjects:
            self._start_positions.append(mob.get_center().copy())

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        opacity = 1.0 - alpha

        for i, mob in enumerate(self.mobjects):
            set_anim_opacity(mob, opacity)

            if self.fade_scale != 1.0:
                scale_factor = 1.0 + (self.fade_scale - 1.0) * alpha
                mob.scale(scale_factor / getattr(mob, '_last_fade_scale', 1.0))
                mob._last_fade_scale = scale_factor

            if self.fade_shift is not None and alpha > 0.0:
                mob.move_to(self._start_positions[i] + self.fade_shift * alpha)

            if self.target_position is not None and i < len(self._start_positions):
                if hasattr(self.target_position, 'get_center'):
                    target = self.target_position.get_center()
                else:
                    target = np.array(self.target_position, dtype=float)
                original = self._start_positions[i]
                mob.move_to(original + (target - original) * alpha)

    def finish(self):
        super().finish()
        for mob in self.mobjects:
            set_anim_opacity(mob, 0.0)

    def clean_up_from_scene(self, scene):
        for mob in self.mobjects:
            if mob in scene.mobjects:
                scene.remove(mob)

    def get_all_mobjects(self):
        return list(self.mobjects)


class Rotating(Animation):
    def __init__(
        self,
        mobject,
        angle=2 * math.pi,
        about_point=None,
        about_edge=None,
        run_time=5.0,
        rate_func=None,
        **kwargs,
    ):
        self.rot_angle = angle
        self.about_point = about_point
        self.about_edge = about_edge
        super().__init__(mobject, run_time=run_time, rate_func=rate_func or _linear, **kwargs)

    def begin(self, t):
        super().begin(t)
        self._start_rotation = get_anim_rotation(self.mobject)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        current = self._start_rotation + self.rot_angle * alpha
        set_anim_rotation(self.mobject, current)


class Rotate(Animation):
    def __init__(
        self,
        mobject,
        angle=math.pi,
        about_point=None,
        about_edge=None,
        run_time=1.0,
        rate_func=None,
        **kwargs,
    ):
        self.rot_angle = angle
        self.about_point = about_point
        self.about_edge = about_edge
        super().__init__(mobject, run_time=run_time, rate_func=rate_func or _smooth, **kwargs)

    def begin(self, t):
        super().begin(t)
        self._start_rotation = get_anim_rotation(self.mobject)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        current = self._start_rotation + self.rot_angle * alpha
        set_anim_rotation(self.mobject, current)


class Transform(Animation):
    def __init__(self, mobject, target_mobject, replace_mobject_with_target_in_scene=False, run_time=1.0, **kwargs):
        self.target_mobject = target_mobject
        self.replace_mobject_with_target_in_scene = replace_mobject_with_target_in_scene
        super().__init__(mobject, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)
        self._starting_mobject = self.mobject.copy()
        self._target_copy = self.target_mobject.copy()
        try:
            self.mobject.align_data(self._target_copy)
        except Exception:
            pass
        set_anim_opacity(self.mobject, 1.0)
        self._set_transforming(self.mobject, True)
        self._set_transforming(self.target_mobject, True)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        try:
            self.mobject.interpolate(self._starting_mobject, self._target_copy, alpha)
        except Exception:
            pass

    def finish(self):
        super().finish()
        set_anim_opacity(self.mobject, 1.0)
        self._set_transforming(self.mobject, True)
        self._set_transforming(self.target_mobject, False)

    @staticmethod
    def _set_transforming(mob, val):
        Transform._set_transforming_impl(mob, val, set())

    @staticmethod
    def _set_transforming_impl(mob, val, seen):
        mid = id(mob)
        if mid in seen:
            return
        seen.add(mid)
        mob._transforming = val
        if hasattr(mob, 'family_members_with_points'):
            for sub in mob.family_members_with_points():
                Transform._set_transforming_impl(sub, val, seen)
        elif hasattr(mob, 'submobjects'):
            for sub in mob.submobjects:
                Transform._set_transforming_impl(sub, val, seen)

    def clean_up_from_scene(self, scene):
        if self.replace_mobject_with_target_in_scene:
            if self.mobject in scene.mobjects:
                scene.remove(self.mobject)
            if self.target_mobject not in scene.mobjects:
                scene.add(self.target_mobject)
            set_anim_opacity(self.target_mobject, 1.0)
            self._set_transforming(self.target_mobject, False)
        else:
            if self.target_mobject in scene.mobjects:
                scene.remove(self.target_mobject)


class ReplacementTransform(Transform):
    def __init__(self, mobject, target_mobject, **kwargs):
        kwargs['replace_mobject_with_target_in_scene'] = True
        super().__init__(mobject, target_mobject, **kwargs)


class FadeTransform(Animation):
    def __init__(self, mobject, target_mobject, run_time=1.0, **kwargs):
        self.target_mobject = target_mobject
        self.to_add_on_completion = target_mobject
        self._source_start_pos = None
        self._target_start_pos = None
        try:
            self._ghost = target_mobject.copy()
            self._ghost.move_to(mobject.get_center())
        except Exception:
            self._ghost = None
        super().__init__(mobject, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)
        self.mobject.save_state()
        self.target_mobject.save_state()
        self._source_start_pos = self.mobject.get_center().copy()
        self._target_start_pos = self.target_mobject.get_center().copy()
        if self._ghost is not None:
            self._ghost.move_to(self._source_start_pos)
        set_anim_opacity(self.mobject, 1.0)
        set_anim_opacity(self.target_mobject, 1.0)
        if self._ghost is not None:
            set_anim_opacity(self._ghost, 0.0)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        cur_pos = (
            self._source_start_pos * (1.0 - alpha)
            + self._target_start_pos * alpha
        )
        self.mobject.move_to(cur_pos)
        if self._ghost is not None:
            self._ghost.move_to(cur_pos)
            set_anim_opacity(self._ghost, max(0.0, alpha))
        set_anim_opacity(self.mobject, max(0.0, 1.0 - alpha))
        set_anim_opacity(self.target_mobject, 1.0)

    def finish(self):
        super().finish()
        self.mobject.move_to(self._target_start_pos)
        set_anim_opacity(self.mobject, 0.0)
        set_anim_opacity(self.target_mobject, 1.0)
        if self._ghost is not None:
            set_anim_opacity(self._ghost, 0.0)
        try:
            self.mobject.restore()
            self.target_mobject.restore()
        except Exception:
            pass

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if self.mobject in scene.mobjects:
            scene.remove(self.mobject)
        if self._ghost is not None and self._ghost in scene.mobjects:
            scene.remove(self._ghost)
        if self.target_mobject not in scene.mobjects:
            scene.add(self.target_mobject)
        set_anim_opacity(self.target_mobject, 1.0)

    def get_all_mobjects(self):
        mobs = [self.mobject, self.target_mobject]
        if self._ghost is not None:
            mobs.append(self._ghost)
        return mobs


def _normalize_points(pts):
    if len(pts) == 0:
        return ()
    import numpy as _np
    arr = _np.array(pts, dtype=float)
    center = arr.mean(axis=0)
    arr = arr - center
    height = arr[:, 1].max() - arr[:, 1].min()
    if height > 1e-6:
        arr = arr / height
    return tuple(tuple(round(c, 3) for c in row) for row in arr)


class TransformMatchingAbstractBase(Animation):
    def __init__(
        self,
        mobject,
        target_mobject,
        transform_mismatches=False,
        fade_transform_mismatches=False,
        key_map=None,
        run_time=1.0,
        **kwargs,
    ):
        self.target_mobject = target_mobject
        self.transform_mismatches = transform_mismatches
        self.fade_transform_mismatches = fade_transform_mismatches
        self.key_map = key_map or {}
        self._anims = []
        self._scene = None
        super().__init__(mobject, run_time=run_time, **kwargs)

    def get_shape_map(self, mobject):
        shape_map = {}
        for sm in self.get_mobject_parts(mobject):
            key = self.get_mobject_key(sm)
            if key not in shape_map:
                shape_map[key] = VGroup()
            shape_map[key].add(sm)
        return shape_map

    def begin(self, t):
        super().begin(t)
        if hasattr(self.mobject, '_letter_alphas'):
            self.mobject._letter_alphas = None
        if hasattr(self.target_mobject, '_letter_alphas'):
            self.target_mobject._letter_alphas = None

        source_map = self.get_shape_map(self.mobject)
        target_map = self.get_shape_map(self.target_mobject)

        transform_source = VGroup()
        transform_target = VGroup()
        for key in set(source_map).intersection(target_map):
            transform_source.add(source_map[key])
            transform_target.add(target_map[key])
        self._anims.append(
            Transform(transform_source, transform_target, run_time=self.run_time)
        )

        key_mapped_source = VGroup()
        key_mapped_target = VGroup()
        for key1, key2 in self.key_map.items():
            if key1 in source_map and key2 in target_map:
                key_mapped_source.add(source_map[key1])
                key_mapped_target.add(target_map[key2])
                source_map.pop(key1, None)
                target_map.pop(key2, None)
        if len(key_mapped_source.submobjects) > 0:
            self._anims.append(
                FadeTransform(key_mapped_source, key_mapped_target, run_time=self.run_time)
            )

        fade_source = VGroup()
        fade_target = VGroup()
        for key in set(source_map).difference(target_map):
            fade_source.add(source_map[key])
        for key in set(target_map).difference(source_map):
            fade_target.add(target_map[key])

        if self.transform_mismatches:
            self._anims.append(
                Transform(fade_source, fade_target, run_time=self.run_time,
                          replace_mobject_with_target_in_scene=True)
            )
        elif self.fade_transform_mismatches:
            self._anims.append(
                FadeTransformPieces(fade_source, fade_target, run_time=self.run_time)
            )
        else:
            self._anims.append(
                FadeOut(self.mobject, target_position=fade_target, run_time=self.run_time)
            )

        for anim in self._anims:
            anim.begin(t)

    def interpolate(self, t):
        for anim in self._anims:
            anim.interpolate(t)

    def finish(self):
        super().finish()
        for anim in self._anims:
            anim.finish()

    def get_all_mobjects(self):
        return [self.mobject, self.target_mobject]

    def clean_up_from_scene(self, scene):
        if self.mobject in scene.mobjects:
            scene.remove(self.mobject)
        if self.target_mobject not in scene.mobjects:
            scene.add(self.target_mobject)
        if hasattr(self.mobject, '_transforming'):
            self.mobject._transforming = False
        if hasattr(self.target_mobject, '_transforming'):
            self.target_mobject._transforming = False

    @staticmethod
    def get_mobject_parts(mobject):
        if hasattr(mobject, 'family_members_with_points'):
            return mobject.family_members_with_points()
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        raise NotImplementedError


class TransformMatchingShapes(TransformMatchingAbstractBase):
    @staticmethod
    def get_mobject_parts(mobject):
        if hasattr(mobject, 'family_members_with_points'):
            return mobject.family_members_with_points()
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        mobject.save_state()
        mobject.center()
        mobject.set(height=1)
        rounded_points = np.round(mobject.points, 3) + 0.0
        result = hash(rounded_points.tobytes())
        mobject.restore()
        return result


class TransformMatchingTex(TransformMatchingAbstractBase):
    @staticmethod
    def get_mobject_parts(mobject):
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        return getattr(mobject, 'tex_string',
                       getattr(mobject, '_tex_string',
                               str(id(mobject))))


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
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddCircle.restype = None
        self.dll.AddCircle.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddLine.restype = None
        self.dll.AddLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddEllipse.restype = None
        self.dll.AddEllipse.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddPolygon.restype = None
        self.dll.AddPolygon.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_float,
        ]
        self.dll.AddDashedLine.restype = None
        self.dll.AddDashedLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddArc.restype = None
        self.dll.AddArc.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddPoint.restype = None
        self.dll.AddPoint.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddBezierPath.restype = None
        self.dll.AddBezierPath.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_float, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]

        self.dll.SaveScreenshot.restype = ctypes.c_int
        self.dll.SaveScreenshot.argtypes = [ctypes.c_char_p]

        if self.dll.Vulkan_Init(w, h) != 1:
            raise RuntimeError("Vulkan_Init failed")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        for mob in scene.mobjects:
            self._send(mob, angle, parent_alpha=1.0)

    def _send(self, mob, angle=0.0, parent_alpha=1.0, parent_offset=None):
        w, h = self.win_w, self.win_h
        own_alpha = get_anim_opacity(mob)
        a = parent_alpha * own_alpha
        if a <= 0:
            return

        rot = get_anim_rotation(mob) + angle

        if isinstance(mob, Text):
            if getattr(mob, '_letter_alphas', None) is not None and hasattr(mob, 'submobjects') and mob.submobjects:
                self._send_text_write(mob, mob._letter_alphas, w, h, a)
            elif hasattr(mob, 'submobjects') and mob.submobjects:
                if a < 1.0:
                    self._send_transformed_text(mob, w, h, alpha=a)
                else:
                    self._send_text_bitmap(mob, w, h, a)

        elif isinstance(mob, (VGroup, Group)):
            own_alpha = get_anim_opacity(mob)
            effective_alpha = parent_alpha * own_alpha
            if effective_alpha <= 0:
                return
            vgroup_center = np.array(mob.get_center(), dtype=float)
            try:
                original_center = np.array(mob.get_points().mean(axis=0) if len(mob.get_points()) > 0 else mob.get_center(), dtype=float)
            except Exception:
                original_center = vgroup_center.copy()
            offset = vgroup_center - original_center
            if parent_offset is not None:
                offset = offset + parent_offset
            for sub in mob:
                self._send(sub, angle, parent_alpha=effective_alpha, parent_offset=offset)
            return

        if getattr(mob, '_transforming', False):
            self._send_vmobject(mob, a, w, h, parent_offset)
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
                progress = getattr(mob, '_vulkan_progress', 1.0)
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
                progress = getattr(mob, '_vulkan_progress', 1.0)
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
                progress = getattr(mob, '_vulkan_progress', 1.0)
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
                progress = getattr(mob, '_vulkan_progress', 1.0)
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

        elif isinstance(mob, Arrow):
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
                    sx2, sy2, 0.0,
                    sx2, sy2, 0.0,
                    hx1, hy1, 0.0,
                    hx1, hy1, 0.0,
                    hx1, hy1, 0.0,
                    hx1, hy1, 0.0,
                    hx2, hy2, 0.0,
                    hx2, hy2, 0.0,
                    hx2, hy2, 0.0,
                    hx2, hy2, 0.0,
                    sx2, sy2, 0.0,
                    sx2, sy2, 0.0,
                ]
                head_arr = (ctypes.c_float * len(head_pts))(*head_pts)
                self.dll.AddBezierPath(
                    head_arr, 12,
                    r, g, b, float(sw),
                    r, g, b, 1.0,
                    1.0, 1, 1, a,
                )

        elif isinstance(mob, Line):
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

        elif isinstance(mob, Dot):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_y = h / 8.0
            rad = mob.radius * scale_y if hasattr(mob, 'radius') else 6.0
            r, g, b = self._color(mob, a)
            self.dll.AddCircle(sx, sy, rad, r, g, b, 0, 0, 0, 0.0, 1.0, a)

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
            self.dll.AddDashedLine(sx1, sy1, sx2, sy2, sw, r, g, b, dl, gl, a)

        elif isinstance(mob, Arc):
            cx, cy, _ = mob.get_center()
            sx, sy = manim_to_screen(cx, cy, w, h)
            scale_y = h / 8.0
            rad = mob.radius * scale_y if hasattr(mob, 'radius') else 100.0
            sa = mob.start_angle if hasattr(mob, 'start_angle') else 0
            ang = mob.angle if hasattr(mob, 'angle') else math.pi
            r, g, b = self._stroke_color(mob)
            sw = max(1, round(self._stroke_width(mob)))
            self.dll.AddArc(sx, sy, rad, sa, ang, r, g, b, sw, a)

        elif isinstance(mob, Polygon):
            verts = mob.get_vertices()
            self._send_polygon(mob, verts, a)

        elif isinstance(mob, Polygram):
            verts = mob.get_vertices()
            self._send_polygon(mob, verts, a)

        elif isinstance(mob, Point):
            pos = mob.get_location()
            sx, sy = manim_to_screen(pos[0], pos[1], w, h)
            r, g, b = self._color(mob, a)
            self.dll.AddPoint(sx, sy, r, g, b, a)

        else:
            try:
                pts = mob.get_points()
                if len(pts) >= 4:
                    self._send_vmobject(mob, a, w, h, parent_offset)
            except Exception:
                pass

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

    def _fill_quad_alpha(self, x0, y0, x1, y1, x2, y2, x3, y3, r, g, b, alpha):
        w, h = self.win_w, self.win_h
        corners = [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]
        flat = []
        for i in range(4):
            j = (i + 1) % 4
            for _ in range(4):
                sx, sy = manim_to_screen(corners[i][0], corners[i][1], w, h)
                flat.extend([sx, sy, 0.0])
        arr = (ctypes.c_float * len(flat))(*flat)
        ri, gi, bi = int(r), int(g), int(b)
        self.dll.AddBezierPath(
            arr, 16,
            ri, gi, bi, 0.0,
            ri, gi, bi, 1.0,
            1.0, 0, 1, alpha,
        )

    def _color(self, mob, alpha=1.0):
        try:
            rgbas = mob.get_fill_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                fo = float(a)
                return int(r * 255 * alpha * fo), int(g * 255 * alpha * fo), int(b * 255 * alpha * fo)
        except Exception:
            pass
        try:
            rgbas = mob.get_stroke_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                return int(r * 255 * alpha), int(g * 255 * alpha), int(b * 255 * alpha)
        except Exception:
            pass
        return int(255 * alpha), int(255 * alpha), int(255 * alpha)

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

    def _rotate_point(self, x, y, cx, cy, angle):
        if angle == 0:
            return x, y
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        dx = x - cx
        dy = y - cy
        nx = dx * cos_a - dy * sin_a + cx
        ny = dx * sin_a + dy * cos_a + cy
        return nx, ny

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

        screenshot_at = kwargs.get('screenshot_at', None)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))

        all_mobjects = list(add_mobs)
        for anim in animations:
            if isinstance(anim, (Create, Write, FadeIn, Rotating, Rotate)) and anim.mobject:
                if isinstance(anim, Create):
                    anim.mobject._vulkan_progress = 0.0
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
            elif isinstance(anim, (FadeIn, FadeOut)):
                for mob in anim.mobjects:
                    if isinstance(anim, FadeIn):
                        set_anim_opacity(mob, 0.0)
                    if mob not in all_mobjects:
                        all_mobjects.append(mob)
            elif isinstance(anim, TransformMatchingAbstractBase):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.target_mobject not in all_mobjects:
                    all_mobjects.append(anim.target_mobject)
                anim.mobject._transforming = True
                for sub_anim in getattr(anim, '_anims', []):
                    if isinstance(sub_anim, (FadeIn, FadeOut)):
                        for mob in sub_anim.mobjects:
                            if isinstance(sub_anim, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub_anim, Transform):
                        if sub_anim.mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.mobject)
                        if sub_anim.target_mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.target_mobject)
            elif isinstance(anim, Transform):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.replace_mobject_with_target_in_scene:
                    if anim.target_mobject not in all_mobjects:
                        all_mobjects.append(anim.target_mobject)
                    set_anim_opacity(anim.target_mobject, 0.0)
            elif isinstance(anim, FadeTransform):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.target_mobject not in all_mobjects:
                    all_mobjects.append(anim.target_mobject)
                ghost = getattr(anim, '_ghost', None)
                if ghost is not None and ghost not in all_mobjects:
                    all_mobjects.append(ghost)
            elif isinstance(anim, Succession):
                for sub in anim.animations:
                    if isinstance(sub, (Create, Write, FadeIn, Rotating, Rotate)) and sub.mobject:
                        if isinstance(sub, Create):
                            sub.mobject._vulkan_progress = 0.0
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                    elif isinstance(sub, (FadeIn, FadeOut)):
                        for mob in sub.mobjects:
                            if isinstance(sub, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub, TransformMatchingAbstractBase):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        if hasattr(sub, '_fade_target_copy') and sub._fade_target_copy not in all_mobjects:
                            all_mobjects.append(sub._fade_target_copy)
                        sub.mobject._transforming = True
                        for sub_anim in getattr(sub, '_anims', []):
                            if isinstance(sub_anim, (FadeIn, FadeOut)):
                                for mob in sub_anim.mobjects:
                                    if isinstance(sub_anim, FadeIn):
                                        set_anim_opacity(mob, 0.0)
                                    if mob not in all_mobjects:
                                        all_mobjects.append(mob)
                            elif isinstance(sub_anim, Transform):
                                if sub_anim.mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.mobject)
                                if sub_anim.target_mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.target_mobject)
                    elif isinstance(sub, FadeTransform):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        ghost = getattr(sub, '_ghost', None)
                        if ghost is not None and ghost not in all_mobjects:
                            all_mobjects.append(ghost)

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

        for a in real_anims:
            if isinstance(a, TransformMatchingAbstractBase):
                for sub_anim in getattr(a, '_anims', []):
                    if isinstance(sub_anim, Transform):
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                        if sub_anim.target_mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.target_mobject)

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

            if screenshot_at:
                for a in self._active_anims:
                    if a in screenshot_at:
                        alpha = (now - a.start_time) / a.run_time if a.run_time > 0 else 1.0
                        alpha = max(0.0, min(1.0, alpha))
                        alpha = a.rate_func(alpha)
                        for threshold, path in screenshot_at[a]:
                            if abs(alpha - threshold) < 0.02:
                                self.screenshot(path)
                                del screenshot_at[a][screenshot_at[a].index((threshold, path))]
                                break

            if all_done:
                break

            elapsed = time.time() - frame_start
            if elapsed < FRAME_DURATION:
                time.sleep(FRAME_DURATION - elapsed)

        for a in real_anims:
            if hasattr(a, 'clean_up_from_scene'):
                a.clean_up_from_scene(self.scene)

    def screenshot(self, path):
        path_bytes = path.encode('utf-8') if isinstance(path, str) else path
        return self.dll.SaveScreenshot(path_bytes)

    def close(self):
        self.dll.Vulkan_Shutdown()
