from window.glfw_window import GLFWWindow

class VulkanRenderer:
    def __init__(self):
        self.window = GLFWWindow()

    def run(self):
        while not self.window.should_close():
            self.window.poll_events()

    def cleanup(self):
        self.window.destroy()

if __name__ == "__main__":
    app = None
    try:
        app = VulkanRenderer()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if app is not None:
            app.cleanup()