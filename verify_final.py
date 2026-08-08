"""Focused verification: scale fix + retina rendering + text path."""
import sys, os, ctypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.vulkan_bind import VulkanRender
from manim import Scene, Text, Square, BLUE, DOWN

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    mark = "PASS" if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f"  ({detail})" if detail else ""))
    if cond: PASS += 1
    else: FAIL += 1

class _S(Scene):
    def __init__(self):
        super().__init__()
        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=1.0)
        sq.set_stroke(width=4)
        self.add(sq)
        self.add(Text("SCALE TEST 42", font_size=48).shift(DOWN * 2))

print("=== Scale / resolution / text verification ===")
render = VulkanRender(1920, 1080)
scene = _S()
render.scene = scene
dll = render.dll

# Warm up (window settles; may resize swapchain a few times)
for _ in range(5):
    dll.ClearShapes()
    render.sync(scene)
    render.tick()
win_w, win_h = render.win_w, render.win_h

# Two-phase readback with retries
w = ctypes.c_int(0); h = ctypes.c_int(0)
buf = (ctypes.c_ubyte * (4 * 8192 * 8192))()
dll.Vulkan_ReadPixels.restype = ctypes.c_int
dll.Vulkan_ReadPixels.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
rc = 0
for _ in range(10):
    dll.ClearShapes()
    render.sync(scene)
    render.tick()
    rc = dll.Vulkan_ReadPixels(buf, ctypes.byref(w), ctypes.byref(h))
    if rc == 1:
        break

print(f"  window coords: {win_w}x{win_h}, framebuffer: {w.value}x{h.value}, rc={rc}")
check("window coords match framebuffer size", win_w == w.value and win_h == h.value and rc == 1,
      f"{win_w}x{win_h} vs {w.value}x{h.value}")

def px(x, y):
    i = (y * w.value + x) * 4
    return buf[i], buf[i+1], buf[i+2]

# Square side 1.0 at ORIGIN
cx, cy = win_w // 2, win_h // 2
scale_px = win_h / 8.0
half = 0.5 * scale_px
x0 = x1 = None
for x in range(int(cx - 2*half), int(cx + 2*half)):
    r_, g_, b_ = px(x, cy)
    if b_ > 180 and b_ > r_ and b_ > g_:
        if x0 is None: x0 = x
        x1 = x
if x0 and x1:
    center = (x0 + x1) / 2
    width = x1 - x0
    check("square centered at origin", abs(center - cx) < 10, f"center={center:.0f} expected≈{cx}")
    check("square side correct length", abs(width - 2*half) < 30, f"width={width} expected≈{2*half:.0f}")
else:
    check("square found on scanline", False, "not found")

# Text below center
ty = cy + int(2 * scale_px)
bright = 0
for y in range(int(ty - scale_px), int(ty + scale_px), 3):
    for x in range(int(cx - 3*scale_px), int(cx + 3*scale_px), 3):
        r_, g_, b_ = px(x, y)
        if r_ + g_ + b_ > 200:
            bright += 1
check("text renders below center", bright > 20, f"{bright} px")

# Bezier path (text glyph path) renders
print("\n=== AddBezierPath (text glyph path) ===")
pts = (ctypes.c_float * 48)()
sq = [(100,100),(200,100),(200,100),(200,200),(200,200),(200,300),(200,300),(100,300),
      (100,300),(100,300),(100,300),(100,200),(100,200),(100,100),(100,100),(100,100)]
for i, (x, y) in enumerate(sq):
    pts[i*3], pts[i*3+1], pts[i*3+2] = x, y, 0.0
b2 = (ctypes.c_ubyte * (4 * 8192 * 8192))()
found = 0
for _ in range(10):
    dll.ClearShapes()
    render.sync(scene)
    dll.AddBezierPath(pts, 16, 255, 255, 255, 3.0, 255, 255, 255, 0.5, 1.0, 1, 1, 1.0)
    render.tick()
    rc = dll.Vulkan_ReadPixels(b2, ctypes.byref(w), ctypes.byref(h))
    if rc == 1:
        for yy in range(90, 310, 4):
            for xx in range(90, 210, 4):
                i = (yy * w.value + xx) * 4
                if b2[i] + b2[i+1] + b2[i+2] > 200:
                    found += 1
        break
check("bezier fill renders", found > 20, f"{found} px")

render.close()
print(f"\nRESULT: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
