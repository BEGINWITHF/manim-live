from manim import *
from core.vulkan_bind import (
    VulkanRender, Animation, Create, Write, Unwrite, Succession, Wait, Add,
    FadeIn, FadeOut, FadeTransform,
    Rotating, Rotate,
    Transform, ReplacementTransform, TransformMatchingShapes, TransformMatchingTex,
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth, _lingering,
    _wiggle, _exponential_decay,
    set_anim_opacity,
)
import math


class TestTransform(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("Test 1: Transform", font_size=36)
        title.shift(UP * 3.0)
        render.play(Add(title))
        render.play(Wait(0.5))

        s1 = Square(side_length=1.5, color=BLUE)
        s1.set_fill(BLUE, opacity=0.7)
        s1.set_stroke(width=4)
        s1.shift(LEFT * 3)

        lbl_src = Text("Square", font_size=20)
        lbl_src.shift(LEFT * 3 + DOWN * 1.5)

        render.play(Add(s1), Add(lbl_src))
        render.play(Wait(0.5))

        t1 = Triangle(color=RED, fill_opacity=0.7, stroke_width=4)
        t1.scale(1.0)
        t1.shift(RIGHT * 3)

        lbl_tgt = Text("Triangle", font_size=20)
        lbl_tgt.shift(RIGHT * 3 + DOWN * 1.5)

        render.play(Add(t1), Add(lbl_tgt))
        render.play(Wait(0.5))

        render.play(Transform(s1, t1, run_time=2.0))
        render.play(Wait(1.0))

        render.close()


class TestTransformMatchingShapes(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("Test 2: TransformMatchingShapes", font_size=36)
        title.shift(UP * 3.0)
        render.play(Add(title))
        render.play(Wait(0.5))

        src = Text("abc", font_size=60)
        src.shift(LEFT * 3)

        tar = Text("xyz", font_size=60)
        tar.shift(RIGHT * 3)

        arrow_lbl = Text("->", font_size=36)
        arrow_lbl.shift(UP * 0.0)

        lbl_src = Text("Source", font_size=20)
        lbl_src.shift(LEFT * 3 + DOWN * 1.8)
        lbl_tgt = Text("Target", font_size=20)
        lbl_tgt.shift(RIGHT * 3 + DOWN * 1.8)

        render.play(Write(src, run_time=1.0))
        render.play(Add(tar), Add(arrow_lbl), Add(lbl_src), Add(lbl_tgt))
        render.play(Wait(0.5))

        render.play(
            TransformMatchingShapes(src, tar, run_time=2.0),
        )
        render.play(Wait(1.0))

        render.close()


class TestFadeTransform(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("Test 3: FadeTransform", font_size=36)
        title.shift(UP * 3.0)
        render.play(Add(title))
        render.play(Wait(0.5))

        s1 = Square(side_length=1.5, color=BLUE)
        s1.set_fill(BLUE, opacity=0.7)
        s1.set_stroke(width=4)

        s2 = Circle(radius=0.8, color=RED)
        s2.set_fill(RED, opacity=0.7)
        s2.set_stroke(width=4)

        lbl_src = Text("Square", font_size=20)
        lbl_src.shift(DOWN * 1.8)
        lbl_tgt = Text("Circle", font_size=20)
        lbl_tgt.shift(DOWN * 1.8)

        render.play(Add(s1), Add(lbl_src))
        render.play(Wait(0.5))

        render.play(FadeTransform(s1, s2, run_time=2.0))
        render.play(Wait(1.0))

        render.close()
