from manim import *
from core.vulkan_bind import VulkanRender, Create, Succession, Wait, Add


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1280, 720)
        render.scene = self

        section_title = Text("Vulkan Full Function Test", font_size=40)
        section_title.shift(UP * 3.3)

        sq = Square(side_length=1.0, color=RED)
        sq.shift(LEFT * 5 + UP * 1.5)

        rect = Rectangle(width=2.0, height=1.2, color=ORANGE)
        rect.shift(LEFT * 2 + UP * 1.5)

        circ = Circle(radius=0.6, color=BLUE)
        circ.shift(RIGHT * 1.5 + UP * 1.5)

        ell = Ellipse(width=1.8, height=0.8, color=TEAL)
        ell.shift(RIGHT * 4.5 + UP * 1.5)

        ln = Line(start=LEFT * 5 + UP * 0, end=RIGHT * 5 + UP * 0, color=GREEN)
        ln.set_stroke(width=3)

        arr = Arrow(start=LEFT * 3 + DOWN * 1, end=RIGHT * 3 + DOWN * 1, color=YELLOW)
        arr.set_stroke(width=3)

        dl = DashedLine(
            start=LEFT * 4 + DOWN * 1.8,
            end=RIGHT * 4 + DOWN * 1.8,
            color=PINK,
        )

        arc = Arc(radius=0.8, start_angle=0, angle=PI, color=GOLD)
        arc.shift(LEFT * 5 + DOWN * 3)

        pt = Dot(point=RIGHT * 5 + DOWN * 3, radius=0.08, color=RED)

        tri = Polygon(
            LEFT * 2 + DOWN * 2.8,
            RIGHT * 1 + DOWN * 2.8,
            LEFT * 0.5 + DOWN * 4,
            color=MAROON,
        )

        label_sq = Text("Square", font_size=16)
        label_sq.shift(LEFT * 5 + UP * 0.3)
        label_rect = Text("Rectangle", font_size=16)
        label_rect.shift(LEFT * 2 + UP * 0.3)
        label_circ = Text("Circle", font_size=16)
        label_circ.shift(RIGHT * 1.5 + UP * 0.3)
        label_ell = Text("Ellipse", font_size=16)
        label_ell.shift(RIGHT * 4.5 + UP * 0.3)
        label_line = Text("Line", font_size=16)
        label_line.shift(RIGHT * 3 + UP * 0.3)
        label_arrow = Text("Arrow", font_size=16)
        label_arrow.shift(RIGHT * 4 + DOWN * 0.7)
        label_dash = Text("DashedLine", font_size=16)
        label_dash.shift(RIGHT * 3 + DOWN * 1.5)
        label_arc = Text("Arc", font_size=16)
        label_arc.shift(LEFT * 5 + DOWN * 4)
        label_dot = Text("Dot", font_size=16)
        label_dot.shift(RIGHT * 4 + DOWN * 3)
        label_tri = Text("Polygon", font_size=16)
        label_tri.shift(RIGHT * 1.5 + DOWN * 3.5)

        lang_en = Text("English: Hello World", font_size=22)
        lang_en.shift(LEFT * 4 + DOWN * 4.5)
        lang_cn = Text("Chinese: 你好世界", font_size=22)
        lang_cn.shift(LEFT * 0.5 + DOWN * 4.5)
        lang_jp = Text("Japanese: こんにちは", font_size=22)
        lang_jp.shift(RIGHT * 3.5 + DOWN * 4.5)

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
            Create(tri, run_time=1.0),
            Succession(
                Wait(0.2),
                Add(pt, label_arc, label_dot, label_tri),
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
