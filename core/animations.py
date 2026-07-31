import math
import numpy as np
from functools import partialmethod
from manim import VGroup, Group

TAU = 2.0 * math.pi
from core.rate_functions import (
    _smooth, _linear, _double_smooth, _there_and_back,
)

DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0.0
TARGET_FPS = 60
FRAME_DURATION = 1.0 / TARGET_FPS

_anim_opacity = {}
_anim_rotation = {}
_anim_rotation_delta = {}


def set_anim_opacity(mob, val):
    _anim_opacity[id(mob)] = val


def get_anim_opacity(mob):
    return _anim_opacity.get(id(mob), 1.0)


def set_anim_rotation(mob, val):
    _anim_rotation[id(mob)] = val


def get_anim_rotation(mob):
    return _anim_rotation.get(id(mob), 0.0)


def set_anim_rotation_delta(mob, val):
    _anim_rotation_delta[id(mob)] = val


def get_anim_rotation_delta(mob):
    return _anim_rotation_delta.get(id(mob), 0.0)


def clear_anim_rotation_delta():
    _anim_rotation_delta.clear()


class Animation:
    _original__init__ = None

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

    @classmethod
    def set_default(cls, **kwargs):
        if cls._original__init__ is None:
            cls._original__init__ = cls.__init__
        if kwargs:
            cls.__init__ = partialmethod(cls.__init__, **kwargs)
        else:
            cls.__init__ = cls._original__init__

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '_original__init__' not in cls.__dict__:
            cls._original__init__ = cls.__init__

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

    def get_sub_alpha(self, alpha, index, num_submobjects):
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        raw_sub_alpha = max(0.0, min(1.0, value - lower))
        return self.rate_func(raw_sub_alpha)

    def clean_up_from_scene(self, scene):
        pass

    def get_all_mobjects(self):
        if self.mobject is not None:
            return [self.mobject]
        return []


