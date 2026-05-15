from manim import *
from core.vulkan_bind import VulkanRender

def manim_to_ndc(x, y):
    return x / 4.0, -y / 3.0

class VulkanLiveScene(Scene):
    def construct(self):
        render = VulkanRender(800, 600)

        squares = []
        angles = []
        
        for i in range(50):
            angle = i * 0.1
            pos = LEFT * (i - 25) * 0.2
            sq = Square(side_length=0.3).move_to(pos)
            squares.append(sq)
            angles.append(angle)
            self.add(sq)

        while render.tick():
            for i in range(50):
                angles[i] += 0.05 + i * 0.001
                squares[i].set_angle(angles[i])
                x, y = manim_to_ndc(*squares[i].get_center()[:2])
                render.add_rect(x, y, 0.3/4, 0.3/4, angles[i], 100+i*3, 200-i*2, 255-i)

        render.close()