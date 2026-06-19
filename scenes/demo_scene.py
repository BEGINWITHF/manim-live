from manim import *
from core.vulkan_bind import VulkanRender


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1280, 720)

        title = Text("Vulkan Shape Showcase", font_size=48)
        self.add(title)

        subtitle = Text("Text Rendering Works!", font_size=32)
        subtitle.shift(DOWN * 1.5)
        self.add(subtitle)

        small = Text("Small text", font_size=18)
        small.shift(DOWN * 3.0)
        self.add(small)

        while render.tick():
            render.sync(self)
        render.close()
