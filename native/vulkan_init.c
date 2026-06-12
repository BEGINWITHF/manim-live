#include "vulkan_core.h"

#define VK_CHECK(call) do { \
    VkResult _result = (call); \
    if (_result != VK_SUCCESS) { \
        fprintf(stderr, "[Vulkan ERROR] %s returned %d\n", #call, _result); \
    } \
} while(0)



VkInstance g_inst = VK_NULL_HANDLE;

VkPhysicalDevice g_phys_dev = VK_NULL_HANDLE;

VkDevice g_dev = VK_NULL_HANDLE;

VkQueue g_gfx_queue = VK_NULL_HANDLE;

VkQueue g_present_queue = VK_NULL_HANDLE;

VkSurfaceKHR g_surface = VK_NULL_HANDLE;

VkSwapchainKHR g_swapchain = VK_NULL_HANDLE;

VkFormat g_swapchain_fmt;

VkExtent2D g_swapchain_ext;

VkImage *g_swapchain_imgs = NULL;

VkImageView *g_swapchain_img_views = NULL;

uint32_t g_swapchain_img_count = 0;

VkRenderPass g_render_pass = VK_NULL_HANDLE;

VkFramebuffer *g_framebuffers = NULL;

VkPipelineLayout g_pipeline_layout = VK_NULL_HANDLE;

VkPipeline g_pipeline = VK_NULL_HANDLE;

VkCommandPool g_cmd_pool = VK_NULL_HANDLE;

VkCommandBuffer *g_cmd_bufs = NULL;

uint32_t g_cmd_buf_count = 0;

VkSemaphore *g_img_avail_sems = NULL;

VkSemaphore *g_render_done_sems = NULL;

VkFence *g_in_flight_fences = NULL;

VkBuffer g_vert_buf = VK_NULL_HANDLE;

VkDeviceMemory g_vert_buf_mem = VK_NULL_HANDLE;

VkDeviceSize g_vert_buf_size = 0;

HWND g_hwnd = NULL;

HINSTANCE g_hinst = NULL;

bool g_is_ready = false;

uint32_t g_current_frame = 0;

bool g_framebuffer_resized = false;



