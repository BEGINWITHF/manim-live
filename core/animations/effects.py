from core.animations.base import Animation, set_anim_opacity, get_anim_opacity, get_anim_rotation, set_anim_rotation
import numpy as np
import math
from manim import VGroup, ORIGIN, OUT, YELLOW
from core.rate_functions import _smooth, _linear, _there_and_back


class ApplyWave(Animation):
    def __init__(self, mobject, direction=(0.0, 1.0, 0.0), amplitude=0.2,
                 wave_func=None, time_width=1, ripples=1,
                 run_time=2.0, **kwargs):
        self._direction = list(direction)
        self._amplitude = amplitude
        self._wave_func = wave_func if wave_func else _smooth
        self._time_width = time_width
        self._ripples = ripples
        self._orig_points = {}
        super().__init__(mobject, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        if hasattr(mob, 'family_members_with_points'):
            for fm in mob.family_members_with_points():
                try:
                    self._orig_points[id(fm)] = fm.points.copy()
                except Exception:
                    pass

    def _wave_val(self, t):
        if t >= 1 or t <= 0:
            return 0
        phases = self._ripples * 2
        phase = int(t * phases)
        if phase == 0:
            return self._wave_func(t * phases)
        elif phase == phases - 1:
            t -= phase / phases
            return (1 - self._wave_func(t * phases)) * (2 * (self._ripples % 2) - 1)
        else:
            phase_idx = (phase - 1) // 2
            t -= (2 * phase_idx + 1) / phases
            return (1 - 2 * self._wave_func(t * self._ripples)) * (1 - 2 * (phase_idx % 2))

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        x_min = mob.get_left()[0]
        x_max = mob.get_right()[0]
        direction = np.array(self._direction, dtype=float)
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction = direction / norm
        vect = self._amplitude * direction

        time_width = self._time_width
        upper = (1 + time_width) * alpha
        lower = upper - time_width
        x_range = x_max - x_min if x_max != x_min else 1.0

        if not hasattr(mob, 'family_members_with_points'):
            return

        for fm in mob.family_members_with_points():
            if id(fm) not in self._orig_points:
                continue
            orig = self._orig_points[id(fm)]
            fm.points = orig.copy()
            for i in range(len(fm.points)):
                px, py, pz = orig[i][0], orig[i][1], orig[i][2]
                relative_x = (px - x_min) / x_range
                phase_val = (relative_x - lower) / (upper - lower) if upper != lower else 0
                nudge = self._wave_val(phase_val) * vect
                fm.points[i][0] = px + nudge[0]
                fm.points[i][1] = py + nudge[1]
                fm.points[i][2] = pz + nudge[2]

    def finish(self):
        super().finish()
        mob = self.mobject
        if hasattr(mob, 'family_members_with_points'):
            for fm in mob.family_members_with_points():
                if id(fm) in self._orig_points:
                    fm.points = self._orig_points[id(fm)].copy()


class Homotopy(Animation):
    def __init__(self, homotopy, mobject, run_time=3.0, **kwargs):
        self.homotopy = homotopy
        self._orig_points = {}
        super().__init__(mobject, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        mob._transforming = True
        if hasattr(mob, 'family_members_with_points'):
            for fm in mob.family_members_with_points():
                try:
                    self._orig_points[id(fm)] = fm.points.copy()
                except Exception:
                    pass

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        if not hasattr(mob, 'family_members_with_points'):
            return

        for fm in mob.family_members_with_points():
            if id(fm) not in self._orig_points:
                continue
            orig = self._orig_points[id(fm)]
            fm.points = orig.copy()
            for i in range(len(fm.points)):
                px, py, pz = orig[i][0], orig[i][1], orig[i][2]
                nx, ny, nz = self.homotopy(px, py, pz, alpha)
                fm.points[i][0] = nx
                fm.points[i][1] = ny
                fm.points[i][2] = nz

    def finish(self):
        super().finish()
        mob = self.mobject
        mob._transforming = False
        if hasattr(mob, 'family_members_with_points'):
            for fm in mob.family_members_with_points():
                if id(fm) in self._orig_points:
                    fm.points = self._orig_points[id(fm)].copy()


class MoveAlongPath(Animation):
    def __init__(self, mobject, path, suspend_mobject_updating=False, **kwargs):
        self.path = path
        super().__init__(mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)


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
        about_point=None,
        **kwargs,
    ):
        self.rot_angle = angle
        self.about_point = about_point
        super().__init__(mobject, run_time=run_time, rate_func=rate_func or _smooth, **kwargs)

    def begin(self, t):
        super().begin(t)
        self._start_rotation = get_anim_rotation(self.mobject)
        if self.about_point is not None:
            self.mobject._rotation_about_point = np.array(self.about_point, dtype=float)

    def finish(self):
        super().finish()
        if hasattr(self.mobject, '_rotation_about_point'):
            del self.mobject._rotation_about_point

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        current = self._start_rotation - self.rot_angle * alpha
        set_anim_rotation(self.mobject, current)
