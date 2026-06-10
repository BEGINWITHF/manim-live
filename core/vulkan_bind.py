import ctypes
import os
from manim import Mobject, Square, Circle, Line
# 1. 导入颜色处理工具
from manim.utils.color import color_to_int_rgba

def manim_to_screen(x, y, w=800, h=600, scale=200):
    cx, cy = w / 2.0, h / 2.0
    sx = cx + x * scale
    sy = cy - y * scale
    return float(sx), float(sy)

class VulkanRender:
    def __init__(self, w=800, h=600):
        self.win_w = w
        self.win_h = h

        base_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dll"))
        if not os.path.exists(dll_path):
            dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dll"))
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"找不到 vulkan_core.dll")

        self.dll = ctypes.CDLL(dll_path)

        # ... (保持原有的 DLL 定义不变) ...
        self.dll.Vulkan_Init.restype = ctypes.c_int
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Tick.restype = ctypes.c_int
        self.dll.Vulkan_Tick.argtypes = []
        self.dll.Vulkan_Shutdown.restype = None
        self.dll.Vulkan_Shutdown.argtypes = []
        self.dll.ClearShapes.restype = None
        self.dll.ClearShapes.argtypes = []

        # 注意：这里假设你的 C++ AddRect/AddCircle 等函数的最后三个参数确实是 R, G, B
        # 如果 C++ 端还需要 Alpha，你需要确认参数数量是否匹配
        self.dll.AddRect.restype = None
        self.dll.AddRect.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]

        self.dll.AddCircle.restype = None
        self.dll.AddCircle.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]

        self.dll.AddLine.restype = None
        self.dll.AddLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int
        ]

        if self.dll.Vulkan_Init(w, h) != 1:
            raise RuntimeError("Vulkan_Init 失败")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        count = 0
        for mob in scene.mobjects:
            # print(f"[PY] Drawing: {type(mob).__name__}")
            self.draw(mob, angle)
            count += 1
        # print(f"[PY] Total shapes sent this frame: {count}")

    def draw(self, mob, angle=0.0):
        if isinstance(mob, Square):
            self._draw_square(mob, angle)
        elif isinstance(mob, Circle):
            self._draw_circle(mob)
        elif isinstance(mob, Line):
            self._draw_line(mob)

    # --- 新增辅助函数：安全获取颜色 ---
    def _get_color_rgb(self, mob):
        """尝试获取填充颜色，如果没有则回退到描边颜色，再没有则回退白色"""
        try:
            # Manim 内部通常用 fill_rgbas 存储颜色
            rgbas = mob.get_fill_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                return int(r * 255), int(g * 255), int(b * 255)
        except Exception:
            pass

        try:
            rgbas = mob.get_stroke_rgbas()
            if len(rgbas) > 0:
                r, g, b, a = rgbas[0]
                return int(r * 255), int(g * 255), int(b * 255)
        except Exception:
            pass

        return 255, 255, 255 # 默认白色

    def _draw_square(self, sq, angle):
        cx, cy, _ = sq.get_center()
        half = sq.side_length / 2.0
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sh = half * 200.0

        # 2. 动态获取颜色
        r, g, b = self._get_color_rgb(sq)

        # 传入动态颜色，而不是硬编码的 255, 130, 80
        self.dll.AddRect(sx, sy, sh, sh, angle, r, g, b)

    def _draw_circle(self, cr):
        cx, cy, _ = cr.get_center()
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sr = cr.radius * 200.0

        # 获取填充色
        r, g, b = self._get_color_rgb(cr)

        # 调用 C 函数，只传入基本参数
        self.dll.AddCircle(sx, sy, sr, r, g, b)

    def _draw_line(self, line):
        s = line.get_start()
        e = line.get_end()
        sx1, sy1 = manim_to_screen(s[0], s[1], self.win_w, self.win_h)
        sx2, sy2 = manim_to_screen(e[0], e[1], self.win_w, self.win_h)

        # 线条通常使用 stroke_color
        try:
            rgbas = line.get_stroke_rgbas()
            r, g, b = int(rgbas[0][0]*255), int(rgbas[0][1]*255), int(rgbas[0][2]*255)
        except:
            r, g, b = 255, 255, 255

        # 这里的第一个 3 可能是线宽，后面是颜色
        self.dll.AddLine(sx1, sy1, sx2, sy2, 3, r, g, b)

    def tick(self):
        return self.dll.Vulkan_Tick() != 0

    def close(self):
        self.dll.Vulkan_Shutdown()