static const uint32_t vert_spv[] = {

    0x07230203,0x00010000,0x0008000b,0x00000021,0x00000000,0x00020011,0x00000001,0x0006000b,

    0x00000001,0x4c534c47,0x6474732e,0x3035342e,0x00000000,0x0003000e,0x00000000,0x00000001,

    0x0009000f,0x00000000,0x00000004,0x6e69616d,0x00000000,0x0000000d,0x00000012,0x0000001d,

    0x0000001f,0x00030003,0x00000002,0x000001c2,0x00040005,0x00000004,0x6e69616d,0x00000000,

    0x00060005,0x0000000b,0x505f6c67,0x65567265,0x78657472,0x00000000,0x00060006,0x0000000b,

    0x00000000,0x505f6c67,0x7469736f,0x006e6f69,0x00070006,0x0000000b,0x00000001,0x505f6c67,

    0x746e696f,0x657a6953,0x00000000,0x00070006,0x0000000b,0x00000002,0x435f6c67,0x4470696c,

    0x61747369,0x0065636e,0x00070006,0x0000000b,0x00000003,0x435f6c67,0x446c6c75,0x61747369,

    0x0065636e,0x00030005,0x0000000d,0x00000000,0x00040005,0x00000012,0x6f506e69,0x00000073,

    0x00050005,0x0000001d,0x4374756f,0x726f6c6f,0x00000000,0x00040005,0x0000001f,0x6f436e69,

    0x00726f6c,0x00030047,0x0000000b,0x00000002,0x00050048,0x0000000b,0x00000000,0x0000000b,

    0x00000000,0x00050048,0x0000000b,0x00000001,0x0000000b,0x00000001,0x00050048,0x0000000b,

    0x00000002,0x0000000b,0x00000003,0x00050048,0x0000000b,0x00000003,0x0000000b,0x00000004,

    0x00040047,0x00000012,0x0000001e,0x00000000,0x00040047,0x0000001d,0x0000001e,0x00000000,

    0x00040047,0x0000001f,0x0000001e,0x00000001,0x00020013,0x00000002,0x00030021,0x00000003,

    0x00000002,0x00030016,0x00000006,0x00000020,0x00040017,0x00000007,0x00000006,0x00000004,

    0x00040015,0x00000008,0x00000020,0x00000000,0x0004002b,0x00000008,0x00000009,0x00000001,

    0x0004001c,0x0000000a,0x00000006,0x00000009,0x0006001e,0x0000000b,0x00000007,0x00000006,

    0x0000000a,0x0000000a,0x00040020,0x0000000c,0x00000003,0x0000000b,0x0004003b,0x0000000c,

    0x0000000d,0x00000003,0x00040015,0x0000000e,0x00000020,0x00000001,0x0004002b,0x0000000e,

    0x0000000f,0x00000000,0x00040017,0x00000010,0x00000006,0x00000002,0x00040020,0x00000011,

    0x00000001,0x00000010,0x0004003b,0x00000011,0x00000012,0x00000001,0x0004002b,0x00000006,

    0x00000014,0x00000000,0x0004002b,0x00000006,0x00000015,0x3f800000,0x00040020,0x00000019,

    0x00000003,0x00000007,0x00040017,0x0000001b,0x00000006,0x00000003,0x00040020,0x0000001c,

    0x00000003,0x0000001b,0x0004003b,0x0000001c,0x0000001d,0x00000003,0x00040020,0x0000001e,

    0x00000001,0x0000001b,0x0004003b,0x0000001e,0x0000001f,0x00000001,0x00050036,0x00000002,

    0x00000004,0x00000000,0x00000003,0x000200f8,0x00000005,0x0004003d,0x00000010,0x00000013,

    0x00000012,0x00050051,0x00000006,0x00000016,0x00000013,0x00000000,0x00050051,0x00000006,

    0x00000017,0x00000013,0x00000001,0x00070050,0x00000007,0x00000018,0x00000016,0x00000017,

    0x00000014,0x00000015,0x00050041,0x00000019,0x0000001a,0x0000000d,0x0000000f,0x0003003e,

    0x0000001a,0x00000018,0x0004003d,0x0000001b,0x00000020,0x0000001f,0x0003003e,0x0000001d,

    0x00000020,0x000100fd,0x00010038,

};



static const uint32_t frag_spv[] = {

    0x07230203,0x00010000,0x0008000b,0x00000013,0x00000000,0x00020011,0x00000001,0x0006000b,

    0x00000001,0x4c534c47,0x6474732e,0x3035342e,0x00000000,0x0003000e,0x00000000,0x00000001,

    0x0007000f,0x00000004,0x00000004,0x6e69616d,0x00000000,0x00000009,0x0000000c,0x00030010,

    0x00000004,0x00000007,0x00030003,0x00000002,0x000001c2,0x00040005,0x00000004,0x6e69616d,

    0x00000000,0x00050005,0x00000009,0x67617266,0x6f6c6f43,0x00000072,0x00040005,0x0000000c,

    0x6f436e69,0x00726f6c,0x00040047,0x00000009,0x0000001e,0x00000000,0x00040047,0x0000000c,

    0x0000001e,0x00000000,0x00020013,0x00000002,0x00030021,0x00000003,0x00000002,0x00030016,

    0x00000006,0x00000020,0x00040017,0x00000007,0x00000006,0x00000004,0x00040020,0x00000008,

    0x00000003,0x00000007,0x0004003b,0x00000008,0x00000009,0x00000003,0x00040017,0x0000000a,

    0x00000006,0x00000003,0x00040020,0x0000000b,0x00000001,0x0000000a,0x0004003b,0x0000000b,

    0x0000000c,0x00000001,0x0004002b,0x00000006,0x0000000e,0x3f800000,0x00050036,0x00000002,

    0x00000004,0x00000000,0x00000003,0x000200f8,0x00000005,0x0004003d,0x0000000a,0x0000000d,

    0x0000000c,0x00050051,0x00000006,0x0000000f,0x0000000d,0x00000000,0x00050051,0x00000006,

    0x00000010,0x0000000d,0x00000001,0x00050051,0x00000006,0x00000011,0x0000000d,0x00000002,

    0x00070050,0x00000007,0x00000012,0x0000000f,0x00000010,0x00000011,0x0000000e,0x0003003e,

    0x00000009,0x00000012,0x000100fd,0x00010038,

};



