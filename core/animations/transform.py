# This might not cause a bug or issue, check for other place first --TT Noted
from core.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np


class Transform(Animation):
    def __init__(self, mobject, target_mobject, replace_mobject_with_target_in_scene=False, run_time=1.0, **kwargs):
        self.target_mobject = target_mobject
        self.replace_mobject_with_target_in_scene = replace_mobject_with_target_in_scene
        self.path_arc = kwargs.pop('path_arc', 0.0)
        self._path_arc = self.path_arc
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
        # Save positions for path_arc movement
        self._start_pos = self.mobject.get_center().copy()
        self._end_pos = self.target_mobject.get_center().copy()

    def _path_along_arc(self, alpha):
        """Move mobject along an arc from start to end."""
        if abs(self._path_arc) < 1e-9:
            return
        import math
        arc = self._path_arc
        # Compute position along circular arc
        start, end = self._start_pos[:2], self._end_pos[:2]
        center = (start + end) / 2.0
        diff = end - start
        chord = np.linalg.norm(diff)
        if chord < 1e-9:
            return
        radius = chord / (2.0 * math.sin(abs(arc) / 2.0)) if abs(math.sin(abs(arc) / 2.0)) > 1e-9 else chord
        mid_normal = np.array([-diff[1], diff[0]]) / chord if chord > 1e-9 else np.array([0.0, 0.0])
        arc_center = center - mid_normal * (radius * math.cos(arc / 2.0))
        start_angle = math.atan2(start[1] - arc_center[1], start[0] - arc_center[0])
        current_angle = start_angle + arc * alpha
        pos = np.array([
            arc_center[0] + radius * math.cos(current_angle),
            arc_center[1] + radius * math.sin(current_angle),
            0.0,
        ])
        # Apply position — shift relative to the interpolated center
        interp_center = start + diff * alpha
        self.mobject.shift(pos - np.array([interp_center[0], interp_center[1], 0.0]))

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        try:
            mob_fam = self.mobject.family_members_with_points()
            start_fam = self._starting_mobject.family_members_with_points()
            target_fam = self._target_copy.family_members_with_points()
            for m, s, t in zip(mob_fam, start_fam, target_fam):
                m.interpolate(s, t, alpha)
        except Exception:
            pass
        # Arc path movement
        self._path_along_arc(alpha)

    def finish(self):
        super().finish()
        set_anim_opacity(self.mobject, 1.0)
        try:
            mob_fam = self.mobject.family_members_with_points()
            target_fam = self.target_mobject.family_members_with_points()
            for m, t in zip(mob_fam, target_fam):
                m.set_points(t.get_points().copy())
        except Exception:
            try:
                self.mobject.set_points(self.target_mobject.get_points().copy())
            except Exception:
                pass
        # Move to final position for path_arc
        if abs(self._path_arc) > 1e-9:
            self.mobject.move_to(self._end_pos)
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
