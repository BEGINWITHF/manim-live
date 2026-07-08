from manim import *


class CompareAllShapes(Scene):
    def construct(self):
        title = Text("Original Manim - Shape Comparison", font_size=36).to_edge(UP)
        self.add(title)

        # Row 1: Basic shapes with fill + stroke
        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 5 + UP * 1)

        rect = Rectangle(width=1.6, height=0.9, color=GREEN)
        rect.set_fill(GREEN, opacity=0.6)
        rect.set_stroke(width=4)
        rect.shift(LEFT * 2 + UP * 1)

        circ = Circle(radius=0.5, color=RED)
        circ.set_fill(RED, opacity=0.6)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 1 + UP * 1)

        tri = Triangle(color=YELLOW)
        tri.set_fill(YELLOW, opacity=0.6)
        tri.set_stroke(width=4)
        tri.scale(0.6)
        tri.shift(RIGHT * 4 + UP * 1)

        # Row 2: Line, Arrow, DashedLine
        line = Line(LEFT * 5, RIGHT * 1, color=ORANGE)
        line.set_stroke(width=4)
        line.shift(DOWN * 0.5)

        arrow = Arrow(LEFT * 1, RIGHT * 4, color=PURPLE)
        arrow.set_stroke(width=4)
        arrow.shift(DOWN * 0.5)

        dash = DashedLine(LEFT * 5 + DOWN * 2, RIGHT * 4 + DOWN * 2, color=TEAL)
        dash.set_stroke(width=3)

        # Row 3: Ellipse, Arc, Polygon
        ell = Ellipse(width=1.6, height=0.8, color=BLUE_B)
        ell.set_fill(BLUE_B, opacity=0.6)
        ell.set_stroke(width=4)
        ell.shift(LEFT * 5 + DOWN * 3)

        arc = Arc(radius=0.6, start_angle=0, angle=PI * 1.5, color=RED_B)
        arc.set_stroke(width=4)
        arc.shift(LEFT * 2 + DOWN * 3)

        poly = Polygon(
            [0, 0.6, 0],
            [0.6, -0.3, 0],
            [-0.6, -0.3, 0],
            color=GREEN_B,
        )
        poly.set_fill(GREEN_B, opacity=0.6)
        poly.set_stroke(width=4)
        poly.shift(RIGHT * 1 + DOWN * 3)

        # Arrow with bigger head for comparison
        arrow2 = Arrow(LEFT * 1, RIGHT * 4, color=RED)
        arrow2.set_stroke(width=4)
        arrow2.shift(DOWN * 4.5)

        self.add(sq, rect, circ, tri, line, arrow, dash, ell, arc, poly, arrow2)
        self.wait(2)