VkShaderModule CreateShaderModule(const uint32_t *code, size_t size) {

    VkShaderModuleCreateInfo ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;

    ci.codeSize = size;

    ci.pCode = code;

    VkShaderModule mod;

    VK_CHECK(vkCreateShaderModule(g_dev, &ci, NULL, &mod));

    return mod;

}



uint32_t FindMemoryType(uint32_t type_filter, VkMemoryPropertyFlags props) {

    VkPhysicalDeviceMemoryProperties mem_props;

    vkGetPhysicalDeviceMemoryProperties(g_phys_dev, &mem_props);

    for (uint32_t i = 0; i < mem_props.memoryTypeCount; i++) {

        if ((type_filter & (1 << i)) && 

            (mem_props.memoryTypes[i].propertyFlags & props) == props) {

            return i;

        }

    }

    fprintf(stderr, "Failed to find suitable memory type!\n");

    exit(-1);

}



void CreateBuffer(VkDeviceSize size, VkBufferUsageFlags usage,

                  VkMemoryPropertyFlags props, VkBuffer *buf, VkDeviceMemory *mem) {

    VkBufferCreateInfo bi = {0};

    bi.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;

    bi.size = size;

    bi.usage = usage;

    bi.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    VK_CHECK(vkCreateBuffer(g_dev, &bi, NULL, buf));



    VkMemoryRequirements mr;

    vkGetBufferMemoryRequirements(g_dev, *buf, &mr);



    VkMemoryAllocateInfo ai = {0};

    ai.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;

    ai.allocationSize = mr.size;

    ai.memoryTypeIndex = FindMemoryType(mr.memoryTypeBits, props);

    VK_CHECK(vkAllocateMemory(g_dev, &ai, NULL, mem));

    VK_CHECK(vkBindBufferMemory(g_dev, *buf, *mem, 0));

}



void CopyBuffer(VkBuffer src, VkBuffer dst, VkDeviceSize size) {

    VkCommandBufferAllocateInfo ai = {0};

    ai.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;

    ai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;

    ai.commandPool = g_cmd_pool;

    ai.commandBufferCount = 1;

    VkCommandBuffer cb;

    vkAllocateCommandBuffers(g_dev, &ai, &cb);



    VkCommandBufferBeginInfo bi = {0};

    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;

    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;

    vkBeginCommandBuffer(cb, &bi);



    VkBufferCopy region = {0};

    region.srcOffset = 0;

    region.dstOffset = 0;

    region.size = size;

    vkCmdCopyBuffer(cb, src, dst, 1, &region);

    vkEndCommandBuffer(cb);



    VkSubmitInfo si = {0};

    si.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;

    si.commandBufferCount = 1;

    si.pCommandBuffers = &cb;

    vkQueueSubmit(g_gfx_queue, 1, &si, VK_NULL_HANDLE);

    vkQueueWaitIdle(g_gfx_queue);

    vkFreeCommandBuffers(g_dev, g_cmd_pool, 1, &cb);

}



