import math


def manim_to_screen(x, y, w=800, h=600):
    frame_width = w * 8.0 / h
    sx = w / frame_width
    sy = h / 8.0
    cx, cy = w / 2.0, h / 2.0
    return float(cx + x * sx), float(cy - y * sy)


def rotate_point(x, y, cx, cy, angle):
    if angle == 0:
        return x, y
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dx = x - cx
    dy = y - cy
    nx = dx * cos_a - dy * sin_a + cx
    ny = dx * sin_a + dy * cos_a + cy
    return nx, ny


def get_fill_rgb(mob, alpha=1.0):
    try:
        rgbas = mob.get_fill_rgbas()
        if len(rgbas) > 0:
            r, g, b, a = rgbas[0]
            fo = float(a)
            return int(r * 255 * alpha * fo), int(g * 255 * alpha * fo), int(b * 255 * alpha * fo)
    except Exception:
        pass
    try:
        rgbas = mob.get_stroke_rgbas()
        if len(rgbas) > 0:
            r, g, b, a = rgbas[0]
            return int(r * 255 * alpha), int(g * 255 * alpha), int(b * 255 * alpha)
    except Exception:
        pass
    return int(255 * alpha), int(255 * alpha), int(255 * alpha)


def get_fill_rgb_raw(mob):
    try:
        rgbas = mob.get_fill_rgbas()
        if len(rgbas) > 0:
            r, g, b, _ = rgbas[0]
            return int(r * 255), int(g * 255), int(b * 255)
    except Exception:
        pass
    try:
        rgbas = mob.get_stroke_rgbas()
        if len(rgbas) > 0:
            r, g, b, _ = rgbas[0]
            return int(r * 255), int(g * 255), int(b * 255)
    except Exception:
        pass
    return 255, 255, 255


def get_stroke_rgb(mob):
    try:
        rgbas = mob.get_stroke_rgbas()
        if len(rgbas) > 0:
            r, g, b, a = rgbas[0]
            return int(r * 255), int(g * 255), int(b * 255)
    except Exception:
        pass
    return 255, 255, 255


def get_stroke_w(mob):
    try:
        sw = mob.get_stroke_width()
        if isinstance(sw, (int, float)):
            return float(sw)
        elif hasattr(sw, '__len__') and len(sw) > 0:
            return float(sw[0])
    except Exception:
        pass
    return 0.0
