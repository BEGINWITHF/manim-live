import ctypes
import inspect
import os
import math
import time
import numpy as np
from manim import (
    Square, Circle, Line, Rectangle, Polygon, Polygram,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group, OUT, ORIGIN
)
from manim.animation.transform import Transform as _ManimTransform

from core.rate_functions import (
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth,
    _wiggle, _lingering, _exponential_decay,
    _squish_rate_func, _sigmoid,
)
from core.animations import (
    Animation, Create, Uncreate, DrawBorderThenFill, Write, Unwrite,
    ShowIncreasingSubsets, SpiralIn,
    Blink, TypeWithCursor, UntypeWithCursor,
    Succession, Wait, Add, AnimationGroup, MoveToTarget, Indicate,
    FadeIn, FadeOut, FadeTransform,
    Rotating, Rotate,
    Transform, ReplacementTransform,
    TransformMatchingAbstractBase, TransformMatchingShapes, TransformMatchingTex,
    GrowFromCenter, GrowArrow, GrowFromEdge, GrowFromPoint, SpinInFromNothing,
    ApplyWave, Circumscribe, ShowPassingFlash, Homotopy, MoveAlongPath,
    set_anim_opacity, get_anim_opacity,
    set_anim_rotation, get_anim_rotation,
    set_anim_rotation_delta, get_anim_rotation_delta, clear_anim_rotation_delta,
    TARGET_FPS, FRAME_DURATION,
    TextDecimalNumber,
)
from core.vulkan_util import manim_to_screen, rotate_point, get_fill_rgb, get_stroke_rgb, get_stroke_w
from core.vulkan_shapes import ShapeMixin
from core.vulkan_text import TextMixin

