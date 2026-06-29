import sys, os
sys.path.insert(0, os.getcwd())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import core.vulkan_bind as vb

_orig_send_text_write = vb.VulkanRender._send_text_write
_call_log = []

def debug_send_text_write(self, mob, letter_alphas, w, h):
    txt = mob.original_text if hasattr(mob, 'original_text') else (mob.text if hasattr(mob, 'text') else "")
    subs = len(mob.submobjects) if hasattr(mob, 'submobjects') else 0
    _call_log.append(f"_send_text_write: text='{txt}' subs={subs} letter_alphas={len(letter_alphas)}")
    
    for i, sub in enumerate(mob.submobjects):
        sub_alpha = letter_alphas.get(i, 0.0)
        if sub_alpha > 0.001:
            pts = sub.get_points() if hasattr(sub, 'get_points') else sub.points
            char = txt[i] if i < len(txt) else '?'
            phase = "STROKE" if sub_alpha < 0.5 else "FILL"
            _call_log.append(f"  [{i}] char='{char}' alpha={sub_alpha:.3f} phase={phase} pts={len(pts)}")
    
    return _orig_send_text_write(self, mob, letter_alphas, w, h)

vb.VulkanRender._send_text_write = debug_send_text_write

from manim import Scene, Text, UP, DOWN, YELLOW, RED
from core.vulkan_bind import VulkanRender, Write, Wait

class DebugWriteTest(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        t1 = Text("Hi", font_size=72)
        t1.shift(UP * 1)

        render.play(Write(t1, run_time=2.0))
        render.play(Wait(1.0))
        render.close()

scene = DebugWriteTest()
scene.construct()

for line in _call_log[:50]:
    print(line)
print(f"Total log entries: {len(_call_log)}")
