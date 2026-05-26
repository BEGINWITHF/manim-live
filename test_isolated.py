import sys
import importlib.util

spec = importlib.util.spec_from_file_location(
    "vulkan_bind_test", 
    r"C:\Users\10288\Desktop\manim-vulkan-7c58da2527990ca6d5930c96642369b1e929a632\core\vulkan_bind.py"
)
mod = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(mod)
    print("✅ SUCCEED")
    print(f"   VulkanRender = {mod.VulkanRender}")
except Exception as e:
    import traceback
    print("❌ FAILED: ")
    traceback.print_exc()