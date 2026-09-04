"""Smoke test: open the Vulkan window on macOS, render a probe frame,
read it back, and verify pixels. Used during porting; not part of the API."""
import ctypes
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from real_time_manim.vulkan_bind import MLWindow

def main():
    render = MLWindow(1280, 720)
    print("[smoke] Vulkan_Init OK, window open")
    print(f"[smoke] requested 1280x720, win_w={render.win_w} win_h={render.win_h}")

    # Probe shapes: red square at UP*2, blue circle at DOWN*2 (asymmetric
    # probe to detect vertical flips later).
    import numpy as np
    from manim import Scene, Square, Circle, UP, DOWN

    scene = Scene()
    render.scene = scene
    sq = Square(side_length=1.5, color="#FF0000")
    sq.set_fill("#FF0000", opacity=1.0)
    sq.shift(UP * 2)
    cr = Circle(radius=0.9, color="#0000FF")
    cr.set_fill("#0000FF", opacity=1.0)
    cr.shift(DOWN * 2)
    scene.add(sq, cr)

    # warm-up ticks
    for i in range(30):
        if not render.tick():
            print("[smoke] tick returned 0 (window closed?)")
            break
        render.sync(scene, 0.0)
    print(f"[smoke] after ticks: win_w={render.win_w} win_h={render.win_h}")

    # Two-phase framebuffer readback
    w = ctypes.c_int(0)
    h = ctypes.c_int(0)
    buf = (ctypes.c_ubyte * (4 * 4096 * 4096))()
    dll = render.dll
    dll.Vulkan_ReadPixels.restype = ctypes.c_int
    dll.Vulkan_ReadPixels.argtypes = [
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    dll.Vulkan_ReadPixels(buf, ctypes.byref(w), ctypes.byref(h))  # phase 1: request
    render.tick()
    render.sync(scene, 0.0)
    rc = dll.Vulkan_ReadPixels(buf, ctypes.byref(w), ctypes.byref(h))  # phase 2
    print(f"[smoke] readback rc={rc} size={w.value}x{h.value}")

    if rc == 1:
        W, H = w.value, h.value
        arr = np.frombuffer(buf, dtype=np.uint8, count=W * H * 4).reshape(H, W, 4)

        def sample(fx, fy, label):
            x = int(fx * W)
            y = int(fy * H)
            px = arr[y, x]
            print(f"[smoke] {label} @({x},{y}): RGBA={tuple(int(v) for v in px)}")

        sample(0.5, 0.5, "center")
        # red square at UP*2 -> manim y=+2 -> screen y = H/2 - 2*(H/8) = H*0.25
        sample(0.5, 0.25, "upper (expect RED)")
        # blue circle at DOWN*2 -> screen y = H/2 + 2*(H/8) = H*0.75
        sample(0.5, 0.75, "lower (expect BLUE)")

        # background sample
        sample(0.02, 0.02, "corner (expect BLACK)")

    render.close()
    print("[smoke] done")


if __name__ == "__main__":
    main()
