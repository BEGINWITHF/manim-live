from manim import *
import math


class ManimCompare(Scene):
    def construct(self):
        title = Text("Manim Features Demo你好", font_size=42)
        title.shift(UP * 3.3)
        title_box = SurroundingRectangle(title, buff=0.3)

        self.play(Create(title_box, run_time=1.0))
        self.play(Write(title, run_time=1.5))
        self.wait(0.5)

        self.section_rotation()
        self.section_fade()
        self.section_transform()
        self.section_transform_matching()
        self.section_write_stagger()
        self.section_rate_functions()

        self.wait(2.0)

    def section_rotation(self):
        for m in self.mobjects:
            m.set_opacity(0)
        self.wait(0.1)

        sec = Text("Rotation", font_size=28)
        sec.shift(UP * 2.5)
        self.play(FadeIn(sec, run_time=0.5))

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=3)
        sq.shift(LEFT * 4.5)

        circ = Circle(radius=0.6, color=GREEN)
        circ.set_fill(GREEN, opacity=0.6)
        circ.set_stroke(width=3)
        circ.shift(LEFT * 1.5)

        tri = Triangle(color=RED, fill_opacity=0.6, stroke_width=3)
        tri.scale(0.8)
        tri.shift(RIGHT * 1.5)

        arrow = Arrow(ORIGIN, RIGHT * 2, color=YELLOW, stroke_width=4)
        arrow.shift(RIGHT * 4.5)

        lbl_sq = Text("Rotate", font_size=16)
        lbl_sq.shift(LEFT * 4.5 + DOWN * 1.5)
        lbl_circ = Text("Rotating", font_size=16)
        lbl_circ.shift(LEFT * 1.5 + DOWN * 1.5)
        lbl_tri = Text("90°", font_size=16)
        lbl_tri.shift(RIGHT * 1.5 + DOWN * 1.5)

        self.play(
            FadeIn(sq), FadeIn(circ), FadeIn(tri), FadeIn(arrow),
            FadeIn(lbl_sq), FadeIn(lbl_circ), FadeIn(lbl_tri),
        )
        self.wait(0.3)

        self.play(Rotate(sq, angle=math.pi / 2, run_time=1.5))
        self.wait(0.3)

        self.play(Rotating(tri, angle=2 * math.pi, run_time=2.0))
        self.wait(0.3)

        self.play(Rotating(arrow, angle=2 * math.pi, run_time=2.0))
        self.wait(1.0)

    def section_fade(self):
        for m in self.mobjects:
            m.set_opacity(0)
        self.wait(0.1)

        sec = Text("FadeIn & FadeOut", font_size=28)
        sec.shift(UP * 2.5)
        self.play(FadeIn(sec, run_time=0.5))

        sq1 = Square(side_length=1.0, color=BLUE)
        sq1.set_fill(BLUE, opacity=0.7)
        sq1.set_stroke(width=3)
        sq1.shift(LEFT * 4)

        sq2 = Square(side_length=1.0, color=GREEN)
        sq2.set_fill(GREEN, opacity=0.7)
        sq2.set_stroke(width=3)
        sq2.shift(LEFT * 1.5)

        sq3 = Square(side_length=1.0, color=RED)
        sq3.set_fill(RED, opacity=0.7)
        sq3.set_stroke(width=3)
        sq3.shift(RIGHT * 1.5)

        sq4 = Square(side_length=1.0, color=YELLOW)
        sq4.set_fill(YELLOW, opacity=0.7)
        sq4.set_stroke(width=3)
        sq4.shift(RIGHT * 4)

        lbl1 = Text("FadeIn", font_size=16)
        lbl1.shift(LEFT * 4 + DOWN * 1.5)
        lbl2 = Text("FadeOut", font_size=16)
        lbl2.shift(LEFT * 1.5 + DOWN * 1.5)
        lbl3 = Text("FadeTransform", font_size=16)
        lbl3.shift(RIGHT * 1.5 + DOWN * 1.5)
        lbl4 = Text("Shift", font_size=16)
        lbl4.shift(RIGHT * 4 + DOWN * 1.5)

        self.play(FadeIn(lbl1), FadeIn(lbl2), FadeIn(lbl3), FadeIn(lbl4))

        self.play(FadeIn(sq1, run_time=1.0))
        self.wait(0.3)

        self.play(FadeIn(sq2, run_time=0.01))
        self.play(FadeOut(sq2, run_time=1.0))
        self.wait(0.3)

        self.play(FadeIn(sq3, run_time=0.01))
        self.play(FadeTransform(sq3, sq4, run_time=1.5))
        self.wait(1.0)

    def section_transform(self):
        for m in self.mobjects:
            m.set_opacity(0)
        self.wait(0.1)

        sec = Text("Transform & ReplacementTransform", font_size=28)
        sec.shift(UP * 2.5)
        self.play(FadeIn(sec, run_time=0.5))

        s1 = Square(side_length=1.0, color=BLUE)
        s1.set_fill(BLUE, opacity=0.7)
        s1.set_stroke(width=3)
        s1.shift(LEFT * 5 + DOWN * 0.5)

        lbl1 = Text("Transform", font_size=16)
        lbl1.shift(LEFT * 5 + DOWN * 1.8)

        self.play(FadeIn(s1), FadeIn(lbl1))
        self.wait(0.3)

        t1 = Triangle(color=RED, fill_opacity=0.7, stroke_width=3)
        t1.scale(0.7)
        t1.shift(LEFT * 2 + DOWN * 0.5)

        self.play(Transform(s1, t1, run_time=1.5))
        self.wait(0.8)

        s2 = Square(side_length=1.0, color=GREEN)
        s2.set_fill(GREEN, opacity=0.7)
        s2.set_stroke(width=3)
        s2.shift(RIGHT * 2 + DOWN * 0.5)

        lbl2 = Text("ReplacementTransform", font_size=16)
        lbl2.shift(RIGHT * 2 + DOWN * 1.8)

        self.play(FadeIn(s2), FadeIn(lbl2))
        self.wait(0.3)

        t2 = Triangle(color=YELLOW, fill_opacity=0.7, stroke_width=3)
        t2.scale(0.7)
        t2.shift(RIGHT * 5 + DOWN * 0.5)

        self.play(ReplacementTransform(s2, t2, run_time=1.5))
        self.wait(1.5)

    def section_transform_matching(self):
        for m in self.mobjects:
            m.set_opacity(0)
        self.wait(0.1)

        sec = Text("Transform Matching Shapes", font_size=28)
        sec.shift(UP * 2.5)
        self.play(FadeIn(sec, run_time=0.5))

        src = Text("abc", font_size=48)
        src.shift(LEFT * 3 + UP * 0.5)

        tar = Text("xyz", font_size=48)
        tar.shift(RIGHT * 3 + UP * 0.5)

        arrow_lbl = Text("→", font_size=36)
        arrow_lbl.shift(UP * 0.5)

        self.play(Write(src, run_time=1.5))
        self.play(FadeIn(tar), FadeIn(arrow_lbl))
        self.wait(0.5)

        self.play(
            TransformMatchingShapes(src, tar, run_time=2.0),
        )
        self.wait(1.5)

    def section_write_stagger(self):
        for m in self.mobjects:
            m.set_opacity(0)
        self.wait(0.1)

        sec = Text("Write Stagger Effect", font_size=28)
        sec.shift(UP * 2.5)
        self.play(FadeIn(sec, run_time=0.5))

        line1 = Text("Staggered writing", font_size=32)
        line1.shift(UP * 1.0)

        line2 = Text("with lag ratio", font_size=32)
        line2.shift(DOWN * 0.0)

        line3 = Text("animation timing", font_size=32)
        line3.shift(DOWN * 1.0)

        self.play(Write(line1, run_time=2.0, lag_ratio=0.15))
        self.wait(0.3)
        self.play(Write(line2, run_time=2.0, lag_ratio=0.15))
        self.wait(0.3)
        self.play(Write(line3, run_time=2.0, lag_ratio=0.15))
        self.wait(1.0)

    def section_rate_functions(self):
        for m in self.mobjects:
            m.set_opacity(0)
        self.wait(0.1)

        sec = Text("Rate Functions", font_size=28)
        sec.shift(UP * 2.5)
        self.play(FadeIn(sec, run_time=0.5))

        funcs = [
            ("smooth", smooth),
            ("linear", linear),
            ("rush_into", rush_into),
            ("rush_from", rush_from),
            ("there_and_back", there_and_back),
            ("double_smooth", double_smooth),
        ]

        circles = []
        labels = []
        for i, (name, func) in enumerate(funcs):
            col = i % 3
            row = i // 3
            x = (col - 1) * 3.5
            y = 0.8 - row * 2.0

            c = Circle(radius=0.4, color=BLUE)
            c.set_fill(BLUE, opacity=0.7)
            c.set_stroke(width=2)
            c.shift(LEFT * x + UP * y)

            lbl = Text(name, font_size=14)
            lbl.shift(LEFT * x + UP * (y - 0.7))

            circles.append((c, func))
            labels.append(lbl)

        for lbl in labels:
            self.play(FadeIn(lbl, run_time=0.1))

        for c, func in circles:
            self.play(Create(c, rate_func=func, run_time=1.5))

        self.wait(1.0)