static void CreateInstance(void) {

    VkApplicationInfo app_info = {0};

    app_info.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;

    app_info.pApplicationName = "Manim Vulkan";

    app_info.applicationVersion = VK_MAKE_VERSION(1, 0, 0);

    app_info.pEngineName = "No Engine";

    app_info.engineVersion = VK_MAKE_VERSION(1, 0, 0);

    app_info.apiVersion = VK_API_VERSION_1_0;



    const char *extensions[] = {

        VK_KHR_SURFACE_EXTENSION_NAME,

        VK_KHR_WIN32_SURFACE_EXTENSION_NAME

    };



    VkInstanceCreateInfo ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;

    ci.pApplicationInfo = &app_info;

    ci.enabledExtensionCount = 2;

    ci.ppEnabledExtensionNames = extensions;



    if (vkCreateInstance(&ci, NULL, &g_inst) != VK_SUCCESS) {

        fprintf(stderr, "Failed to create Vulkan instance!\n");

        exit(-1);

    }

}



static void CreateSurface(void) {

    VkWin32SurfaceCreateInfoKHR ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR;

    ci.hinstance = g_hinst;

    ci.hwnd = g_hwnd;

    if (vkCreateWin32SurfaceKHR(g_inst, &ci, NULL, &g_surface) != VK_SUCCESS) {

        fprintf(stderr, "Failed to create Win32 surface!\n");

        exit(-1);

    }

}



static void PickPhysicalDevice(void) {

    uint32_t count = 0;

    vkEnumeratePhysicalDevices(g_inst, &count, NULL);

    if (count == 0) { fprintf(stderr, "No GPU found!\n"); exit(-1); }

    VkPhysicalDevice *devs = malloc(sizeof(VkPhysicalDevice) * count);

    vkEnumeratePhysicalDevices(g_inst, &count, devs);

    g_phys_dev = devs[0];

    free(devs);

}



static void CreateLogicalDevice(void) {

    float prio = 1.0f;

    VkDeviceQueueCreateInfo qci = {0};

    qci.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;

    qci.queueFamilyIndex = 0;

    qci.queueCount = 1;

    qci.pQueuePriorities = &prio;



    const char *exts[] = { VK_KHR_SWAPCHAIN_EXTENSION_NAME };

    VkDeviceCreateInfo dci = {0};

    dci.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;

    dci.queueCreateInfoCount = 1;

    dci.pQueueCreateInfos = &qci;

    dci.enabledExtensionCount = 1;

    dci.ppEnabledExtensionNames = exts;



    vkCreateDevice(g_phys_dev, &dci, NULL, &g_dev);

    vkGetDeviceQueue(g_dev, 0, 0, &g_gfx_queue);

    vkGetDeviceQueue(g_dev, 0, 0, &g_present_queue);

}



void CreateSwapchain(void) {

    VkSwapchainCreateInfoKHR sci = {0};

    sci.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;

    sci.surface = g_surface;

    sci.minImageCount = 2;

    sci.imageFormat = VK_FORMAT_B8G8R8A8_SRGB;

    sci.imageColorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR;

    sci.imageExtent = g_swapchain_ext;

    sci.imageArrayLayers = 1;

    sci.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;

    sci.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;

    sci.preTransform = VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR;

    sci.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;

    sci.presentMode = VK_PRESENT_MODE_FIFO_KHR;

    sci.clipped = VK_TRUE;



    VK_CHECK(vkCreateSwapchainKHR(g_dev, &sci, NULL, &g_swapchain));

    g_swapchain_fmt = VK_FORMAT_B8G8R8A8_SRGB;



    vkGetSwapchainImagesKHR(g_dev, g_swapchain, &g_swapchain_img_count, NULL);

    g_swapchain_imgs = malloc(sizeof(VkImage) * g_swapchain_img_count);

    vkGetSwapchainImagesKHR(g_dev, g_swapchain, &g_swapchain_img_count, g_swapchain_imgs);

}



