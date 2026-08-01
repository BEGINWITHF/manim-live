from core.animations.base import Animation, set_anim_opacity, get_anim_opacity, clear_anim_rotation_delta
import numpy as np
from manim import VGroup, Group, ORIGIN, UP
from core.rate_functions import _smooth, _linear, _double_smooth


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
