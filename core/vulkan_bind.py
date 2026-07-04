import ctypes
import os
import math
import time
import numpy as np
from manim import (
    Square, Circle, Line, Rectangle, Polygon, Polygram,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group
)

from core.rate_functions import (
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth,
    _wiggle, _lingering, _exponential_decay,
    _squish_rate_func, _sigmoid,
)
from core.animations import (
    Animation, Create, DrawBorderThenFill, Write, Unwrite,
    Succession, Wait, Add,
    FadeIn, FadeOut, FadeTransform,
    Rotating, Rotate,
    Transform, ReplacementTransform,
    TransformMatchingAbstractBase, TransformMatchingShapes, TransformMatchingTex,
    set_anim_opacity, get_anim_opacity,
    set_anim_rotation, get_anim_rotation,
    TARGET_FPS, FRAME_DURATION,
)
from core.vulkan_util import manim_to_screen, rotate_point, get_fill_rgb, get_stroke_rgb, get_stroke_w
from core.vulkan_shapes import ShapeMixin
from core.vulkan_text import TextMixin


class VulkanRender(ShapeMixin, TextMixin):
    def __init__(self, w=1920, h=1080):
        self.win_w = w
        self.win_h = h
        self.frame_count = 0
        self.scene = None
        self._active_anims = []

        base_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dll"))
        if not os.path.exists(dll_path):
            dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dll"))
        if not os.path.exists(dll_path):
            raise FileNotFoundError("vulkan_core.dll not found")

        self.dll = ctypes.CDLL(dll_path)

        self.dll.Vulkan_Init.restype = ctypes.c_int
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Tick.restype = ctypes.c_int
        self.dll.Vulkan_Tick.argtypes = []
        self.dll.Vulkan_Shutdown.restype = None
        self.dll.Vulkan_Shutdown.argtypes = []
        self.dll.ClearShapes.restype = None
        self.dll.ClearShapes.argtypes = []

        self.dll.AddRect.restype = None
        self.dll.AddRect.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddCircle.restype = None
        self.dll.AddCircle.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddLine.restype = None
        self.dll.AddLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddEllipse.restype = None
        self.dll.AddEllipse.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddPolygon.restype = None
        self.dll.AddPolygon.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_float,
        ]
        self.dll.AddDashedLine.restype = None
        self.dll.AddDashedLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddArc.restype = None
        self.dll.AddArc.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddPoint.restype = None
        self.dll.AddPoint.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddBezierPath.restype = None
        self.dll.AddBezierPath.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_float, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]

        self.dll.SaveScreenshot.restype = ctypes.c_int
        self.dll.SaveScreenshot.argtypes = [ctypes.c_char_p]

        if self.dll.Vulkan_Init(w, h) != 1:
            raise RuntimeError("Vulkan_Init failed")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        for mob in scene.mobjects:
            self._send(mob, angle, parent_alpha=1.0)

    def _send(self, mob, angle=0.0, parent_alpha=1.0, parent_offset=None):
        w, h = self.win_w, self.win_h
        own_alpha = get_anim_opacity(mob)
        a = parent_alpha * own_alpha
        if a <= 0:
            return

        rot = get_anim_rotation(mob) + angle

        if isinstance(mob, Text):
            if getattr(mob, '_letter_alphas', None) is not None and hasattr(mob, 'submobjects') and mob.submobjects:
                self._send_text_write(mob, mob._letter_alphas, w, h, a)
            elif hasattr(mob, 'submobjects') and mob.submobjects:
                if a < 1.0:
                    self._send_transformed_text(mob, w, h, alpha=a)
                else:
                    self._send_text_bitmap(mob, w, h, a)

        elif isinstance(mob, (VGroup, Group)):
            effective_alpha = parent_alpha * own_alpha
            if effective_alpha <= 0:
                return
            vgroup_center = np.array(mob.get_center(), dtype=float)
            try:
                original_center = np.array(mob.get_points().mean(axis=0) if len(mob.get_points()) > 0 else mob.get_center(), dtype=float)
            except Exception:
                original_center = vgroup_center.copy()
            offset = vgroup_center - original_center
            if parent_offset is not None:
                offset = offset + parent_offset
            for sub in mob:
                self._send(sub, angle, parent_alpha=effective_alpha, parent_offset=offset)
            return

        if getattr(mob, '_transforming', False):
            self._send_vmobject(mob, a, w, h, parent_offset)
            return

        if isinstance(mob, Square):
            self._send_square(mob, a, w, h, rot)
        elif isinstance(mob, Rectangle):
            self._send_rectangle(mob, a, w, h, rot)
        elif isinstance(mob, Ellipse):
            self._send_ellipse(mob, a, w, h, rot)
        elif isinstance(mob, Circle):
            self._send_circle(mob, a, w, h, rot)
        elif isinstance(mob, Arrow):
            self._send_arrow(mob, a, w, h, rot)
        elif isinstance(mob, Line):
            self._send_line(mob, a, w, h, rot)
        elif isinstance(mob, Dot):
            self._send_dot(mob, a, w, h)
        elif isinstance(mob, DashedLine):
            self._send_dashed_line(mob, a, w, h)
        elif isinstance(mob, Arc):
            self._send_arc(mob, a, w, h)
        elif isinstance(mob, Polygon):
            self._send_polygon(mob, mob.get_vertices(), a)
        elif isinstance(mob, Polygram):
            self._send_polygon(mob, mob.get_vertices(), a)
        elif isinstance(mob, Point):
            self._send_point(mob, a, w, h)
        else:
            try:
                pts = mob.get_points()
                if len(pts) >= 4:
                    self._send_vmobject(mob, a, w, h, parent_offset)
            except Exception:
                pass

    def tick(self):
        self.frame_count += 1
        result = self.dll.Vulkan_Tick()
        if result == 0:
            return False
        self.win_w = (result >> 16) & 0xFFFF
        self.win_h = result & 0xFFFF
        return True

    def _extract_add_mobjects(self, anim):
        mobjects = []
        if isinstance(anim, Add):
            mobjects.extend(anim.mobjects)
        elif isinstance(anim, Succession):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub))
        return mobjects

    def play(self, *animations, **kwargs):
        if not self.scene:
            return

        screenshot_at = kwargs.get('screenshot_at', None)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))

        all_mobjects = list(add_mobs)
        for anim in animations:
            if isinstance(anim, (Create, Write, FadeIn, Rotating, Rotate)) and anim.mobject:
                if isinstance(anim, Create):
                    anim.mobject._vulkan_progress = 0.0
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
            elif isinstance(anim, (FadeIn, FadeOut)):
                for mob in anim.mobjects:
                    if isinstance(anim, FadeIn):
                        set_anim_opacity(mob, 0.0)
                    if mob not in all_mobjects:
                        all_mobjects.append(mob)
            elif isinstance(anim, TransformMatchingAbstractBase):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.target_mobject not in all_mobjects:
                    all_mobjects.append(anim.target_mobject)
                anim.mobject._transforming = True
                for sub_anim in getattr(anim, '_anims', []):
                    if isinstance(sub_anim, (FadeIn, FadeOut)):
                        for mob in sub_anim.mobjects:
                            if isinstance(sub_anim, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub_anim, Transform):
                        if sub_anim.mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.mobject)
                        if sub_anim.target_mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.target_mobject)
            elif isinstance(anim, Transform):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.replace_mobject_with_target_in_scene:
                    if anim.target_mobject not in all_mobjects:
                        all_mobjects.append(anim.target_mobject)
                    set_anim_opacity(anim.target_mobject, 0.0)
            elif isinstance(anim, FadeTransform):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.target_mobject not in all_mobjects:
                    all_mobjects.append(anim.target_mobject)
                ghost = getattr(anim, '_ghost', None)
                if ghost is not None and ghost not in all_mobjects:
                    all_mobjects.append(ghost)
            elif isinstance(anim, Succession):
                for sub in anim.animations:
                    if isinstance(sub, (Create, Write, FadeIn, Rotating, Rotate)) and sub.mobject:
                        if isinstance(sub, Create):
                            sub.mobject._vulkan_progress = 0.0
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                    elif isinstance(sub, (FadeIn, FadeOut)):
                        for mob in sub.mobjects:
                            if isinstance(sub, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub, TransformMatchingAbstractBase):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        sub.mobject._transforming = True
                        for sub_anim in getattr(sub, '_anims', []):
                            if isinstance(sub_anim, (FadeIn, FadeOut)):
                                for mob in sub_anim.mobjects:
                                    if isinstance(sub_anim, FadeIn):
                                        set_anim_opacity(mob, 0.0)
                                    if mob not in all_mobjects:
                                        all_mobjects.append(mob)
                            elif isinstance(sub_anim, Transform):
                                if sub_anim.mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.mobject)
                                if sub_anim.target_mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.target_mobject)
                    elif isinstance(sub, FadeTransform):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        ghost = getattr(sub, '_ghost', None)
                        if ghost is not None and ghost not in all_mobjects:
                            all_mobjects.append(ghost)

        for mob in all_mobjects:
            if mob not in self.scene.mobjects:
                self.scene.add(mob)
        for mob in add_mobs:
            set_anim_opacity(mob, 0.0)

        for a in animations:
            if isinstance(a, Add):
                for mob in a.mobjects:
                    set_anim_opacity(mob, 1.0)

        real_anims = [a for a in animations if not isinstance(a, Add)]

        for a in real_anims:
            a.begin(time.time())

        for a in real_anims:
            if isinstance(a, TransformMatchingAbstractBase):
                for sub_anim in getattr(a, '_anims', []):
                    if isinstance(sub_anim, Transform):
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                        if sub_anim.target_mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.target_mobject)

        self._active_anims = real_anims

        while True:
            frame_start = time.time()
            now = frame_start
            all_done = True
            for a in self._active_anims:
                a.interpolate(now)
                if not a.finished and (now - a.start_time) >= a.run_time:
                    a.finish()
                if not a.finished:
                    all_done = False

            if not self.tick():
                break
            self.sync(self.scene)

            if screenshot_at:
                for a in self._active_anims:
                    if a in screenshot_at:
                        alpha = (now - a.start_time) / a.run_time if a.run_time > 0 else 1.0
                        alpha = max(0.0, min(1.0, alpha))
                        alpha = a.rate_func(alpha)
                        for threshold, path in screenshot_at[a]:
                            if abs(alpha - threshold) < 0.02:
                                self.screenshot(path)
                                del screenshot_at[a][screenshot_at[a].index((threshold, path))]
                                break

            if all_done:
                break

            elapsed = time.time() - frame_start
            if elapsed < FRAME_DURATION:
                time.sleep(FRAME_DURATION - elapsed)

        for a in real_anims:
            if hasattr(a, 'clean_up_from_scene'):
                a.clean_up_from_scene(self.scene)

    def screenshot(self, path):
        path_bytes = path.encode('utf-8') if isinstance(path, str) else path
        return self.dll.SaveScreenshot(path_bytes)

    def close(self):
        self.dll.Vulkan_Shutdown()