void CreateImageViews(void) {

    g_swapchain_img_views = malloc(sizeof(VkImageView) * g_swapchain_img_count);

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {

        VkImageViewCreateInfo vci = {0};

        vci.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;

        vci.image = g_swapchain_imgs[i];

        vci.viewType = VK_IMAGE_VIEW_TYPE_2D;

        vci.format = g_swapchain_fmt;

        vci.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;

        vci.subresourceRange.baseMipLevel = 0;

        vci.subresourceRange.levelCount = 1;

        vci.subresourceRange.baseArrayLayer = 0;

        vci.subresourceRange.layerCount = 1;

        vkCreateImageView(g_dev, &vci, NULL, &g_swapchain_img_views[i]);

    }

}



static void CreateRenderPass(void) {

    VkAttachmentDescription att = {0};

    att.format = g_swapchain_fmt;

    att.samples = VK_SAMPLE_COUNT_1_BIT;

    att.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;

    att.storeOp = VK_ATTACHMENT_STORE_OP_STORE;

    att.stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;

    att.stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;

    att.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;

    att.finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;



    VkAttachmentReference ref = {0};

    ref.attachment = 0;

    ref.layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;



    VkSubpassDescription sub = {0};

    sub.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;

    sub.colorAttachmentCount = 1;

    sub.pColorAttachments = &ref;



    VkSubpassDependency dep = {0};

    dep.srcSubpass = VK_SUBPASS_EXTERNAL;

    dep.dstSubpass = 0;

    dep.srcStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT;

    dep.dstStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT;

    dep.dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT;



    VkRenderPassCreateInfo rpci = {0};

    rpci.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;

    rpci.attachmentCount = 1;

    rpci.pAttachments = &att;

    rpci.subpassCount = 1;

    rpci.pSubpasses = &sub;

    rpci.dependencyCount = 1;

    rpci.pDependencies = &dep;



    vkCreateRenderPass(g_dev, &rpci, NULL, &g_render_pass);

}



