from manim import *
from core.vulkan_bind import VulkanRender

def manim_to_ndc(x, y):
    return x / 4.0, -y / 3.0

class VulkanLiveScene(Scene):
    def construct(self):
        render = VulkanRender(800, 600)
        angle = 0

        sq = Square(0.4).shift(LEFT*2)
        cr = Circle(0.2).shift(RIGHT*2)
        line = Line(LEFT*3, RIGHT*3)
        arrow = Arrow(LEFT+DOWN, RIGHT+DOWN)
        
        self.add(sq, cr, line, arrow)

        while render.tick():
            angle += 0.05
            sq.set_angle(angle)

            # 正方形
            cx, cy, _ = sq.get_center()
            x, y = manim_to_ndc(cx, cy)
            render.add_rect(x, y, 0.4/4, 0.4/4, angle, 255,120,80)

            # 圆形
            cx, cy, _ = cr.get_center()
            x, y = manim_to_ndc(cx, cy)
            render.add_circle(x, y, 0.2/4, 80,180,255)

            # 直线
            s, e = line.get_start(), line.get_end()
            x1,y1 = manim_to_ndc(s[0],s[1])
            x2,y2 = manim_to_ndc(e[0],e[1])
            render.add_line(x1,y1,x2,y2,3,200,200,200)

            # 箭头
            s,e = arrow.get_start(), arrow.get_end()
            x1,y1 = manim_to_ndc(s[0],s[1])
            x2,y2 = manim_to_ndc(e[0],e[1])
            render.add_arrow(x1,y1,x2,y2,3,255,220,80)

            # ✅ 文字渲染测试
            render.add_text("Manim Vulkan Renderer", 0, 0, 24, 255,255,255)
            render.add_text("Hello, World!", 0, 1, 18, 100,200,255)

        render.close()