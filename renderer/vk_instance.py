import vulkan as vk

class VulkanInstance:
    def __init__(self):
        self.instance = None
        self.physical_device = None
        self.device = None
        self.graphics_queue_family = None
        self.queue = None

        self._create_instance()
        self._pick_physical_device()
        self._create_logical_device()

    def _create_instance(self):
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="ManimVulkan",
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName="ManimVulkanEngine",
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_API_VERSION_1_0,
        )

        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )

        self.instance = vk.vkCreateInstance(create_info, None)

    def _pick_physical_device(self):
        physical_devices = vk.vkEnumeratePhysicalDevices(self.instance)
        if not physical_devices:
            raise RuntimeError("No Vulkan physical devices found.")

        for dev in physical_devices:
            queue_props = vk.vkGetPhysicalDeviceQueueFamilyProperties(dev)
            for i, q in enumerate(queue_props):
                if q.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                    self.graphics_queue_family = i
                    self.physical_device = dev
                    return
        raise RuntimeError("No graphics queue family found.")

    def _create_logical_device(self):
        queue_priorities = [1.0]
        queue_info = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=self.graphics_queue_family,
            queueCount=1,
            pQueuePriorities=queue_priorities,
        )

        device_info = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[queue_info],
        )

        self.device = vk.vkCreateDevice(self.physical_device, device_info, None)
        self.queue = vk.vkGetDeviceQueue(self.device, self.graphics_queue_family, 0)

    def destroy(self):
        vk.vkDestroyDevice(self.device, None)
        vk.vkDestroyInstance(self.instance, None)