from manim import *
import os

config.pixel_height = 1080
config.pixel_width = 1920
config.frame_height = 8
config.frame_width = 14.222
config.output_file = "RefFadeTransform"
config.disable_caching = True

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

        self.play(
            Create(sq), Create(circ),
            Write(Text("FadeTransform", font_size=28).shift(UP * 2.5)),
        )
        self.play(Wait(0.5))

        self.play(FadeTransform(sq, circ, run_time=2.0))
        self.play(Wait(1.0))

        self.play(Wait(2.0))
