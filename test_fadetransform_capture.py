import sys, time, ctypes
sys.path.insert(0, 'core')
from vulkan_bind import VulkanRender, FadeTransform, Add, Wait, set_anim_opacity
from manim import *

v = VulkanRender(1920, 1080)

sq = Square(side_length=1.5, color=BLUE)
sq.set_fill(BLUE, opacity=0.7)
sq.set_stroke(width=4)
sq.shift(LEFT * 4)

circ = Circle(radius=0.8, color=RED)
circ.set_fill(RED, opacity=0.7)
circ.set_stroke(width=4)
circ.shift(RIGHT * 4)

# Sync initial state
v.dll.ClearShapes()
v.sync = lambda: None

ft = FadeTransform(sq, circ, run_time=1.5)
ft.begin(time.time())

screenshots = [0.0, 0.25, 0.5, 0.75, 1.0]
next_ss = 0

while next_ss < len(screenshots):
    now = time.time()
    pct = (now - ft.start_time) / ft.run_time
    if pct > 1.0:
        pct = 1.0
    
    ft.interpolate(now)
    
    v.dll.ClearShapes()
    
    # Source
    a_src = getattr(sq, '_anim_opacity', 1.0)
    a_ghost = getattr(ft._ghost, '_anim_opacity', 0.0) if ft._ghost else 0.0
    
    if a_src > 0.01:
        cx, cy, _ = sq.get_center()
        sx, sy = v.dll.Vulkan_Tick() >> 16, v.dll.Vulkan_Tick() & 0xFFFF
        v.dll.AddRect(
            ctypes.c_float(960 + cx * (960/7)),
            ctypes.c_float(540 - cy * (540/4)),
            ctypes.c_float(96.0),
            ctypes.c_int(0), ctypes.c_int(180), ctypes.c_int(220)
        )
    
    # Ghost
    if a_ghost > 0.01 and ft._ghost:
        gcx, gcy, _ = ft._ghost.get_center()
        v.dll.AddCircle(
            ctypes.c_float(960 + gcx * (960/7)),
            ctypes.c_float(540 - gcy * (540/4)),
            ctypes.c_float(48.0),
            ctypes.c_int(0), ctypes.c_int(180), ctypes.c_int(100),
            ctypes.c_int(4), ctypes.c_int(180), ctypes.c_int(80)
        )
    
    # Target (always visible)
    tcx, tcy, _ = circ.get_center()
    v.dll.AddCircle(
        ctypes.c_float(960 + tcx * (960/7)),
        ctypes.c_float(540 - tcy * (540/4)),
        ctypes.c_float(48.0),
        ctypes.c_int(0), ctypes.c_int(180), ctypes.c_int(100),
        ctypes.c_int(4), ctypes.c_int(180), ctypes.c_int(80)
    )
    
    if pct >= screenshots[next_ss] - 0.02:
        fname = f'C:/Users/begin/Desktop/ft4_pct_{int(screenshots[next_ss]*100):03d}.png'
        v.dll.SaveScreenshot(fname.encode('utf-8'))
        print(f'Saved {fname} at pct={pct:.3f}')
        next_ss += 1
    
    v.tick()
    time.sleep(0.005)

ft.finish()
v.dll.Vulkan_Cleanup()
print('Done')
