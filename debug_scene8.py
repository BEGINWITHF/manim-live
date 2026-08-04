import sys
sys.path.insert(0, r'C:\Users\begin\Desktop\manim-booster')
from core.vulkan_bind import VulkanRender
from core.animations.base import set_anim_opacity, get_anim_opacity, _anim_opacity
from core.animations.add import Add
from core.animations.write import Write
from core.animations.wait import Wait
from core.animations.transform_matching import TransformMatchingShapes
from manim import Text, Scene

render = VulkanRender(1920, 1080)
scene = Scene()
render.scene = scene

src = Text("abc", font_size=72)
src.shift([-3.5, 0, 0])

tar = Text("xyz", font_size=72)
tar.shift([3.5, 0, 0])

render.play(Write(src, run_time=1.5))

print("=== After Write(src) ===")
print(f"scene.mobjects: {[type(m).__name__ for m in scene.mobjects]}")
print(f"tar in scene.mobjects: {tar in scene.mobjects}")
print(f"tar anim_opacity: {get_anim_opacity(tar)}")

render.play(Add(tar), run_time=0.5)

print("=== After Add(tar) ===")
print(f"scene.mobjects: {[type(m).__name__ for m in scene.mobjects]}")
print(f"tar in scene.mobjects: {tar in scene.mobjects}")
print(f"tar anim_opacity: {get_anim_opacity(tar)}")
print(f"tar submobjects: {len(tar.submobjects)}")
for i, sub in enumerate(tar.submobjects):
    print(f"  sub[{i}] type={type(sub).__name__} pts={len(sub.get_points())} opacity={get_anim_opacity(sub)}")

render.play(Wait(0.5))
print("=== After Wait ===")

render.play(TransformMatchingShapes(src, tar, run_time=2.0))
print("=== After TransformMatchingShapes ===")
print(f"scene.mobjects: {[type(m).__name__ for m in scene.mobjects]}")
for m in scene.mobjects:
    print(f"  {type(m).__name__} id={id(m)} opacity={get_anim_opacity(m)}")

render.play(Wait(1.5))
render.close()
print("Done")
