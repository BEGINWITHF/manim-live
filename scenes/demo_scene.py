from manim import *
from core.vulkan_bind import VulkanRender

class VulkanLiveScene(Scene):
    def construct(self):
        square = Square(side_length=1.5).shift(LEFT * 3)
        square.set_color(BLUE)
        self.add(square)

        circle = Circle(radius=1).shift(RIGHT * 3)
        circle.set_color(RED)
        self.add(circle)

        line = Line(UP * 2, DOWN * 2, color=GREEN, stroke_width=3)
        self.add(line)

        arrow = Arrow(LEFT * 2, RIGHT * 2, color=YELLOW, stroke_width=4)
        self.add(arrow)

        text = Text("ALL FUNCTIONS OK!", font_size=24).shift(DOWN * 2)
        text.set_color(WHITE)
        self.add(text)

        render = VulkanRender()
        angle = 0
        while render.tick():
            render.sync(self, angle)
            angle += 0.02
        render.shutdown()