import glfw
import vulkan as vk
import sys
import ctypes

def log(msg):
    print(f"[LOG] {msg}")
    sys.stdout.flush()

class GLFWWindow:
    def __init__(self, width=800, height=600, title="Vulkan"):
        self.width = width
        self.height = height
        self.title = title

        self.window = None
        self.instance = None
        self.surface = None
        self.physical_device = None
        self.device = None
        self.graphics_queue = None
        self.graphics_family = -1

        try:
            self.init_glfw()
            self.init_vulkan()
            self.main_loop()
        except Exception as e:
            log(f"[FATAL] {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def init_glfw(self):
        glfw.init()
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        log("✅ GLFW window created")

    def init_vulkan(self):
        exts = glfw.get_required_instance_extensions()
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="ManimVulkan",
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_API_VERSION_1_0
        )
        instance_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
            enabledExtensionCount=len(exts),
            ppEnabledExtensionNames=exts
        )
        self.instance = vk.vkCreateInstance(instance_info, None)
        log("✅ Vulkan instance created")

        surface_handle = ctypes.c_uint64(0)
        glfw.create_window_surface(self.instance, self.window, None, ctypes.byref(surface_handle))
        self.surface = surface_handle.value
        log("✅ Surface created")

        physical_devices = vk.vkEnumeratePhysicalDevices(self.instance)
        self.physical_device = physical_devices[0]
        props = vk.vkGetPhysicalDeviceProperties(self.physical_device)
        log(f"✅ Using GPU: {props.deviceName}")

        families = vk.vkGetPhysicalDeviceQueueFamilyProperties(self.physical_device)
        for i, family in enumerate(families):
            if family.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                self.graphics_family = i
                break

        queue_priorities = [1.0]
        queue_info = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=self.graphics_family,
            queueCount=1,
            pQueuePriorities=queue_priorities
        )
        device_exts = [vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
        device_info = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[queue_info],
            enabledExtensionCount=len(device_exts),
            ppEnabledExtensionNames=device_exts
        )
        self.device = vk.vkCreateDevice(self.physical_device, device_info, None)
        self.graphics_queue = vk.vkGetDeviceQueue(self.device, self.graphics_family, 0)
        log("✅ Logical device created")

    def main_loop(self):
        log("✅ Render loop running. Close window to exit.")
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

    def cleanup(self):
        if self.device:
            vk.vkDestroyDevice(self.device, None)
        if self.instance:
            vk.vkDestroyInstance(self.instance, None)
        if self.window:
            glfw.destroy_window(self.window)
        glfw.terminate()
        log("✅ Cleanup complete")