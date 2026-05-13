import glfw
import vulkan as vk
from renderer.vk_instance import VulkanInstance

class GLFWWindow:
    def __init__(self, width=800, height=600, title="Manim Vulkan"):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.surface = None
        self.vk_instance = VulkanInstance()

        self._init_glfw()
        self._create_window()

    def _init_glfw(self):
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW.")
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)

    def _create_window(self):
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window.")

    def should_close(self):
        return glfw.window_should_close(self.window)

    def poll_events(self):
        glfw.poll_events()

    def destroy(self):
        glfw.destroy_window(self.window)
        glfw.terminate()