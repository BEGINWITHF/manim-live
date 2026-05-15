def manim_to_ndc(manim_x: float, manim_y: float):
    nx = manim_x / 4.0
    ny = -manim_y / 3.0
    return nx, ny