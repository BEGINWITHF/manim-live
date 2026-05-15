import ctypes
import os
from manim import *

DLL_PATH = os.path.abspath("native/vulkan_present.dll")
lib = ctypes.CDLL(DLL_PATH)

lib.InitManimWindow.restype = ctypes.c_int
lib.WindowTick.restype = ctypes.c_int

lib.ClearWindow.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
lib.DrawLine.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
lib.DrawCircle.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
lib.DrawRect.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
lib.RenderText.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

def manim_to_screen(pos):
    x = int((pos[0] + 4.0) * 100)
    y = int((-pos[1] + 3.0) * 100)
    return x, y

def init_window():
    lib.InitManimWindow()

def tick():
    return lib.WindowTick()

def clear(r=10, g=15, b=30):
    lib.ClearWindow(r, g, b)

def draw_circle(mob):
    cx, cy = manim_to_screen(mob.get_center())
    rad = int(mob.radius * 100)
    lib.DrawCircle(cx, cy, rad, 0, 220, 255)

def draw_line(mob):
    x1, y1 = manim_to_screen(mob.start)
    x2, y2 = manim_to_screen(mob.end)
    lib.DrawLine(x1, y1, x2, y2, 255, 60, 60, 3)

def draw_rect(mob):
    p1 = manim_to_screen(mob.get_corner(DL))
    p2 = manim_to_screen(mob.get_corner(UR))
    lib.DrawRect(p1[0], p1[1], p2[0], p2[1], 100, 180, 255, 2)

def draw_text(text, x, y, size=24):
    lib.RenderText(text.encode("ascii"), x, y, 255, 255, 255, size)