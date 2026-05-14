from manim import config, Scene
from renderer.vulkan_renderer import VulkanRenderer
from .mobject_converter import convert_mobject

class VulkanManimHook:
    def __init__(self):
        self.vk_renderer = VulkanRenderer(
            width=config.pixel_width,
            height=config.pixel_height
        )
        self._patch_manim_renderer()

    def _patch_manim_renderer(self):
        original_render_frame = Scene.render_frame
        
        def new_render_frame(scene, frame):
            self.vk_renderer.begin_frame()
            
            for mob in scene.mobjects:
                vertices, color = convert_mobject(mob)
                self.vk_renderer.draw_shape(vertices, color)
            
            self.vk_renderer.end_frame()
            scene.camera.get_frame = lambda: self.vk_renderer.get_frame_image()
            
            return original_render_frame(scene, frame)

        Scene.render_frame = new_render_frame


hook = VulkanManimHook()