from manim import *


class TransformOriginal(Scene):
    def construct(self):
        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        self.play(Add(sq), Add(circ), run_time=0.5)
        self.wait(0.5)

        self.play(Transform(sq, circ, run_time=1.5))
        self.wait(1.0)
