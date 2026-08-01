import math
from core.animations.base import Animation, set_anim_opacity, get_anim_opacity, TARGET_FPS
import numpy as np
from core.rate_functions import _smooth

TAU = 2.0 * math.pi


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
