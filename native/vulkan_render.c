#define VK_USE_PLATFORM_WIN32_KHR

#include "vulkan_render.h"
#include <stdlib.h>

static VkInstance       g_inst        = VK_NULL_HANDLE;
static VkSurfaceKHR     g_surface     = VK_NULL_HANDLE;
static VkPhysicalDevice g_phy_dev     = VK_NULL_HANDLE;
static VkDevice         g_dev         = VK_NULL_HANDLE;
static uint32_t         g_gfx_qf      = 0;
static uint32_t         g_pres_qf     = 0;
static VkQueue          g_gfx_queue   = VK_NULL_HANDLE;
static VkQueue          g_pres_queue  = VK_NULL_HANDLE;

static VkSwapchainKHR   g_swap        = VK_NULL_HANDLE;
static VkImage*         g_swap_imgs   = NULL;
static uint32_t         g_swap_cnt    = 0;
static VkRenderPass     g_rp          = VK_NULL_HANDLE;
static VkFramebuffer*   g_fbs         = NULL;
static VkCommandPool    g_cmd_pool    = VK_NULL_HANDLE;
static VkCommandBuffer  g_cmd_buf     = VK_NULL_HANDLE;

static int g_w = 800, g_h = 600;
static float g_clr_r = 0.05f, g_clr_g = 0.07f, g_clr_b = 0.14f;

static void PickDevice(void)
{
    uint32_t dev_cnt = 0;
    vkEnumeratePhysicalDevices(g_inst, &dev_cnt, NULL);
    VkPhysicalDevice* devs = malloc(dev_cnt * sizeof(VkPhysicalDevice));
    vkEnumeratePhysicalDevices(g_inst, &dev_cnt, devs);

    for(uint32_t i = 0; i < dev_cnt; i++)
    {
        uint32_t fam_cnt = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(devs[i], &fam_cnt, NULL);
        VkQueueFamilyProperties* fams = malloc(fam_cnt * sizeof(VkQueueFamilyProperties));
        vkGetPhysicalDeviceQueueFamilyProperties(devs[i], &fam_cnt, fams);

        uint32_t g = UINT32_MAX, p = UINT32_MAX;
        for(uint32_t j = 0; j < fam_cnt; j++)
        {
            if(fams[j].queueFlags & VK_QUEUE_GRAPHICS_BIT) g = j;
            VkBool32 ok;
            vkGetPhysicalDeviceSurfaceSupportKHR(devs[i], j, g_surface, &ok);
            if(ok) p = j;
        }
        if(g != UINT32_MAX && p != UINT32_MAX)
        {
            g_phy_dev = devs[i];
            g_gfx_qf = g;
            g_pres_qf = p;
            free(fams);
            free(devs);
            return;
        }
        free(fams);
    }
    free(devs);
}

static void CreateDevice(void)
{
    float prio = 1.0f;
    VkDeviceQueueCreateInfo q_info = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
        .queueFamilyIndex = g_gfx_qf,
        .queueCount = 1,
        .pQueuePriorities = &prio
    };
    const char* ext = VK_KHR_SWAPCHAIN_EXTENSION_NAME;
    VkDeviceCreateInfo dev_info = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        .queueCreateInfoCount = 1,
        .pQueueCreateInfos = &q_info,
        .enabledExtensionCount = 1,
        .ppEnabledExtensionNames = &ext
    };
    vkCreateDevice(g_phy_dev, &dev_info, NULL, &g_dev);
    vkGetDeviceQueue(g_dev, g_gfx_qf, 0, &g_gfx_queue);
    vkGetDeviceQueue(g_dev, g_pres_qf, 0, &g_pres_queue);
}

static void CreateSwapchain(void)
{
    VkSurfaceCapabilitiesKHR cap;
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR(g_phy_dev, g_surface, &cap);
    VkSurfaceFormatKHR fmt = {VK_FORMAT_B8G8R8A8_UNORM, VK_COLOR_SPACE_SRGB_NONLINEAR_KHR};
    VkPresentModeKHR mode = VK_PRESENT_MODE_FIFO_KHR;

    VkSwapchainCreateInfoKHR sc_info = {
        .sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
        .surface = g_surface,
        .minImageCount = cap.minImageCount + 1,
        .imageFormat = fmt.format,
        .imageColorSpace = fmt.colorSpace,
        .imageExtent = cap.currentExtent,
        .imageArrayLayers = 1,
        .imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
        .preTransform = cap.currentTransform,
        .compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
        .presentMode = mode,
        .clipped = VK_TRUE
    };
    vkCreateSwapchainKHR(g_dev, &sc_info, NULL, &g_swap);
    vkGetSwapchainImagesKHR(g_dev, g_swap, &g_swap_cnt, NULL);
    g_swap_imgs = malloc(g_swap_cnt * sizeof(VkImage));
    vkGetSwapchainImagesKHR(g_dev, g_swap, &g_swap_cnt, g_swap_imgs);
}

static void CreateRenderPass(void)
{
    VkAttachmentDescription att = {
        .format = VK_FORMAT_B8G8R8A8_UNORM,
        .samples = VK_SAMPLE_COUNT_1_BIT,
        .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
        .storeOp = VK_ATTACHMENT_STORE_OP_STORE,
        .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
        .finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
    };
    VkAttachmentReference ref = {0, VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL};
    VkSubpassDescription sub = {
        .pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS,
        .colorAttachmentCount = 1,
        .pColorAttachments = &ref
    };
    VkRenderPassCreateInfo rp_info = {
        .sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
        .attachmentCount = 1,
        .pAttachments = &att,
        .subpassCount = 1,
        .pSubpasses = &sub
    };
    vkCreateRenderPass(g_dev, &rp_info, NULL, &g_rp);
}

