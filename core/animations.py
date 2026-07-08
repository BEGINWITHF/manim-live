import math
import numpy as np
from manim import VGroup, Group
from core.rate_functions import (
    _smooth, _linear, _double_smooth,
)

DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0.0
TARGET_FPS = 60
FRAME_DURATION = 1.0 / TARGET_FPS

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
        super().__init__(mobject, rate_func=rate_func, reverse=False, run_time=run_time, **kwargs)

    def begin(self, t):
        super(Write, self).begin(t)

    def _apply_to_submobjects(self, alpha):
        mob = self.mobject
        if not hasattr(mob, 'submobjects') or not mob.submobjects:
            mob._vulkan_progress = self.rate_func(1.0 - alpha)
            return
        num_subs = len(mob.submobjects)
        letter_alphas = {}
        for i in range(num_subs):
            rev_i = num_subs - 1 - i
            sub_alpha = self.get_sub_alpha(alpha, rev_i, num_subs)
            letter_alphas[i] = self.rate_func(1.0 - sub_alpha)
        mob._letter_alphas = letter_alphas

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
        current = self._start_rotation + self.rot_angle * alpha
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
