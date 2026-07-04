from manim import *
from core.vulkan_bind import (
    VulkanRender, Write, Wait, Add,
    FadeTransform,
    Transform, TransformMatchingShapes,
)


class TestTransform(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        tri = Triangle(color=RED, fill_opacity=0.7, stroke_width=4)
        tri.scale(0.9)
        tri.shift(RIGHT * 4)

        render.play(
            Add(sq), Add(tri),
            Write(Text("Transform", font_size=28).shift(UP * 2.5)),
        )
        render.play(Wait(0.5))

        render.play(Transform(sq, tri, run_time=1.5))
        render.play(Wait(1.0))

        render.play(Wait(2.0))
        render.close()


class TestTransformMatchingShapes(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        src = Text("abc", font_size=72)
        src.shift(LEFT * 3.5)

        tar = Text("xyz", font_size=72)
        tar.shift(RIGHT * 3.5)

        arrow = Text("→", font_size=48)
        arrow.shift(UP * 0.2)

        render.play(Write(src, run_time=1.5))
        render.play(Add(tar), Add(arrow))
        render.play(Wait(0.5))

        render.play(TransformMatchingShapes(src, tar, run_time=2.0))
        render.play(Wait(1.0))

        render.play(Wait(2.0))
        render.close()


class TestFadeTransform(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        render.play(
            Add(sq), Add(circ),
            Write(Text("FadeTransform", font_size=28).shift(UP * 2.5)),
        )
        render.screenshot(r"C:\Users\begin\Desktop\our_ft_before.png")

        ft = FadeTransform(sq, circ, run_time=2.0)
        render.play(
            ft,
            screenshot_at={
                ft: [
                    (0.25, r"C:\Users\begin\Desktop\our_ft_25.png"),
                    (0.50, r"C:\Users\begin\Desktop\our_ft_50.png"),
                    (0.75, r"C:\Users\begin\Desktop\our_ft_75.png"),
                ]
            }
        )
        render.screenshot(r"C:\Users\begin\Desktop\our_ft_after.png")

        render.play(Wait(1.0))
        render.close()
