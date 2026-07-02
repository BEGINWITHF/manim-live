"""Test TransformMatchingShapes visual correctness via proper play() simulation."""
import sys
sys.path.insert(0, '.')

from manim import *
from core.vulkan_bind import (
    VulkanRender, Animation, Write, Wait, Add,
    FadeIn, FadeOut, FadeTransform,
    Transform, ReplacementTransform, TransformMatchingShapes,
    set_anim_opacity, get_anim_opacity,
)
import time
import os

class TestTMSVisual(Scene):
    def construct(self):
        render = VulkanRender(1920, 1080)
        render.scene = self

        src = Text("abc", font_size=72)
        src.shift(LEFT * 3.5)

        tar = Text("xyz", font_size=72)
        tar.shift(RIGHT * 3.5)

        arrow = Text("→", font_size=48)
        arrow.shift(UP * 0.2)

        render.play(Write(src, run_time=1.5))
        render.play(Add(tar), Add(arrow))
        render.play(Wait(0.5))

        # Screenshot before TMS
        render.screenshot("C:\\Users\\begin\\Desktop\\tms_visual_before.png")
        print("Before TMS: mobjects =", [type(m).__name__ for m in self.mobjects])

        # Now manually simulate TMS like play() does
        anim = TransformMatchingShapes(src, tar, run_time=2.0)

        # Mimic what play() does for TransformMatchingAbstractBase
        if anim.mobject in self.mobjects:
            self.mobjects.remove(anim.mobject)
        if anim.target_mobject in self.mobjects:
            self.mobjects.remove(anim.target_mobject)
        anim.mobject._transforming = True
        anim.target_mobject._transforming = True

        all_mobjects = []
        for sub_anim in anim._anims:
            print(f"Sub-anim: {type(sub_anim).__name__}")
            if isinstance(sub_anim, (FadeIn, FadeOut)):
                for mob in sub_anim.mobjects:
                    if isinstance(sub_anim, FadeIn):
                        set_anim_opacity(mob, 0.0)
                        print(f"  FadeIn mob: opacity set to 0")
                    if mob not in all_mobjects:
                        all_mobjects.append(mob)
                        if mob not in self.mobjects:
                            self.mobjects.append(mob)
            elif isinstance(sub_anim, Transform):
                if sub_anim.mobject not in all_mobjects:
                    all_mobjects.append(sub_anim.mobject)
                    if sub_anim.mobject not in self.mobjects:
                        self.mobjects.append(sub_anim.mobject)
                if sub_anim.target_mobject not in all_mobjects:
                    all_mobjects.append(sub_anim.target_mobject)
                    if sub_anim.target_mobject not in self.mobjects:
                        self.mobjects.append(sub_anim.target_mobject)

        print("After setup: mobjects =", [type(m).__name__ for m in self.mobjects])

        # Begin
        anim.begin(time.time())

        # Screenshot at 0%
        render.tick()
        render.sync(self)
        render.screenshot("C:\\Users\\begin\\Desktop\\tms_visual_0pct.png")
        print("0% captured")

        # 25%
        t25 = anim.start_time + anim.run_time * 0.25
        anim.interpolate(t25)
        render.tick()
        render.sync(self)
        render.screenshot("C:\\Users\\begin\\Desktop\\tms_visual_25pct.png")
        print("25% captured")

        # 50%
        t50 = anim.start_time + anim.run_time * 0.5
        anim.interpolate(t50)
        render.tick()
        render.sync(self)
        render.screenshot("C:\\Users\\begin\\Desktop\\tms_visual_50pct.png")
        print("50% captured")

        # 75%
        t75 = anim.start_time + anim.run_time * 0.75
        anim.interpolate(t75)
        render.tick()
        render.sync(self)
        render.screenshot("C:\\Users\\begin\\Desktop\\tms_visual_75pct.png")
        print("75% captured")

        # 100%
        t100 = anim.start_time + anim.run_time
        anim.interpolate(t100)
        anim.finish()
        render.tick()
        render.sync(self)
        render.screenshot("C:\\Users\\begin\\Desktop\\tms_visual_100pct.png")
        print("100% captured")

        # Cleanup
        anim.clean_up_from_scene(self)
        render.tick()
        render.sync(self)
        render.screenshot("C:\\Users\\begin\\Desktop\\tms_visual_cleanup.png")
        print("Cleanup captured")

        render.close()
        print("Done")

scene = TestTMSVisual()
scene.construct()