from manim import ChangingDecimal as _OrigChangingDecimal
from manim import ChangeDecimalToValue as _OrigChangeDecimalToValue
_OrigChangingDecimal.check_validity_of_input = lambda self, dm: None
_OrigChangeDecimalToValue.check_validity_of_input = lambda self, dm: None


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
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
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
        self.dll.AddLineStrip.restype = None
        self.dll.AddLineStrip.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddEllipse.restype = None
        self.dll.AddEllipse.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddPolygon.restype = None
        self.dll.AddPolygon.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int,
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
        grow_rot = getattr(mob, '_grow_rot', 0.0)
        rot += grow_rot

        if isinstance(mob, Text):
            has_stroke = False
            if hasattr(mob, 'family_members_with_points'):
                for fm in mob.family_members_with_points():
                    sw = fm.get_stroke_width() if hasattr(fm, 'get_stroke_width') else 0
                    if sw > 0:
                        try:
                            sa = float(fm.stroke_rgbas[:, 3].max())
                        except Exception:
                            sa = 1.0
                        if sa > 0:
                            has_stroke = True
                            break
            if has_stroke:
                self._send_text_stroke(mob, a, w, h, parent_offset)
            elif getattr(mob, '_letter_alphas', None) is not None and hasattr(mob, 'submobjects') and mob.submobjects:
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
            vgroup_progress = getattr(mob, '_vulkan_progress', 1.0)
            num_subs = len(list(mob)) if hasattr(mob, '__len__') else 0
            about = getattr(mob, '_rotation_about_point', None)
            vgroup_center = np.array(mob.get_center(), dtype=float)
            try:
                original_center = np.array(mob.get_points().mean(axis=0) if len(mob.get_points()) > 0 else mob.get_center(), dtype=float)
            except Exception:
                original_center = vgroup_center.copy()
            offset = vgroup_center - original_center
            if parent_offset is not None:
                offset = offset + parent_offset
            for i, sub in enumerate(mob):
                sub_offset = offset
                if about is not None and rot != 0.0:
                    sub_center = np.array(sub.get_center(), dtype=float)
                    rel = sub_center - np.array(about, dtype=float)
                    cos_a = math.cos(rot)
                    sin_a = math.sin(rot)
                    rx = rel[0] * cos_a - rel[1] * sin_a
                    ry = rel[0] * sin_a + rel[1] * cos_a
                    new_center = np.array(about, dtype=float) + np.array([rx, ry, 0.0])
                    sub_offset = sub_offset + (new_center - sub_center)
                if vgroup_progress < 1.0 and num_subs > 1:
                    full_length = (num_subs - 1) * 1.0 + 1
                    value = vgroup_progress * full_length
                    lower = i * 1.0
                    sub_progress = max(0.0, min(1.0, value - lower))
                    sub._vulkan_progress = sub_progress
                elif vgroup_progress < 1.0:
                    sub._vulkan_progress = vgroup_progress
                self._send(sub, rot, parent_alpha=effective_alpha, parent_offset=sub_offset)
            return

        if getattr(mob, '_transforming', False):
            # Points already have the cumulative rotation applied by the
            # correction + updater, so pass rot=0 to avoid double rotation.
            self._send_vmobject(mob, a, w, h, parent_offset, 0.0)
            return

        if isinstance(mob, Square):
            self._send_square(mob, a, w, h, rot)
        elif isinstance(mob, Rectangle):
            self._send_rectangle(mob, a, w, h, rot)
        elif isinstance(mob, Ellipse):
            self._send_ellipse(mob, a, w, h, rot)
        elif isinstance(mob, Dot):
            self._send_dot(mob, a, w, h)
        elif isinstance(mob, Circle):
            self._send_circle(mob, a, w, h, rot)
        elif isinstance(mob, Arrow):
            self._send_arrow(mob, a, w, h, rot)
        elif isinstance(mob, DashedLine):
            self._send_dashed_line(mob, a, w, h)
        elif isinstance(mob, Line):
            self._send_line(mob, a, w, h, rot)
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
                if len(pts) >= 2:
                    self._send_vmobject(mob, a, w, h, parent_offset, rot)
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
        elif isinstance(anim, AnimationGroup):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub))
        return mobjects

    def play(self, *animations, **kwargs):
        if not self.scene:
            return

        screenshot_at = kwargs.get('screenshot_at', None)

        resolved = []
        for anim in animations:
            from manim.mobject.mobject import _AnimationBuilder
            if isinstance(anim, _AnimationBuilder):
                anim.anim_args['suspend_mobject_updating'] = False
                built = anim.build()
                resolved.append(built)
            elif isinstance(anim, AnimationGroup):
                sub_resolved = []
                for sub in anim.animations:
                    if isinstance(sub, _AnimationBuilder):
                        sub.anim_args['suspend_mobject_updating'] = False
                        built = sub.build()
                        sub_resolved.append(built)
                    else:
                        sub_resolved.append(sub)
                anim.animations = sub_resolved
                resolved.append(anim)
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))

        all_mobjects = list(add_mobs)
        for anim in animations:
            if isinstance(anim, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate, GrowArrow, Indicate, ShowPassingFlash)) and anim.mobject:
                if isinstance(anim, (Create, DrawBorderThenFill)):
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
                    elif isinstance(sub_anim, (Transform, _ManimTransform)):
                        if sub_anim.mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.mobject)
                        if sub_anim.target_mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.target_mobject)
            elif isinstance(anim, (Transform, _ManimTransform)):
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
                    if isinstance(sub, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate)) and sub.mobject:
                        if isinstance(sub, (Create, DrawBorderThenFill)):
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
                                    set_anim_opacity(mob, 0.0)
                                    if mob not in all_mobjects:
                                        all_mobjects.append(mob)
                            elif isinstance(sub_anim, (Transform, _ManimTransform)):
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
            elif isinstance(anim, AnimationGroup):
                for sub in anim.animations:
                    if isinstance(sub, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate, GrowArrow)) and sub.mobject:
                        if isinstance(sub, (Create, DrawBorderThenFill)):
                            sub.mobject._vulkan_progress = 0.0
                        if isinstance(sub, FadeIn):
                            set_anim_opacity(sub.mobject, 0.0)
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                    elif isinstance(sub, (FadeIn, FadeOut)):
                        for mob in sub.mobjects:
                            if isinstance(sub, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub, Transform):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        sub.mobject._transforming = True

        for mob in all_mobjects:
            if mob not in self.scene.mobjects:
                self.scene.add(mob)

        for anim in animations:
            if hasattr(anim, 'mobject') and anim.mobject is not None:
                if anim.mobject not in self.scene.mobjects:
                    self.scene.mobjects.append(anim.mobject)
            cursor = getattr(anim, 'cursor', None)
            if cursor is not None and cursor not in self.scene.mobjects:
                self.scene.mobjects.append(cursor)

        for mob in add_mobs:
            set_anim_opacity(mob, 0.0)

        for a in animations:
            if isinstance(a, Add):
                for mob in a.mobjects:
                    set_anim_opacity(mob, 1.0)

        real_anims = [a for a in animations if not isinstance(a, Add)]

        if 'run_time' in kwargs:
            shared_rt = kwargs['run_time']
            for a in real_anims:
                if isinstance(a, (Wait, Succession)):
                    continue
                a.run_time = shared_rt
        if 'rate_func' in kwargs:
            shared_rf = kwargs['rate_func']
            for a in real_anims:
                if isinstance(a, (Wait, Succession)):
                    continue
                a.rate_func = shared_rf

        for a in real_anims:
            is_manim = type(a).__module__.startswith('manim')
            if is_manim:
                a.start_time = time.time()
                a.begin()
                tm = getattr(a, 'target_mobject', None)
                if tm is not None and hasattr(tm, 'get_updaters') and tm.get_updaters():
                    for upd in tm.get_updaters():
                        upd(tm)
                    tc = getattr(a, 'target_copy', None)
                    if tc is not None:
                        tc.move_to(tm.get_center())
                if a.mobject is not None and a.mobject not in self.scene.mobjects:
                    self.scene.mobjects.append(a.mobject)
            else:
                a.begin(time.time())

        for a in real_anims:
            if isinstance(a, TransformMatchingAbstractBase):
                for sub_anim in getattr(a, '_anims', []):
                    if isinstance(sub_anim, (Transform, _ManimTransform)):
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                        if sub_anim.target_mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.target_mobject)

        self._active_anims = real_anims
        self._last_frame_time = time.time() - (1.0 / 30.0)
        _orig_vgroup_rotate = {}
        _prev_vg_rotation = {}

        def _rotation_pivot(vg):
            if hasattr(vg, '_rotation_about_point'):
                return np.array(vg._rotation_about_point, dtype=float)
            return vg.get_center()

        def _patch_vgroup(vg):
            if id(vg) in _orig_vgroup_rotate:
                return
            _orig_vgroup_rotate[id(vg)] = vg.rotate
            def _propagating_rotate(angle, axis=OUT, about_point=None, about_edge=None, **kwargs):
                alpha = _anim_alpha[0]
                effective = angle * alpha
                pivot = _rotation_pivot(vg)
                for m in vg.family_members_with_points():
                    if hasattr(m, 'points') and len(m.points) > 0:
                        c, s = np.cos(effective), np.sin(effective)
                        rot_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                        m.points = (m.points - pivot) @ rot_matrix.T + pivot
                current = get_anim_rotation(vg)
                set_anim_rotation(vg, current + effective)
                return vg
            vg.rotate = _propagating_rotate

        def _unpatch_vgroup(vg):
            if id(vg) in _orig_vgroup_rotate:
                vg.rotate = _orig_vgroup_rotate.pop(id(vg))

        frame_count = 0
        # Mutable container so _patch_vgroup's closure reads the latest alpha
        _anim_alpha = [1.0]
        while True:
            frame_start = time.time()
            now = frame_start
            dt = now - self._last_frame_time
            self._last_frame_time = now
            all_done = True

            # Time-based rotation: original manim uses -0.3 rad/frame at 30fps
            # which is -9 rad/s.  current_alpha = dt * 30 gives:
            #   30fps → 1.0, 60fps → 0.5, etc.
            current_alpha = dt * 30
            _anim_alpha[0] = current_alpha

            for a in self._active_anims:
                is_manim = type(a).__module__.startswith('manim')
                if is_manim:
                    elapsed = now - a.start_time
                    alpha = elapsed / a.run_time if a.run_time > 0 else 1.0
                    alpha = max(0.0, min(1.0, alpha))
                    a.interpolate(alpha)

                    if not getattr(a, 'finished', False) and elapsed >= a.run_time:
                        a.finish()
                        a.finished = True
                        mob = getattr(a, 'mobject', None)
                        if mob:
                            mob.resume_updating()
                else:
                    a.interpolate(now)
                    if not a.finished and (now - a.start_time) >= a.run_time:
                        a.finish()
                if not getattr(a, 'finished', False):
                    all_done = False

            # Apply rotation delta per VGroup.
            for mob in self.scene.mobjects:
                if isinstance(mob, (VGroup, Group)):
                    vg_rot = get_anim_rotation(mob)
                    prev_rot = _prev_vg_rotation.get(id(mob), 0.0)
                    delta = vg_rot - prev_rot
                    if abs(delta) > 1e-12:
                        pivot = _rotation_pivot(mob)
                        c, s = np.cos(delta), np.sin(delta)
                        rot_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                        for sub in mob.family_members_with_points():
                            if hasattr(sub, 'points') and len(sub.points) > 0:
                                sub.points = (sub.points - pivot) @ rot_matrix.T + pivot
                    _prev_vg_rotation[id(mob)] = vg_rot

            for mob in self.scene.mobjects:
                if isinstance(mob, (VGroup, Group)) and getattr(mob, 'updaters', None):
                    _patch_vgroup(mob)

            for mob in reversed(self.scene.mobjects):
                if hasattr(mob, 'updaters') and mob.updaters and not getattr(mob, 'updating_suspended', False):
                    for updater in mob.updaters:
                        nparams = len(inspect.signature(updater).parameters)
                        if nparams == 0:
                            updater()
                        elif nparams == 1:
                            updater(mob)
                        else:
                            updater(mob, dt)

            clear_anim_rotation_delta()

            for mob in self.scene.mobjects:
                if isinstance(mob, (VGroup, Group)) and id(mob) in _orig_vgroup_rotate:
                    _unpatch_vgroup(mob)

            if not self.tick():
                break
            self.sync(self.scene)

            frame_count += 1

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
