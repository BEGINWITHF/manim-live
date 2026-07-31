from manim import *
from core.vulkan_bind import VulkanRender, Wait, GrowArrow, GrowFromCenter


class TestGrowSimple(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self
        render.play(Wait(1.0))
        
        sq = Square()
        self.add(sq)
        
        render.play(GrowFromCenter(sq))
        render.play(Wait(2.0))
        render.close()
