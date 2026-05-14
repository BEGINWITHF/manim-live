import vulkan as vk
import numpy as np
from glfw import poll_events, window_should_close


class VulkanRenderer:
    def __init__(
        self,
        device,
        physical_device,
        graphics_queue,
        queue_family,
        swapchain,
        window
    ):
        self.device = device
        self.physical_device = physical_device
        self.graphics_queue = graphics_queue
        self.queue_family = queue_family
        self.swapchain = swapchain
        self.window = window

        self.pipeline = None
        self.vertex_buffer = None
        self.vertex_buffer_memory = None
        self.command_pool = None
        self.command_buffers = []
        self.image_available = None
        self.render_finished = None
        self.in_flight_fence = None

        self.init()

    def init(self):
        from renderer.vk_pipeline import VkPipeline
        self.pipeline = VkPipeline(
            self.device,
            self.swapchain.image_views,
            self.swapchain.image_format,
            self.swapchain.extent
        )
        self.create_vertex_buffer()
        self.create_command_pool()
        self.create_command_buffers()
        self.create_sync_objects()

    def create_vertex_buffer(self):
        vertices = np.array([
             0.0, -0.5,  1.0, 0.0, 0.0,
             0.5,  0.5,  0.0, 1.0, 0.0,
            -0.5,  0.5,  0.0, 0.0, 1.0
        ], dtype=np.float32)
        size = vertices.nbytes

        buffer_info = vk.VkBufferCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
            size=size,
            usage=vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
        )
        self.vertex_buffer = vk.vkCreateBuffer(self.device, buffer_info, None)

        mem_reqs = vk.vkGetBufferMemoryRequirements(self.device, self.vertex_buffer)
        mem_idx = self.find_memory_type(
            mem_reqs.memoryTypeBits,
            vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        )

        alloc_info = vk.VkMemoryAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
            allocationSize=mem_reqs.size,
            memoryTypeIndex=mem_idx
        )
        self.vertex_buffer_memory = vk.vkAllocateMemory(self.device, alloc_info, None)
        vk.vkBindBufferMemory(self.device, self.vertex_buffer, self.vertex_buffer_memory, 0)

        data = vk.vkMapMemory(self.device, self.vertex_buffer_memory, 0, size, 0)
        np.copyto(np.frombuffer(data, dtype=np.float32, count=15), vertices)
        vk.vkUnmapMemory(self.device, self.vertex_buffer_memory)

    def find_memory_type(self, type_filter, properties):
        mem_props = vk.vkGetPhysicalDeviceMemoryProperties(self.physical_device)
        for i in range(mem_props.memoryTypeCount):
            if (type_filter & (1 << i)) and \
               (mem_props.memoryTypes[i].propertyFlags & properties) == properties:
                return i
        raise RuntimeError("No suitable memory type found")

    def create_command_pool(self):
        info = vk.VkCommandPoolCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            queueFamilyIndex=self.queue_family
        )
        self.command_pool = vk.vkCreateCommandPool(self.device, info, None)

    def create_command_buffers(self):
        alloc_info = vk.VkCommandBufferAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool=self.command_pool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=len(self.pipeline.framebuffers)
        )
        self.command_buffers = vk.vkAllocateCommandBuffers(self.device, alloc_info)

        for i, cmd in enumerate(self.command_buffers):
            begin_info = vk.VkCommandBufferBeginInfo(
                sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO
            )
            vk.vkBeginCommandBuffer(cmd, begin_info)

            clear = vk.VkClearValue(color=[0.1,0.1,0.1,1.0])
            rp_begin = vk.VkRenderPassBeginInfo(
                sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
                renderPass=self.pipeline.render_pass,
                framebuffer=self.pipeline.framebuffers[i],
                renderArea=vk.VkRect2D([0,0], self.swapchain.extent),
                clearValueCount=1,
                pClearValues=[clear]
            )
            vk.vkCmdBeginRenderPass(cmd, rp_begin, vk.VK_SUBPASS_CONTENTS_INLINE)
            vk.vkCmdBindPipeline(cmd, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, self.pipeline.graphics_pipeline)
            vk.vkCmdBindVertexBuffers(cmd, 0, 1, [self.vertex_buffer], [0])
            vk.vkCmdDraw(cmd, 3, 1, 0, 0)
            vk.vkCmdEndRenderPass(cmd)
            vk.vkEndCommandBuffer(cmd)

    def create_sync_objects(self):
        semaphore_info = vk.VkSemaphoreCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO
        )
        fence_info = vk.VkFenceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_FENCE_CREATE_INFO,
            flags=vk.VK_FENCE_CREATE_SIGNALED_BIT
        )
        self.image_available = vk.vkCreateSemaphore(self.device, semaphore_info, None)
        self.render_finished = vk.vkCreateSemaphore(self.device, semaphore_info, None)
        self.in_flight_fence = vk.vkCreateFence(self.device, fence_info, None)

    def draw_frame(self):
        vk.vkWaitForFences(self.device, 1, [self.in_flight_fence], True, 10**18)
        vk.vkResetFences(self.device, 1, [self.in_flight_fence])

        image_idx = vk.vkAcquireNextImageKHR(
            self.device, self.swapchain.swapchain, 10**18,
            self.image_available, None
        )

        submit = vk.VkSubmitInfo(
            sType=vk.VK_STRUCTURE_TYPE_SUBMIT_INFO,
            waitSemaphoreCount=1,
            pWaitSemaphores=[self.image_available],
            pWaitDstStageMask=[vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT],
            commandBufferCount=1,
            pCommandBuffers=[self.command_buffers[image_idx]],
            signalSemaphoreCount=1,
            pSignalSemaphores=[self.render_finished]
        )
        vk.vkQueueSubmit(self.graphics_queue, 1, [submit], self.in_flight_fence)

        present = vk.VkPresentInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
            waitSemaphoreCount=1,
            pWaitSemaphores=[self.render_finished],
            swapchainCount=1,
            pSwapchains=[self.swapchain.swapchain],
            pImageIndices=[image_idx]
        )
        vk.vkQueuePresentKHR(self.graphics_queue, present)

    def run(self):
        while not window_should_close(self.window):
            poll_events()
            self.draw_frame()

    def cleanup(self):
        vk.vkDeviceWaitIdle(self.device)
        vk.vkDestroyBuffer(self.device, self.vertex_buffer, None)
        vk.vkFreeMemory(self.device, self.vertex_buffer_memory, None)
        self.pipeline.cleanup()
        vk.vkDestroyCommandPool(self.device, self.command_pool, None)
        vk.vkDestroySemaphore(self.device, self.image_available, None)
        vk.vkDestroySemaphore(self.device, self.render_finished, None)
        vk.vkDestroyFence(self.device, self.in_flight_fence, None)


class ManimVulkanBackend(VulkanRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw_mobject(self, mobject):
        pass

    def draw_animation_frame(self, alpha):
        pass

    def render_scene(self, scene):
        pass