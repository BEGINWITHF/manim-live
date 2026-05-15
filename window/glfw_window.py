import ctypes
import os
import time

def main():
    dll_path = os.path.join(os.path.dirname(__file__), "..", "native", "vulkan_present.dll")
    lib = ctypes.CDLL(dll_path)

    # 函数名完全匹配
    lib.RenderText.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

    lib.InitManimWindow()

    cx, cy = 400, 300
    radius = 80
    dx, dy = 2, 1

    while lib.WindowTick():
        lib.ClearWindow(255, 255, 255)

        lib.DrawLine(100, 100, 700, 500, 255, 0, 0)
        lib.DrawCircle(cx, cy, radius, 0, 200, 255)

        lib.RenderText(b"Hello Manim C+Python", 50, 50, 0, 0, 0, 24)
        lib.RenderText(b"Ready for Vulkan!", 50, 85, 120, 120, 120, 18)

        cx += dx
        cy += dy

        if cx - radius < 0 or cx + radius > 800: dx *= -1
        if cy - radius < 0 or cy + radius > 600: dy *= -1

        time.sleep(0.016)

if __name__ == "__main__":
    main()