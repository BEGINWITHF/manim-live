from manim import *


class CreateOriginal(Scene):
    def construct(self):
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
        self.wait(1.5)
