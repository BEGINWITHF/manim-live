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
    Animation, AnimationGroup, Succession, DrawBorderThenFill,
    ShowIncreasingSubsets, SpiralIn, GrowFromCenter, GrowArrow, GrowFromEdge, GrowFromPoint,
    SpinInFromNothing, ApplyWave, Circumscribe,
    Blink, TypeWithCursor, UntypeWithCursor, Indicate, ShowPassingFlash, Homotopy, MoveAlongPath,
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


class DemoUntypeWithCursor(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "UntypeWithCursor + Blink")
        text = Text("Deleting", color=PURPLE).scale(1.5).to_edge(LEFT)
        cursor = Rectangle(
            color=GREY_A,
            fill_color=GREY_A,
            fill_opacity=1.0,
            height=1.1,
            width=0.5,
        ).move_to(text[0])

        render.play(UntypeWithCursor(text, cursor))
        render.play(Blink(cursor, blinks=2))
        render.close()


class DemoUnwriteReverseTrue(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Unwrite reverse=True")

        text = Text("Alice and Bob").scale(3)
        render.play(Write(text))
        render.play(Wait(1.0))
        render.play(Unwrite(text, reverse=True))
        render.play(Wait(1.0))
        render.close()


class DemoUnwriteReverseFalse(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Unwrite reverse=False")

        text = Text("Alice and Bob").scale(3)
        render.play(Write(text))
        render.play(Wait(1.0))
        render.play(Unwrite(text, reverse=False))
        render.play(Wait(1.0))
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


class DemoShowWrite(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write - font_size=144")

        text = Text("Hello", font_size=144)
        render.play(Write(text))
        render.play(Wait(1.5))
        render.close()


class DemoShowWriteReversed(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write reversed - font_size=144")

        text = Text("Hello", font_size=144)
        render.play(Write(text, reverse=True, remover=False))
        render.play(Wait(1.5))
        render.close()


class DemoFadeInExample(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeIn with shift/target_position/scale")

        dot = Dot(UP * 2 + LEFT)
        self.add(dot)

        w0 = Text("FadeIn with", font_size=36)
        w1 = Text("shift", font_size=36)
        w2 = Text("target_position", font_size=36)
        w3 = Text("and scale", font_size=36)
        words = VGroup(w0, w1, w2, w3).arrange(RIGHT, buff=0.3)

        animations = [
            FadeIn(w0),
            FadeIn(w1, shift=DOWN),
            FadeIn(w2, target_position=dot),
            FadeIn(w3, scale=1.5),
        ]
        render.play(AnimationGroup(*animations, lag_ratio=0.5))
        render.play(Wait(1.5))
        render.close()


class DemoFadeOutExample(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeOut with shift/target_position/scale")

        dot = Dot(UP * 2 + LEFT)
        self.add(dot)

        t0 = Text("FadeOut with", font_size=36)
        t1 = Text("shift", font_size=36)
        t2 = Text("target_position", font_size=36)
        t3 = Text("and scale", font_size=36)
        tex = VGroup(t0, t1, t2, t3).arrange(RIGHT, buff=0.3)
        self.add(t0, t1, t2, t3)

        animations = [
            FadeOut(t0),
            FadeOut(t1, shift=DOWN),
            FadeOut(t2, target_position=dot),
            FadeOut(t3, scale=0.5),
        ]
        render.play(AnimationGroup(*animations, lag_ratio=0.5))
        render.play(Wait(1.5))
        render.close()


class DemoGrowFromCenter(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowFromCenter")

        squares = [Square() for _ in range(2)]
        VGroup(*squares).set_x(0).arrange(buff=2)

        render.play(GrowFromCenter(squares[0]))
        render.play(GrowFromCenter(squares[1], point_color=RED))
        render.play(Wait(1.5))
        render.close()


class DemoGrowArrow(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowArrow")

        arrows = [Arrow(2 * LEFT, 2 * RIGHT), Arrow(2 * DR, 2 * UL)]
        VGroup(*arrows).set_x(0).arrange(buff=2)

        render.play(GrowArrow(arrows[0]))
        render.play(GrowArrow(arrows[1], point_color=RED))
        render.play(Wait(1.5))
        render.close()


class DemoGrowFromEdge(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowFromEdge")

        squares = [Square() for _ in range(4)]
        VGroup(*squares).set_x(0).arrange(buff=1)

        render.play(GrowFromEdge(squares[0], DOWN))
        render.play(GrowFromEdge(squares[1], RIGHT))
        render.play(GrowFromEdge(squares[2], UR))
        render.play(GrowFromEdge(squares[3], UP, point_color=RED))
        render.play(Wait(1.5))
        render.close()


class DemoGrowFromPoint(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowFromPoint")

        dot = Dot(3 * UR, color=GREEN)
        squares = [Square() for _ in range(4)]
        VGroup(*squares).set_x(0).arrange(buff=1)
        self.add(dot)

        render.play(GrowFromPoint(squares[0], ORIGIN))
        render.play(GrowFromPoint(squares[1], [-2, 2, 0]))
        render.play(GrowFromPoint(squares[2], [3, -2, 0], RED))
        render.play(GrowFromPoint(squares[3], dot, dot.get_color()))
        render.play(Wait(1.5))
        render.close()


class DemoSpinInFromNothing(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "SpinInFromNothing")

        squares = [Square() for _ in range(3)]
        VGroup(*squares).set_x(0).arrange(buff=2)

        render.play(SpinInFromNothing(squares[0]))
        render.play(SpinInFromNothing(squares[1], angle=2 * PI))
        render.play(SpinInFromNothing(squares[2], point_color=RED))
        render.play(Wait(1.5))
        render.close()


class DemoApplyingWaves(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ApplyWave")

        tex = Text("WaveWaveWaveWaveWave", font_size=36).scale(2)
        self.add(tex)

        render.play(ApplyWave(tex))
        render.play(ApplyWave(tex, direction=RIGHT, time_width=0.5, amplitude=0.3))
        render.play(ApplyWave(tex, rate_func=linear, ripples=4))
        render.play(Wait(1.5))
        render.close()


class DemoBlinking(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Blink")

        text = Text("Blinking", font_size=36).scale(1.5)
        self.add(text)

        render.play(Blink(text, blinks=3))
        render.play(Wait(1.5))
        render.close()


class DemoCircumscribe(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Circumscribe")

        lbl = Text("Circum-\nscribe", font_size=36).scale(2)
        self.add(lbl)

        render.play(Circumscribe(lbl))
        render.play(Circumscribe(lbl, Circle))
        render.play(Circumscribe(lbl, fade_out=True))
        render.play(Circumscribe(lbl, time_width=2))
        render.play(Circumscribe(lbl, Circle, True))
        render.play(Wait(1.5))
        render.close()


class DemoUsingIndicate(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Indicate")

        tex = Text("Indicate", font_size=36).scale(3)
        self.add(tex)

        render.play(Indicate(tex))
        render.play(Wait(1.5))
        render.close()


class DemoUsingFlash(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Flash")

        dot = Dot(color=PURE_YELLOW).shift(DOWN)
        self.add(Text("Flash the dot below:"), dot)
        render.play(Flash(dot))
        render.play(Wait(1.5))
        render.close()


class DemoFlashOnCircle(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Flash on Circle")
        radius = 2
        circle = Circle(radius)
        self.add(circle)
        render.play(Flash(
            circle, line_length=1,
            num_lines=30, color=RED,
            flash_radius=radius + SMALL_BUFF,
            time_width=0.3, run_time=2,
            rate_func=rush_from,
        ))
        render.play(Wait(1.5))
        render.close()


class DemoFocusOn(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FocusOn")
        dot = Dot(color=PURE_YELLOW).shift(DOWN)
        self.add(Text("Focusing on the dot below:"), dot)
        anim = FocusOn(dot, run_time=1, opacity=0.03)
        anim.mobject.move_to(dot.get_center())
        render.play(anim)
        render.play(Wait(1.5))
        render.close()


class DemoTimeWidthValues(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        p = RegularPolygon(5, color=DARK_GRAY, stroke_width=6).scale(3)
        self.add(p)

        p = p.copy().set_color(BLUE)

        for time_width in [0.2, 0.5, 1, 2]:
            lbl = Text(f"time_width={time_width:.1f}", font_size=36)
            self.add(lbl)
            render.play(ShowPassingFlash(p.copy().set_color(BLUE), run_time=2, time_width=time_width))
            self.remove(lbl)

        render.play(Wait(1.5))
        render.close()


class DemoHomotopy(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        square = Square()
        self.add(square)

        def homotopy(x, y, z, t):
            if t <= 0.25:
                progress = t / 0.25
                return (x, y + progress * 0.2 * np.sin(x), z)
            else:
                wave_progress = (t - 0.25) / 0.75
                return (x, y + 0.2 * np.sin(x + 10 * wave_progress), z)

        render.play(Homotopy(homotopy, square, rate_func=linear, run_time=2))
        render.play(Wait(1.5))
        render.close()

class DemoMoveAlongPath(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        d1 = Dot().set_color(ORANGE)
        l1 = Line(LEFT, RIGHT)
        self.add(d1, l1)

        render.play(MoveAlongPath(d1, l1), rate_func=linear)
        render.play(Wait(1.5))
        render.close()


class DemoWiggle(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Wiggle")
        tex = Text("Wiggle").scale(3)
        self.add(tex)
        render.play(Wiggle(tex))
        render.play(Wait(1.5))
        render.close()


class DemoChangeDecimalToValue(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        _title(render, "ChangeDecimalToValue")
        start_num = Text("0.00", font_size=144)
        end_num = Text("99.99", font_size=144)
        self.add(start_num)
        render.play(Transform(start_num, end_num), run_time=3)
        render.play(Wait(1))
        render.close()