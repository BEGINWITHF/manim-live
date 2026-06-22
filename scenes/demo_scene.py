from manim import *
from core.vulkan_bind import (
    VulkanRender, Animation, Create, Succession, Wait, Add,
    FadeIn, FadeOut,
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth, _lingering,
    _wiggle, _exponential_decay,
    set_anim_opacity,
)


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("FadeIn / FadeOut Demo", font_size=40)
        title.shift(UP * 3.3)
        title_box = SurroundingRectangle(title, buff=0.15)

        render.play(
            Create(title_box, run_time=1.0),
            Succession(Wait(0.2), Add(title)),
        )
        render.play(Wait(0.5))

        self.section_fade_in_basic(render)
        self.section_fade_in_options(render)
        self.section_fade_out_basic(render)
        self.section_fade_out_options(render)
        self.section_fade_in_out_combined(render)
        self.section_fade_rate_functions(render)

        render.play(Wait(2.0))
        render.close()

    def _clear(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

    def _make_shapes(self):
        sq = Square(side_length=1.0, color=RED)
        sq.set_fill(opacity=0)
        sq.set_stroke(width=3)

        rect = Rectangle(width=2.0, height=1.0, color=GREEN)
        rect.set_fill(opacity=0)
        rect.set_stroke(width=3)

        circ = Circle(radius=0.5, color=BLUE)
        circ.set_fill(opacity=0)
        circ.set_stroke(width=3)

        tri = Polygon(
            UP * 0.8 + LEFT * 0.6,
            UP * 0.8 + RIGHT * 0.6,
            DOWN * 0.4,
            color=YELLOW,
        )
        tri.set_fill(opacity=0)
        tri.set_stroke(width=3)

        return [sq, rect, circ, tri]

    def section_fade_in_basic(self, render):
        self._clear(render)

        sec = Text("FadeIn: Basic", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        shapes = self._make_shapes()
        positions = [LEFT * 5, LEFT * 1.7, RIGHT * 1.7, RIGHT * 5]
        for s, p in zip(shapes, positions):
            s.shift(p + UP * 0.3)

        render.play(
            *[FadeIn(s, run_time=2.0) for s in shapes],
        )
        render.play(Wait(1.5))

    def section_fade_in_options(self, render):
        self._clear(render)

        sec = Text("FadeIn: Options", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        r1 = Rectangle(width=2.0, height=1.0, color=RED)
        r1.set_fill(opacity=0)
        r1.set_stroke(width=3)
        r1.shift(LEFT * 5 + UP * 0.3)

        r2 = Rectangle(width=2.0, height=1.0, color=GREEN)
        r2.set_fill(opacity=0)
        r2.set_stroke(width=3)
        r2.shift(LEFT * 1.7 + UP * 0.3)

        r3 = Rectangle(width=2.0, height=1.0, color=BLUE)
        r3.set_fill(opacity=0)
        r3.set_stroke(width=3)
        r3.shift(RIGHT * 1.7 + UP * 0.3)

        r4 = Rectangle(width=2.0, height=1.0, color=YELLOW)
        r4.set_fill(opacity=0)
        r4.set_stroke(width=3)
        r4.shift(RIGHT * 5 + UP * 0.3)

        lbl1 = Text("shift DOWN", font_size=14)
        lbl1.shift(LEFT * 5 + DOWN * 0.8)
        lbl2 = Text("scale 2.0", font_size=14)
        lbl2.shift(LEFT * 1.7 + DOWN * 0.8)
        lbl3 = Text("target LEFT", font_size=14)
        lbl3.shift(RIGHT * 1.7 + DOWN * 0.8)
        lbl4 = Text("shift UP+RIGHT", font_size=14)
        lbl4.shift(RIGHT * 5 + DOWN * 0.8)

        render.play(
            FadeIn(r1, shift=DOWN, run_time=1.5),
            FadeIn(r2, scale=2.0, run_time=1.5),
            FadeIn(r3, target_position=LEFT * 5, run_time=1.5),
            FadeIn(r4, shift=UP + RIGHT, run_time=1.5),
            Add(lbl1, lbl2, lbl3, lbl4),
        )
        render.play(Wait(1.5))

    def section_fade_out_basic(self, render):
        self._clear(render)

        sec = Text("FadeOut: Basic", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        shapes = self._make_shapes()
        positions = [LEFT * 5, LEFT * 1.7, RIGHT * 1.7, RIGHT * 5]
        for s, p in zip(shapes, positions):
            s.shift(p + UP * 0.3)

        render.play(Add(*shapes))
        render.play(Wait(0.5))

        render.play(
            *[FadeOut(s, run_time=2.0) for s in shapes],
        )
        render.play(Wait(1.5))

    def section_fade_out_options(self, render):
        self._clear(render)

        sec = Text("FadeOut: Options", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        r1 = Rectangle(width=2.0, height=1.0, color=RED)
        r1.set_fill(opacity=0)
        r1.set_stroke(width=3)
        r1.shift(LEFT * 5 + UP * 0.3)

        r2 = Rectangle(width=2.0, height=1.0, color=GREEN)
        r2.set_fill(opacity=0)
        r2.set_stroke(width=3)
        r2.shift(LEFT * 1.7 + UP * 0.3)

        r3 = Rectangle(width=2.0, height=1.0, color=BLUE)
        r3.set_fill(opacity=0)
        r3.set_stroke(width=3)
        r3.shift(RIGHT * 1.7 + UP * 0.3)

        r4 = Rectangle(width=2.0, height=1.0, color=YELLOW)
        r4.set_fill(opacity=0)
        r4.set_stroke(width=3)
        r4.shift(RIGHT * 5 + UP * 0.3)

        lbl1 = Text("shift UP", font_size=14)
        lbl1.shift(LEFT * 5 + DOWN * 0.8)
        lbl2 = Text("scale 0.3", font_size=14)
        lbl2.shift(LEFT * 1.7 + DOWN * 0.8)
        lbl3 = Text("target RIGHT", font_size=14)
        lbl3.shift(RIGHT * 1.7 + DOWN * 0.8)
        lbl4 = Text("shift DOWN+LEFT", font_size=14)
        lbl4.shift(RIGHT * 5 + DOWN * 0.8)

        render.play(Add(r1, r2, r3, r4, lbl1, lbl2, lbl3, lbl4))
        render.play(Wait(0.5))

        render.play(
            FadeOut(r1, shift=UP, run_time=1.5),
            FadeOut(r2, scale=0.3, run_time=1.5),
            FadeOut(r3, target_position=RIGHT * 7, run_time=1.5),
            FadeOut(r4, shift=DOWN + LEFT, run_time=1.5),
        )
        render.play(Wait(1.5))

    def section_fade_in_out_combined(self, render):
        self._clear(render)

        sec = Text("FadeIn + FadeOut: Combined", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        rects = []
        for i, c in enumerate(colors):
            r = Rectangle(width=1.5, height=0.8, color=c)
            r.set_fill(opacity=0)
            r.set_stroke(width=3)
            x = LEFT * 5 + RIGHT * i * 2.0
            r.shift(x + UP * 0.3)
            rects.append(r)

        render.play(
            *[FadeIn(s, run_time=1.0) for s in rects],
        )
        render.play(Wait(1.0))

        render.play(
            Succession(
                Wait(0.2),
                FadeOut(rects[0], shift=UP, run_time=0.8),
                Wait(0.2),
                FadeOut(rects[1], shift=DOWN, run_time=0.8),
                Wait(0.2),
                FadeOut(rects[2], scale=0.3, run_time=0.8),
                Wait(0.2),
                FadeOut(rects[3], target_position=RIGHT * 5, run_time=0.8),
                Wait(0.2),
                FadeOut(rects[4], shift=LEFT * 2, run_time=0.8),
                Wait(0.2),
                FadeOut(rects[5], scale=2.0, run_time=0.8),
            ),
        )
        render.play(Wait(1.5))

    def section_fade_rate_functions(self, render):
        self._clear(render)

        sec = Text("FadeIn: Rate Functions", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        funcs = [
            ("smooth", _smooth),
            ("linear", _linear),
            ("rush_into", _rush_into),
            ("rush_from", _rush_from),
        ]

        rects = []
        labels = []
        for i, (name, func) in enumerate(funcs):
            x = LEFT * 5.25 + RIGHT * i * 3.5
            r = Rectangle(width=2.5, height=1.2, color=BLUE + i * 0.3)
            r.set_fill(opacity=0)
            r.set_stroke(width=3)
            r.shift(x + UP * 0.3)
            rects.append((r, func))

            lbl = Text(name, font_size=14)
            lbl.shift(x + DOWN * 0.8)
            labels.append(lbl)

        render.play(
            *[FadeIn(r, run_time=2.0, rate_func=f) for r, f in rects],
            Add(*labels),
        )
        render.play(Wait(1.5))
