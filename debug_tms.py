import sys, os
sys.path.insert(0, os.getcwd())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import core.vulkan_bind as vb

_orig_send = vb.VulkanRender._send
_call_count = [0]

def debug_send(self, mob, angle=0.0):
    a = vb.get_anim_opacity(mob)
    tname = type(mob).__name__
    transforming = getattr(mob, '_transforming', False)
    subs = len(mob.submobjects) if hasattr(mob, 'submobjects') else 0
    if tname == 'Text' or transforming:
        _call_count[0] += 1
        if _call_count[0] <= 50:
            sub_ops = []
            if subs > 0 and hasattr(mob, 'submobjects'):
                for s in mob.submobjects[:3]:
                    sub_ops.append(f"{vb.get_anim_opacity(s):.2f}")
            print(f"  _send({tname}) op={a:.2f} tf={transforming} subs={subs} sub_ops=[{','.join(sub_ops)}]")
    return _orig_send(self, mob, angle)

vb.VulkanRender._send = debug_send

_orig_play = vb.VulkanRender.play
def debug_play(self, *animations, **kwargs):
    print(f"\n=== play() with {len(animations)} anims ===")
    for a in animations:
        tn = type(a).__name__
        has_m = hasattr(a, 'mobject') and a.mobject is not None
        has_t = hasattr(a, 'target_mobject') and a.target_mobject is not None
        print(f"  {tn}: mobject={type(a.mobject).__name__ if has_m else 'None'} target={type(a.target_mobject).__name__ if has_t else 'None'}")
        if hasattr(a, '_matched_anims'):
            print(f"    matched: {len(a._matched_anims)}")
        if hasattr(a, '_fade_out_anims'):
            print(f"    fade_out: {len(a._fade_out_anims)}")
        if hasattr(a, '_fade_in_anims'):
            print(f"    fade_in: {len(a._fade_in_anims)}")
    return _orig_play(self, *animations, **kwargs)

vb.VulkanRender.play = debug_play

_orig_begin_tma = vb.TransformMatchingAbstractBase.begin
def debug_begin_tma(self, t):
    _orig_begin_tma(self, t)
    print(f"\n  TransformMatchingAbstractBase.begin() done")
    print(f"    matched_anims: {len(self._matched_anims)}")
    print(f"    fade_out: {len(self._fade_out_anims)}")
    print(f"    fade_in: {len(self._fade_in_anims)}")
    if self._fade_out_anims:
        for p in self._fade_out_anims:
            print(f"      fade_out part: {type(p).__name__} op={vb.get_anim_opacity(p):.2f}")
    if self._fade_in_anims:
        for p in self._fade_in_anims:
            print(f"      fade_in part: {type(p).__name__} op={vb.get_anim_opacity(p):.2f}")

vb.TransformMatchingAbstractBase.begin = debug_begin_tma

from scenes.demo_scene import VulkanShapeShowcase
scene = VulkanShapeShowcase()
scene.render()
print("\n=== DONE ===")
