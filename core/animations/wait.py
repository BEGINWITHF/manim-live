from core.animations.base import Animation, set_anim_opacity
from core.rate_functions import _linear


class Wait(Animation):
    def __init__(
        self,
        run_time=1.0,
        rate_func=None,
        **kwargs,
    ):
        super().__init__(None, run_time=run_time, rate_func=rate_func or _linear, **kwargs)

    def interpolate(self, alpha):
        self.rate_func(alpha)


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
