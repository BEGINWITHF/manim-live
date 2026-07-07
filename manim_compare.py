from manim import *


def _title(scene, text):
    scene.play(Write(Text(text, font_size=32).shift(UP * 3.2), run_time=0.8))


class DemoCreate(Scene):
    def construct(self):
        _title(self, "Create - draw shapes")

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

        self.play(Create(sq), Create(circ), Create(tri), run_time=2.0)
        self.play(Wait(1.5))


class DemoWriteUnwrite(Scene):
    def construct(self):
        _title(self, "Write / Unwrite - text")

        t1 = Text("Hello World", font_size=60).shift(UP * 1)
        t2 = Text("Vulkan Render", font_size=48).shift(DOWN * 1)

        self.play(Write(t1, run_time=2.0))
        self.play(Wait(0.5))
        self.play(Write(t2, run_time=1.5))
        self.play(Wait(0.5))
        self.play(Unwrite(t1, run_time=1.5))
        self.play(Wait(0.5))


class DemoTransform(Scene):
    def construct(self):
        _title(self, "Transform - morph shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        self.play(Create(sq), Create(circ), run_time=0.5)
        self.play(Wait(0.5))

        self.play(Transform(sq, circ, run_time=1.5))
        self.play(Wait(1.0))


class DemoReplacementTransform(Scene):
    def construct(self):
        _title(self, "ReplacementTransform - replace in scene")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)

        tri = Triangle(color=RED)
        tri.set_fill(RED, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.9)

        self.play(Create(sq), run_time=0.5)
        self.play(Wait(0.5))

        self.play(ReplacementTransform(sq, tri, run_time=1.5))
        self.play(Wait(1.0))


class DemoFadeInFadeOut(Scene):
    def construct(self):
        _title(self, "FadeIn / FadeOut")

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

        self.play(FadeIn(sq), FadeIn(circ), FadeIn(tri), run_time=1.5)
        self.play(Wait(0.5))
        self.play(FadeOut(sq), FadeOut(circ), FadeOut(tri), run_time=1.5)
        self.play(Wait(0.5))


class DemoFadeTransform(Scene):
    def construct(self):
        _title(self, "FadeTransform - crossfade shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 3)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 3)

        self.play(Create(sq), Create(circ), run_time=0.5)
        self.play(Wait(0.5))

        self.play(FadeTransform(sq, circ, run_time=2.0))
        self.play(Wait(1.0))


class DemoRotating(Scene):
    def construct(self):
        _title(self, "Rotating / Rotate")

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

        self.play(Create(sq), Create(tri), Create(circ), run_time=0.5)
        self.play(Wait(0.3))

        self.play(Rotating(sq, run_time=3.0))
        self.play(Rotate(tri, angle=PI, run_time=1.5))
        self.play(Rotate(circ, angle=PI / 2, run_time=1.0))
        self.play(Wait(0.5))


class DemoTransformMatchingShapes(Scene):
    def construct(self):
        _title(self, "TransformMatchingShapes")

        src = Text("abc", font_size=72)
        src.shift(LEFT * 3.5)

        tar = Text("xyz", font_size=72)
        tar.shift(RIGHT * 3.5)

        self.play(Write(src, run_time=1.5))
        self.play(Create(tar), run_time=0.5)
        self.play(Wait(0.5))

        self.play(TransformMatchingShapes(src, tar, run_time=2.0))
        self.play(Wait(1.5))


class DemoVGroup(Scene):
    def construct(self):
        _title(self, "VGroup - grouped animations")

        squares = VGroup()
        for i in range(5):
            sq = Square(side_length=0.8, color=[BLUE, GREEN, YELLOW, ORANGE, RED][i])
            sq.set_fill(opacity=0.7)
            sq.set_stroke(width=3)
            sq.shift(LEFT * 4 + RIGHT * 2 * i)
            squares.add(sq)

        self.play(Create(squares, run_time=2.0, lag_ratio=0.3))
        self.play(Wait(0.5))
        self.play(FadeOut(squares, run_time=1.5))
        self.play(Wait(0.5))


class DemoAllShapes(Scene):
    def construct(self):
        _title(self, "All supported shapes")

        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 5 + UP * 1.5)

        rect = Rectangle(width=1.6, height=0.9, color=GREEN)
        rect.set_fill(GREEN, opacity=0.6)
        rect.set_stroke(width=3)
        rect.shift(LEFT * 2 + UP * 1.5)

        circ = Circle(radius=0.5, color=RED)
        circ.set_fill(RED, opacity=0.6)
        circ.set_stroke(width=3)
        circ.shift(RIGHT * 1 + UP * 1.5)

        tri = Triangle(color=YELLOW)
        tri.set_fill(YELLOW, opacity=0.6)
        tri.set_stroke(width=3)
        tri.scale(0.6)
        tri.shift(RIGHT * 4 + UP * 1.5)

        line = Line(LEFT * 5, RIGHT * 1, color=ORANGE)
        line.set_stroke(width=4)
        line.shift(DOWN * 1)

        arrow = Arrow(LEFT * 1, RIGHT * 4, color=PURPLE)
        arrow.set_stroke(width=4)
        arrow.shift(DOWN * 1)

        dash = DashedLine(LEFT * 5 + DOWN * 2.5, RIGHT * 4 + DOWN * 2.5, color=TEAL)
        dash.set_stroke(width=3)

        self.play(
            Create(sq), Create(rect), Create(circ), Create(tri),
            Create(line), Create(arrow), Create(dash),
            run_time=2.5,
        )
        self.play(Wait(2.0))


class DemoSuccession(Scene):
    def construct(self):
        _title(self, "Succession - chained animations")

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

        self.play(Create(sq), run_time=0.5)
        self.play(Wait(0.3))

        self.play(
            Succession(
                Transform(sq, circ, run_time=1.0),
                Transform(sq, tri, run_time=1.0),
            )
        )
        self.play(Wait(1.0))


class DemoFadeInShift(Scene):
    def construct(self):
        _title(self, "FadeIn with shift/scale")

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

        self.play(
            FadeIn(sq, shift=UP * 2),
            FadeIn(circ, scale=2.0),
            FadeIn(tri, target_position=sq.get_center()),
            run_time=2.0,
        )
        self.play(Wait(1.5))
        self.play(
            FadeOut(sq, shift=DOWN * 2),
            FadeOut(circ, scale=0.0),
            FadeOut(tri, shift=UP * 2),
            run_time=2.0,
        )
        self.play(Wait(0.5))


class DemoTextFeatures(Scene):
    def construct(self):
        _title(self, "Text rendering")

        self.play(Write(Text("Hello World", font_size=60).shift(UP * 1.5)), run_time=2.0)
        self.play(Wait(0.5))
        self.play(Write(Text("Bold Text", font_size=48, weight=BOLD).shift(UP * 0.0)), run_time=1.5)
        self.play(Wait(0.5))
        self.play(Write(Text("Vulkan Renderer", font_size=48).shift(DOWN * 1.5)), run_time=1.5)
        self.play(Wait(1.5))


class DemoCombined(Scene):
    def construct(self):
        _title(self, "Combined demo")

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4 + UP * 1)

        circ = Circle(radius=0.7, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4 + UP * 1)

        label = Write(Text("Combined Demo", font_size=28).shift(DOWN * 2.5))

        self.play(Create(sq), Create(circ), label, run_time=1.5)
        self.play(Wait(0.3))

        self.play(Transform(sq, circ, run_time=1.5))
        self.play(Wait(0.5))

        self.play(FadeOut(sq), FadeOut(circ), run_time=1.0)
        self.play(Wait(0.5))
