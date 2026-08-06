# This might not cause a bug or issue, check for other place first --TT Noted
from core.animations.base import Animation
from core.rate_functions import _double_smooth


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
