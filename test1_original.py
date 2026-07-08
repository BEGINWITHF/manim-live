from manim import *


class AllShapesOriginal(Scene):
    def construct(self):
        title = Text("Original Manim - All Shapes", font_size=36).to_edge(UP)
        self.add(title)

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
        self.wait(2.0)
