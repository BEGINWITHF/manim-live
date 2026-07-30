import time
import numpy as np
from manim import *
from core.vulkan_bind import (
    VulkanRender, Write, Wait, Add,
    Create, Uncreate, Unwrite,
    FadeIn, FadeOut, FadeTransform,
    Transform, ReplacementTransform,
    Rotating, Rotate,
    TransformMatchingShapes, TransformMatchingTex,
    Animation, Succession, DrawBorderThenFill,
    ShowIncreasingSubsets, SpiralIn,
    Blink, TypeWithCursor,
)


def _title(render, text):
    t = Write(Text(text, font_size=32).shift(UP * 3.2), run_time=0.8)
    render.play(t)


class DemoCreate(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Create - draw shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.6)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.6)
        tri.set_stroke(width=4)
        tri.scale(0.9)
        tri.shift(RIGHT * 4)

        render.play(Create(sq), Create(circ), Create(tri), run_time=2.0)
        render.play(Wait(1.5))
        render.close()


class DemoWriteUnwrite(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write / Unwrite - text")

        t1 = Text("Hello World", font_size=60).shift(UP * 1)
        t2 = Text("Vulkan Render", font_size=48).shift(DOWN * 1)

        render.play(Write(t1, run_time=2.0))
        render.play(Wait(0.5))
        render.play(Write(t2, run_time=1.5))
        render.play(Wait(0.5))
        render.play(Unwrite(t1, run_time=1.5))
        render.play(Wait(0.5))
        render.close()


class DemoTransform(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Transform - morph shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        render.play(Add(sq), Add(circ), run_time=0.5)
        render.play(Wait(0.5))

        render.play(Transform(sq, circ, run_time=1.5))
        render.play(Wait(1.0))
        render.close()


class DemoReplacementTransform(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ReplacementTransform - replace in scene")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)

        tri = Triangle(color=RED)
        tri.set_fill(RED, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.9)

        render.play(Add(sq), run_time=0.5)
        render.play(Wait(0.5))

        render.play(ReplacementTransform(sq, tri, run_time=1.5))
        render.play(Wait(1.0))
        render.close()


class DemoFadeInFadeOut(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeIn / FadeOut")

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 3)

        circ = Circle(radius=0.7, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.8)
        tri.shift(RIGHT * 3)

        render.play(FadeIn(sq), FadeIn(circ), FadeIn(tri), run_time=1.5)
        render.play(Wait(0.5))
        render.play(FadeOut(sq), FadeOut(circ), FadeOut(tri), run_time=1.5)
        render.play(Wait(0.5))
        render.close()


class DemoFadeTransform(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeTransform - crossfade shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 3)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 3)

        render.play(Add(sq), Add(circ), run_time=0.5)
        render.play(Wait(0.5))

        render.play(FadeTransform(sq, circ, run_time=2.0))
        render.play(Wait(1.0))
        render.close()


class DemoRotating(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Rotating / Rotate")

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        tri = Triangle(color=RED)
        tri.set_fill(RED, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.8)

        circ = Circle(radius=0.6, color=GREEN)
        circ.set_fill(GREEN, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        render.play(Add(sq), Add(tri), Add(circ), run_time=0.5)
        render.play(Wait(0.3))

        render.play(Rotating(sq, run_time=3.0))
        render.play(Rotate(tri, angle=PI, run_time=1.5))
        render.play(Rotate(circ, angle=PI / 2, run_time=1.0))
        render.play(Wait(0.5))
        render.close()


class DemoTransformMatchingShapes(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TransformMatchingShapes")

        src = Text("abc", font_size=72)
        src.shift(LEFT * 3.5)

        tar = Text("xyz", font_size=72)
        tar.shift(RIGHT * 3.5)

        render.play(Write(src, run_time=1.5))
        render.play(Add(tar), run_time=0.5)
        render.play(Wait(0.5))

        render.play(TransformMatchingShapes(src, tar, run_time=2.0))
        render.play(Wait(1.5))
        render.close()


class DemoVGroup(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "VGroup - grouped animations")

        squares = VGroup()
        for i in range(5):
            sq = Square(side_length=0.8, color=[BLUE, GREEN, YELLOW, ORANGE, RED][i])
            sq.set_fill(opacity=0.7)
            sq.set_stroke(width=4)
            sq.shift(LEFT * 4 + RIGHT * 2 * i)
            squares.add(sq)

        render.play(Create(squares, run_time=2.0, lag_ratio=0.3))
        render.play(Wait(0.5))
        render.play(FadeOut(squares, run_time=1.5))
        render.play(Wait(0.5))
        render.close()


class DemoAllShapes(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "All supported shapes")

        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 5 + UP * 1.5)

        rect = Rectangle(width=1.6, height=0.9, color=GREEN)
        rect.set_fill(GREEN, opacity=0.6)
        rect.set_stroke(width=4)
        rect.shift(LEFT * 2 + UP * 1.5)

        circ = Circle(radius=0.5, color=RED)
        circ.set_fill(RED, opacity=0.6)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 1 + UP * 1.5)

        tri = Triangle(color=YELLOW)
        tri.set_fill(YELLOW, opacity=0.6)
        tri.set_stroke(width=4)
        tri.scale(0.6)
        tri.shift(RIGHT * 4 + UP * 1.5)

        line = Line(LEFT * 5, RIGHT * 1, color=ORANGE)
        line.set_stroke(width=4)
        line.shift(DOWN * 1)

        arrow = Arrow(LEFT * 1, RIGHT * 4, color=PURPLE)
        arrow.set_stroke(width=4)
        arrow.shift(DOWN * 1)

        dash = DashedLine(LEFT * 5 + DOWN * 2.5, RIGHT * 4 + DOWN * 2.5, color=TEAL)
        dash.set_stroke(width=4)

        render.play(
            Create(sq), Create(rect), Create(circ), Create(tri),
            Create(line), Create(arrow), Create(dash),
            run_time=2.5,
        )
        render.play(Wait(2.0))
        render.close()


class DemoSuccession(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Succession - chained animations")

        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)

        circ = Circle(radius=0.6, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.6)

        render.play(Add(sq), run_time=0.5)
        render.play(Wait(0.3))

        render.play(
            Succession(
                Transform(sq, circ, run_time=1.0),
                Transform(sq, tri, run_time=1.0),
            )
        )
        render.play(Wait(1.0))
        render.close()


class DemoFadeInShift(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeIn with shift/scale")

        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.6, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.6)
        tri.shift(RIGHT * 4)

        render.play(
            FadeIn(sq, shift=UP * 2),
            FadeIn(circ, scale=2.0),
            FadeIn(tri, target_position=sq.get_center()),
            run_time=2.0,
        )
        render.play(Wait(1.5))
        render.play(
            FadeOut(sq, shift=DOWN * 2),
            FadeOut(circ, scale=0.0),
            FadeOut(tri, shift=UP * 2),
            run_time=2.0,
        )
        render.play(Wait(0.5))
        render.close()


class DemoTextFeatures(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Text rendering")

        render.play(Write(Text("Hello World", font_size=60).shift(UP * 1.5)), run_time=2.0)
        render.play(Wait(0.5))
        render.play(Write(Text("Bold Text", font_size=48, weight=BOLD).shift(UP * 0.0)), run_time=1.5)
        render.play(Wait(0.5))
        render.play(Write(Text("Vulkan Renderer", font_size=48).shift(DOWN * 1.5)), run_time=1.5)
        render.play(Wait(1.5))
        render.close()


class DemoCombined(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Combined demo")

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4 + UP * 1)

        circ = Circle(radius=0.7, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4 + UP * 1)

        label = Write(Text("Combined Demo", font_size=28).shift(DOWN * 2.5))

        render.play(Add(sq), Add(circ), label, run_time=1.5)
        render.play(Wait(0.3))

        render.play(Transform(sq, circ, run_time=1.5))
        render.play(Wait(0.5))

        render.play(FadeOut(sq), FadeOut(circ), run_time=1.0)
        render.play(Wait(0.5))
        render.close()


class DemoDefaultAdd(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        text_1 = Text("I was added with Add!")
        text_2 = Text("Me too!")
        text_3 = Text("And me!")
        texts = VGroup(text_1, text_2, text_3).arrange(DOWN)
        rect = SurroundingRectangle(texts, buff=0.5)

        render.play(
            Create(rect, run_time=3.0),
            Succession(
                Wait(1.0),
                Add(text_1),
                Wait(1.0),
                Add(text_2, text_3),
            ),
        )
        render.play(Wait(2.0))
        render.close()


class DemoAddWithRunTime(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        circles = VGroup(
            *[Circle(radius=0.5) for _ in range(25)]
        ).arrange_in_grid(5, 5)

        render.play(
            Succession(
                *[Add(circle, run_time=0.2) for circle in circles],
                rate_func=smooth,
            ),
        )
        render.play(Wait(2.0))
        render.close()


class DemoLagRatios(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        ratios = [0, 0.1, 0.5, 1, 2]

        group = VGroup(*[Dot() for _ in range(4)]).arrange_submobjects()
        groups = VGroup(*[group.copy() for _ in ratios]).arrange_submobjects(buff=1)
        self.add(groups)

        self.add(Text("lag_ratio = ", font_size=36).next_to(groups, UP, buff=1.5))
        for grp, ratio in zip(groups, ratios):
            self.add(Text(str(ratio), font_size=36).next_to(grp, UP))

        render.play(AnimationGroup(*[
            grp.animate(lag_ratio=ratio, run_time=1.5).shift(DOWN * 2)
            for grp, ratio in zip(groups, ratios)
        ]))

        render.play(groups.animate(run_time=1, lag_ratio=0.1).shift(UP * 2))
        render.play(Wait(1.0))
        render.close()


class DemoChangeDefaultAnimation(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        Rotate.set_default(run_time=2, rate_func=rate_functions.linear)
        Indicate.set_default(color=None)

        S = Square(color=BLUE, fill_color=BLUE, fill_opacity=0.25)
        self.add(S)
        render.play(Rotate(S, PI))
        render.play(Indicate(S))

        Rotate.set_default()
        Indicate.set_default()
        render.play(Wait(0.5))
        render.close()


class DemoAnimatedBoundary(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        text = Text("So shiny!")
        boundary = AnimatedBoundary(text, colors=[RED, GREEN, BLUE],
                                    cycle_rate=3)
        self.add(text, boundary)
        render.play(Wait(2.0))
        render.close()


# you are not allowed to change any code here --TT Noted
class DemoTracedPath(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        circ = Circle(color=RED).shift(4 * LEFT)
        dot = Dot(color=RED).move_to(circ.get_start())
        rolling_circle = VGroup(circ, dot)
        trace = TracedPath(circ.get_start)
        rolling_circle.add_updater(lambda m: m.rotate(-0.3))
        self.add(trace, rolling_circle)
        render.play(rolling_circle.animate.shift(8 * RIGHT), run_time=4, rate_func=linear)


class DemoDissipatingPath(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        a = Dot(RIGHT * 2)
        b = TracedPath(a.get_center, dissipating_time=0.5, stroke_opacity=[0, 1])
        self.add(a, b)
        render.play(a.animate(path_arc=PI / 4).shift(LEFT * 2))
        render.play(a.animate(path_arc=-PI / 4).shift(LEFT * 2))
        render.play(Wait(1.0))
        render.close()


class DemoLaggedStartMap(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        title = Text("LaggedStartMap").to_edge(UP, buff=LARGE_BUFF)
        dots = VGroup(
            *[Dot(radius=0.16) for _ in range(35)]
            ).arrange_in_grid(rows=5, cols=7, buff=MED_LARGE_BUFF)
        self.add(dots, title)

        for mob in dots, title:
            render.play(LaggedStartMap(
                ApplyMethod, mob,
                lambda m: (m.set_color, YELLOW),
                lag_ratio=0.1,
                rate_func=there_and_back,
                run_time=2
            ))
        render.play(Wait(0.5))
        render.close()


class DemoLaggedStart(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        title = Text("lag_ratio = 0.25").to_edge(UP)

        dot1 = Dot(point=LEFT * 2 + UP, radius=0.16)
        dot2 = Dot(point=LEFT * 2, radius=0.16)
        dot3 = Dot(point=LEFT * 2 + DOWN, radius=0.16)
        line_25 = DashedLine(
            start=LEFT + UP * 2,
            end=LEFT + DOWN * 2,
            color=RED
        )
        label = Text("25%", font_size=24).next_to(line_25, UP)
        self.add(title, dot1, dot2, dot3, line_25, label)

        render.play(LaggedStart(
            dot1.animate.shift(RIGHT * 4),
            dot2.animate.shift(RIGHT * 4),
            dot3.animate.shift(RIGHT * 4),
            lag_ratio=0.25,
            run_time=4
        ))
        render.play(Wait(1.0))
        render.close()


class DemoSuccessionDots(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        dot1 = Dot(point=LEFT * 2 + UP * 2, radius=0.16, color=BLUE)
        dot2 = Dot(point=LEFT * 2 + DOWN * 2, radius=0.16, color=MAROON)
        dot3 = Dot(point=RIGHT * 2 + DOWN * 2, radius=0.16, color=GREEN)
        dot4 = Dot(point=RIGHT * 2 + UP * 2, radius=0.16, color=YELLOW)
        self.add(dot1, dot2, dot3, dot4)

        render.play(Succession(
            dot1.animate.move_to(dot2),
            dot2.animate.move_to(dot3),
            dot3.animate.move_to(dot4),
            dot4.animate.move_to(dot1)
        ))
        render.play(Wait(0.5))
        render.close()


class DemoCreateSquare(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        sq = Square()
        self.add(sq)
        render.play(Create(sq))
        render.play(Wait(1.0))
        render.close()

# you are not allowed to change any code here --TT Noted
class DemoDrawBorderThenFill(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "DrawBorderThenFill")

        sq = Square(fill_opacity=1, fill_color=ORANGE)
        sq.set_stroke(width=4)

        render.play(DrawBorderThenFill(sq, run_time=2.0))
        render.play(Wait(1.5))
        render.close()


class DemoShowIncreasingSubsets(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ShowIncreasingSubsets")

        p = VGroup(Dot(), Square(), Triangle())
        self.add(p)
        render.play(ShowIncreasingSubsets(p, run_time=2.0))
        render.play(Wait(1.5))
        render.close()


class DemoSpiralIn(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "SpiralIn")

        circle = Circle(color=GREEN_C, fill_opacity=1).shift(LEFT)
        square = Square(color=BLUE_D, fill_opacity=1).shift(UP)
        shapes = VGroup(circle, square)
        self.add(shapes)
        render.play(SpiralIn(shapes))
        render.play(Wait(1.5))
        render.close()


class DemoTypeWithCursor(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TypeWithCursor + Blink")

        text = Text("Inserting", color=PURPLE).scale(1.5).to_edge(LEFT)
        cursor = Rectangle(
            color=GREY_A,
            fill_color=GREY_A,
            fill_opacity=1.0,
            height=1.1,
            width=0.5,
        ).move_to(text[0])

        render.play(TypeWithCursor(text, cursor, time_per_char=0.15, run_time=2.5))
        render.play(Blink(cursor, blinks=2, time_on=0.4, time_off=0.4, run_time=2.0))
        render.play(Wait(0.5))
        render.close()


class DemoUncreate(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Uncreate - reverse of Create")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)

        render.play(Create(sq, run_time=1.0))
        render.play(Wait(0.5))
        render.play(Uncreate(sq, run_time=1.5))
        render.play(Wait(0.5))
        render.close()
