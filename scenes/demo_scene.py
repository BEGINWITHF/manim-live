from manim import *
from core.vulkan_bind import VulkanRender

class VulkanLiveScene(Scene):
    def construct(self):
        render = VulkanRender(800, 600)
        
        circle = Circle()
        circle.set_fill(YELLOW, opacity=0.5)
        self.add(circle)
        
        angle = 0.0
        while render.tick():
            angle += 0.05
            render.sync(self, angle)
            
        render.close()