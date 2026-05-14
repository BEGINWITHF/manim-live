import numpy as np
from manim import VMobject

def convert_mobject(mob: VMobject):
    points = mob.get_points()
    vertices = triangulate_path(points)
    color = mob.get_color().to_rgba()
    return vertices, color

def triangulate_path(points):
    return np.array(points, dtype=np.float32)