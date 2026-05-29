import ctypes
import os
import platform
from manim import Mobject, Square, Circle, Line


def manim_to_screen(x, y, w=800, h=600, scale=200):
    cx, cy = w / 2.0, h / 2.0
    sx = cx + x * scale
    sy = cy - y * scale
    return float(sx), float(sy)


class VulkanRender:
    def __init__(self, w=800, h=600):
        self.win_w = w
        self.win_h = h

        # Detect platform and set library name
        system = platform.system()
        if system == "Windows":
            lib_name = "vulkan_core.dll"
            lib_prefix = ""
        elif system == "Darwin":  # macOS
            lib_name = "libvulkan_core.dylib"
            lib_prefix = "lib"
        else:  # Linux and others
            lib_name = "libvulkan_core.so"
            lib_prefix = "lib"
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try release first, then debug
        for config in ["release", "debug"]:
            lib_path = os.path.normpath(os.path.join(base_dir, "..", "dist", config, lib_name))
            if os.path.exists(lib_path):
                self.dll = ctypes.CDLL(lib_path)
                break
        else:
            # If no library found, raise error with platform-specific message
            error_msg = f"找不到 {lib_name}，已尝试路径:\n"
            for config in ["release", "debug"]:
                error_msg += f"  {os.path.join(base_dir, '..', 'dist', config, lib_name)}\n"
            error_msg += f"\n当前系统: {system}\n"
            error_msg += "请确保已编译对应平台的 Vulkan 库文件"
            raise FileNotFoundError(error_msg)

        self.dll.Vulkan_Init.restype = ctypes.c_int
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]

        self.dll.Vulkan_Tick.restype = ctypes.c_int
        self.dll.Vulkan_Tick.argtypes = []

        self.dll.Vulkan_Shutdown.restype = None
        self.dll.Vulkan_Shutdown.argtypes = []

        self.dll.ClearShapes.restype = None
        self.dll.ClearShapes.argtypes = []

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
            print(f"[PY] Drawing: {type(mob).__name__}")
            self.draw(mob, angle)
            count += 1
        print(f"[PY] Total shapes sent this frame: {count}")

    def draw(self, mob, angle=0.0):
        if isinstance(mob, Square):
            self._draw_square(mob, angle)
        elif isinstance(mob, Circle):
            self._draw_circle(mob)
        elif isinstance(mob, Line):
            self._draw_line(mob)

    def _draw_square(self, sq, angle):
        cx, cy, _ = sq.get_center()
        half = sq.side_length / 2.0
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sh = half * 200.0
        self.dll.AddRect(sx, sy, sh, sh, angle, 255, 130, 80)

    def _draw_circle(self, cr):
        cx, cy, _ = cr.get_center()
        sx, sy = manim_to_screen(cx, cy, self.win_w, self.win_h)
        sr = cr.radius * 200.0
        self.dll.AddCircle(sx, sy, sr, 80, 180, 255)

    def _draw_line(self, line):
        s = line.get_start()
        e = line.get_end()
        sx1, sy1 = manim_to_screen(s[0], s[1], self.win_w, self.win_h)
        sx2, sy2 = manim_to_screen(e[0], e[1], self.win_w, self.win_h)
        self.dll.AddLine(sx1, sy1, sx2, sy2, 3, 220, 220, 220)

    def tick(self):
        return self.dll.Vulkan_Tick() != 0

    def close(self):
        self.dll.Vulkan_Shutdown()