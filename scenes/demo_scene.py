from manim import *
import time
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

        start_time = time.monotonic()
        rotation_speed = 1.0
        while render.tick():
            angle = (time.monotonic() - start_time) * rotation_speed
            render.sync(self, angle)
            time.sleep(1.0 / 60.0)

        render.close()