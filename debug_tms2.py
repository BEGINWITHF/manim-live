import sys, os
sys.path.insert(0, os.getcwd())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import core.vulkan_bind as vb

_orig_send = vb.VulkanRender._send
_seen_tms = [False]
_frame_count = [0]

def debug_send(self, mob, angle=0.0):
    a = vb.get_anim_opacity(mob)
    tname = type(mob).__name__
    transforming = getattr(mob, '_transforming', False)
    if transforming or (tname == 'Text' and _seen_tms[0]):
        subs = len(mob.submobjects) if hasattr(mob, 'submobjects') else 0
        sub_ops = []
        if subs > 0 and hasattr(mob, 'submobjects') and subs <= 10:
            for s in mob.submobjects:
                sub_ops.append(f"{vb.get_anim_opacity(s):.2f}")
        _frame_count[0] += 1
        if _frame_count[0] <= 20:
            print(f"  frame={_frame_count[0]} _send({tname}) op={a:.2f} tf={transforming} subs={subs} sub_ops=[{','.join(sub_ops)}]")
    return _orig_send(self, mob, angle)

vb.VulkanRender._send = debug_send

_orig_play = vb.VulkanRender.play
def debug_play(self, *animations, **kwargs):
    for a in animations:
        if type(a).__name__ == 'TransformMatchingShapes':
            _seen_tms[0] = True
            print(f"\n=== TransformMatchingShapes play() ===")
            print(f"  source: {type(a.mobject).__name__} submobs={len(a.mobject.submobjects)}")
            print(f"  target: {type(a.target_mobject).__name__} submobs={len(a.target_mobject.submobjects)}")
            # Check scene state
            print(f"  source in scene: {a.mobject in self.scene.mobjects}")
            print(f"  target in scene: {a.target_mobject in self.scene.mobjects}")
            print(f"  source op: {vb.get_anim_opacity(a.mobject):.2f}")
            print(f"  target op: {vb.get_anim_opacity(a.target_mobject):.2f}")
            print(f"  source _transforming: {getattr(a.mobject, '_transforming', 'NOT SET')}")
            print(f"  target _transforming: {getattr(a.target_mobject, '_transforming', 'NOT SET')}")
    return _orig_play(self, *animations, **kwargs)

vb.VulkanRender.play = debug_play

_orig_begin = vb.TransformMatchingAbstractBase.begin
def debug_begin(self, t):
    _orig_begin(self, t)
    print(f"\n  begin() done:")
    print(f"    matched: {len(self._matched_anims)}")
    print(f"    fade_out: {len(self._fade_out_anims)}")
    print(f"    fade_in: {len(self._fade_in_anims)}")
    print(f"    source op: {vb.get_anim_opacity(self.mobject):.2f}")
    print(f"    target op: {vb.get_anim_opacity(self.target_mobject):.2f}")
    print(f"    source _transforming: {getattr(self.mobject, '_transforming', 'NOT SET')}")
    print(f"    target _transforming: {getattr(self.target_mobject, '_transforming', 'NOT SET')}")
    for i, p in enumerate(self._fade_out_anims):
        print(f"    fade_out[{i}]: op={vb.get_anim_opacity(p):.2f}")
    for i, p in enumerate(self._fade_in_anims):
        print(f"    fade_in[{i}]: op={vb.get_anim_opacity(p):.2f}")

vb.TransformMatchingAbstractBase.begin = debug_begin

_orig_sync = vb.VulkanRender.sync
def debug_sync(self, scene, angle=0.0):
    if _seen_tms[0] and _frame_count[0] <= 5:
        print(f"\n  sync() scene.mobjects:")
        for m in scene.mobjects:
            a = vb.get_anim_opacity(m)
            tf = getattr(m, '_transforming', False)
            print(f"    {type(m).__name__} op={a:.2f} tf={tf}")
    return _orig_sync(self, scene, angle)
vb.VulkanRender.sync = debug_sync

from scenes.demo_scene import VulkanShapeShowcase
scene = VulkanShapeShowcase()
scene.render()
print("\n=== DONE ===")
