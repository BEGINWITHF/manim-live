import vulkan as vk
from typing import List, Optional, Tuple

class VkSwapchain:
    def __init__(
        self,
        instance: vk.VkInstance,
        physical_device: vk.VkPhysicalDevice,
        device: vk.VkDevice,
        surface: vk.VkSurfaceKHR,
        queue_family_index: int,
        desired_extent: Tuple[int, int]
    ):
        self.instance = instance
        self.physical_device = physical_device
        self.device = device
        self.surface = surface
        self.queue_family_index = queue_family_index
        self.desired_extent = desired_extent

        self.swapchain: Optional[vk.VkSwapchainKHR] = None
        self.images: List[vk.VkImage] = []
        self.image_format: Optional[vk.VkFormat] = None
        self.extent: Optional[vk.VkExtent2D] = None
        self.image_views: List[vk.VkImageView] = []

        self.create_swapchain()
        self.create_image_views()

    def _choose_surface_format(self, available_formats: List[vk.VkSurfaceFormatKHR]) -> vk.VkSurfaceFormatKHR:
        for fmt in available_formats:
            if (fmt.format == vk.VK_FORMAT_B8G8R8A8_UNORM and
                fmt.colorSpace == vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
                return fmt
        return available_formats[0]

    def _choose_present_mode(self, available_modes: List[int]) -> int:
        if vk.VK_PRESENT_MODE_MAILBOX_KHR in available_modes:
            return vk.VK_PRESENT_MODE_MAILBOX_KHR
        return vk.VK_PRESENT_MODE_FIFO_KHR

    def _choose_extent(self, capabilities: vk.VkSurfaceCapabilitiesKHR) -> vk.VkExtent2D:
        if capabilities.currentExtent.width != 0xFFFFFFFF:
            return capabilities.currentExtent
        else:
            return vk.VkExtent2D(
                width=min(max(self.desired_extent[0], capabilities.minImageExtent.width), capabilities.maxImageExtent.width),
                height=min(max(self.desired_extent[1], capabilities.minImageExtent.height), capabilities.maxImageExtent.height)
            )

    def create_swapchain(self) -> None:
        capabilities = vk.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(self.physical_device, self.surface)
        available_formats = vk.vkGetPhysicalDeviceSurfaceFormatsKHR(self.physical_device, self.surface)
        available_modes = vk.vkGetPhysicalDevicePresentModesKHR(self.physical_device, self.surface)

        surface_format = self._choose_surface_format(available_formats)
        present_mode = self._choose_present_mode(available_modes)
        extent = self._choose_extent(capabilities)

        image_count = capabilities.minImageCount + 1
        if capabilities.maxImageCount > 0 and image_count > capabilities.maxImageCount:
            image_count = capabilities.maxImageCount

        create_info = vk.VkSwapchainCreateInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            surface=self.surface,
            minImageCount=image_count,
            imageFormat=surface_format.format,
            imageColorSpace=surface_format.colorSpace,
            imageExtent=extent,
            imageArrayLayers=1,
            imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            queueFamilyIndexCount=1,
            pQueueFamilyIndices=[self.queue_family_index],
            preTransform=capabilities.currentTransform,
            compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=present_mode,
            clipped=vk.VK_TRUE,
            oldSwapchain=None
        )

        self.swapchain = vk.vkCreateSwapchainKHR(self.device, create_info, None)
        self.images = vk.vkGetSwapchainImagesKHR(self.device, self.swapchain)
        self.image_format = surface_format.format
        self.extent = extent

    def create_image_views(self) -> None:
        self.image_views.clear()
        for img in self.images:
            create_info = vk.VkImageViewCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                image=img,
                viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                format=self.image_format,
                components=vk.VkComponentMapping(
                    r=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                    g=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                    b=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                    a=vk.VK_COMPONENT_SWIZZLE_IDENTITY
                ),
                subresourceRange=vk.VkImageSubresourceRange(
                    aspectMask=vk.VK_IMAGE_ASPECT_COLOR_BIT,
                    baseMipLevel=0,
                    levelCount=1,
                    baseArrayLayer=0,
                    layerCount=1
                )
            )
            self.image_views.append(vk.vkCreateImageView(self.device, create_info, None))

    def cleanup(self) -> None:
        for view in self.image_views:
            vk.vkDestroyImageView(self.device, view, None)
        vk.vkDestroySwapchainKHR(self.device, self.swapchain, None)