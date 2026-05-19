#define VK_USE_PLATFORM_WIN32_KHR
#include "vulkan_render.h"
#include <vulkan/vulkan.h>
#include <string.h>
#include <stdlib.h>

static VkInstance       g_inst         = VK_NULL_HANDLE;
static VkSurfaceKHR     g_surface      = VK_NULL_HANDLE;
static VkPhysicalDevice g_phys_dev     = VK_NULL_HANDLE;
static VkDevice         g_device       = VK_NULL_HANDLE;
static uint32_t         g_gfx_queue_family = 0;
static VkQueue          g_gfx_queue    = VK_NULL_HANDLE;
static VkRenderPass     g_render_pass  = VK_NULL_HANDLE;
static VkCommandPool    g_cmd_pool     = VK_NULL_HANDLE;
static VkCommandBuffer  g_main_cmd_buf = VK_NULL_HANDLE;
static int              g_width        = 0;
static int              g_height       = 0;
static float            g_clr_r = 0.1f, g_clr_g = 0.2f, g_clr_b = 0.4f;

void VK_SetClearColor(float r, float g, float b)
{
    g_clr_r = r;
    g_clr_g = g;
    g_clr_b = b;
}

static void CreateVulkanInstance(void)
{
    VkInstanceCreateInfo inst_info;
    memset(&inst_info, 0, sizeof(VkInstanceCreateInfo));
    inst_info.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    vkCreateInstance(&inst_info, NULL, &g_inst);
}

static void CreateWin32Surface(HWND hwnd)
{
    VkWin32SurfaceCreateInfoKHR surf_info;
    memset(&surf_info, 0, sizeof(VkWin32SurfaceCreateInfoKHR));
    surf_info.sType = VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR;
    surf_info.hinstance = GetModuleHandleA(NULL);
    surf_info.hwnd = hwnd;
    vkCreateWin32SurfaceKHR(g_inst, &surf_info, NULL, &g_surface);
}

static void PickPhysicalDevice(void)
{
    uint32_t dev_count = 0;
    vkEnumeratePhysicalDevices(g_inst, &dev_count, NULL);
    if(dev_count == 0) return;

    VkPhysicalDevice* devs = (VkPhysicalDevice*)malloc(dev_count * sizeof(VkPhysicalDevice));
    vkEnumeratePhysicalDevices(g_inst, &dev_count, devs);
    g_phys_dev = devs[0];
    free(devs);

    uint32_t family_cnt = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(g_phys_dev, &family_cnt, NULL);
    VkQueueFamilyProperties* families = (VkQueueFamilyProperties*)malloc(family_cnt * sizeof(VkQueueFamilyProperties));
    vkGetPhysicalDeviceQueueFamilyProperties(g_phys_dev, &family_cnt, families);

    for(uint32_t i = 0; i < family_cnt; i++)
    {
        if(families[i].queueFlags & VK_QUEUE_GRAPHICS_BIT)
        {
            g_gfx_queue_family = i;
            break;
        }
    }
    free(families);
}

static void CreateLogicalDevice(void)
{
    float queue_prio = 1.0f;
    VkDeviceQueueCreateInfo queue_info;
    memset(&queue_info, 0, sizeof(VkDeviceQueueCreateInfo));
    queue_info.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
    queue_info.queueFamilyIndex = g_gfx_queue_family;
    queue_info.queueCount = 1;
    queue_info.pQueuePriorities = &queue_prio;

    VkDeviceCreateInfo dev_info;
    memset(&dev_info, 0, sizeof(VkDeviceCreateInfo));
    dev_info.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
    dev_info.queueCreateInfoCount = 1;
    dev_info.pQueueCreateInfos = &queue_info;

    vkCreateDevice(g_phys_dev, &dev_info, NULL, &g_device);
    vkGetDeviceQueue(g_device, g_gfx_queue_family, 0, &g_gfx_queue);
}

static void CreateRenderPass(void)
{
    VkAttachmentDescription attach_desc;
    memset(&attach_desc, 0, sizeof(VkAttachmentDescription));
    attach_desc.format = VK_FORMAT_B8G8R8A8_UNORM;
    attach_desc.samples = VK_SAMPLE_COUNT_1_BIT;
    attach_desc.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
    attach_desc.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
    attach_desc.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    attach_desc.finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;

    VkAttachmentReference color_ref;
    memset(&color_ref, 0, sizeof(VkAttachmentReference));
    color_ref.attachment = 0;
    color_ref.layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;

    VkSubpassDescription subpass;
    memset(&subpass, 0, sizeof(VkSubpassDescription));
    subpass.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
    subpass.colorAttachmentCount = 1;
    subpass.pColorAttachments = &color_ref;

    VkRenderPassCreateInfo rp_info;
    memset(&rp_info, 0, sizeof(VkRenderPassCreateInfo));
    rp_info.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;
    rp_info.attachmentCount = 1;
    rp_info.pAttachments = &attach_desc;
    rp_info.subpassCount = 1;
    rp_info.pSubpasses = &subpass;

    vkCreateRenderPass(g_device, &rp_info, NULL, &g_render_pass);
}

static void CreateCommandPoolAndBuffer(void)
{
    VkCommandPoolCreateInfo pool_info;
    memset(&pool_info, 0, sizeof(VkCommandPoolCreateInfo));
    pool_info.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
    pool_info.queueFamilyIndex = g_gfx_queue_family;
    vkCreateCommandPool(g_device, &pool_info, NULL, &g_cmd_pool);

    VkCommandBufferAllocateInfo buf_alloc;
    memset(&buf_alloc, 0, sizeof(VkCommandBufferAllocateInfo));
    buf_alloc.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    buf_alloc.commandPool = g_cmd_pool;
    buf_alloc.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    buf_alloc.commandBufferCount = 1;
    vkAllocateCommandBuffers(g_device, &buf_alloc, &g_main_cmd_buf);
}

void VK_Init(HWND hwnd, int w, int h)
{
    g_width = w;
    g_height = h;
    CreateVulkanInstance();
    CreateWin32Surface(hwnd);
    PickPhysicalDevice();
    CreateLogicalDevice();
    CreateRenderPass();
    CreateCommandPoolAndBuffer();
}

void VK_Draw(void)
{
    if(g_device == VK_NULL_HANDLE) return;
    vkDeviceWaitIdle(g_device);
}

void VK_Cleanup(void)
{
    if(g_device != VK_NULL_HANDLE)
    {
        vkDestroyCommandPool(g_device, g_cmd_pool, NULL);
        vkDestroyRenderPass(g_device, g_render_pass, NULL);
        vkDestroyDevice(g_device, NULL);
    }
    if(g_surface != VK_NULL_HANDLE)
        vkDestroySurfaceKHR(g_inst, g_surface, NULL);
    if(g_inst != VK_NULL_HANDLE)
        vkDestroyInstance(g_inst, NULL);
}