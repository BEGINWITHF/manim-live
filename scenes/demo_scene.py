from manim import *
from core.vulkan_bind import (
    VulkanRender, Animation, Create, Succession, Wait, Add,
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth, _lingering,
    _wiggle, _exponential_decay,
    set_anim_opacity,
)


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("Vulkan Animation Demo", font_size=40)
        title.shift(UP * 3.3)
        title_box = SurroundingRectangle(title, buff=0.3)

        render.play(
            Create(title_box, run_time=1.0),
            Succession(Wait(0.2), Add(title)),
        )
        render.play(Wait(0.5))

        self.section_rate_functions(render)
        self.section_shape_types(render)
        self.section_create_progress(render)
        self.section_succession(render)
        self.section_add_stagger(render)
        self.section_advanced(render)
        self.section_mixed_language(render)
        self.section_font_sizes(render)

        render.play(Wait(2.0))
        render.close()

    def section_rate_functions(self, render):
        sec = Text("Rate Functions", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        funcs = [
            ("smooth", _smooth),
            ("linear", _linear),
            ("rush_into", _rush_into),
            ("rush_from", _rush_from),
            ("there_and_back", _there_and_back),
            ("double_smooth", _double_smooth),
            ("slow_into", _slow_into),
            ("lingering", _lingering),
        ]

        items = []
        for i, (name, func) in enumerate(funcs):
            row = i // 4
            col = i % 4
            x = LEFT * 5.25 + RIGHT * col * 3.5
            y = UP * 1.0 - DOWN * row * 2.0

            box = Rectangle(width=2.5, height=1.0, color=BLUE + i * 0.2)
            box.set_fill(opacity=0)
            box.set_stroke(width=3)
            box.shift(x + y)

            lbl = Text(name, font_size=14)
            lbl.shift(x + y + DOWN * 0.8)

            items.append((box, func, lbl))

        render.play(
            *[Create(b, run_time=2.0, rate_func=f) for b, f, l in items],
            Add(*[l for _, _, l in items]),
        )
        render.play(Wait(1.0))
        render.play(
            *[Succession(Wait(0.1), Add(l)) for _, _, l in items],
        )
        render.play(Wait(1.5))

    def section_shape_types(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Shape Types", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        shapes = []

        sq = Square(side_length=0.8, color=RED)
        sq.set_fill(opacity=0)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 5.5 + UP * 0.5)
        shapes.append(sq)

        rect = Rectangle(width=1.5, height=0.8, color=ORANGE)
        rect.set_fill(opacity=0)
        rect.set_stroke(width=3)
        rect.shift(LEFT * 2.5 + UP * 0.5)
        shapes.append(rect)

        circ = Circle(radius=0.4, color=BLUE)
        circ.set_fill(opacity=0)
        circ.set_stroke(width=3)
        circ.shift(RIGHT * 0.5 + UP * 0.5)
        shapes.append(circ)

        ell = Ellipse(width=1.2, height=0.6, color=TEAL)
        ell.set_fill(opacity=0)
        ell.set_stroke(width=3)
        ell.shift(RIGHT * 3.5 + UP * 0.5)
        shapes.append(ell)

        ln = Line(start=LEFT * 1.5 + DOWN * 0.8, end=RIGHT * 1.5 + DOWN * 0.8, color=GREEN)
        ln.set_stroke(width=3)
        shapes.append(ln)

        arr = Arrow(start=LEFT * 1.5 + DOWN * 1.8, end=RIGHT * 1.5 + DOWN * 1.8, color=YELLOW)
        arr.set_stroke(width=3)
        shapes.append(arr)

        dl = DashedLine(start=LEFT * 1.5 + DOWN * 2.8, end=RIGHT * 1.5 + DOWN * 2.8, color=PINK)
        dl.set_stroke(width=3)
        shapes.append(dl)

        arc = Arc(radius=0.4, start_angle=0, angle=PI, color=GOLD)
        arc.shift(LEFT * 5.5 + DOWN * 1.0)
        shapes.append(arc)

        pt = Dot(point=RIGHT * 3.5 + DOWN * 1.0, radius=0.1, color=RED)
        shapes.append(pt)

        tri = Polygon(
            LEFT * 1 + DOWN * 2.5,
            RIGHT * 1 + DOWN * 2.5,
            RIGHT * 0 + DOWN * 1.3,
            color=MAROON,
        )
        tri.set_fill(opacity=0)
        tri.set_stroke(width=3)
        shapes.append(tri)

        render.play(
            *[Create(s, run_time=1.0) for s in shapes],
        )
        render.play(Wait(1.5))

    def section_create_progress(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Create: Progressive Drawing", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        r1 = Rectangle(width=3, height=1.5, color=BLUE)
        r1.set_fill(opacity=0)
        r1.set_stroke(width=4)
        r1.shift(LEFT * 3.5 + UP * 0.5)

        r2 = Rectangle(width=3, height=1.5, color=GREEN)
        r2.set_fill(opacity=0)
        r2.set_stroke(width=4)
        r2.shift(RIGHT * 3.5 + UP * 0.5)

        lbl1 = Text("slow (3s)", font_size=16)
        lbl1.shift(LEFT * 3.5 + DOWN * 0.5)
        lbl2 = Text("fast (0.5s)", font_size=16)
        lbl2.shift(RIGHT * 3.5 + DOWN * 0.5)

        render.play(
            Create(r1, run_time=3.0),
            Create(r2, run_time=0.5),
            Add(lbl1, lbl2),
        )
        render.play(Wait(1.5))

    def section_succession(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Succession: Sequential Animations", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        colors = [RED, ORANGE, YELLOW, GREEN, BLUE]
        rects = []
        for i in range(5):
            r = Rectangle(width=1.5, height=0.8, color=colors[i])
            r.set_fill(opacity=0)
            r.set_stroke(width=3)
            x = LEFT * 5 + RIGHT * i * 2.5
            r.shift(x + UP * 0.5)
            rects.append(r)

        render.play(
            Succession(
                Wait(0.2),
                Create(rects[0], run_time=0.5),
                Wait(0.2),
                Create(rects[1], run_time=0.5),
                Wait(0.2),
                Create(rects[2], run_time=0.5),
                Wait(0.2),
                Create(rects[3], run_time=0.5),
                Wait(0.2),
                Create(rects[4], run_time=0.5),
            ),
        )
        render.play(Wait(1.5))

    def section_add_stagger(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Add: Instant Appearance + Stagger", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        dots = []
        for i in range(10):
            d = Dot(color=BLUE + i * 0.3, radius=0.12)
            x = LEFT * 5.5 + RIGHT * i * 1.2
            d.shift(x + UP * 0.5)
            dots.append(d)

        render.play(Add(*dots))

        render.play(
            *[
                Create(d, run_time=0.5, rate_func=_rush_into)
                for d in dots
            ],
        )
        render.play(Wait(1.5))

    def section_advanced(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Advanced: Reverse + Exponential Decay", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        r1 = Rectangle(width=3, height=1.5, color=RED)
        r1.set_fill(opacity=0)
        r1.set_stroke(width=4)
        r1.shift(LEFT * 3.5 + UP * 0.5)

        r2 = Rectangle(width=3, height=1.5, color=BLUE)
        r2.set_fill(opacity=0)
        r2.set_stroke(width=4)
        r2.shift(RIGHT * 3.5 + UP * 0.5)

        lbl1 = Text("reverse_rate_function", font_size=14)
        lbl1.shift(LEFT * 3.5 + DOWN * 0.5)
        lbl2 = Text("exponential_decay", font_size=14)
        lbl2.shift(RIGHT * 3.5 + DOWN * 0.5)

        render.play(
            Create(r1, run_time=2.0, rate_func=_smooth, reverse_rate_function=True),
            Create(r2, run_time=2.0, rate_func=_exponential_decay),
            Add(lbl1, lbl2),
        )
        render.play(Wait(1.5))

    def section_mixed_language(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Mixed Language Support", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        test_strings = [
            ("Hello World", UP * 1.5 + LEFT * 3),
            ("你好世界", UP * 1.5 + RIGHT * 3),
            ("こんにちは", DOWN * 0.0 + LEFT * 3),
            ("Mixed: Hello 你好", DOWN * 0.0 + RIGHT * 3),
            ("Korean + English", DOWN * 1.5 + LEFT * 3),
            ("한글 English", DOWN * 1.5 + RIGHT * 3),
        ]

        labels = []
        for text, pos in test_strings:
            lbl = Text(text, font_size=24)
            lbl.shift(pos)
            labels.append(lbl)

        render.play(Add(*labels))
        render.play(Wait(2.0))

    def section_font_sizes(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Different Font Sizes", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        sizes = [12, 18, 24, 32, 40, 48, 64]
        labels = []
        for i, size in enumerate(sizes):
            lbl = Text(f"Size {size}", font_size=size)
            y = 2.0 - i * 0.7
            lbl.shift(UP * y + LEFT * 3)
            labels.append(lbl)

        render.play(Add(*labels))
        render.play(Wait(2.0))