class SpiralIn(Animation):
    def __init__(self, shapes, scale_factor=8, fade_in_fraction=0.3, run_time=1.0, **kwargs):
        self.shapes_data = []
        self.scale_factor = scale_factor
        self.shape_center = shapes.get_center().copy()
        self.fade_in_fraction = fade_in_fraction
        for shape in shapes:
            final_pos = shape.get_center().copy()
            initial_pos = final_pos + (final_pos - self.shape_center) * scale_factor
            self.shapes_data.append({
                'mobject': shape,
                'final_position': final_pos,
                'initial_position': initial_pos,
            })
            shape.move_to(initial_pos)
            set_anim_opacity(shape, 0.0)
        super().__init__(shapes, run_time=run_time, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        for data in self.shapes_data:
            shape = data['mobject']
            init = data['initial_position']
            final = data['final_position']
            linear_pos = init + (final - init) * alpha
            dx = linear_pos[0] - self.shape_center[0]
            dy = linear_pos[1] - self.shape_center[1]
            angle = TAU * alpha
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            cx = self.shape_center[0] + dx * cos_a - dy * sin_a
            cy = self.shape_center[1] + dx * sin_a + dy * cos_a
            shape.move_to(np.array([cx, cy, 0.0]))
            fade = min(1.0, alpha / self.fade_in_fraction) if self.fade_in_fraction > 0 else 1.0
            set_anim_opacity(shape, fade)

    def finish(self):
        super().finish()
        for data in self.shapes_data:
            shape = data['mobject']
            shape.move_to(data['final_position'])
            set_anim_opacity(shape, 1.0)


class ShowIncreasingSubsets(Animation):
    def __init__(self, group, int_func=None, run_time=2.0, **kwargs):
        self.all_submobs = list(group.submobjects)
        self.int_func = int_func
        for mobj in self.all_submobs:
            set_anim_opacity(mobj, 0.0)
            try:
                mobj.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                mobj.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
        super().__init__(group, run_time=run_time, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        n_submobs = len(self.all_submobs)
        if self.int_func is not None:
            index = int(self.int_func(alpha * n_submobs))
        else:
            index = int(np.floor(alpha * n_submobs))
        self.update_submobject_list(index)

    def _set_mobj_visible(self, mobj):
        set_anim_opacity(mobj, 1.0)
        try:
            mobj.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            mobj.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass

    def _set_mobj_hidden(self, mobj):
        set_anim_opacity(mobj, 0.0)
        try:
            mobj.fill_rgbas[:, 3] = 0.0
        except Exception:
            pass
        try:
            mobj.stroke_rgbas[:, 3] = 0.0
        except Exception:
            pass

    def update_submobject_list(self, index):
        for mobj in self.all_submobs[:index]:
            self._set_mobj_visible(mobj)
        for mobj in self.all_submobs[index:]:
            self._set_mobj_hidden(mobj)

    def finish(self):
        super().finish()
        for mobj in self.all_submobs:
            self._set_mobj_visible(mobj)


class Create(Animation):
    def __init__(self, mobject, run_time=1.0, lag_ratio=1.0, **kwargs):
        super().__init__(mobject, run_time=run_time, lag_ratio=lag_ratio, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        self.mobject._vulkan_progress = alpha


class Uncreate(Create):
    def __init__(self, mobject, run_time=1.0, lag_ratio=1.0, remover=True,
                 rate_func=None, **kwargs):
        if rate_func is None:
            rate_func = lambda t: 1.0 - t
        super().__init__(mobject, run_time=run_time, lag_ratio=lag_ratio,
                         remover=remover, rate_func=rate_func, **kwargs)


class DrawBorderThenFill(Animation):
    def __init__(self, mobject, run_time=2.0, stroke_width=2, stroke_color=None,
                 rate_func=_double_smooth, introducer=True, **kwargs):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func,
                         introducer=introducer, **kwargs)
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def begin(self, t):
        super().begin(t)
        self._starting_mobject = self.mobject.copy() if hasattr(self.mobject, 'copy') else self.mobject
        mob = self.mobject
        self._orig_fill_opacity = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0
        self._orig_stroke_opacity = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        self._apply_two_phase(alpha)

    def _apply_two_phase(self, alpha):
        mob = self.mobject
        has_subs = hasattr(mob, 'submobjects') and mob.submobjects
        if has_subs:
            num_subs = len(mob.submobjects)
            for i in range(num_subs):
                sub = mob.submobjects[i]
                sub_alpha = self.get_sub_alpha(alpha, i, num_subs)
                self._apply_single_two_phase(sub, sub_alpha)
            mob._letter_alphas = {i: self.get_sub_alpha(alpha, i, num_subs) for i in range(num_subs)}
        else:
            self._apply_single_two_phase(mob, alpha)

    def _set_fo(self, mob, value):
        if hasattr(mob, 'fill_rgbas') and mob.fill_rgbas is not None and len(mob.fill_rgbas) > 0:
            mob.fill_rgbas[:, 3] = value
        elif hasattr(mob, 'set'):
            mob.set(fill_opacity=value)

    def _set_so(self, mob, value):
        if hasattr(mob, 'stroke_rgbas') and mob.stroke_rgbas is not None and len(mob.stroke_rgbas) > 0:
            mob.stroke_rgbas[:, 3] = value
        elif hasattr(mob, 'set'):
            mob.set(stroke_opacity=value)

    def _apply_single_two_phase(self, mob, alpha):
        border_frac = 0.5
        if alpha < border_frac:
            stroke_alpha = self.rate_func(alpha / border_frac)
            mob._vulkan_progress = stroke_alpha
            self._set_fo(mob, 0.0)
            self._set_so(mob, self._orig_stroke_opacity)
        else:
            fill_alpha = (alpha - border_frac) / (1.0 - border_frac)
            mob._vulkan_progress = 1.0
            self._set_fo(mob, self._orig_fill_opacity * fill_alpha)
            self._set_so(mob, self._orig_stroke_opacity)

    def finish(self):
        super().finish()
        mob = self.mobject
        if hasattr(mob, 'submobjects') and mob.submobjects:
            mob._letter_alphas = {i: 1.0 for i in range(len(mob.submobjects))}
        else:
            mob._vulkan_progress = 1.0
        self._set_fo(mob, self._orig_fill_opacity)
        self._set_so(mob, self._orig_stroke_opacity)


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
        self._unwrite_reverse = reverse
        super().__init__(mobject, rate_func=rate_func, reverse=False, run_time=run_time, **kwargs)

    def begin(self, t):
        super(Write, self).begin(t)

    def _apply_two_phase(self, alpha):
        mob = self.mobject
        has_subs = hasattr(mob, 'submobjects') and mob.submobjects
        if has_subs:
            num_subs = len(mob.submobjects)
            letter_alphas = {}
            for i in range(num_subs):
                if self._unwrite_reverse:
                    idx = num_subs - 1 - i
                else:
                    idx = i
                sub_alpha = self.get_sub_alpha(alpha, idx, num_subs)
                letter_alphas[i] = self.rate_func(1.0 - sub_alpha)
            mob._letter_alphas = letter_alphas
        else:
            mob._vulkan_progress = self.rate_func(1.0 - alpha)

    def finish(self):
        Animation.finish(self)
        mob = self.mobject
        if hasattr(mob, 'submobjects') and mob.submobjects:
            mob._letter_alphas = {i: 0.0 for i in range(len(mob.submobjects))}
        else:
            mob._vulkan_progress = 0.0


class Succession(Animation):
    def __init__(self, *animations, rate_func=None, **kwargs):
        from manim.mobject.mobject import _AnimationBuilder
        resolved = []
        for a in animations:
            if isinstance(a, _AnimationBuilder):
                resolved.append(a.build())
            else:
                resolved.append(a)
        self.animations = resolved
        total = sum(a.run_time for a in self.animations)
        kwargs.pop('run_time', None)
        super().__init__(run_time=total, rate_func=rate_func, **kwargs)
        self._begun = set()

    def begin(self, t):
        super().begin(t)
        self._begun = set()

    def interpolate(self, t):
        elapsed = t - self.start_time
        total = self.run_time
        if total > 0:
            raw_alpha = max(0.0, min(1.0, elapsed / total))
            mapped_alpha = self.rate_func(raw_alpha)
            elapsed = mapped_alpha * total
        cumulative = 0.0
        for i, a in enumerate(self.animations):
            end = cumulative + a.run_time
            is_manim = type(a).__module__.startswith('manim')
            if a.run_time > 0:
                active = elapsed >= cumulative and elapsed < end
            else:
                active = elapsed >= cumulative and i not in self._begun
            if active:
                if i not in self._begun:
                    if is_manim:
                        a.begin()
                    else:
                        a.begin(t)
                    self._begun.add(i)
                if is_manim:
                    sub_alpha = (elapsed - cumulative) / a.run_time if a.run_time > 0 else 1.0
                    sub_alpha = max(0.0, min(1.0, sub_alpha))
                    a.interpolate(sub_alpha)
                else:
                    a.interpolate(t)
                return
            cumulative = end
        if self.animations:
            last_idx = len(self.animations) - 1
            if last_idx not in self._begun:
                is_manim = type(self.animations[last_idx]).__module__.startswith('manim')
                if is_manim:
                    self.animations[last_idx].begin()
                else:
                    self.animations[last_idx].begin(t)
                self._begun.add(last_idx)
            is_manim = type(self.animations[last_idx]).__module__.startswith('manim')
            if is_manim:
                self.animations[last_idx].interpolate(1.0)
            else:
                self.animations[last_idx].interpolate(t)

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
        rate_func=None,
        **kwargs,
    ):
        super().__init__(None, run_time=run_time, rate_func=rate_func or _linear, **kwargs)

    def interpolate(self, alpha):
        pass


class Add(Animation):
    def __init__(self, *mobjects, run_time=0.0, **kwargs):
        self.mobjects = list(mobjects)
        super().__init__(mobjects[0] if mobjects else None, run_time=run_time, **kwargs)

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
        self._orig_radius = {}
        self._orig_stroke_width = {}
        self._orig_points = {}
        for mob in self.mobjects:
            set_anim_opacity(mob, 0.0)
            self._start_positions.append(mob.get_center().copy())
            if hasattr(mob, 'radius'):
                self._orig_radius[id(mob)] = mob.radius
            if hasattr(mob, 'stroke_width'):
                self._orig_stroke_width[id(mob)] = mob.stroke_width
            if self.fade_scale != 1.0 and not hasattr(mob, 'radius'):
                self._orig_points[id(mob)] = [
                    (fm, fm.get_points().copy())
                    for fm in mob.family_members_with_points()
                    if fm is not mob
                ]

    def interpolate(self, t):
        if getattr(self, '_use_alpha', False):
            alpha = float(t)
        else:
            alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
            alpha = max(0.0, min(1.0, alpha))
            if self.reverse_rate_function:
                alpha = 1.0 - alpha
            alpha = self.rate_func(alpha)

        for i, mob in enumerate(self.mobjects):
            set_anim_opacity(mob, alpha)

            if self.fade_scale != 1.0:
                target_scale = self.fade_scale + (1.0 - self.fade_scale) * alpha
                if id(mob) in self._orig_radius:
                    mob.radius = self._orig_radius[id(mob)] * target_scale
                    if id(mob) in self._orig_stroke_width:
                        mob.stroke_width = self._orig_stroke_width[id(mob)] * target_scale
                elif id(mob) in self._orig_points:
                    cx, cy = self._start_positions[i][0], self._start_positions[i][1]
                    for fm, orig in self._orig_points[id(mob)]:
                        scaled = orig.copy()
                        scaled[:, 0] = cx + (orig[:, 0] - cx) * target_scale
                        scaled[:, 1] = cy + (orig[:, 1] - cy) * target_scale
                        fm.points = scaled

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
            for fm, orig in self._orig_points.get(id(mob), []):
                fm.points = orig.copy()

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
        self._orig_radius = {}
        self._orig_stroke_width = {}
        self._orig_points = {}
        for mob in self.mobjects:
            set_anim_opacity(mob, 1.0)
            self._start_positions.append(mob.get_center().copy())
            if hasattr(mob, 'radius'):
                self._orig_radius[id(mob)] = mob.radius
            if hasattr(mob, 'stroke_width'):
                self._orig_stroke_width[id(mob)] = mob.stroke_width
            if self.fade_scale != 1.0 and not hasattr(mob, 'radius'):
                self._orig_points[id(mob)] = [
                    (fm, fm.get_points().copy())
                    for fm in mob.family_members_with_points()
                    if fm is not mob
                ]

    def interpolate(self, t):
        if getattr(self, '_use_alpha', False):
            alpha = float(t)
        else:
            alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
            alpha = max(0.0, min(1.0, alpha))
            if self.reverse_rate_function:
                alpha = 1.0 - alpha
            alpha = self.rate_func(alpha)
        opacity = 1.0 - alpha

        for i, mob in enumerate(self.mobjects):
            set_anim_opacity(mob, opacity)

            if self.fade_scale != 1.0:
                target_scale = 1.0 + (self.fade_scale - 1.0) * alpha
                if id(mob) in self._orig_radius:
                    mob.radius = self._orig_radius[id(mob)] * target_scale
                    if id(mob) in self._orig_stroke_width:
                        mob.stroke_width = self._orig_stroke_width[id(mob)] * target_scale
                elif id(mob) in self._orig_points:
                    cx, cy = self._start_positions[i][0], self._start_positions[i][1]
                    for fm, orig in self._orig_points[id(mob)]:
                        scaled = orig.copy()
                        scaled[:, 0] = cx + (orig[:, 0] - cx) * target_scale
                        scaled[:, 1] = cy + (orig[:, 1] - cy) * target_scale
                        fm.points = scaled

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
            for fm, orig in self._orig_points.get(id(mob), []):
                fm.points = orig.copy()


class GrowArrow(Animation):
    def __init__(self, arrow, point_color=None, run_time=1.0, **kwargs):
        self.point_color = point_color
        self._orig_fill = None
        self._orig_stroke = None
        self._orig_stroke_width = None
        super().__init__(arrow, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        self._grow_point = mob.get_start()

        if hasattr(mob, 'get_fill_rgbas'):
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    self._orig_fill = [float(frgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'get_stroke_rgbas'):
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    self._orig_stroke = [float(srgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'stroke_width'):
            self._orig_stroke_width = mob.stroke_width

        mob._grow_scale = 0.0
        mob._grow_point = self._grow_point
        if self.point_color:
            self._pc = (self.point_color[0], self.point_color[1], self.point_color[2])
            mob.set_color(self.point_color)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        mob._grow_scale = alpha
        if self.point_color and self._orig_fill:
            fr, fg, fb = self._orig_fill[0], self._orig_fill[1], self._orig_fill[2]
            cr = self._pc[0] + (fr - self._pc[0]) * alpha
            cg = self._pc[1] + (fg - self._pc[1]) * alpha
            cb = self._pc[2] + (fb - self._pc[2]) * alpha
            if hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
                mob.fill_rgbas[:, 0] = cr
                mob.fill_rgbas[:, 1] = cg
                mob.fill_rgbas[:, 2] = cb
        if self.point_color and self._orig_stroke:
            fr, fg, fb = self._orig_stroke[0], self._orig_stroke[1], self._orig_stroke[2]
            cr = self._pc[0] + (fr - self._pc[0]) * alpha
            cg = self._pc[1] + (fg - self._pc[1]) * alpha
            cb = self._pc[2] + (fb - self._pc[2]) * alpha
            if hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
                mob.stroke_rgbas[:, 0] = cr
                mob.stroke_rgbas[:, 1] = cg
                mob.stroke_rgbas[:, 2] = cb

    def finish(self):
        super().finish()
        mob = self.mobject
        if hasattr(mob, '_grow_scale'):
            del mob._grow_scale
        if hasattr(mob, '_grow_point'):
            del mob._grow_point
        if self._orig_fill and hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
            mob.fill_rgbas[:, 0] = self._orig_fill[0]
            mob.fill_rgbas[:, 1] = self._orig_fill[1]
            mob.fill_rgbas[:, 2] = self._orig_fill[2]
        if self._orig_stroke and hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
            mob.stroke_rgbas[:, 0] = self._orig_stroke[0]
            mob.stroke_rgbas[:, 1] = self._orig_stroke[1]
            mob.stroke_rgbas[:, 2] = self._orig_stroke[2]
        if self._orig_stroke_width is not None:
            try:
                mob.stroke_width = self._orig_stroke_width
            except Exception:
                pass


class GrowFromCenter(GrowArrow):
    def begin(self, t):
        Animation.begin(self, t)
        mob = self.mobject
        self._grow_point = mob.get_center()

        if hasattr(mob, 'get_fill_rgbas'):
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    self._orig_fill = [float(frgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'get_stroke_rgbas'):
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    self._orig_stroke = [float(srgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'stroke_width'):
            self._orig_stroke_width = mob.stroke_width

        mob._grow_scale = 0.0
        mob._grow_point = self._grow_point
        if self.point_color:
            self._pc = (float(self.point_color[0]), float(self.point_color[1]), float(self.point_color[2]))
            if hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
                mob.fill_rgbas[:, 0] = self._pc[0]
                mob.fill_rgbas[:, 1] = self._pc[1]
                mob.fill_rgbas[:, 2] = self._pc[2]
            if hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
                mob.stroke_rgbas[:, 0] = self._pc[0]
                mob.stroke_rgbas[:, 1] = self._pc[1]
                mob.stroke_rgbas[:, 2] = self._pc[2]


class GrowFromEdge(GrowArrow):
    def __init__(self, mobject, edge, point_color=None, run_time=1.0, **kwargs):
        self.edge = edge
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def begin(self, t):
        Animation.begin(self, t)
        mob = self.mobject
        self._grow_point = mob.get_critical_point(self.edge)

        if hasattr(mob, 'get_fill_rgbas'):
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    self._orig_fill = [float(frgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'get_stroke_rgbas'):
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    self._orig_stroke = [float(srgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'stroke_width'):
            self._orig_stroke_width = mob.stroke_width

        mob._grow_scale = 0.0
        mob._grow_point = self._grow_point
        if self.point_color:
            self._pc = (float(self.point_color[0]), float(self.point_color[1]), float(self.point_color[2]))
            if hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
                mob.fill_rgbas[:, 0] = self._pc[0]
                mob.fill_rgbas[:, 1] = self._pc[1]
                mob.fill_rgbas[:, 2] = self._pc[2]
            if hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
                mob.stroke_rgbas[:, 0] = self._pc[0]
                mob.stroke_rgbas[:, 1] = self._pc[1]
                mob.stroke_rgbas[:, 2] = self._pc[2]


class GrowFromPoint(GrowArrow):
    def __init__(self, mobject, point, point_color=None, run_time=1.0, **kwargs):
        self._given_point = point
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def begin(self, t):
        Animation.begin(self, t)
        mob = self.mobject
        point = self._given_point
        if hasattr(point, 'get_center'):
            point = point.get_center()
        self._grow_point = np.array(point, dtype=float)

        if hasattr(mob, 'get_fill_rgbas'):
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    self._orig_fill = [float(frgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'get_stroke_rgbas'):
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    self._orig_stroke = [float(srgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'stroke_width'):
            self._orig_stroke_width = mob.stroke_width

        mob._grow_scale = 0.0
        mob._grow_point = self._grow_point
        if self.point_color:
            self._pc = (float(self.point_color[0]), float(self.point_color[1]), float(self.point_color[2]))
            if hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
                mob.fill_rgbas[:, 0] = self._pc[0]
                mob.fill_rgbas[:, 1] = self._pc[1]
                mob.fill_rgbas[:, 2] = self._pc[2]
            if hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
                mob.stroke_rgbas[:, 0] = self._pc[0]
                mob.stroke_rgbas[:, 1] = self._pc[1]
                mob.stroke_rgbas[:, 2] = self._pc[2]


class SpinInFromNothing(GrowFromCenter):
    def __init__(self, mobject, angle=math.pi / 2, point_color=None, run_time=1.0, **kwargs):
        self._spin_angle = angle
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        mob._grow_scale = alpha
        mob._grow_rot = -self._spin_angle * alpha
        if self.point_color and self._orig_fill:
            fr, fg, fb = self._orig_fill[0], self._orig_fill[1], self._orig_fill[2]
            cr = self._pc[0] + (fr - self._pc[0]) * alpha
            cg = self._pc[1] + (fg - self._pc[1]) * alpha
            cb = self._pc[2] + (fb - self._pc[2]) * alpha
            if hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
                mob.fill_rgbas[:, 0] = cr
                mob.fill_rgbas[:, 1] = cg
                mob.fill_rgbas[:, 2] = cb
        if self.point_color and self._orig_stroke:
            fr, fg, fb = self._orig_stroke[0], self._orig_stroke[1], self._orig_stroke[2]
            cr = self._pc[0] + (fr - self._pc[0]) * alpha
            cg = self._pc[1] + (fg - self._pc[1]) * alpha
            cb = self._pc[2] + (fb - self._pc[2]) * alpha
            if hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
                mob.stroke_rgbas[:, 0] = cr
                mob.stroke_rgbas[:, 1] = cg
                mob.stroke_rgbas[:, 2] = cb

    def finish(self):
        super().finish()
        if hasattr(self.mobject, '_grow_rot'):
            del self.mobject._grow_rot


class Rotating(Animation):
    def __init__(
        self,
        mobject,
        angle=2 * math.pi,
        run_time=5.0,
        rate_func=None,
        **kwargs,
    ):
        self.rot_angle = angle
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
        current = self._start_rotation - self.rot_angle * alpha
        set_anim_rotation(self.mobject, current)


class Rotate(Animation):
    def __init__(
        self,
        mobject,
        angle=math.pi,
        run_time=1.0,
        rate_func=None,
        **kwargs,
    ):
        self.rot_angle = angle
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
        current = self._start_rotation - self.rot_angle * alpha
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
            self._starting_mobject.align_data(self._target_copy)
            self.mobject.align_data(self._target_copy)
        except Exception:
            pass
        set_anim_opacity(self.mobject, 1.0)
        self._set_transforming(self.mobject, True)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        try:
            self.mobject._points_just_reset = True
            self.mobject.interpolate(self._starting_mobject, self._target_copy, alpha)
        except Exception:
            pass

    def finish(self):
        super().finish()
        set_anim_opacity(self.mobject, 1.0)
        try:
            self.mobject.set_points(self.target_mobject.get_points().copy())
        except Exception:
            pass
        if not self.replace_mobject_with_target_in_scene:
            set_anim_opacity(self.target_mobject, 0.0)
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
            self._set_transforming(self.mobject, True)
            self._set_transforming(self.target_mobject, False)


class ReplacementTransform(Transform):
    def __init__(self, mobject, target_mobject, **kwargs):
        kwargs['replace_mobject_with_target_in_scene'] = True
        super().__init__(mobject, target_mobject, **kwargs)


class MoveToTarget(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.target if hasattr(mobject, 'target') else mobject.copy()
        super().__init__(mobject, target, **kwargs)


class Indicate(Transform):
    def __init__(self, mobject, scale_factor=1.2, color=None, rate_func=None, **kwargs):
        self.scale_factor = scale_factor
        self.color = color
        target = mobject.copy()
        target.scale(scale_factor)
        if color is not None:
            target.set_color(color)
        super().__init__(mobject, target, run_time=1.0, rate_func=rate_func or _there_and_back, **kwargs)

    def finish(self):
        super().finish()
        set_anim_opacity(self.mobject, 1.0)
        self._set_transforming(self.mobject, False)


class AnimationGroup(Animation):
    def __init__(self, *animations, lag_ratio=0.0, **kwargs):
        from manim.mobject.mobject import _AnimationBuilder
        resolved = []
        for a in animations:
            if isinstance(a, _AnimationBuilder):
                resolved.append(a.build())
            else:
                resolved.append(a)
        self.animations = resolved
        self.lag_ratio = lag_ratio
        for i, a in enumerate(self.animations):
            a._group_start = i * lag_ratio
        total_runs = [a._group_start + a.run_time for a in self.animations]
        total = max(total_runs) if total_runs else 0
        super().__init__(run_time=total, **kwargs)
        self._begun = set()

    def begin(self, t):
        super().begin(t)
        self._begun = set()

    def interpolate(self, t):
        elapsed = t - self.start_time
        total = self.run_time
        if total > 0:
            raw_alpha = max(0.0, min(1.0, elapsed / total))
            mapped_alpha = self.rate_func(raw_alpha)
            group_time = mapped_alpha * total
        else:
            group_time = elapsed

        for i, a in enumerate(self.animations):
            a_start = getattr(a, '_group_start', 0.0)
            a_end = a_start + a.run_time
            is_manim = type(a).__module__.startswith('manim')

            if group_time >= a_start and group_time < a_end:
                if i not in self._begun:
                    if is_manim:
                        a.begin()
                    else:
                        a.begin(t)
                    self._begun.add(i)
                sub_alpha = (group_time - a_start) / a.run_time if a.run_time > 0 else 1.0
                sub_alpha = max(0.0, min(1.0, sub_alpha))
                if is_manim:
                    a.interpolate(sub_alpha)
                else:
                    a._use_alpha = True
                    a.interpolate(sub_alpha)
            elif group_time >= a_end:
                if i not in self._begun:
                    if is_manim:
                        a.begin()
                    else:
                        a.begin(t)
                    self._begun.add(i)
                if is_manim:
                    a.interpolate(1.0)
                else:
                    a._use_alpha = True
                    a.interpolate(1.0)

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
                FadeTransform(fade_source, fade_target, run_time=self.run_time)
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


class Blink(Succession):
    def __init__(self, mobject, time_on=0.5, time_off=0.5, blinks=1,
                 hide_at_end=False, **kwargs):
        self.blink_mobject = mobject
        self.hide_at_end = hide_at_end

        animations = []
        for _ in range(blinks):
            animations.append(Wait(time_on))
            animations.append(Wait(time_off))

        if not hide_at_end:
            animations.append(Wait(time_on))

        total_time = sum(a.run_time for a in animations)
        kwargs.pop('run_time', None)
        super().__init__(*animations, run_time=total_time, **kwargs)
        self._blink_mobject = mobject
        self._blink_time_on = time_on
        self._blink_time_off = time_off
        self._blink_blinks = blinks

    def _set_visible(self):
        set_anim_opacity(self._blink_mobject, 1.0)
        try:
            self._blink_mobject.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            self._blink_mobject.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass

    def _set_hidden(self):
        set_anim_opacity(self._blink_mobject, 0.0)
        try:
            self._blink_mobject.fill_rgbas[:, 3] = 0.0
        except Exception:
            pass
        try:
            self._blink_mobject.stroke_rgbas[:, 3] = 0.0
        except Exception:
            pass

    def begin(self, t):
        super().begin(t)
        self._set_visible()

    def interpolate(self, t):
        elapsed = t - self.start_time
        total = self.run_time
        if total <= 0:
            return

        time_on = self._blink_time_on
        time_off = self._blink_time_off
        cycle = time_on + time_off
        pos_in_cycle = elapsed % cycle

        if pos_in_cycle < time_on:
            self._set_visible()
        else:
            self._set_hidden()

    def finish(self):
        super().finish()
        if self.hide_at_end:
            self._set_hidden()
        else:
            self._set_visible()


class TypeWithCursor(ShowIncreasingSubsets):
    def __init__(self, text, cursor, buff=0.1, keep_cursor_y=True,
                 leave_cursor_on=True, time_per_char=0.1, run_time=None, **kwargs):
        self.cursor = cursor
        self.buff = buff
        self.keep_cursor_y = keep_cursor_y
        self.leave_cursor_on = leave_cursor_on
        self.time_per_char = time_per_char
        if run_time is None:
            n_chars = len(text.submobjects) if hasattr(text, 'submobjects') else max(1, len(str(text)))
            run_time = max(0.1, time_per_char) * n_chars
        self.all_submobs = list(text.submobjects) if hasattr(text, 'submobjects') else []
        self.int_func = None
        self._orig_fo = {}
        self._orig_so = {}
        for mobj in self.all_submobs:
            try:
                self._orig_fo[id(mobj)] = mobj.fill_rgbas[:, 3].copy()
            except Exception:
                self._orig_fo[id(mobj)] = 1.0
            try:
                self._orig_so[id(mobj)] = mobj.stroke_rgbas[:, 3].copy()
            except Exception:
                self._orig_so[id(mobj)] = 1.0
            set_anim_opacity(mobj, 0.0)
            try:
                mobj.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                mobj.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
        Animation.__init__(self, text, run_time=run_time, **kwargs)

    def begin(self, t):
        self.y_cursor = self.cursor.get_center()[1]
        self.initial_cursor_y = self.y_cursor
        set_anim_opacity(self.cursor, 0.0)
        try:
            self.cursor.fill_rgbas[:, 3] = 0.0
        except Exception:
            pass
        try:
            self.cursor.stroke_rgbas[:, 3] = 0.0
        except Exception:
            pass
        Animation.begin(self, t)

    def update_submobject_list(self, index):
        for mobj in self.all_submobs[:index]:
            set_anim_opacity(mobj, 1.0)
            if hasattr(mobj, 'family_members_with_points'):
                for fm in mobj.family_members_with_points():
                    set_anim_opacity(fm, 1.0)
            try:
                orig = self._orig_fo.get(id(mobj))
                if orig is not None:
                    mobj.fill_rgbas[:, 3] = orig
                else:
                    mobj.fill_rgbas[:, 3] = 1.0
            except Exception:
                pass
            try:
                orig = self._orig_so.get(id(mobj))
                if orig is not None:
                    mobj.stroke_rgbas[:, 3] = orig
                else:
                    mobj.stroke_rgbas[:, 3] = 1.0
            except Exception:
                pass
        for mobj in self.all_submobs[index:]:
            set_anim_opacity(mobj, 0.0)
            if hasattr(mobj, 'family_members_with_points'):
                for fm in mobj.family_members_with_points():
                    set_anim_opacity(fm, 0.0)
            try:
                mobj.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                mobj.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass

        if index > 0:
            last_visible = self.all_submobs[index - 1]
            last_center = last_visible.get_center()
            self.cursor.move_to(last_center)
            self.cursor.shift(np.array([1, 0, 0]) * (last_visible.get_width() / 2 + self.buff * 4))
        else:
            self.cursor.move_to(self.all_submobs[0].get_center())

        if self.keep_cursor_y:
            self.cursor.move_to([
                self.cursor.get_center()[0],
                self.initial_cursor_y,
                0
            ])
        set_anim_opacity(self.cursor, 1.0)
        try:
            self.cursor.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            self.cursor.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass

    def finish(self):
        Animation.finish(self)
        if self.all_submobs:
            last = self.all_submobs[-1]
            self.cursor.move_to(last.get_center())
            self.cursor.shift(np.array([1, 0, 0]) * (last.get_width() / 2 + self.buff * 4))
        if self.keep_cursor_y:
            self.cursor.move_to([
                self.cursor.get_center()[0],
                self.initial_cursor_y,
                0
            ])
        if self.leave_cursor_on:
            set_anim_opacity(self.cursor, 1.0)
            try:
                self.cursor.fill_rgbas[:, 3] = 1.0
            except Exception:
                pass
            try:
                self.cursor.stroke_rgbas[:, 3] = 1.0
            except Exception:
                pass
        else:
            set_anim_opacity(self.cursor, 0.0)
            try:
                self.cursor.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                self.cursor.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                self.cursor.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass


class UntypeWithCursor(Animation):
    def __init__(self, text, cursor, buff=0.1, keep_cursor_y=True,
                 leave_cursor_on=True, time_per_char=0.1, run_time=None, **kwargs):
        self.cursor = cursor
        self.buff = buff
        self.keep_cursor_y = keep_cursor_y
        self.leave_cursor_on = leave_cursor_on
        self.time_per_char = time_per_char
        if run_time is None:
            n_chars = len(text.submobjects) if hasattr(text, 'submobjects') else max(1, len(str(text)))
            run_time = max(0.1, time_per_char) * n_chars
        self.all_submobs = list(text.submobjects) if hasattr(text, 'submobjects') else []
        self._orig_fo = {}
        self._orig_so = {}
        for mobj in self.all_submobs:
            try:
                self._orig_fo[id(mobj)] = mobj.fill_rgbas[:, 3].copy()
            except Exception:
                self._orig_fo[id(mobj)] = 1.0
            try:
                self._orig_so[id(mobj)] = mobj.stroke_rgbas[:, 3].copy()
            except Exception:
                self._orig_so[id(mobj)] = 1.0
        Animation.__init__(self, text, run_time=run_time, **kwargs)

    def begin(self, t):
        self.y_cursor = self.cursor.get_center()[1]
        self.initial_cursor_y = self.y_cursor
        for mobj in self.all_submobs:
            set_anim_opacity(mobj, 1.0)
            if hasattr(mobj, 'family_members_with_points'):
                for fm in mobj.family_members_with_points():
                    set_anim_opacity(fm, 1.0)
            try:
                orig = self._orig_fo.get(id(mobj))
                if orig is not None:
                    mobj.fill_rgbas[:, 3] = orig
                else:
                    mobj.fill_rgbas[:, 3] = 1.0
            except Exception:
                pass
            try:
                orig = self._orig_so.get(id(mobj))
                if orig is not None:
                    mobj.stroke_rgbas[:, 3] = orig
                else:
                    mobj.stroke_rgbas[:, 3] = 1.0
            except Exception:
                pass
        if self.all_submobs:
            last = self.all_submobs[-1]
            self.cursor.move_to(last.get_center())
            self.cursor.shift(np.array([1, 0, 0]) * (last.get_width() / 2 + self.buff * 4))
            if self.keep_cursor_y:
                self.cursor.move_to([
                    self.cursor.get_center()[0],
                    self.initial_cursor_y,
                    0
                ])
        set_anim_opacity(self.cursor, 1.0)
        try:
            self.cursor.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            self.cursor.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass
        Animation.begin(self, t)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        alpha = self.rate_func(alpha)
        n = len(self.all_submobs)
        index = n - int(np.floor(alpha * n))
        index = max(0, min(index, n))
        self.update_submobject_list(index)

    def update_submobject_list(self, index):
        for i, mobj in enumerate(self.all_submobs):
            if i < index:
                set_anim_opacity(mobj, 1.0)
                if hasattr(mobj, 'family_members_with_points'):
                    for fm in mobj.family_members_with_points():
                        set_anim_opacity(fm, 1.0)
                try:
                    orig = self._orig_fo.get(id(mobj))
                    if orig is not None:
                        mobj.fill_rgbas[:, 3] = orig
                    else:
                        mobj.fill_rgbas[:, 3] = 1.0
                except Exception:
                    pass
                try:
                    orig = self._orig_so.get(id(mobj))
                    if orig is not None:
                        mobj.stroke_rgbas[:, 3] = orig
                    else:
                        mobj.stroke_rgbas[:, 3] = 1.0
                except Exception:
                    pass
            else:
                set_anim_opacity(mobj, 0.0)
                if hasattr(mobj, 'family_members_with_points'):
                    for fm in mobj.family_members_with_points():
                        set_anim_opacity(fm, 0.0)
                try:
                    mobj.fill_rgbas[:, 3] = 0.0
                except Exception:
                    pass
                try:
                    mobj.stroke_rgbas[:, 3] = 0.0
                except Exception:
                    pass

        if index > 0:
            last_visible = self.all_submobs[index - 1]
            last_center = last_visible.get_center()
            self.cursor.move_to(last_center)
            self.cursor.shift(np.array([1, 0, 0]) * (last_visible.get_width() / 2 + self.buff * 4))

        if self.keep_cursor_y:
            self.cursor.move_to([
                self.cursor.get_center()[0],
                self.initial_cursor_y,
                0
            ])
        set_anim_opacity(self.cursor, 1.0)
        try:
            self.cursor.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            self.cursor.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass

    def finish(self):
        Animation.finish(self)
        for mobj in self.all_submobs:
            set_anim_opacity(mobj, 0.0)
            if hasattr(mobj, 'family_members_with_points'):
                for fm in mobj.family_members_with_points():
                    set_anim_opacity(fm, 0.0)
            try:
                mobj.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                mobj.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
        if self.all_submobs:
            first = self.all_submobs[0]
            self.cursor.move_to(first.get_center())
        if self.keep_cursor_y:
            self.cursor.move_to([
                self.cursor.get_center()[0],
                self.initial_cursor_y,
                0
            ])
        if self.leave_cursor_on:
            set_anim_opacity(self.cursor, 1.0)
            try:
                self.cursor.fill_rgbas[:, 3] = 1.0
            except Exception:
                pass
            try:
                self.cursor.stroke_rgbas[:, 3] = 1.0
            except Exception:
                pass
        else:
            set_anim_opacity(self.cursor, 0.0)
            try:
                self.cursor.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                self.cursor.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
