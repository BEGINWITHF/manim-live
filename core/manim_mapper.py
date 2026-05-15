def manim_to_vk(manim_x: float, manim_y: float, screen_w=800, screen_h=600):
    """Convert Manim world coordinates -> Vulkan NDC (-1 to 1)"""
    nx = manim_x / 4.0
    ny = -manim_y / 3.0
    return nx, ny