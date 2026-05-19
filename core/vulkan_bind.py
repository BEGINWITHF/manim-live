import ctypes
import os

dll_path = os.path.abspath("build/bin/native.dll")
lib = ctypes.WinDLL(dll_path)  # 必须用 WinDLL！！！

lib.SceneInit.argtypes = (ctypes.c_int, ctypes.c_int)
lib.SceneInit.restype = ctypes.c_int

lib.SceneSetBgColor.argtypes = (ctypes.c_float, ctypes.c_float, ctypes.c_float)

def init_scene(w, h):
    return lib.SceneInit(w, h)

def set_background(r, g, b):
    lib.SceneSetBgColor(r, g, b)

def render_frame():
    lib.SceneRender()

def close_scene():
    lib.SceneExit()