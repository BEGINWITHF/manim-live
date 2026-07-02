from manim import *

class RefTransformMatching(Scene):
    def construct(self):
        src = Text("abc", font_size=72)
        src.shift(LEFT * 3.5)

        tar = Text("xyz", font_size=72)
        tar.shift(RIGHT * 3.5)

        arrow = Text("→", font_size=48)
        arrow.shift(UP * 0.2)

        self.play(Write(src, run_time=1.5))
        self.play(FadeIn(tar), FadeIn(arrow))
        self.wait(0.5)

        self.play(TransformMatchingShapes(src, tar, run_time=2.0))
        self.wait(3.0)


class RefFadeTransform(Scene):
    def construct(self):
        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        self.play(FadeIn(sq), FadeIn(circ))
        self.wait(0.5)

        self.play(FadeTransform(sq, circ, run_time=2.0))
        self.wait(3.0)
