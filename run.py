from adapter.manim_bridge import init_window
from scenes.test_scene import FullRenderScene

def main():
    print("Starting Manim + Vulkan Renderer...")
    init_window()
    scene = FullRenderScene()
    scene.construct()

if __name__ == "__main__":
    main()