static void CreateGraphicsPipeline(void) {

    VkShaderModule vs = CreateShaderModule(vert_spv, sizeof(vert_spv));

    VkShaderModule fs = CreateShaderModule(frag_spv, sizeof(frag_spv));



    VkPipelineShaderStageCreateInfo stages[2] = {{0}};

    stages[0].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;

    stages[0].stage = VK_SHADER_STAGE_VERTEX_BIT;

    stages[0].module = vs;

    stages[0].pName = "main";

    stages[1].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;

    stages[1].stage = VK_SHADER_STAGE_FRAGMENT_BIT;

    stages[1].module = fs;

    stages[1].pName = "main";



    VkVertexInputBindingDescription bind_desc = {0};

    bind_desc.binding = 0;

    bind_desc.stride = sizeof(float) * 5;

    bind_desc.inputRate = VK_VERTEX_INPUT_RATE_VERTEX;



    VkVertexInputAttributeDescription attr_descs[2] = {{0}};

    attr_descs[0].location = 0;

    attr_descs[0].binding = 0;

    attr_descs[0].format = VK_FORMAT_R32G32_SFLOAT;

    attr_descs[0].offset = 0;

    attr_descs[1].location = 1;

    attr_descs[1].binding = 0;

    attr_descs[1].format = VK_FORMAT_R32G32B32_SFLOAT;

    attr_descs[1].offset = sizeof(float) * 2;



    VkPipelineVertexInputStateCreateInfo vi = {0};

    vi.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;

    vi.vertexBindingDescriptionCount = 1;

    vi.pVertexBindingDescriptions = &bind_desc;

    vi.vertexAttributeDescriptionCount = 2;

    vi.pVertexAttributeDescriptions = attr_descs;



    VkPipelineInputAssemblyStateCreateInfo ia = {0};

    ia.sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO;

    ia.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;



    VkViewport vp = {0, 0, (float)g_swapchain_ext.width, (float)g_swapchain_ext.height, 0, 1};

    VkRect2D sc = {{0, 0}, g_swapchain_ext};

    VkPipelineViewportStateCreateInfo vps = {0};

    vps.sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO;

    vps.viewportCount = 1;

    vps.pViewports = &vp;

    vps.scissorCount = 1;

    vps.pScissors = &sc;



    VkPipelineRasterizationStateCreateInfo rs = {0};

    rs.sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO;

    rs.polygonMode = VK_POLYGON_MODE_FILL;

    rs.cullMode = VK_CULL_MODE_NONE;

    rs.frontFace = VK_FRONT_FACE_CLOCKWISE;

    rs.lineWidth = 1.0f;



    VkPipelineMultisampleStateCreateInfo ms = {0};

    ms.sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO;

    ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;



    VkPipelineColorBlendAttachmentState cba = {0};

    cba.colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | 

                         VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT;

    cba.blendEnable = VK_TRUE;

    cba.srcColorBlendFactor = VK_BLEND_FACTOR_SRC_ALPHA;

    cba.dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA;

    cba.colorBlendOp = VK_BLEND_OP_ADD;

    cba.srcAlphaBlendFactor = VK_BLEND_FACTOR_ONE;

    cba.dstAlphaBlendFactor = VK_BLEND_FACTOR_ZERO;

    cba.alphaBlendOp = VK_BLEND_OP_ADD;



    VkPipelineColorBlendStateCreateInfo cb = {0};

    cb.sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO;

    cb.attachmentCount = 1;

    cb.pAttachments = &cba;



    VkPipelineLayoutCreateInfo plci = {0};

    plci.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;

    vkCreatePipelineLayout(g_dev, &plci, NULL, &g_pipeline_layout);



    VkGraphicsPipelineCreateInfo pci = {0};

    pci.sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO;

    pci.stageCount = 2;

    pci.pStages = stages;

    pci.pVertexInputState = &vi;

    pci.pInputAssemblyState = &ia;

    pci.pViewportState = &vps;

    pci.pRasterizationState = &rs;

    pci.pMultisampleState = &ms;

    pci.pColorBlendState = &cb;

    pci.layout = g_pipeline_layout;

    pci.renderPass = g_render_pass;



    vkCreateGraphicsPipelines(g_dev, VK_NULL_HANDLE, 1, &pci, NULL, &g_pipeline);



    vkDestroyShaderModule(g_dev, vs, NULL);

    vkDestroyShaderModule(g_dev, fs, NULL);

}



void CreateFramebuffers(void) {

    g_framebuffers = malloc(sizeof(VkFramebuffer) * g_swapchain_img_count);

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {

        VkFramebufferCreateInfo fci = {0};

        fci.sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO;

        fci.renderPass = g_render_pass;

        fci.attachmentCount = 1;

        fci.pAttachments = &g_swapchain_img_views[i];

        fci.width = g_swapchain_ext.width;

        fci.height = g_swapchain_ext.height;

        fci.layers = 1;

        vkCreateFramebuffer(g_dev, &fci, NULL, &g_framebuffers[i]);

    }

}



static void CreateCommandPool(void) {

    VkCommandPoolCreateInfo cpci = {0};

    cpci.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;

    cpci.queueFamilyIndex = 0;

    cpci.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;

    vkCreateCommandPool(g_dev, &cpci, NULL, &g_cmd_pool);

}



static void CreateCommandBuffers(void) {

    g_cmd_buf_count = g_swapchain_img_count;

    g_cmd_bufs = malloc(sizeof(VkCommandBuffer) * g_cmd_buf_count);

    VkCommandBufferAllocateInfo ai = {0};

    ai.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;

    ai.commandPool = g_cmd_pool;

    ai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;

    ai.commandBufferCount = g_cmd_buf_count;

    vkAllocateCommandBuffers(g_dev, &ai, g_cmd_bufs);

}



