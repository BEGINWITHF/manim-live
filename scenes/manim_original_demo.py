from manim import *


class ManimOriginalDemo(Scene):
    def construct(self):
        title = Text("Animation API Demo", font_size=40)
        title.shift(UP * 3.3)
        title_box = SurroundingRectangle(title, buff=0.3)

        self.play(
            Create(title_box, run_time=1.0),
        )
        self.add(title)

        self.wait(0.5)

        sec1 = Text("Rate Functions: smooth vs linear vs rush", font_size=24)
        sec1.shift(UP * 2.0)
        self.add(sec1)

        box_smooth = Rectangle(width=2, height=1, color=BLUE)
        box_smooth.set_fill(opacity=0)
        box_smooth.set_stroke(width=3)
        box_smooth.shift(LEFT * 5 + UP * 0.5)

        box_linear = Rectangle(width=2, height=1, color=GREEN)
        box_linear.set_fill(opacity=0)
        box_linear.set_stroke(width=3)
        box_linear.shift(UP * 0.5)

        box_rush = Rectangle(width=2, height=1, color=RED)
        box_rush.set_fill(opacity=0)
        box_rush.set_stroke(width=3)
        box_rush.shift(RIGHT * 5 + UP * 0.5)

        lbl_smooth = Text("smooth", font_size=18)
        lbl_smooth.shift(LEFT * 5 + DOWN * 0.5)
        lbl_linear = Text("linear", font_size=18)
        lbl_linear.shift(DOWN * 0.5)
        lbl_rush = Text("rush_into", font_size=18)
        lbl_rush.shift(RIGHT * 5 + DOWN * 0.5)

        self.play(
            Create(box_smooth, run_time=2.0, rate_func=smooth),
            Create(box_linear, run_time=2.0, rate_func=linear),
            Create(box_rush, run_time=2.0, rate_func=rush_into),
        )
        self.add(lbl_smooth, lbl_linear, lbl_rush)

        self.wait(1.0)

        sec2 = Text("there_and_back + double_smooth", font_size=24)
        sec2.shift(UP * 2.0)
        self.add(sec2)

        box_tab = Rectangle(width=2, height=1, color=YELLOW)
        box_tab.set_fill(opacity=0)
        box_tab.set_stroke(width=3)
        box_tab.shift(LEFT * 3 + DOWN * 1.5)

        box_ds = Rectangle(width=2, height=1, color=ORANGE)
        box_ds.set_fill(opacity=0)
        box_ds.set_stroke(width=3)
        box_ds.shift(RIGHT * 3 + DOWN * 1.5)

        lbl_tab = Text("there_and_back", font_size=18)
        lbl_tab.shift(LEFT * 3 + DOWN * 2.5)
        lbl_ds = Text("double_smooth", font_size=18)
        lbl_ds.shift(RIGHT * 3 + DOWN * 2.5)

        self.play(
            Create(box_tab, run_time=2.5, rate_func=there_and_back),
            Create(box_ds, run_time=2.5, rate_func=double_smooth),
        )
        self.add(lbl_tab, lbl_ds)

        self.wait(1.0)

        sec3 = Text("Create + Succession stagger", font_size=24)
        sec3.shift(UP * 2.0)
        self.add(sec3)

        stagger_dots = []
        for i in range(8):
            d = Dot(color=BLUE + i * 0.3, radius=0.15)
            x = LEFT * 5.25 + RIGHT * i * 1.5
            d.shift(x + DOWN * 1.0)
            stagger_dots.append(d)

        self.add(*stagger_dots)

        self.play(
            *[
                Create(d, run_time=0.8, rate_func=smooth)
                for d in stagger_dots
            ],
        )

        self.wait(0.5)

        self.play(
            *[
                Create(d, run_time=0.8, rate_func=rush_into)
                for d in stagger_dots
            ],
        )

        self.wait(1.0)

        sec4 = Text("Add with run_time", font_size=24)
        sec4.shift(UP * 2.0)
        self.add(sec4)

        add_rects = []
        for i in range(5):
            r = Rectangle(width=1.5, height=0.8, color=TEAL)
            r.set_fill(opacity=0)
            r.set_stroke(width=3)
            x = LEFT * 5 + RIGHT * i * 2.5
            r.shift(x + DOWN * 1.5)
            add_rects.append(r)

        for i, r in enumerate(add_rects):
            self.play(Succession(Wait(0.3), Create(r, run_time=0.3)))

        self.wait(2.0)

        sec5 = Text("Lingering + slow_into", font_size=24)
        sec5.shift(UP * 2.0)
        self.add(sec5)

        box_linger = Rectangle(width=2, height=1, color=PURPLE)
        box_linger.set_fill(opacity=0)
        box_linger.set_stroke(width=3)
        box_linger.shift(LEFT * 3 + DOWN * 1.5)

        box_slow = Rectangle(width=2, height=1, color=MAROON)
        box_slow.set_fill(opacity=0)
        box_slow.set_stroke(width=3)
        box_slow.shift(RIGHT * 3 + DOWN * 1.5)

        lbl_linger = Text("lingering", font_size=18)
        lbl_linger.shift(LEFT * 3 + DOWN * 2.5)
        lbl_slow = Text("slow_into", font_size=18)
        lbl_slow.shift(RIGHT * 3 + DOWN * 2.5)

        self.play(
            Create(box_linger, run_time=2.5, rate_func=lingering),
            Create(box_slow, run_time=2.5, rate_func=slow_into),
        )
        self.add(lbl_linger, lbl_slow)

        self.wait(3.0)
