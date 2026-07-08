from manim import *


class WriteUnwriteOriginal(Scene):
    def construct(self):
        t1 = Text("Hello World", font_size=60).shift(UP * 1)
        t2 = Text("Vulkan Render", font_size=48).shift(DOWN * 1)

        self.play(Write(t1, run_time=2.0))
        self.wait(0.5)
        self.play(Write(t2, run_time=1.5))
        self.wait(0.5)
        self.play(Unwrite(t1, run_time=1.5))
        self.wait(0.5)
