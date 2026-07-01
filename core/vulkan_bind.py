import ctypes
import os
import math



def manim_to_screen(x, y, w=800, h=600, scale=200):

    cx, cy = w / 2.0, h / 2.0

    sx = cx + x * scale

    sy = cy - y * scale

    return float(sx), float(sy)



class VulkanRender:

    def __init__(self, w=800, h=600):

        self.win_w = w

        self.win_h = h

        self.frame_count = 0



        base_dir = os.path.dirname(os.path.abspath(__file__))

        dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dll"))

        if not os.path.exists(dll_path):

            dll_path = os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dll"))

        if not os.path.exists(dll_path):

            raise FileNotFoundError(f"找不到 vulkan_core.dll")



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

            ctypes.c_int, ctypes.c_int, ctypes.c_int

        ]



        self.dll.AddCircle.restype = None

        self.dll.AddCircle.argtypes = [

            ctypes.c_float, ctypes.c_float, ctypes.c_float,

            ctypes.c_int, ctypes.c_int, ctypes.c_int,

            ctypes.c_int, ctypes.c_int, ctypes.c_int,

            ctypes.c_float,

            ctypes.c_float

        ]



        self.dll.AddLine.restype = None

        self.dll.AddLine.argtypes = [

            ctypes.c_float, ctypes.c_float,

            ctypes.c_float, ctypes.c_float,

            ctypes.c_int, ctypes.c_int,

            ctypes.c_int, ctypes.c_int

        ]

        self.dll.AddText.restype = None

        self.dll.AddText.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_char_p, ctypes.c_char_p
        ]



        if self.dll.Vulkan_Init(w, h) != 1:

            raise RuntimeError("Vulkan_Init 失败")



    def sync(self, scene, angle=0.0):
        self.dll.ClearShapes()
        count = 0
        for mob in scene.mobjects:
            self.draw(mob, angle)
            count += 1

    def draw(self, mob, angle=0.0):
        # Render TextObject
        if hasattr(mob, 'text') and hasattr(mob, 'x'):
            self.dll.AddText(
                mob.x, mob.y,
                mob.r, mob.g, mob.b,
                mob.font_size,
                mob.opacity,
                mob.text,
                mob.font_name
            )

    def _get_color_rgb(self, mob):
        return 255, 255, 255



    def tick(self):

        self.frame_count += 1

        return self.dll.Vulkan_Tick() != 0



    def close(self):
        self.dll.Vulkan_Shutdown()

    def play(self, *animations):
        for anim in animations:
            anim.apply(self)
        self.sync(self.scene)

    def add(self, mob):
        self.scene.add(mob)


# Animation classes
class Animation:
    def __init__(self, mobject, run_time=1.0, rate_func=None, lag_ratio=0.0):
        self.mobject = mobject
        self.run_time = run_time
        self.rate_func = rate_func
        self.lag_ratio = lag_ratio
        self.frame_count = 0

    def apply(self, render):
        pass


class Create(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=None, lag_ratio=0.0):
        super().__init__(mobject, run_time, rate_func, lag_ratio)
        self.original_opacity = 1.0

    def apply(self, render):
        set_anim_opacity(self.mobject, 1.0)
        render.sync(render.scene)


class Write(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=None, lag_ratio=0.0):
        super().__init__(mobject, run_time, rate_func, lag_ratio)

    def apply(self, render):
        if isinstance(self.mobject, Text):
            total_chars = len(self.mobject.text)
            frames = int(self.run_time * 60)
            for i in range(frames):
                progress = i / frames
                set_anim_opacity(self.mobject, progress)
                render.sync(render.scene)
                render.tick()
        else:
            set_anim_opacity(self.mobject, 1.0)
            render.sync(render.scene)


class Unwrite(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=None, lag_ratio=0.0):
        super().__init__(mobject, run_time, rate_func, lag_ratio)

    def apply(self, render):
        set_anim_opacity(self.mobject, 0.0)
        render.sync(render.scene)


class Succession(Animation):
    def __init__(self, *animations):
        super().__init__(None)
        self.animations = animations

    def apply(self, render):
        for anim in self.animations:
            anim.apply(render)