static void CreateFramebuffer(void)
{
    g_fbs = malloc(g_swap_cnt * sizeof(VkFramebuffer));
    for(uint32_t i = 0; i < g_swap_cnt; i++)
    {
        VkImageViewCreateInfo iv_info = {
            .sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
            .image = g_swap_imgs[i],
            .viewType = VK_IMAGE_VIEW_TYPE_2D,
            .format = VK_FORMAT_B8G8R8A8_UNORM,
            .subresourceRange = {VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1}
        };
        VkImageView view;
        vkCreateImageView(g_dev, &iv_info, NULL, &view);

        VkFramebufferCreateInfo fb_info = {
            .sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
            .renderPass = g_rp,
            .attachmentCount = 1,
            .pAttachments = &view,
            .width = g_w,
            .height = g_h,
            .layers = 1
        };
        vkCreateFramebuffer(g_dev, &fb_info, NULL, &g_fbs[i]);
        vkDestroyImageView(g_dev, view, NULL);
    }
}

static void CreateCmdResource(void)
{
    VkCommandPoolCreateInfo cp_info = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
        .queueFamilyIndex = g_gfx_qf
    };
    vkCreateCommandPool(g_dev, &cp_info, NULL, &g_cmd_pool);

    VkCommandBufferAllocateInfo cb_alloc = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
        .commandPool = g_cmd_pool,
        .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
        .commandBufferCount = 1
    };
    vkAllocateCommandBuffers(g_dev, &cb_alloc, &g_cmd_buf);
}

void Render_Init(HWND hwnd, int width, int height)
{
    g_w = width; g_h = height;

    // 创建实例
    VkInstanceCreateInfo inst_info = {.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    const char* exts[] = {VK_KHR_SURFACE_EXTENSION_NAME, VK_KHR_WIN32_SURFACE_EXTENSION_NAME};
    inst_info.enabledExtensionCount = 2;
    inst_info.ppEnabledExtensionNames = exts;
    vkCreateInstance(&inst_info, NULL, &g_inst);

    VkWin32SurfaceCreateInfoKHR surf_info = {
        .sType = VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR,
        .hinstance = GetModuleHandleW(NULL),
        .hwnd = hwnd
    };
    vkCreateWin32SurfaceKHR(g_inst, &surf_info, NULL, &g_surface);

    PickDevice();
    CreateDevice();
    CreateSwapchain();
    CreateRenderPass();
    CreateFramebuffer();
    CreateCmdResource();
}

void Render_SetClear(float r, float g, float b)
{
    g_clr_r = r;
    g_clr_g = g;
    g_clr_b = b;
}

void Render_Frame(void)
{
    if(g_dev == VK_NULL_HANDLE) return;
    vkDeviceWaitIdle(g_dev);

    uint32_t img_idx;
    vkAcquireNextImageKHR(g_dev, g_swap, UINT64_MAX, VK_NULL_HANDLE, VK_NULL_HANDLE, &img_idx);

    vkResetCommandBuffer(g_cmd_buf, 0);
    VkCommandBufferBeginInfo begin = {.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    vkBeginCommandBuffer(g_cmd_buf, &begin);

    VkClearValue clear = {{g_clr_r, g_clr_g, g_clr_b, 1.0f}};
    VkRenderPassBeginInfo rp_begin = {
        .sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
        .renderPass = g_rp,
        .framebuffer = g_fbs[img_idx],
        .renderArea = {{0,0},{(uint32_t)g_w,(uint32_t)g_h}},
        .clearValueCount = 1,
        .pClearValues = &clear
    };
    vkCmdBeginRenderPass(g_cmd_buf, &rp_begin, VK_SUBPASS_CONTENTS_INLINE);
    vkCmdEndRenderPass(g_cmd_buf);
    vkEndCommandBuffer(g_cmd_buf);

    VkSubmitInfo submit = {
        .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
        .commandBufferCount = 1,
        .pCommandBuffers = &g_cmd_buf
    };
    vkQueueSubmit(g_gfx_queue, 1, &submit, VK_NULL_HANDLE);

    VkPresentInfoKHR present = {
        .sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
        .swapchainCount = 1,
        .pSwapchains = &g_swap,
        .pImageIndices = &img_idx
    };
    vkQueuePresentKHR(g_pres_queue, &present);
}

void Render_Cleanup(void)
{
    if(g_dev != VK_NULL_HANDLE)
    {
        vkDeviceWaitIdle(g_dev);
        vkFreeCommandBuffers(g_dev, g_cmd_pool, 1, &g_cmd_buf);
        vkDestroyCommandPool(g_dev, g_cmd_pool, NULL);
        for(uint32_t i=0;i<g_swap_cnt;i++) vkDestroyFramebuffer(g_dev, g_fbs[i], NULL);
        free(g_fbs);
        vkDestroyRenderPass(g_dev, g_rp, NULL);
        vkDestroySwapchainKHR(g_dev, g_swap, NULL);
        free(g_swap_imgs);
        vkDestroyDevice(g_dev, NULL);
    }
    vkDestroySurfaceKHR(g_inst, g_surface, NULL);
    vkDestroyInstance(g_inst, NULL);
}