import vulkan as vk

class VulkanSwapchain:
    def __init__(self, instance, physical_device, device, surface, width, height):
        self.instance = instance
        self.physical_device = physical_device
        self.device = device
        self.surface = surface
        self.width = width
        self.height = height

        self.swapchain = None
        self.image_views = []

    def cleanup(self):
        for view in self.image_views:
            vk.vkDestroyImageView(self.device, view, None)
        vk.vkDestroySwapchainKHR(self.device, self.swapchain, None)