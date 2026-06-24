from manim import *
from core.vulkan_bind import (
    VulkanRender, Animation, Create, Write, Unwrite, Succession, Wait, Add,
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth, _lingering,
    _wiggle, _exponential_decay,
    set_anim_opacity,
)


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        title = Text("New Features Demo", font_size=40)
        title.shift(UP * 3.3)
        title_box = SurroundingRectangle(title, buff=0.3)

        render.play(
            Create(title_box, run_time=1.0),
            Write(title, run_time=1.5),
        )
        render.play(Wait(0.5))

        self.section_write(render)
        self.section_mixed_language(render)
        self.section_font_sizes(render)

        render.play(Wait(2.0))
        render.close()

    def section_write(self, render):
        for m in render.scene.mobjects:
            set_anim_opacity(m, 0.0)
        render.sync(render.scene)

        sec = Text("Write & Unwrite", font_size=28)
        sec.shift(UP * 2.5)
        render.play(Add(sec))

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 3.5 + UP * 0.5)

        rect = Rectangle(width=2.5, height=1.5, color=GREEN)
        rect.set_fill(GREEN, opacity=0.7)
        rect.set_stroke(width=3)
        rect.shift(RIGHT * 3.5 + UP * 0.5)

        lbl1 = Text("Write", font_size=18)
        lbl1.shift(LEFT * 3.5 + DOWN * 1.0)
        lbl2 = Text("Unwrite", font_size=18)
        lbl2.shift(RIGHT * 3.5 + DOWN * 1.0)

        render.play(Write(sq, run_time=2.0), Add(lbl1))
        render.play(Wait(0.5))

        txt = Text("Write Me", font_size=36)
        txt.shift(UP * 0.5)
        render.play(Write(txt, run_time=2.0))
        render.play(Wait(0.5))

        render.play(Add(rect))
        render.play(Wait(0.5))
        render.play(Unwrite(rect, run_time=2.0), Add(lbl2))
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