class Wait(Animation):
    def __init__(self, duration=1.0):
        super().__init__(None, run_time=duration)

    def apply(self, render):
        frames = int(self.run_time * 60)
        for _ in range(frames):
            render.tick()


class Add(Animation):
    def __init__(self, mobject):
        super().__init__(mobject, run_time=0.0)

    def apply(self, render):
        set_anim_opacity(self.mobject, 1.0)
        render.scene.add(self.mobject)
        render.sync(render.scene)


class FadeIn(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)

    def apply(self, render):
        frames = int(self.run_time * 60)
        for i in range(frames):
            progress = i / frames
            set_anim_opacity(self.mobject, progress)
            render.sync(render.scene)
            render.tick()


class FadeOut(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)

    def apply(self, render):
        frames = int(self.run_time * 60)
        for i in range(frames):
            progress = 1.0 - (i / frames)
            set_anim_opacity(self.mobject, progress)
            render.sync(render.scene)
            render.tick()


class FadeTransform(Animation):
    def __init__(self, mobject, target_mobject, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)
        self.target_mobject = target_mobject

    def apply(self, render):
        frames = int(self.run_time * 60)
        for i in range(frames):
            progress = i / frames
            set_anim_opacity(self.mobject, 1.0 - progress)
            set_anim_opacity(self.target_mobject, progress)
            render.sync(render.scene)
            render.tick()


class Rotating(Animation):
    def __init__(self, mobject, angle=math.pi, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)
        self.angle = angle

    def apply(self, render):
        frames = int(self.run_time * 60)
        for i in range(frames):
            progress = i / frames
            current_angle = self.angle * progress
            self.mobject.rotate(current_angle)
            render.sync(render.scene)
            render.tick()


class Rotate(Animation):
    def __init__(self, mobject, angle=math.pi, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)
        self.angle = angle

    def apply(self, render):
        self.mobject.rotate(self.angle)
        render.sync(render.scene)


class Transform(Animation):
    def __init__(self, mobject, target_mobject, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)
        self.target_mobject = target_mobject

    def apply(self, render):
        frames = int(self.run_time * 60)
        for i in range(frames):
            progress = i / frames
            set_anim_opacity(self.mobject, 1.0 - progress)
            set_anim_opacity(self.target_mobject, progress)
            render.sync(render.scene)
            render.tick()


class TransformMatchingShapes(Animation):
    def __init__(self, mobject, target_mobject, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)
        self.target_mobject = target_mobject

    def apply(self, render):
        frames = int(self.run_time * 60)
        for i in range(frames):
            progress = i / frames
            set_anim_opacity(self.mobject, 1.0 - progress)
            set_anim_opacity(self.target_mobject, progress)
            render.sync(render.scene)
            render.tick()


class TransformMatchingTex(Animation):
    def __init__(self, mobject, target_mobject, run_time=1.0, rate_func=None):
        super().__init__(mobject, run_time, rate_func)
        self.target_mobject = target_mobject

    def apply(self, render):
        frames = int(self.run_time * 60)
        for i in range(frames):
            progress = i / frames
            set_anim_opacity(self.mobject, 1.0 - progress)
            set_anim_opacity(self.target_mobject, progress)
            render.sync(render.scene)
            render.tick()


# Rate functions
def _smooth(t):
    return t * t * (3 - 2 * t)


def _linear(t):
    return t


def _rush_into(t):
    return t * t


def _rush_from(t):
    return 1 - (1 - t) * (1 - t)


def _there_and_back(t):
    if t < 0.5:
        return _smooth(t * 2)
    else:
        return _smooth(2 - t * 2)


def _slow_into(t):
    return t * (2 - t)


def _double_smooth(t):
    if t < 0.5:
        return 0.5 * _smooth(t * 2)
    else:
        return 0.5 + 0.5 * _smooth(t * 2 - 1)


def _lingering(t):
    return t


def _wiggle(t):
    return t + 0.1 * (0.5 - abs(t - 0.5))


def _exponential_decay(t):
    return 1 - (1 - t) ** 2


def set_anim_opacity(mobject, opacity):
    try:
        if hasattr(mobject, 'set_fill'):
            mobject.set_fill(opacity=opacity)
        if hasattr(mobject, 'set_stroke'):
            mobject.set_stroke(opacity=opacity)
    except:
        pass