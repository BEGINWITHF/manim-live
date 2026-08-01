from core.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import Rectangle, YELLOW
from core.rate_functions import _smooth, _double_smooth
from core.animations.succession import Succession
from core.animations.wait import Wait
from core.animations.fade import FadeIn, FadeOut
from core.animations.create import Create, Uncreate


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


class Circumscribe(Succession):
    def __init__(self, mobject, shape=Rectangle, fade_in=False, fade_out=False,
                 time_width=0.3, buff=0.1, color=None, run_time=1.0,
                 stroke_width=4, **kwargs):

        if shape is Rectangle:
            from manim import SurroundingRectangle
            frame = SurroundingRectangle(mobject, color=color or YELLOW, buff=buff,
                                         stroke_width=stroke_width)
        else:
            from manim import Circle
            frame = Circle(color=color or YELLOW, stroke_width=stroke_width)
            frame.surround(mobject, buffer_factor=1)
            radius = frame.width / 2
            frame.scale((radius + buff) / radius)

        if hasattr(mobject, 'font_size'):
            frame.scale(0.875)

        if fade_in and fade_out:
            animations = [
                FadeIn(frame, run_time=run_time / 2),
                FadeOut(frame, run_time=run_time / 2),
            ]
        elif fade_in:
            animations = [
                FadeIn(frame, run_time=run_time / 2),
                Uncreate(frame, run_time=run_time / 2),
            ]
        elif fade_out:
            animations = [
                Create(frame, run_time=run_time / 2),
                FadeOut(frame, run_time=run_time / 2),
            ]
        else:
            animations = [
                Create(frame, run_time=run_time),
            ]

        self._frame = frame
        kwargs.pop('run_time', None)
        total_time = sum(a.run_time for a in animations)
        super().__init__(*animations, run_time=total_time, **kwargs)

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if hasattr(self, '_frame') and self._frame in scene.mobjects:
            scene.remove(self._frame)