static void CreateSyncObjects(void) {

    g_img_avail_sems = malloc(sizeof(VkSemaphore) * g_swapchain_img_count);

    g_render_done_sems = malloc(sizeof(VkSemaphore) * g_swapchain_img_count);

    g_in_flight_fences = malloc(sizeof(VkFence) * g_swapchain_img_count);



    VkSemaphoreCreateInfo sci = {0};

    sci.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;

    VkFenceCreateInfo fci = {0};

    fci.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    fci.flags = VK_FENCE_CREATE_SIGNALED_BIT;



    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {

        vkCreateSemaphore(g_dev, &sci, NULL, &g_img_avail_sems[i]);

        vkCreateSemaphore(g_dev, &sci, NULL, &g_render_done_sems[i]);

        vkCreateFence(g_dev, &fci, NULL, &g_in_flight_fences[i]);

    }

}



static void CreateVertexBuffer(void) {

    g_vert_buf_size = sizeof(float) * 5 * MAX_SHAPES * 6;

    CreateBuffer(g_vert_buf_size, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,

                 VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,

                 &g_vert_buf, &g_vert_buf_mem);

}



void Render_Init(HWND hwnd, int width, int height, HINSTANCE hinst) {

    g_hwnd = hwnd;

    g_hinst = hinst;

    g_swapchain_ext = (VkExtent2D){(uint32_t)width, (uint32_t)height};



    CreateInstance();

    CreateSurface();

    PickPhysicalDevice();

    CreateLogicalDevice();

    CreateSwapchain();

    CreateImageViews();

    CreateRenderPass();

    CreateGraphicsPipeline();

    CreateFramebuffers();

    CreateCommandPool();

    CreateCommandBuffers();

    CreateSyncObjects();

    CreateVertexBuffer();



    g_is_ready = true;

}



int Render_IsReady(void) {

    return g_is_ready ? 1 : 0;

}



void update_vertex_buffer(const void *data, VkDeviceSize size) {

    void *mapped_data;

    vkMapMemory(g_dev, g_vert_buf_mem, 0, size, 0, &mapped_data);

    memcpy(mapped_data, data, size);

    vkUnmapMemory(g_dev, g_vert_buf_mem);

}



void CleanupSwapchain(void) {
    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroyFramebuffer(g_dev, g_framebuffers[i], NULL);
    }
    free(g_framebuffers);

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroyImageView(g_dev, g_swapchain_img_views[i], NULL);
    }
    free(g_swapchain_img_views);
    free(g_swapchain_imgs);

    vkDestroySwapchainKHR(g_dev, g_swapchain, NULL);
}

void RecreateSwapchain(void) {
    int width = 0, height = 0;
    RECT rect;
    if (GetClientRect(g_hwnd, &rect)) {
        width = rect.right - rect.left;
        height = rect.bottom - rect.top;
    }
    if (width == 0 || height == 0) return;

    vkDeviceWaitIdle(g_dev);

    CleanupSwapchain();

    g_swapchain_ext = (VkExtent2D){(uint32_t)width, (uint32_t)height};
    CreateSwapchain();
    CreateImageViews();
    CreateFramebuffers();
}



void Render_Cleanup(void) {

    if (!g_is_ready) return;

    vkDeviceWaitIdle(g_dev);

    CleanupSwapchain();

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroySemaphore(g_dev, g_img_avail_sems[i], NULL);
        vkDestroySemaphore(g_dev, g_render_done_sems[i], NULL);
        vkDestroyFence(g_dev, g_in_flight_fences[i], NULL);
    }
    free(g_img_avail_sems);
    free(g_render_done_sems);
    free(g_in_flight_fences);

    vkFreeCommandBuffers(g_dev, g_cmd_pool, g_cmd_buf_count, g_cmd_bufs);
    free(g_cmd_bufs);
    vkDestroyCommandPool(g_dev, g_cmd_pool, NULL);

    vkDestroyPipeline(g_dev, g_pipeline, NULL);
    vkDestroyPipelineLayout(g_dev, g_pipeline_layout, NULL);
    vkDestroyRenderPass(g_dev, g_render_pass, NULL);

    vkDestroyBuffer(g_dev, g_vert_buf, NULL);
    vkFreeMemory(g_dev, g_vert_buf_mem, NULL);

    vkDestroySurfaceKHR(g_inst, g_surface, NULL);
    vkDestroyDevice(g_dev, NULL);
    vkDestroyInstance(g_inst, NULL);

    g_is_ready = false;
}

