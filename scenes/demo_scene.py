import math
from manim import *
from core.vulkan_bind import (
    VulkanRender, Animation, Create, Succession, Wait, Add,
    FadeIn, FadeOut, Rotating, Rotate,
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth, _lingering,
    _wiggle, _exponential_decay,
    set_anim_opacity,
)


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("Rotation Demo", font_size=40)
        title.shift(UP * 3.3)
        title_box = SurroundingRectangle(title, buff=0.3)

        render.play(
            Create(title_box, run_time=1.0),
            Succession(Wait(0.2), Add(title)),
        )
        render.play(Wait(0.5))

        self.section_rotate_basic(render)
        self.section_rotate_options(render)
        self.section_rotating_basic(render)
        self.section_rotating_options(render)
        self.section_rotate_group(render)
        self.section_rotate_rate_functions(render)

        render.play(Wait(2.0))
        render.close()

    def _clear(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

    def section_rotate_basic(self, render):
        self._clear(render)

        sec = Text("Rotate: Basic", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        sq = Square(side_length=1.2, color=RED)
        sq.set_fill(opacity=0)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 5 + UP * 0.3)

        rect = Rectangle(width=2.0, height=1.0, color=GREEN)
        rect.set_fill(opacity=0)
        rect.set_stroke(width=3)
        rect.shift(LEFT * 1.7 + UP * 0.3)

        circ = Circle(radius=0.5, color=BLUE)
        circ.set_fill(opacity=0)
        circ.set_stroke(width=3)
        circ.shift(RIGHT * 1.7 + UP * 0.3)

        tri = Polygon(
            UP * 0.8 + LEFT * 0.6,
            UP * 0.8 + RIGHT * 0.6,
            DOWN * 0.4,
            color=YELLOW,
        )
        tri.set_fill(opacity=0)
        tri.set_stroke(width=3)
        tri.shift(RIGHT * 5 + UP * 0.3)

        render.play(Add(sq, rect, circ, tri))
        render.play(Wait(0.5))

        render.play(
            Rotate(sq, angle=math.pi, run_time=1.5),
            Rotate(rect, angle=math.pi / 2, run_time=1.5),
            Rotate(circ, angle=math.pi, run_time=1.5),
            Rotate(tri, angle=-math.pi / 3, run_time=1.5),
        )
        render.play(Wait(1.5))

    def section_rotate_options(self, render):
        self._clear(render)

        sec = Text("Rotate: Options", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        r1 = Square(side_length=1.0, color=RED)
        r1.set_fill(opacity=0)
        r1.set_stroke(width=3)
        r1.shift(LEFT * 5 + UP * 0.3)

        r2 = Square(side_length=1.0, color=GREEN)
        r2.set_fill(opacity=0)
        r2.set_stroke(width=3)
        r2.shift(LEFT * 1.7 + UP * 0.3)

        r3 = Square(side_length=1.0, color=BLUE)
        r3.set_fill(opacity=0)
        r3.set_stroke(width=3)
        r3.shift(RIGHT * 1.7 + UP * 0.3)

        r4 = Square(side_length=1.0, color=YELLOW)
        r4.set_fill(opacity=0)
        r4.set_stroke(width=3)
        r4.shift(RIGHT * 5 + UP * 0.3)

        lbl1 = Text("90 degrees", font_size=14)
        lbl1.shift(LEFT * 5 + DOWN * 0.8)
        lbl2 = Text("180 degrees", font_size=14)
        lbl2.shift(LEFT * 1.7 + DOWN * 0.8)
        lbl3 = Text("fast (0.5s)", font_size=14)
        lbl3.shift(RIGHT * 1.7 + DOWN * 0.8)
        lbl4 = Text("slow (3s)", font_size=14)
        lbl4.shift(RIGHT * 5 + DOWN * 0.8)

        render.play(Add(r1, r2, r3, r4, lbl1, lbl2, lbl3, lbl4))
        render.play(Wait(0.5))

        render.play(
            Rotate(r1, angle=math.pi / 2, run_time=1.5),
            Rotate(r2, angle=math.pi, run_time=1.5),
            Rotate(r3, angle=2 * math.pi, run_time=0.5),
            Rotate(r4, angle=2 * math.pi, run_time=3.0),
        )
        render.play(Wait(1.5))

    def section_rotating_basic(self, render):
        self._clear(render)

        sec = Text("Rotating: Continuous Spin", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        sq = Square(side_length=1.2, color=RED)
        sq.set_fill(opacity=0)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 4 + UP * 0.3)

        arrow = Arrow(start=LEFT * 1 + DOWN * 0.5, end=RIGHT * 1 + UP * 0.5, color=GREEN)
        arrow.set_stroke(width=3)
        arrow.shift(RIGHT * 0 + UP * 0.3)

        line = Line(start=LEFT * 1, end=RIGHT * 1, color=BLUE)
        line.set_stroke(width=3)
        line.shift(RIGHT * 4 + UP * 0.3)

        render.play(Add(sq, arrow, line))
        render.play(Wait(0.5))

        render.play(
            Rotating(sq, angle=2 * math.pi, run_time=3.0, rate_func=_linear),
        )
        render.play(Wait(0.5))

        render.play(
            Rotating(arrow, angle=2 * math.pi, run_time=3.0, rate_func=_linear),
        )
        render.play(Wait(0.5))

        render.play(
            Rotating(line, angle=2 * math.pi, run_time=3.0, rate_func=_linear),
        )
        render.play(Wait(1.0))

    def section_rotating_options(self, render):
        self._clear(render)

        sec = Text("Rotating: Options", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        r1 = Square(side_length=1.0, color=RED)
        r1.set_fill(opacity=0)
        r1.set_stroke(width=3)
        r1.shift(LEFT * 5 + UP * 0.3)

        r2 = Square(side_length=1.0, color=GREEN)
        r2.set_fill(opacity=0)
        r2.set_stroke(width=3)
        r2.shift(LEFT * 1.7 + UP * 0.3)

        r3 = Square(side_length=1.0, color=BLUE)
        r3.set_fill(opacity=0)
        r3.set_stroke(width=3)
        r3.shift(RIGHT * 1.7 + UP * 0.3)

        r4 = Square(side_length=1.0, color=YELLOW)
        r4.set_fill(opacity=0)
        r4.set_stroke(width=3)
        r4.shift(RIGHT * 5 + UP * 0.3)

        lbl1 = Text("half spin", font_size=14)
        lbl1.shift(LEFT * 5 + DOWN * 0.8)
        lbl2 = Text("full spin", font_size=14)
        lbl2.shift(LEFT * 1.7 + DOWN * 0.8)
        lbl3 = Text("smooth", font_size=14)
        lbl3.shift(RIGHT * 1.7 + DOWN * 0.8)
        lbl4 = Text("there_and_back", font_size=14)
        lbl4.shift(RIGHT * 5 + DOWN * 0.8)

        render.play(Add(r1, r2, r3, r4, lbl1, lbl2, lbl3, lbl4))
        render.play(Wait(0.5))

        render.play(
            Rotating(r1, angle=math.pi, run_time=2.0, rate_func=_linear),
            Rotating(r2, angle=2 * math.pi, run_time=2.0, rate_func=_linear),
            Rotating(r3, angle=2 * math.pi, run_time=2.0, rate_func=_smooth),
            Rotating(r4, angle=2 * math.pi, run_time=2.0, rate_func=_there_and_back),
        )
        render.play(Wait(1.5))

    def section_rotate_group(self, render):
        self._clear(render)

        sec = Text("Rotate: Group of Shapes", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        sq = Square(side_length=0.8, color=RED)
        sq.set_fill(opacity=0)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 2)

        circ = Circle(radius=0.4, color=BLUE)
        circ.set_fill(opacity=0)
        circ.set_stroke(width=3)
        circ.shift(RIGHT * 2)

        group = VGroup(sq, circ)
        group.shift(DOWN * 0.5)

        render.play(Add(group))
        render.play(Wait(0.5))

        render.play(
            Rotate(group, angle=math.pi, run_time=2.0),
        )
        render.play(Wait(0.5))

        render.play(
            Rotating(group, angle=2 * math.pi, run_time=3.0, rate_func=_linear),
        )
        render.play(Wait(1.0))

    def section_rotate_rate_functions(self, render):
        self._clear(render)

        sec = Text("Rotate: Rate Functions", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        funcs = [
            ("smooth", _smooth),
            ("linear", _linear),
            ("rush_into", _rush_into),
            ("there_and_back", _there_and_back),
        ]

        rects = []
        labels = []
        for i, (name, func) in enumerate(funcs):
            x = LEFT * 5.25 + RIGHT * i * 3.5
            r = Square(side_length=0.8, color=BLUE + i * 0.3)
            r.set_fill(opacity=0)
            r.set_stroke(width=3)
            r.shift(x + UP * 0.3)
            rects.append((r, func))

            lbl = Text(name, font_size=14)
            lbl.shift(x + DOWN * 0.8)
            labels.append(lbl)

        render.play(
            *[Add(r) for r, _ in rects],
            Add(*labels),
        )
        render.play(Wait(0.5))

        render.play(
            *[Rotating(r, angle=2 * math.pi, run_time=2.0, rate_func=f) for r, f in rects],
        )
        render.play(Wait(1.5))
