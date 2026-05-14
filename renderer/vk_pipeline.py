import vulkan as vk
import os
from typing import List

class VkPipeline:
    def __init__(
        self,
        device: vk.VkDevice,
        swapchain_image_views: List[vk.VkImageView],
        swapchain_image_format: vk.VkFormat,
        swapchain_extent: vk.VkExtent2D
    ):
        self.device = device
        self.swapchain_image_views = swapchain_image_views
        self.swapchain_image_format = swapchain_image_format
        self.extent = swapchain_extent

        self.render_pass = None
        self.framebuffers = []
        self.pipeline_layout = None
        self.graphics_pipeline = None
        self.vert_shader_module = None
        self.frag_shader_module = None

        self.create_render_pass()
        self.create_framebuffers()
        self.create_shader_modules()
        self.create_graphics_pipeline()

    def create_render_pass(self):
        color_attachment = vk.VkAttachmentDescription(
            format=self.swapchain_image_format,
            samples=vk.VK_SAMPLE_COUNT_1_BIT,
            loadOp=vk.VK_ATTACHMENT_LOAD_OP_CLEAR,
            storeOp=vk.VK_ATTACHMENT_STORE_OP_STORE,
            stencilLoadOp=vk.VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp=vk.VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout=vk.VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
        )

        color_ref = vk.VkAttachmentReference(
            attachment=0,
            layout=vk.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
        )

        subpass = vk.VkSubpassDescription(
            pipelineBindPoint=vk.VK_PIPELINE_BIND_POINT_GRAPHICS,
            colorAttachmentCount=1,
            pColorAttachments=[color_ref]
        )

        render_pass_info = vk.VkRenderPassCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
            attachmentCount=1,
            pAttachments=[color_attachment],
            subpassCount=1,
            pSubpasses=[subpass]
        )
        self.render_pass = vk.vkCreateRenderPass(self.device, render_pass_info, None)

    def create_framebuffers(self):
        self.framebuffers = []
        for view in self.swapchain_image_views:
            info = vk.VkFramebufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                renderPass=self.render_pass,
                attachmentCount=1,
                pAttachments=[view],
                width=self.extent.width,
                height=self.extent.height,
                layers=1
            )
            self.framebuffers.append(vk.vkCreateFramebuffer(self.device, info, None))

    def read_shader(self, name: str) -> bytes:
        shader_dir = os.path.join(os.path.dirname(__file__), "shaders")
        with open(os.path.join(shader_dir, name), "rb") as f:
            return f.read()

    def create_shader_modules(self):
        vert_code = self.read_shader("vert.spv")
        frag_code = self.read_shader("frag.spv")

        self.vert_shader_module = vk.vkCreateShaderModule(
            self.device,
            vk.VkShaderModuleCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=len(vert_code),
                pCode=vert_code
            ),
            None
        )

        self.frag_shader_module = vk.vkCreateShaderModule(
            self.device,
            vk.VkShaderModuleCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=len(frag_code),
                pCode=frag_code
            ),
            None
        )

    def create_graphics_pipeline(self):
        shader_stages = [
            vk.VkPipelineShaderStageCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                stage=vk.VK_SHADER_STAGE_VERTEX_BIT,
                module=self.vert_shader_module,
                pName="main"
            ),
            vk.VkPipelineShaderStageCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                stage=vk.VK_SHADER_STAGE_FRAGMENT_BIT,
                module=self.frag_shader_module,
                pName="main"
            )
        ]

        binding = vk.VkVertexInputBindingDescription(
            binding=0, stride=20, inputRate=vk.VK_VERTEX_INPUT_RATE_VERTEX
        )
        attrs = [
            vk.VkVertexInputAttributeDescription(
                location=0, binding=0, format=vk.VK_FORMAT_R32G32_SFLOAT, offset=0
            ),
            vk.VkVertexInputAttributeDescription(
                location=1, binding=0, format=vk.VK_FORMAT_R32G32B32_SFLOAT, offset=8
            )
        ]
        vertex_input = vk.VkPipelineVertexInputStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
            vertexBindingDescriptionCount=1,
            pVertexBindingDescriptions=[binding],
            vertexAttributeDescriptionCount=2,
            pVertexAttributeDescriptions=attrs
        )

        input_assembly = vk.VkPipelineInputAssemblyStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
            topology=vk.VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST
        )

        viewport = vk.VkViewport(
            0, 0, self.extent.width, self.extent.height, 0.0, 1.0
        )
        scissor = vk.VkRect2D([0,0], self.extent)
        viewport_state = vk.VkPipelineViewportStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
            viewportCount=1, pViewports=[viewport],
            scissorCount=1, pScissors=[scissor]
        )

        rasterizer = vk.VkPipelineRasterizationStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
            polygonMode=vk.VK_POLYGON_MODE_FILL,
            lineWidth=1.0,
            cullMode=vk.VK_CULL_MODE_NONE
        )

        multisample = vk.VkPipelineMultisampleStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
            rasterizationSamples=vk.VK_SAMPLE_COUNT_1_BIT
        )

        blend_attach = vk.VkPipelineColorBlendAttachmentState(
            colorWriteMask=0xF, blendEnable=False
        )
        color_blend = vk.VkPipelineColorBlendStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
            attachmentCount=1, pAttachments=[blend_attach]
        )

        layout_info = vk.VkPipelineLayoutCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO
        )
        self.pipeline_layout = vk.vkCreatePipelineLayout(self.device, layout_info, None)

        pipeline_info = vk.VkGraphicsPipelineCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
            stageCount=2,
            pStages=shader_stages,
            pVertexInputState=vertex_input,
            pInputAssemblyState=input_assembly,
            pViewportState=viewport_state,
            pRasterizationState=rasterizer,
            pMultisampleState=multisample,
            pColorBlendState=color_blend,
            layout=self.pipeline_layout,
            renderPass=self.render_pass,
            subpass=0
        )
        self.graphics_pipeline = vk.vkCreateGraphicsPipelines(
            self.device, None, 1, [pipeline_info], None
        )[0]

    def cleanup(self):
        vk.vkDestroyPipeline(self.device, self.graphics_pipeline, None)
        vk.vkDestroyPipelineLayout(self.device, self.pipeline_layout, None)
        for fb in self.framebuffers:
            vk.vkDestroyFramebuffer(self.device, fb, None)
        vk.vkDestroyRenderPass(self.device, self.render_pass, None)
        vk.vkDestroyShaderModule(self.device, self.vert_shader_module, None)
        vk.vkDestroyShaderModule(self.device, self.frag_shader_module, None)