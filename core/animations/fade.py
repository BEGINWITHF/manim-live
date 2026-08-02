from core.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import VGroup, ORIGIN, UP, DOWN, LEFT, RIGHT
from core.rate_functions import _there_and_back, _smooth, _double_smooth


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


class FadeTransform(Animation):
    def __init__(self, mobject, target_mobject, stretch=True, dim_to_match=1, run_time=1.0, **kwargs):
        self.target_mobject = target_mobject
        self.to_add_on_completion = target_mobject
        self.stretch = stretch
        self.dim_to_match = dim_to_match
        self._source_start_pos = None
        self._target_start_pos = None
        try:
            self._ghost = target_mobject.copy()
            self._ghost._transforming = True
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
            if self.stretch:
                scale_x = self.mobject.width / self._ghost.width if self._ghost.width > 0 else 1.0
                scale_y = self.mobject.height / self._ghost.height if self._ghost.height > 0 else 1.0
                uniform_scale = min(scale_x, scale_y)
                self._ghost.scale(uniform_scale)
            else:
                self._ghost.rescale_to_fit(
                    self.mobject.length_over_dim(self.dim_to_match),
                    self.dim_to_match,
                    stretch=False,
                )
            self._ghost.move_to(self._source_start_pos)
            self._source_copy = self._ghost.copy()
            self._target_copy = self.target_mobject.copy()
            self._source_copy.align_data(self._target_copy)
            set_anim_opacity(self._ghost, 0.0)
        set_anim_opacity(self.mobject, 1.0)
        set_anim_opacity(self.target_mobject, 0.0)

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
            self._ghost.interpolate(self._source_copy, self._target_copy, alpha)
            self._ghost.move_to(cur_pos)
            if alpha >= 1.0:
                self._ghost._transforming = False
                for sub in self._ghost.submobjects:
                    sub._transforming = False
            set_anim_opacity(self._ghost, alpha)
        set_anim_opacity(self.mobject, max(0.0, 1.0 - alpha))

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
