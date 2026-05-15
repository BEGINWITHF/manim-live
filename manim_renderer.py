from manim import *
import ctypes
import os

dll_path = os.path.abspath("native/vulkan_present.dll")
lib = ctypes.CDLL(dll_path)

# 配置函数参数
lib.ManimDraw_Text.argtypes = [
    ctypes.c_char_p,
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int
]

class ManimVulkanScene(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        lib.ManimWindow_Init()

    def render_frame(self):
        lib.ManimWindow_Clear(10, 15, 30)

        # 文字
        lib.ManimDraw_Text(b"Manim + C + Vulkan", 50, 40, 255,255,255, 26)

        # 画图形
        cx, cy = 400, 300
        lib.ManimDraw_Circle(cx, cy, 70, 0, 220, 255)
        lib.ManimDraw_Line(cx-150, cy, cx+150, cy, 255,60,60, 4)
        lib.ManimDraw_Line(cx, cy-150, cx, cy+150, 60,255,120, 4)

    def construct(self):
        print("✅ Manim C+Vulkan")

        while lib.ManimWindow_Tick():
            self.render_frame()
            self.wait(0.016)

if __name__ == "__main__":
    scene = ManimVulkanScene()
    scene.render()