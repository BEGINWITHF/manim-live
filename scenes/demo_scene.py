from manim import *
from core.vulkan_bind import VulkanRender, Create, Succession, Wait, Add


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1280, 720)
        render.scene = self

        section_title = Text("Vulkan Full Function Test", font_size=40)
        section_title.shift(UP * 3.3)

        sq = Square(side_length=1.0, color=RED)
        sq.set_fill(opacity=0)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 5.25 + UP * 2)

        rect = Rectangle(width=2.0, height=1.2, color=ORANGE)
        rect.shift(LEFT * 1.75 + UP * 2)

        circ = Circle(radius=0.6, color=BLUE)
        circ.set_fill(opacity=0)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 1.75 + UP * 2)

        ell = Ellipse(width=1.8, height=0.8, color=TEAL)
        ell.set_fill(opacity=0)
        ell.set_stroke(width=4)
        ell.shift(RIGHT * 5.25 + UP * 2)

        ln = Line(start=LEFT * 6 + UP * 0.5, end=RIGHT * 6 + UP * 0.5, color=GREEN)
        ln.set_stroke(width=3)

        arr = Arrow(start=LEFT * 3 + DOWN * 0.2, end=RIGHT * 3 + DOWN * 0.2, color=YELLOW)
        arr.set_stroke(width=3)

        dl = DashedLine(
            start=LEFT * 6 + DOWN * 0.9,
            end=RIGHT * 6 + DOWN * 0.9,
            color=PINK,
        )

        arc = Arc(radius=0.6, start_angle=0, angle=PI, color=GOLD)
        arc.shift(LEFT * 5.5 + DOWN * 2)

        pt = Dot(point=LEFT * 2 + DOWN * 2, radius=0.08, color=RED)

        tri = Polygon(
            LEFT * 1.5 + DOWN * 1.7,
            RIGHT * 1.5 + DOWN * 1.7,
            RIGHT * 0 + DOWN * 3.2,
            color=MAROON,
        )

        label_sq = Text("Square", font_size=16)
        label_sq.shift(LEFT * 5.25 + UP * 1.2)
        label_rect = Text("Rectangle", font_size=16)
        label_rect.shift(LEFT * 1.75 + UP * 1.2)
        label_circ = Text("Circle", font_size=16)
        label_circ.shift(RIGHT * 1.75 + UP * 1.2)
        label_ell = Text("Ellipse", font_size=16)
        label_ell.shift(RIGHT * 5.25 + UP * 1.2)

        label_line = Text("Line", font_size=16)
        label_line.shift(LEFT * 6 + UP * 0.9)
        label_arrow = Text("Arrow", font_size=16)
        label_arrow.shift(RIGHT * 3.5 + DOWN * 0.2)
        label_dash = Text("DashedLine", font_size=16)
        label_dash.shift(RIGHT * 5 + DOWN * 1.3)

        label_arc = Text("Arc", font_size=16)
        label_arc.shift(LEFT * 5.5 + DOWN * 2.8)
        label_dot = Text("Dot", font_size=16)
        label_dot.shift(LEFT * 2 + DOWN * 2.8)
        label_tri = Text("Polygon", font_size=16)
        label_tri.shift(RIGHT * 0 + DOWN * 3.6)

        lang_en = Text("English: Hello World", font_size=20)
        lang_en.shift(LEFT * 4 + DOWN * 3.3)
        lang_cn = Text("Chinese: 你好世界", font_size=20)
        lang_cn.shift(RIGHT * 0 + DOWN * 3.3)
        lang_jp = Text("Japanese: こんにちは", font_size=20)
        lang_jp.shift(RIGHT * 4 + DOWN * 3.3)

        render.play(
            Create(SurroundingRectangle(section_title, buff=0.3), run_time=1.5),
            Succession(
                Wait(0.3),
                Add(section_title),
            ),
        )

        render.play(
            Create(sq, run_time=1.0),
            Create(rect, run_time=1.0),
            Create(circ, run_time=1.0),
            Create(ell, run_time=1.0),
            Succession(
                Wait(0.2),
                Add(label_sq, label_rect, label_circ, label_ell),
            ),
        )

        render.play(
            Create(ln, run_time=0.8),
            Create(arr, run_time=0.8),
            Create(dl, run_time=0.8),
            Succession(
                Wait(0.2),
                Add(label_line, label_arrow, label_dash),
            ),
        )

        render.play(
            Create(arc, run_time=0.8),
            Create(pt, run_time=0.3),
            Create(tri, run_time=1.0),
            Succession(
                Wait(0.2),
                Add(label_arc, label_dot, label_tri),
            ),
        )

        render.play(
            Succession(
                Wait(0.3),
                Add(lang_en),
                Wait(0.3),
                Add(lang_cn),
                Wait(0.3),
                Add(lang_jp),
            ),
        )

        render.play(Wait(5.0))

        while render.tick():
            render.sync(self)
        render.close()
