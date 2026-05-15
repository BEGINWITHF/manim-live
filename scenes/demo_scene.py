from manim import *
from core.vulkan_bind import VulkanRender

class VulkanLiveScene(Scene):
    def construct(self):
        render = VulkanRender(800, 600)
        
        square = Square(side_length=3, color=ORANGE, fill_opacity=0.7)
        self.add(square)

        angle = 0.0

        while render.tick():
            angle += 0.06
            square.set_angle(angle)
            
            render.draw_rect(0, 0, 1.5, 1.5, angle, 255, 165, 0)

        render.close()