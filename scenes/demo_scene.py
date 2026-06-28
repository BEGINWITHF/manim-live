from manim import *
from core.vulkan_bind import (
    VulkanRender, Animation, Create, Write, Unwrite, Succession, Wait, Add,
    FadeIn, FadeOut, FadeTransform,
    Rotating, Rotate,
    Transform, TransformMatchingShapes, TransformMatchingTex,
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth, _lingering,
    _wiggle, _exponential_decay,
    set_anim_opacity,
)
import math


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("Vulkan Features Demo", font_size=42)
        title.shift(UP * 3.3)
        title_box = SurroundingRectangle(title, buff=0.3)

        render.play(
            Create(title_box, run_time=1.0),
            Write(title, run_time=1.5),
        )
        render.play(Wait(0.5))

        self.section_rotation(render)
        self.section_fade(render)
        self.section_transform_matching(render)
        self.section_write_stagger(render)
        self.section_rate_functions(render)

        render.play(Wait(2.0))
        render.close()

    def section_rotation(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Rotation", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 4.5)

        circ = Circle(radius=0.6, color=GREEN)
        circ.set_fill(GREEN, opacity=0.6)
        circ.set_stroke(width=3)
        circ.shift(LEFT * 1.5)

        tri = Triangle(color=RED, fill_opacity=0.6, stroke_width=3)
        tri.scale(0.8)
        tri.shift(RIGHT * 1.5)

        arrow = Arrow(ORIGIN, RIGHT * 2, color=YELLOW, stroke_width=4)
        arrow.shift(RIGHT * 4.5)

        lbl_sq = Text("Rotate", font_size=16)
        lbl_sq.shift(LEFT * 4.5 + DOWN * 1.5)
        lbl_circ = Text("Rotating", font_size=16)
        lbl_circ.shift(LEFT * 1.5 + DOWN * 1.5)
        lbl_tri = Text("90°", font_size=16)
        lbl_tri.shift(RIGHT * 1.5 + DOWN * 1.5)

        render.play(
            Add(sq), Add(circ), Add(tri), Add(arrow),
            Add(lbl_sq), Add(lbl_circ), Add(lbl_tri),
        )
        render.play(Wait(0.3))

        render.play(Rotate(sq, angle=math.pi / 2, run_time=1.5))
        render.play(Wait(0.3))

        render.play(Rotating(tri, angle=2 * math.pi, run_time=2.0))
        render.play(Wait(0.3))

        render.play(Rotating(arrow, angle=2 * math.pi, run_time=2.0))
        render.play(Wait(1.0))

    def section_fade(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("FadeIn & FadeOut", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        sq1 = Square(side_length=1.0, color=BLUE)
        sq1.set_fill(BLUE, opacity=0.7)
        sq1.set_stroke(width=3)
        sq1.shift(LEFT * 4)

        sq2 = Square(side_length=1.0, color=GREEN)
        sq2.set_fill(GREEN, opacity=0.7)
        sq2.set_stroke(width=3)
        sq2.shift(LEFT * 1.5)

        sq3 = Square(side_length=1.0, color=RED)
        sq3.set_fill(RED, opacity=0.7)
        sq3.set_stroke(width=3)
        sq3.shift(RIGHT * 1.5)

        sq4 = Square(side_length=1.0, color=YELLOW)
        sq4.set_fill(YELLOW, opacity=0.7)
        sq4.set_stroke(width=3)
        sq4.shift(RIGHT * 4)

        lbl1 = Text("FadeIn", font_size=16)
        lbl1.shift(LEFT * 4 + DOWN * 1.5)
        lbl2 = Text("FadeOut", font_size=16)
        lbl2.shift(LEFT * 1.5 + DOWN * 1.5)
        lbl3 = Text("FadeTransform", font_size=16)
        lbl3.shift(RIGHT * 1.5 + DOWN * 1.5)
        lbl4 = Text("Shift", font_size=16)
        lbl4.shift(RIGHT * 4 + DOWN * 1.5)

        render.play(Add(lbl1), Add(lbl2), Add(lbl3), Add(lbl4))

        render.play(FadeIn(sq1, run_time=1.0))
        render.play(Wait(0.3))

        render.play(Add(sq2))
        render.play(FadeOut(sq2, run_time=1.0))
        render.play(Wait(0.3))

        render.play(Add(sq3))
        render.play(FadeTransform(sq3, sq4, run_time=1.5))
        render.play(Wait(1.0))

    def section_transform_matching(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Transform Matching Shapes", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        src = Text("abc", font_size=48)
        src.shift(LEFT * 3 + UP * 0.5)

        tar = Text("xyz", font_size=48)
        tar.shift(RIGHT * 3 + UP * 0.5)

        arrow_lbl = Text("→", font_size=36)
        arrow_lbl.shift(UP * 0.5)

        render.play(Write(src, run_time=1.5))
        render.play(Add(tar), Add(arrow_lbl))
        render.play(Wait(0.5))

        render.play(
            TransformMatchingShapes(src, tar, run_time=2.0),
        )
        render.play(Wait(1.5))

    def section_write_stagger(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Write Stagger Effect", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        line1 = Text("Staggered writing", font_size=32)
        line1.shift(UP * 1.0)

        line2 = Text("with lag ratio", font_size=32)
        line2.shift(DOWN * 0.0)

        line3 = Text("animation timing", font_size=32)
        line3.shift(DOWN * 1.0)

        render.play(Write(line1, run_time=2.0, lag_ratio=0.15))
        render.play(Wait(0.3))
        render.play(Write(line2, run_time=2.0, lag_ratio=0.15))
        render.play(Wait(0.3))
        render.play(Write(line3, run_time=2.0, lag_ratio=0.15))
        render.play(Wait(1.0))

    def section_rate_functions(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Rate Functions", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        funcs = [
            ("smooth", _smooth),
            ("linear", _linear),
            ("rush_into", _rush_into),
            ("rush_from", _rush_from),
            ("there_and_back", _there_and_back),
            ("double_smooth", _double_smooth),
        ]

        circles = []
        labels = []
        for i, (name, func) in enumerate(funcs):
            col = i % 3
            row = i // 3
            x = (col - 1) * 3.5
            y = 0.8 - row * 2.0

            c = Circle(radius=0.4, color=BLUE)
            c.set_fill(BLUE, opacity=0.7)
            c.set_stroke(width=2)
            c.shift(LEFT * x + UP * y)

            lbl = Text(name, font_size=14)
            lbl.shift(LEFT * x + UP * (y - 0.7))

            circles.append((c, func))
            labels.append(lbl)

        for lbl in labels:
            render.play(Add(lbl))

        anims = []
        for c, func in circles:
            render.play(Create(c, rate_func=func, run_time=1.5))

        render.play(Wait(1.0))
