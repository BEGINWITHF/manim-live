from manim import *
from core.vulkan_bind import VulkanRender
import math


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1280, 720)

        border_top = Line(LEFT * 7 + UP * 4, RIGHT * 7 + UP * 4)
        border_top.set_stroke(RED, width=0.011)
        border_bot = Line(LEFT * 7 + DOWN * 4, RIGHT * 7 + DOWN * 4)
        border_bot.set_stroke(RED, width=0.011)
        border_left = Line(LEFT * 7 + DOWN * 4, LEFT * 7 + UP * 4)
        border_left.set_stroke(RED, width=0.011)
        border_right = Line(RIGHT * 7 + DOWN * 4, RIGHT * 7 + UP * 4)
        border_right.set_stroke(RED, width=0.011)
        self.add(border_top, border_bot, border_left, border_right)

        title_text = Text("Vulkan Shape Showcase", font_size=28)
        title_text.to_edge(UP, buff=0.3)
        self.add(title_text)

        square = Square(side_length=1.0)
        square.set_fill(BLUE_D, opacity=0.7)
        square.set_stroke(WHITE, width=2)
        square.shift(LEFT * 5 + UP * 1.5)
        self.add(square)

        label_sq = Text("Square", font_size=14)
        label_sq.next_to(square, DOWN, buff=0.15)
        self.add(label_sq)


        rectangle = Rectangle(width=1.8, height=0.9)
        rectangle.set_fill(TEAL_D, opacity=0.7)
        rectangle.set_stroke(WHITE, width=2)
        rectangle.shift(LEFT * 2.5 + UP * 1.5)
        self.add(rectangle)

        label_rect = Text("Rectangle", font_size=14)
        label_rect.next_to(rectangle, DOWN, buff=0.15)
        self.add(label_rect)


        circle = Circle(radius=0.5)
        circle.set_fill(YELLOW_D, opacity=0.7)
        circle.set_stroke(WHITE, width=2)
        circle.shift(UP * 1.5)
        self.add(circle)

        label_circ = Text("Circle", font_size=14)
        label_circ.next_to(circle, DOWN, buff=0.15)
        self.add(label_circ)


        ellipse = Ellipse(width=1.6, height=0.8)
        ellipse.set_fill(RED_D, opacity=0.5)
        ellipse.set_stroke(RED, width=2)
        ellipse.shift(RIGHT * 2.5 + UP * 1.5)
        self.add(ellipse)

        label_ell = Text("Ellipse", font_size=14)
        label_ell.next_to(ellipse, DOWN, buff=0.15)
        self.add(label_ell)


        dot = Dot(LEFT * 5 + UP * 0, radius=0.08)
        dot.set_fill(PINK, opacity=1.0)
        self.add(dot)

        label_dot = Text("Dot", font_size=14)
        label_dot.next_to(dot, DOWN, buff=0.15)
        self.add(label_dot)


        line = Line(LEFT * 3.5 + UP * 0, LEFT * 1.5 + UP * 0)
        line.set_stroke(GREEN, width=4)
        self.add(line)

        label_line = Text("Line", font_size=14)
        label_line.next_to(line, DOWN, buff=0.15)
        self.add(label_line)


        arrow = Arrow(ORIGIN + RIGHT * 0.5, RIGHT * 2.5 + UP * 0)
        arrow.set_stroke(ORANGE, width=3)
        arrow.set_fill(ORANGE, opacity=0.8)
        self.add(arrow)

        label_arrow = Text("Arrow", font_size=14)
        label_arrow.next_to(arrow, DOWN, buff=0.15)
        self.add(label_arrow)


        dash = DashedLine(LEFT * 0.5 + UP * 0, RIGHT * 1.0 + UP * 0)
        dash.set_stroke(PURPLE, width=3)
        dash.dash_length = 0.15
        dash.gap_length = 0.08
        self.add(dash)

        label_dash = Text("DashedLine", font_size=14)
        label_dash.next_to(dash, DOWN, buff=0.15)
        self.add(label_dash)


        triangle = Triangle()
        triangle.set_fill(GREEN_D, opacity=0.6)
        triangle.set_stroke(WHITE, width=2)
        triangle.scale(0.55)
        triangle.shift(LEFT * 4.5 + DOWN * 1.5)
        self.add(triangle)

        label_tri = Text("Triangle", font_size=14)
        label_tri.next_to(triangle, DOWN, buff=0.15)
        self.add(label_tri)


        pentagon = RegularPolygon(n=5, radius=0.55)
        pentagon.set_fill(MAROON_D, opacity=0.6)
        pentagon.set_stroke(WHITE, width=2)
        pentagon.shift(LEFT * 2.0 + DOWN * 1.5)
        self.add(pentagon)

        label_pent = Text("Pentagon", font_size=14)
        label_pent.next_to(pentagon, DOWN, buff=0.15)
        self.add(label_pent)


        hexagon = RegularPolygon(n=6, radius=0.55)
        hexagon.set_fill(TEAL_D, opacity=0.6)
        hexagon.set_stroke(WHITE, width=2)
        hexagon.shift(LEFT * 0.0 + DOWN * 1.5)
        self.add(hexagon)

        label_hex = Text("Hexagon", font_size=14)
        label_hex.next_to(hexagon, DOWN, buff=0.15)
        self.add(label_hex)


        octagon = RegularPolygon(n=8, radius=0.55)
        octagon.set_fill(GOLD_D, opacity=0.6)
        octagon.set_stroke(WHITE, width=2)
        octagon.shift(RIGHT * 2.0 + DOWN * 1.5)
        self.add(octagon)

        label_oct = Text("Octagon", font_size=14)
        label_oct.next_to(octagon, DOWN, buff=0.15)
        self.add(label_oct)


        arc = Arc(radius=0.5, start_angle=0, angle=math.pi * 1.5)
        arc.set_stroke(YELLOW, width=3)
        arc.shift(RIGHT * 4.5 + DOWN * 1.5)
        self.add(arc)

        label_arc = Text("Arc", font_size=14)
        label_arc.next_to(arc, DOWN, buff=0.15)
        self.add(label_arc)


        point = Point(LEFT * 4.5 + DOWN * 3.0)
        point.set_color(WHITE)
        self.add(point)

        label_point = Text("Point", font_size=14)
        label_point.next_to(point, DOWN, buff=0.15)
        self.add(label_point)


        custom_poly = Polygon(
            LEFT * 1.5 + DOWN * 3.0, UP * 0.3 + LEFT * 0.8 + DOWN * 3.0,
            RIGHT * 0.3 + DOWN * 2.7, RIGHT * 1.2 + DOWN * 3.3,
            LEFT * 0.5 + DOWN * 3.5
        )
        custom_poly.set_fill(BLUE_E, opacity=0.5)
        custom_poly.set_stroke(WHITE, width=2)
        self.add(custom_poly)

        label_custom = Text("Irregular", font_size=14)
        label_custom.next_to(custom_poly, DOWN, buff=0.15)
        self.add(label_custom)


        circ1 = Circle(radius=0.4)
        circ1.set_fill(RED, opacity=0.5)
        circ1.set_stroke(RED, width=1)
        circ1.shift(RIGHT * 1.5 + DOWN * 3.0)

        circ2 = Circle(radius=0.4)
        circ2.set_fill(BLUE, opacity=0.5)
        circ2.set_stroke(BLUE, width=1)
        circ2.shift(RIGHT * 2.0 + DOWN * 3.0)

        self.add(circ1, circ2)

        label_blend = Text("Blending", font_size=14)
        label_blend.next_to(circ1, DOWN, buff=0.4)
        self.add(label_blend)

        frame_count = 0

        while render.tick():
            frame_count += 1

            square.rotate(0.02)
            rectangle.rotate(-0.015)

            pentagon.rotate(0.01)
            hexagon.rotate(-0.008)
            octagon.rotate(0.006)

            dot_y = math.sin(frame_count * 0.05) * 0.3
            dot.move_to(LEFT * 5 + UP * dot_y)

            render.sync(self, frame_count * 0.02)

        render.close()
