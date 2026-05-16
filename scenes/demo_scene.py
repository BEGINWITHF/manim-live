from manim import *
from core.vulkan_bind import VulkanRender

class VulkanLiveScene(Scene):
    def construct(self):
        render = VulkanRender(800, 600)

        sq = Square().shift(LEFT*2)
        cr = Circle().shift(RIGHT*2)
        line = Line(LEFT*3, RIGHT*3)
        arrow = Arrow(LEFT+DOWN, RIGHT+DOWN)
        text = Text("ManimVulkanRender").shift(UP*2)

        self.add(sq, cr, line, arrow, text)

        angle = 0.0
        while render.tick():
            angle += 0.05
            render.sync(self, angle)

        render.close()