import ctypes
import inspect
import os
import math
import time
import shutil
import subprocess
import tempfile
import numpy as np
from manim import (
    Square, Circle, Line, Rectangle, Polygon, Polygram,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group, OUT, ORIGIN
)
from manim.animation.transform import Transform as _ManimTransform
from manim.animation.transform import FadeTransform as _ManimFadeTransform

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

from manim.animation.animation import prepare_animation as _orig_prepare_animation
from core.animations.base import Animation as _OurAnimation
def _patched_prepare_animation(anim):
    if isinstance(anim, _OurAnimation):
        return anim
    return _orig_prepare_animation(anim)
import manim.animation.speedmodifier as _sm
_sm.prepare_animation = _patched_prepare_animation
import manim.animation.animation as _aa
_aa.prepare_animation = _patched_prepare_animation


class BITMAPINFOHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]

class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bfType", ctypes.c_uint16),
        ("bfSize", ctypes.c_uint32),
        ("bfReserved1", ctypes.c_uint16),
        ("bfReserved2", ctypes.c_uint16),
        ("bfOffBits", ctypes.c_uint32),
    ]


class VulkanRender(ShapeMixin, TextMixin):
    def __init__(self, w=1920, h=1080):
        self.win_w = w
        self.win_h = h
        self.frame_count = 0
        self.scene = None
        self._active_anims = []
        self._recording = False
        self._record_dir = None
        self._record_frame_idx = 0
        self._record_path = None
        self._record_fps = 60

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
        self.dll.AddText.restype = None
        self.dll.AddText.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_char_p, ctypes.c_float,
        ]
        self.dll.Text_LoadFont.restype = ctypes.c_int
        self.dll.Text_LoadFont.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
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

        font_paths = [r"C:\Windows\Fonts\times.ttf", r"C:\Windows\Fonts\arial.ttf"]
        font_loaded = False
        for fp in font_paths:
            try:
                with open(fp, "rb") as f:
                    data = f.read()
                arr = (ctypes.c_ubyte * len(data))(*data)
                if self.dll.Text_LoadFont(arr, len(data)):
                    font_loaded = True
                    break
            except Exception:
                pass
        if not font_loaded:
            raise RuntimeError("Failed to load any font")

    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        skip_ids = getattr(self, '_skip_mob_ids', None)
        for mob in scene.mobjects:
            if skip_ids and id(mob) in skip_ids:
                continue
            self._send(mob, angle, parent_alpha=1.0)

    def _send(self, mob, angle=0.0, parent_alpha=1.0, parent_offset=None, parent_transforming=False, parent_is_text=False):
        w, h = self.win_w, self.win_h
        own_alpha = get_anim_opacity(mob)
        a = parent_alpha * own_alpha
        if a <= 0:
            return

        rot = get_anim_rotation(mob) + angle
        grow_rot = getattr(mob, '_grow_rot', 0.0)
        rot += grow_rot

        is_text = isinstance(mob, Text) or getattr(mob, '_is_text', False) or parent_is_text

        if isinstance(mob, Text) and hasattr(mob, 'submobjects') and mob.submobjects:
            # Tag all text characters so they're recognized as text even
            # when rendered through an intermediate Group (e.g. LaggedStartMap).
            # This prevents the _transforming stroke logic in _send_vmobject
            # from adding unwanted borders to text characters during animation.
            for sub in mob.submobjects:
                sub._is_text = True
            if getattr(mob, '_letter_alphas', None) is not None:
                self._send_text_write(mob, mob._letter_alphas, w, h, a)
            else:
                self._send_vmobject(mob, a, w, h, parent_offset, 0.0, is_text=is_text)
            return

        elif isinstance(mob, (VGroup, Group)):
            effective_alpha = parent_alpha * own_alpha
            if effective_alpha <= 0:
                return
            # Propagate VGroup stroke_width to descendants that have stroke
            # color but no own stroke_width (e.g. AnimatedBoundary's text chars)
            vg_stroke_w = 0
            try:
                vg_stroke_w = mob.get_stroke_width()
            except Exception:
                pass
            stroke_propagated = set()
            if vg_stroke_w > 0:
                for desc in mob.family_members_with_points():
                    try:
                        dsw = desc.stroke_width
                    except Exception:
                        continue
                    if dsw <= 0:
                        try:
                            sc = desc.get_stroke_color()
                            if sc is not None and sc != '#000000' and sc != '#000':
                                desc.stroke_width = vg_stroke_w
                                stroke_propagated.add(id(desc))
                        except Exception:
                            pass
            vgroup_progress = getattr(mob, '_vulkan_progress', 1.0)
            num_subs = len(list(mob)) if hasattr(mob, '__len__') else 0
            about = getattr(mob, '_rotation_about_point', None)
            is_3d = getattr(mob, '_rotation_3d', False)
            vgroup_center = np.array(mob.get_center(), dtype=float)
            try:
                pts = mob.get_points()
                original_center = np.array(pts.mean(axis=0) if len(pts) > 0 else mob.get_center(), dtype=float)
            except Exception:
                original_center = vgroup_center.copy()
            offset = vgroup_center - original_center
            if parent_offset is not None:
                offset = offset + parent_offset
            if is_3d:
                for sub in mob.family_members_with_points():
                    if hasattr(sub, 'points') and len(sub.points) > 0:
                        self._send_vmobject(sub, effective_alpha, w, h, offset, 0.0, is_text=is_text)
                return
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
                if about is not None:
                    sub_rot = rot
                else:
                    sub_rot = get_anim_rotation(sub)
                sub_is_text = isinstance(sub, Text) or getattr(sub, '_is_text', False)
                effective_sub_offset = None if sub_is_text else sub_offset
                self._send(sub, sub_rot, parent_alpha=effective_alpha, parent_offset=effective_sub_offset, parent_transforming=getattr(mob, '_transforming', False) or parent_transforming, parent_is_text=is_text)
            return

        if getattr(mob, '_transforming', False) or parent_transforming:
            self._send_vmobject(mob, a, w, h, None if is_text else parent_offset, 0.0, is_text=is_text)
            return

        screen_rot = -rot
        if isinstance(mob, Square):
            self._send_square(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Rectangle):
            self._send_rectangle(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Ellipse):
            self._send_ellipse(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Dot):
            self._send_dot(mob, a, w, h)
        elif isinstance(mob, Circle):
            self._send_circle(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Arrow):
            self._send_arrow(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, DashedLine):
            self._send_dashed_line(mob, a, w, h)
        elif isinstance(mob, Line):
            self._send_line(mob, a, w, h, screen_rot, parent_offset)
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
                    self._send_vmobject(mob, a, w, h, parent_offset, rot, is_text=is_text)
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

        self._skip_mob_ids = set()

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
            elif isinstance(anim, FadeTransform):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.target_mobject not in all_mobjects:
                    all_mobjects.append(anim.target_mobject)
                ghost = getattr(anim, '_ghost', None)
                if ghost is not None and ghost not in all_mobjects:
                    all_mobjects.append(ghost)
                is_manim_ft = type(anim).__module__.startswith('manim')
                if is_manim_ft and hasattr(anim.mobject, 'submobjects'):
                    for sub in anim.mobject.submobjects:
                        for existing in self.scene.mobjects:
                            if sub is existing:
                                if not hasattr(self, '_skip_mob_ids'):
                                    self._skip_mob_ids = set()
                                self._skip_mob_ids.add(id(existing))
                                break
            elif isinstance(anim, (Transform, _ManimTransform)):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                Transform._set_transforming(anim.mobject, True)
                if anim.replace_mobject_with_target_in_scene:
                    if anim.target_mobject not in all_mobjects:
                        all_mobjects.append(anim.target_mobject)
                    set_anim_opacity(anim.target_mobject, 0.0)
                if isinstance(anim, _ManimFadeTransform) and hasattr(anim.mobject, 'submobjects'):
                    for sub in anim.mobject.submobjects:
                        for existing in self.scene.mobjects:
                            if sub is existing:
                                self._skip_mob_ids.add(id(existing))
                                break
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
                        is_manim_ft = type(sub).__module__.startswith('manim')
                        if is_manim_ft and hasattr(sub.mobject, 'submobjects'):
                            for child in sub.mobject.submobjects:
                                for existing in self.scene.mobjects:
                                    if child is existing:
                                        self._skip_mob_ids.add(id(existing))
                                        break
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
                    else:
                        # Catch-all for ApplyMethod, etc. — track their mobjects
                        # so _is_descendant_of_scene can prevent double-rendering
                        if hasattr(sub, 'mobject') and sub.mobject is not None:
                            if sub.mobject not in all_mobjects:
                                all_mobjects.append(sub.mobject)
            else:
                from manim.animation.composition import AnimationGroup as _ManimAG
                if isinstance(anim, _ManimAG):
                    for sub in anim.animations:
                        if hasattr(sub, 'mobject') and sub.mobject is not None:
                            if sub.mobject not in all_mobjects:
                                all_mobjects.append(sub.mobject)
                            sub.mobject._transforming = True
                        if hasattr(sub, 'target_mobject') and sub.target_mobject is not None:
                            if not isinstance(sub, _ManimTransform) or type(sub) is _ManimTransform:
                                if sub.target_mobject not in all_mobjects:
                                    all_mobjects.append(sub.target_mobject)

        def _is_descendant_of_scene(mob):
            """Check if mob is already somewhere in the scene mobject tree."""
            def _search(node, target):
                if node is target:
                    return True
                for sub in getattr(node, 'submobjects', []):
                    if _search(sub, target):
                        return True
                return False

            for root in self.scene.mobjects:
                if root is mob:
                    continue
                if _search(root, mob):
                    return True
            return False

        for mob in all_mobjects:
            if _is_descendant_of_scene(mob):
                self._skip_mob_ids.add(id(mob))
                continue
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
                if isinstance(a, _ManimTransform):
                    a.mobject._transforming = True
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
            # Use the first submobject's center as pivot instead of the
            # VGroup aggregate center. This prevents vertical vibration when a
            # dot on the circumference shifts the VGroup center (rolling circle).
            if hasattr(vg, 'submobjects') and len(vg.submobjects) > 0:
                return np.array(vg.submobjects[0].get_center(), dtype=float)
            return vg.get_center()

        def _maybe_clear_prev_vg_rotation(anim):
            """After interpolate() resets mobject points, clear prev-rotation
            tracking so the VGroup delta loop reapplies the FULL accumulated
            rotation, not just the increment since last frame."""
            mob = getattr(anim, 'mobject', None)
            if mob is None:
                return
            for scene_mob in self.scene.mobjects:
                if isinstance(scene_mob, (VGroup, Group)):
                    # Check if anim.mobject is this VGroup or a descendant
                    if mob is scene_mob or (
                        hasattr(scene_mob, 'family_members_with_points') and
                        mob in scene_mob.family_members_with_points()
                    ):
                        _prev_vg_rotation.pop(id(scene_mob), None)

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
                    # interpolate() resets mobject points, erasing accumulated rotation.
                    # Clear _prev_vg_rotation so the delta loop reapplies the FULL rotation.
                    _maybe_clear_prev_vg_rotation(a)

                    if not getattr(a, 'finished', False) and elapsed >= a.run_time:
                        a.finish()
                        a.finished = True
                        if hasattr(a, 'clean_up_from_scene'):
                            a.clean_up_from_scene(self.scene)
                        mob = getattr(a, 'mobject', None)
                        if mob:
                            mob.resume_updating()
                            Transform._set_transforming(mob, False)
                            if hasattr(mob, '_was_transforming_text'):
                                del mob._was_transforming_text
                            target = getattr(a, 'target_mobject', None) or getattr(a, 'target', None)
                            if target and isinstance(mob, Text) and hasattr(mob, 'text') and hasattr(target, 'text'):
                                mob.text = target.text
                        if hasattr(a, 'animations'):
                            for sub in a.animations:
                                sub_mob = getattr(sub, 'mobject', None)
                                if sub_mob and hasattr(sub_mob, '_transforming'):
                                    sub_mob._transforming = False
                        if hasattr(a, '_anims'):
                            for sub in a._anims:
                                sub_mob = getattr(sub, 'mobject', None)
                                if sub_mob and hasattr(sub_mob, '_transforming'):
                                    sub_mob._transforming = False
                else:
                    a.interpolate(now)
                    if not a.finished and (now - a.start_time) >= a.run_time:
                        a.finish()
                if not getattr(a, 'finished', False):
                    all_done = False

            # Apply rotation delta per VGroup.
            for mob in self.scene.mobjects:
                if isinstance(mob, (VGroup, Group)):
                    if getattr(mob, '_rotation_about_point', None) is not None or getattr(mob, '_rotation_3d', False):
                        # Rotation is handled by the VGroup handler in _send().
                        continue
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
            self._capture_frame()

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

    def screenshot_printwindow(self, path):
        import ctypes.wintypes as wt
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        hwnd = user32.FindWindowW(None, "Manim Vulkan")
        if not hwnd:
            return False
        rc = wt.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rc))
        w, h = rc.right, rc.bottom
        hdc_window = user32.GetDC(hwnd)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_window, w, h)
        gdi32.SelectObject(hdc_mem, hbitmap)
        user32.PrintWindow(hwnd, hdc_mem, 2)
        bi = BITMAPINFOHEADER()
        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.biWidth = w
        bi.biHeight = -h
        bi.biPlanes = 1
        bi.biBitCount = 24
        bi.biCompression = 0
        row_bytes = ((w * 3 + 3) & ~3)
        buf = (ctypes.c_ubyte * (row_bytes * h))()
        gdi32.GetDIBits(hdc_mem, hbitmap, 0, h, buf, ctypes.byref(bi), 0)
        bfh = BITMAPFILEHEADER()
        bfh.bfType = 0x4D42
        bfh.bfOffBits = ctypes.sizeof(BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER)
        bfh.bfSize = bfh.bfOffBits + row_bytes * h
        path_b = path.encode('utf-8') if isinstance(path, str) else path
        hdr_buf = ctypes.string_at(ctypes.addressof(bfh), ctypes.sizeof(bfh)) + \
                  ctypes.string_at(ctypes.addressof(bi), ctypes.sizeof(bi))
        with open(path_b, 'wb') as f:
            f.write(hdr_buf)
            f.write(ctypes.string_at(ctypes.addressof(buf), len(buf)))
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(hwnd, hdc_window)
        return True

    def close(self):
        self.dll.Vulkan_Shutdown()

    def start_record(self, path="output.mp4", fps=60):
        if self._recording:
            return
        self._record_path = os.path.abspath(path)
        self._record_fps = fps
        self._record_dir = tempfile.mkdtemp(prefix="manim_record_")
        self._record_frame_idx = 0
        self._recording = True
        import threading
        self._record_stop_event = threading.Event()
        self._record_thread = threading.Thread(target=self._record_worker, daemon=True)
        self._record_thread.start()
        print(f"[Record] Recording to {self._record_path} at {fps} fps")

    def _record_worker(self):
        try:
            import mss as mss_mod
            sct = mss_mod.MSS()
        except Exception:
            sct = None
        bbox = self._get_screen_bbox()
        if not bbox:
            print("[Record] Cannot find window for recording.")
            return
        monitor = {'left': bbox[0], 'top': bbox[1], 'width': bbox[2]-bbox[0], 'height': bbox[3]-bbox[1]}
        interval = 1.0 / self._record_fps
        while not self._record_stop_event.is_set():
            t0 = time.time()
            try:
                path = os.path.join(self._record_dir, f"frame_{self._record_frame_idx:06d}.bmp")
                if sct:
                    shot = sct.grab(monitor)
                    from PIL import Image
                    img = Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')
                    img.save(path)
                else:
                    self.screenshot(path)
                self._record_frame_idx += 1
            except Exception:
                pass
            elapsed = time.time() - t0
            remaining = interval - elapsed
            if remaining > 0:
                self._record_stop_event.wait(remaining)
        self._record_thread = None

    def stop_record(self):
        if not self._recording:
            return
        self._record_stop_event.set()
        self._recording = False
        if self._record_thread:
            self._record_thread.join(timeout=2.0)
            self._record_thread = None
        frame_dir = self._record_dir
        output = self._record_path
        fps = self._record_fps
        total = self._record_frame_idx
        print(f"[Record] Captured {total} frames, encoding to {output} ...")
        if total == 0:
            print("[Record] No frames captured, aborting.")
            if os.path.isdir(frame_dir):
                shutil.rmtree(frame_dir, ignore_errors=True)
            return

        pattern = os.path.join(frame_dir, "frame_%06d.bmp")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "fast",
            output,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"[Record] Saved: {output}")
        except FileNotFoundError:
            print("[Record] ffmpeg not found. Install ffmpeg and add it to PATH.")
            print(f"[Record] Frames are in: {frame_dir}")
            return
        except subprocess.CalledProcessError as e:
            print(f"[Record] ffmpeg failed: {e.stderr.decode(errors='replace')}")
            print(f"[Record] Frames are in: {frame_dir}")
            return
        if os.path.isdir(frame_dir):
            shutil.rmtree(frame_dir, ignore_errors=True)

    def _get_screen_bbox(self):
        import ctypes.wintypes as wt
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, "Manim Vulkan")
        if not hwnd:
            return None
        rc = wt.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rc))
        pt = wt.POINT(0, 0)
        user32.ClientToScreen(hwnd, ctypes.byref(pt))
        return (pt.x, pt.y, pt.x + rc.right, pt.y + rc.bottom)

    def _capture_frame(self):
        pass