void RecordCommandBuffer(VkCommandBuffer cmd_buf, uint32_t img_idx,
                         uint32_t vertex_count) {
    VkCommandBufferBeginInfo begin_info = {0};
    begin_info.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;

    vkBeginCommandBuffer(cmd_buf, &begin_info);

    VkClearValue clear_color = {{{0.0f, 0.0f, 0.0f, 1.0f}}};
    VkRenderPassBeginInfo render_pass_info = {0};
    render_pass_info.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
    render_pass_info.renderPass = g_render_pass;
    render_pass_info.framebuffer = g_framebuffers[img_idx];
    render_pass_info.renderArea.offset.x = 0;
    render_pass_info.renderArea.offset.y = 0;
    render_pass_info.renderArea.extent = g_swapchain_ext;
    render_pass_info.clearValueCount = 1;
    render_pass_info.pClearValues = &clear_color;

    vkCmdBeginRenderPass(cmd_buf, &render_pass_info, VK_SUBPASS_CONTENTS_INLINE);

    vkCmdBindPipeline(cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_pipeline);

    VkBuffer vertex_buffers[] = { g_vert_buf };
    VkDeviceSize offsets[] = { 0 };
    vkCmdBindVertexBuffers(cmd_buf, 0, 1, vertex_buffers, offsets);

    if (vertex_count > 0) {
        vkCmdDraw(cmd_buf, vertex_count, 1, 0, 0);
    }

    vkCmdEndRenderPass(cmd_buf);

    vkEndCommandBuffer(cmd_buf);
}

int Render_DrawFrame(uint32_t vertex_count) {
    if (!g_is_ready) return 0;

    vkWaitForFences(g_dev, 1, &g_in_flight_fences[g_current_frame], VK_TRUE, UINT64_MAX);
    vkResetFences(g_dev, 1, &g_in_flight_fences[g_current_frame]);

    uint32_t img_idx;
    vkAcquireNextImageKHR(g_dev, g_swapchain, UINT64_MAX,
                          g_img_avail_sems[g_current_frame], VK_NULL_HANDLE, &img_idx);

    vkResetCommandBuffer(g_cmd_bufs[g_current_frame], 0);
    RecordCommandBuffer(g_cmd_bufs[g_current_frame], img_idx, vertex_count);

    VkSubmitInfo submit_info = {0};
    submit_info.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;

    VkSemaphore wait_sems[] = { g_img_avail_sems[g_current_frame] };
    VkPipelineStageFlags wait_stages[] = { VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT };
    submit_info.waitSemaphoreCount = 1;
    submit_info.pWaitSemaphores = wait_sems;
    submit_info.pWaitDstStageMask = wait_stages;
    submit_info.commandBufferCount = 1;
    submit_info.pCommandBuffers = &g_cmd_bufs[g_current_frame];

    VkSemaphore signal_sems[] = { g_render_done_sems[g_current_frame] };
    submit_info.signalSemaphoreCount = 1;
    submit_info.pSignalSemaphores = signal_sems;

    vkQueueSubmit(g_gfx_queue, 1, &submit_info, g_in_flight_fences[g_current_frame]);

    VkPresentInfoKHR present_info = {0};
    present_info.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
    present_info.waitSemaphoreCount = 1;
    present_info.pWaitSemaphores = signal_sems;
    present_info.swapchainCount = 1;
    present_info.pSwapchains = &g_swapchain;
    present_info.pImageIndices = &img_idx;

    vkQueuePresentKHR(g_present_queue, &present_info);

    g_current_frame = (g_current_frame + 1) % g_swapchain_img_count;

    return 1;
}