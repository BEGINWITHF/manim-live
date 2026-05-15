from manim import *
import time
from adapter.manim_bridge import *

class FullRenderScene(Scene):
    def construct(self):
        circle = Circle(radius=1.8, color=BLUE)
        line = Line(LEFT * 3, RIGHT * 3, color=RED)
        rect = Rectangle(width=3, height=2, color=BLUE)

        circle.shift(UP * 0.5)
        rect.shift(DOWN * 1)

        self.add(circle, line, rect)
        start_time = time.time()

        while tick():
            clear(12, 18, 35)

            draw_circle(circle)
            draw_line(line)
            draw_rect(rect)
            draw_text("Manim Vulkan Render Running", 50, 40, 28)
            draw_text("All Systems Operational", 50, 75, 20)

            t = time.time() - start_time
            y = np.sin(t) * 1.5
            circle.move_to(np.array([0, y, 0]))
            rect.rotate(0.01)

            self.update_mobjects(self.mobjects)
            time.sleep(0.016)