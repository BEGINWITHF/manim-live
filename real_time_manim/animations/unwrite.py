# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.write import Write
from real_time_manim.animations.base import Animation
from real_time_manim.rate_functions import _linear


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
                sub = mob.submobjects[i]
                if self._unwrite_reverse:
                    idx = num_subs - 1 - i
                else:
                    idx = i
                sub_alpha = self.get_sub_alpha(alpha, idx, num_subs)
                fade = self.rate_func(1.0 - sub_alpha)
                letter_alphas[i] = fade
                # The Vulkan renderer draws the LEAF glyphs (family members
                # with points), not the container parts — fade their fill so
                # MathTex/Tex actually unwrite progressively.
                try:
                    n_leaves = 0
                    for fm in sub.family_members_with_points():
                        n_leaves += 1
                        if hasattr(fm, 'fill_rgbas') and fm.fill_rgbas is not None and len(fm.fill_rgbas) > 0:
                            fm.fill_rgbas[:, 3] = fade
                        if hasattr(fm, 'stroke_rgbas') and fm.stroke_rgbas is not None and len(fm.stroke_rgbas) > 0:
                            fm.stroke_rgbas[:, 3] = fade
                        fm._vulkan_progress = fade
                except Exception:
                    pass
            mob._letter_alphas = letter_alphas
        else:
            mob._vulkan_progress = self.rate_func(1.0 - alpha)

    def finish(self):
        Animation.finish(self)
        mob = self.mobject
        if hasattr(mob, 'submobjects') and mob.submobjects:
            mob._letter_alphas = {i: 0.0 for i in range(len(mob.submobjects))}
            try:
                for fm in mob.family_members_with_points():
                    if hasattr(fm, 'fill_rgbas') and fm.fill_rgbas is not None and len(fm.fill_rgbas) > 0:
                        fm.fill_rgbas[:, 3] = 0.0
                    if hasattr(fm, 'stroke_rgbas') and fm.stroke_rgbas is not None and len(fm.stroke_rgbas) > 0:
                        fm.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
        else:
            mob._vulkan_progress = 0.0
