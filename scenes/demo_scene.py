from manim import *
from core.vulkan_bind import VulkanRender


class VulkanShapeShowcase(Scene):
    def construct(self):
        render = VulkanRender(1280, 720)
        render.scene = self

        title = Text("Vulkan Multi-Language Test", font_size=48)
        render.play(Add(title, run_time=0))

        en = Text("English: Hello World!", font_size=32)
        en.shift(UP * 1.5)
        render.play(Add(en, run_time=0))

        cn = Text("Chinese: 你好世界", font_size=32)
        cn.shift(UP * 0.5)
        render.play(Add(cn, run_time=0))

        jp = Text("Japanese: こんにちは世界", font_size=32)
        jp.shift(DOWN * 0.5)
        render.play(Add(jp, run_time=0))

        kr = Text("Korean: 안녕하세요 세계", font_size=32)
        kr.shift(DOWN * 1.5)
        render.play(Add(kr, run_time=0))

        ru = Text("Russian: Привет мир", font_size=32)
        ru.shift(DOWN * 2.5)
        render.play(Add(ru, run_time=0))

        while render.tick():
            render.sync(self)
        render.close()
