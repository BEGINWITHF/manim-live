#include "vulkan_render.h"
#include "shared_types.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stddef.h>
#include <vulkan/vulkan.h>

static const uint32_t vert_spv[] = {
    0x07230203, 0x00010000, 0x0008000b, 0x00000021, 0x00000000, 0x00020011, 0x00000001, 0x0006000b,
    0x00000001, 0x4c534c47, 0x6474732e, 0x3035342e, 0x00000000, 0x0003000e, 0x00000000, 0x00000001,
    0x0009000f, 0x00000000, 0x00000004, 0x6e69616d, 0x00000000, 0x0000000d, 0x00000012, 0x0000001d,
    0x0000001f, 0x00030003, 0x00000002, 0x000001c2, 0x00040005, 0x00000004, 0x6e69616d, 0x00000000,
    0x00060005, 0x0000000b, 0x505f6c67, 0x65567265, 0x78657472, 0x00000000, 0x00060006, 0x0000000b,
    0x00000000, 0x505f6c67, 0x7469736f, 0x006e6f69, 0x00070006, 0x0000000b, 0x00000001, 0x505f6c67,
    0x746e696f, 0x657a6953, 0x00000000, 0x00070006, 0x0000000b, 0x00000002, 0x435f6c67, 0x4470696c,
    0x61747369, 0x0065636e, 0x00070006, 0x0000000b, 0x00000003, 0x435f6c67, 0x446c6c75, 0x61747369,
    0x0065636e, 0x00030005, 0x0000000d, 0x00000000, 0x00040005, 0x00000012, 0x6f506e69, 0x00000073,
    0x00050005, 0x0000001d, 0x4374756f, 0x726f6c6f, 0x00000000, 0x00040005, 0x0000001f, 0x6f436e69,
    0x00726f6c, 0x00030047, 0x0000000b, 0x00000002, 0x00050048, 0x0000000b, 0x00000000, 0x0000000b,
    0x00000000, 0x00050048, 0x0000000b, 0x00000001, 0x0000000b, 0x00000001, 0x00050048, 0x0000000b,
    0x00000002, 0x0000000b, 0x00000003, 0x00050048, 0x0000000b, 0x00000003, 0x0000000b, 0x00000004,
    0x00040047, 0x00000012, 0x0000001e, 0x00000000, 0x00040047, 0x0000001d, 0x0000001e, 0x00000000,
    0x00040047, 0x0000001f, 0x0000001e, 0x00000001, 0x00020013, 0x00000002, 0x00030021, 0x00000003,
    0x00000002, 0x00030016, 0x00000006, 0x00000020, 0x00040017, 0x00000007, 0x00000006, 0x00000004,
    0x00040015, 0x00000008, 0x00000020, 0x00000000, 0x0004002b, 0x00000008, 0x00000009, 0x00000001,
    0x0004001c, 0x0000000a, 0x00000006, 0x00000009, 0x0006001e, 0x0000000b, 0x00000007, 0x00000006,
    0x0000000a, 0x0000000a, 0x00040020, 0x0000000c, 0x00000003, 0x0000000b, 0x0004003b, 0x0000000c,
    0x0000000d, 0x00000003, 0x00040015, 0x0000000e, 0x00000020, 0x00000001, 0x0004002b, 0x0000000e,
    0x0000000f, 0x00000000, 0x00040017, 0x00000010, 0x00000006, 0x00000002, 0x00040020, 0x00000011,
    0x00000001, 0x00000010, 0x0004003b, 0x00000011, 0x00000012, 0x00000001, 0x0004002b, 0x00000006,
    0x00000014, 0x00000000, 0x0004002b, 0x00000006, 0x00000015, 0x3f800000, 0x00040020, 0x00000019,
    0x00000003, 0x00000007, 0x00040017, 0x0000001b, 0x00000006, 0x00000003, 0x00040020, 0x0000001c,
    0x00000003, 0x0000001b, 0x0004003b, 0x0000001c, 0x0000001d, 0x00000003, 0x00040020, 0x0000001e,
    0x00000001, 0x0000001b, 0x0004003b, 0x0000001e, 0x0000001f, 0x00000001, 0x00050036, 0x00000002,
    0x00000004, 0x00000000, 0x00000003, 0x000200f8, 0x00000005, 0x0004003d, 0x00000010, 0x00000013,
    0x00000012, 0x00050051, 0x00000006, 0x00000016, 0x00000013, 0x00000000, 0x00050051, 0x00000006,
    0x00000017, 0x00000013, 0x00000001, 0x00070050, 0x00000007, 0x00000018, 0x00000016, 0x00000017,
    0x00000014, 0x00000015, 0x00050041, 0x00000019, 0x0000001a, 0x0000000d, 0x0000000f, 0x0003003e,
    0x0000001a, 0x00000018, 0x0004003d, 0x0000001b, 0x00000020, 0x0000001f, 0x0003003e, 0x0000001d,
    0x00000020, 0x000100fd, 0x00010038,
};

static const uint32_t frag_spv[] = {
    0x07230203, 0x00010000, 0x0008000b, 0x00000013, 0x00000000, 0x00020011, 0x00000001, 0x0006000b,
    0x00000001, 0x4c534c47, 0x6474732e, 0x3035342e, 0x00000000, 0x0003000e, 0x00000000, 0x00000001,
    0x0007000f, 0x00000004, 0x00000004, 0x6e69616d, 0x00000000, 0x00000009, 0x0000000c, 0x00030010,
    0x00000004, 0x00000007, 0x00030003, 0x00000002, 0x000001c2, 0x00040005, 0x00000004, 0x6e69616d,
    0x00000000, 0x00050005, 0x00000009, 0x67617266, 0x6f6c6f43, 0x00000072, 0x00040005, 0x0000000c,
    0x6f436e69, 0x00726f6c, 0x00040047, 0x00000009, 0x0000001e, 0x00000000, 0x00040047, 0x0000000c,
    0x0000001e, 0x00000000, 0x00020013, 0x00000002, 0x00030021, 0x00000003, 0x00000002, 0x00030016,
    0x00000006, 0x00000020, 0x00040017, 0x00000007, 0x00000006, 0x00000004, 0x00040020, 0x00000008,
    0x00000003, 0x00000007, 0x0004003b, 0x00000008, 0x00000009, 0x00000003, 0x00040017, 0x0000000a,
    0x00000006, 0x00000003, 0x00040020, 0x0000000b, 0x00000001, 0x0000000a, 0x0004003b, 0x0000000b,
    0x0000000c, 0x00000001, 0x0004002b, 0x00000006, 0x0000000e, 0x3f800000, 0x00050036, 0x00000002,
    0x00000004, 0x00000000, 0x00000003, 0x000200f8, 0x00000005, 0x0004003d, 0x0000000a, 0x0000000d,
    0x0000000c, 0x00050051, 0x00000006, 0x0000000f, 0x0000000d, 0x00000000, 0x00050051, 0x00000006,
    0x00000010, 0x0000000d, 0x00000001, 0x00050051, 0x00000006, 0x00000011, 0x0000000d, 0x00000002,
    0x00070050, 0x00000007, 0x00000012, 0x0000000f, 0x00000010, 0x00000011, 0x0000000e, 0x0003003e,
    0x00000009, 0x00000012, 0x000100fd, 0x00010038,
};

static VkInstance g_inst = VK_NULL_HANDLE;
static VkPhysicalDevice g_phy_dev = VK_NULL_HANDLE;
static VkDevice g_dev = VK_NULL_HANDLE;
static VkQueue g_queue = VK_NULL_HANDLE;
static VkCommandPool g_cmd_pool = VK_NULL_HANDLE;
static VkCommandBuffer g_cmd_buf = VK_NULL_HANDLE;
static VkRenderPass g_render_pass = VK_NULL_HANDLE;
static VkPipelineLayout g_pipeline_layout = VK_NULL_HANDLE;
static VkPipeline g_pipeline = VK_NULL_HANDLE;
static VkSwapchainKHR g_swapchain = VK_NULL_HANDLE;
static VkSurfaceKHR g_surface = VK_NULL_HANDLE;
static VkFence g_fence = VK_NULL_HANDLE;
static VkImageView *g_swapchain_views = NULL;
static VkFramebuffer *g_framebuffers = NULL;
static uint32_t g_image_count = 0;
static uint32_t g_width = 0;
static uint32_t g_height = 0;

static VkShaderModule g_vert_mod = VK_NULL_HANDLE;
static VkShaderModule g_frag_mod = VK_NULL_HANDLE;

static VkBuffer g_vertex_buffer = VK_NULL_HANDLE;
static VkDeviceMemory g_vertex_memory = VK_NULL_HANDLE;

static int g_is_ready = 0;

typedef struct {
    float x, y;
    float r, g, b;
} Vertex;

#define MAX_VERTICES 65536
static Vertex g_vertices[MAX_VERTICES];
static uint32_t g_vertex_count = 0;

static inline void ToNDC(float px, float py, float *nx, float *ny) {
    *nx = (px / (float)g_width) * 2.0f - 1.0f;
    *ny = 1.0f - (py / (float)g_height) * 2.0f;
}

static void PushVertex(float px, float py, float r, float g, float b) {
    if (g_vertex_count >= MAX_VERTICES) return;
    float nx, ny;
    ToNDC(px, py, &nx, &ny);
    g_vertices[g_vertex_count].x = nx;
    g_vertices[g_vertex_count].y = ny;
    g_vertices[g_vertex_count].r = r;
    g_vertices[g_vertex_count].g = g;
    g_vertices[g_vertex_count].b = b;
    g_vertex_count++;
}

static void BuildVerticesFromShapes(
    const Rect *rects, int rect_count,
    const Circle *circles, int circle_count,
    const LineObj *lines, int line_count)
{
    g_vertex_count = 0;

    for (int i = 0; i < rect_count; i++) {
        if (g_vertex_count + 6 > MAX_VERTICES) break;
        const Rect *r = &rects[i];
        float nr = r->r / 255.0f, ng = r->g / 255.0f, nb = r->b / 255.0f;
        float hw = r->hw, hh = r->hh;
        float cos_a = cosf(r->rot), sin_a = sinf(r->rot);
        float corners[4][2] = {{-hw,-hh},{hw,-hh},{hw,hh},{-hw,hh}};
        float rot[4][2];
        for (int j = 0; j < 4; j++) {
            rot[j][0] = r->x + corners[j][0]*cos_a - corners[j][1]*sin_a;
            rot[j][1] = r->y + corners[j][0]*sin_a + corners[j][1]*cos_a;
        }
        PushVertex(rot[0][0],rot[0][1],nr,ng,nb);
        PushVertex(rot[1][0],rot[1][1],nr,ng,nb);
        PushVertex(rot[2][0],rot[2][1],nr,ng,nb);
        PushVertex(rot[0][0],rot[0][1],nr,ng,nb);
        PushVertex(rot[2][0],rot[2][1],nr,ng,nb);
        PushVertex(rot[3][0],rot[3][1],nr,ng,nb);
    }

    for (int i = 0; i < circle_count; i++) {
        const int segs = 32;
        if (g_vertex_count + segs*3 > MAX_VERTICES) break;
        const Circle *c = &circles[i];
        float nr = c->r/255.0f, ng = c->g/255.0f, nb = c->b/255.0f;
        float step = 2.0f*3.14159265f/(float)segs;
        for (int j = 0; j < segs; j++) {
            float a1 = step*(float)j, a2 = step*(float)(j+1);
            PushVertex(c->x, c->y, nr, ng, nb);
            PushVertex(c->x+cosf(a1)*c->radius, c->y+sinf(a1)*c->radius, nr, ng, nb);
            PushVertex(c->x+cosf(a2)*c->radius, c->y+sinf(a2)*c->radius, nr, ng, nb);
        }
    }

    for (int i = 0; i < line_count; i++) {
        if (g_vertex_count + 6 > MAX_VERTICES) break;
        const LineObj *l = &lines[i];
        float nr = l->r/255.0f, ng = l->g/255.0f, nb = l->b/255.0f;
        float dx = l->x2-l->x1, dy = l->y2-l->y1;
        float len = sqrtf(dx*dx+dy*dy);
        if (len < 0.0001f) continue;
        float thick = (float)l->width;
        float nx = (-dy/len)*(thick*0.5f), ny = (dx/len)*(thick*0.5f);
        PushVertex(l->x1+nx,l->y1+ny,nr,ng,nb);
        PushVertex(l->x1-nx,l->y1-ny,nr,ng,nb);
        PushVertex(l->x2+nx,l->y2+ny,nr,ng,nb);
        PushVertex(l->x1-nx,l->y1-ny,nr,ng,nb);
        PushVertex(l->x2-nx,l->y2-ny,nr,ng,nb);
        PushVertex(l->x2+nx,l->y2+ny,nr,ng,nb);
    }
}

int Render_IsReady(void) {
    return g_is_ready;
}

void Render_Init(HWND hwnd, int w, int h, HINSTANCE hinst) {
    printf("[VULKAN] Render_Init %dx%d hwnd=%p hinst=%p\n", w, h, (void*)hwnd, (void*)hinst);
    g_width = (uint32_t)w;
    g_height = (uint32_t)h;
    g_is_ready = 0;

    VkApplicationInfo app_info = {
        .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
        .pApplicationName = "manim-vulkan",
        .apiVersion = VK_API_VERSION_1_0
    };
    const char *inst_exts[] = {
        VK_KHR_SURFACE_EXTENSION_NAME,
        VK_KHR_WIN32_SURFACE_EXTENSION_NAME
    };
    VkInstanceCreateInfo inst_ci = {
        .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        .pApplicationInfo = &app_info,
        .enabledExtensionCount = 2,
        .ppEnabledExtensionNames = inst_exts
    };
    if (vkCreateInstance(&inst_ci, NULL, &g_inst) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateInstance failed\n"); return;
    }
    printf("[VULKAN] Instance created\n");

    VkWin32SurfaceCreateInfoKHR surf_ci = {
        .sType = VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR,
        .hinstance = hinst, .hwnd = hwnd
    };
    if (vkCreateWin32SurfaceKHR(g_inst, &surf_ci, NULL, &g_surface) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateWin32SurfaceKHR failed\n"); return;
    }
    printf("[VULKAN] Win32 surface created\n");

    uint32_t phys_count = 0;
    vkEnumeratePhysicalDevices(g_inst, &phys_count, NULL);
    if (phys_count == 0) { fprintf(stderr, "[FATAL] No physical devices\n"); return; }

    VkPhysicalDevice *phys_devs = malloc(sizeof(VkPhysicalDevice) * phys_count);
    vkEnumeratePhysicalDevices(g_inst, &phys_count, phys_devs);

    uint32_t qfi = UINT32_MAX;
    for (uint32_t i = 0; i < phys_count && qfi == UINT32_MAX; i++) {
        uint32_t qf_count = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(phys_devs[i], &qf_count, NULL);
        VkQueueFamilyProperties *qfp = malloc(sizeof(VkQueueFamilyProperties) * qf_count);
        vkGetPhysicalDeviceQueueFamilyProperties(phys_devs[i], &qf_count, qfp);
        for (uint32_t j = 0; j < qf_count; j++) {
            VkBool32 present = VK_FALSE;
            vkGetPhysicalDeviceSurfaceSupportKHR(phys_devs[i], j, g_surface, &present);
            if ((qfp[j].queueFlags & VK_QUEUE_GRAPHICS_BIT) && present) {
                g_phy_dev = phys_devs[i]; qfi = j; break;
            }
        }
        free(qfp);
    }
    free(phys_devs);
    if (qfi == UINT32_MAX) { fprintf(stderr, "[FATAL] No suitable queue family\n"); return; }
    printf("[VULKAN] Physical device selected, queue family: %u\n", qfi);

    float prio = 1.0f;
    VkDeviceQueueCreateInfo dq_ci = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
        .queueFamilyIndex = qfi, .queueCount = 1, .pQueuePriorities = &prio
    };
    const char *dev_exts[] = { VK_KHR_SWAPCHAIN_EXTENSION_NAME };
    VkDeviceCreateInfo dev_ci = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        .queueCreateInfoCount = 1, .pQueueCreateInfos = &dq_ci,
        .enabledExtensionCount = 1, .ppEnabledExtensionNames = dev_exts
    };
    if (vkCreateDevice(g_phy_dev, &dev_ci, NULL, &g_dev) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateDevice failed\n"); return;
    }
    vkGetDeviceQueue(g_dev, qfi, 0, &g_queue);
    printf("[VULKAN] Logical device created\n");

    VkSurfaceCapabilitiesKHR caps;
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR(g_phy_dev, g_surface, &caps);

    uint32_t fmt_count = 0;
    vkGetPhysicalDeviceSurfaceFormatsKHR(g_phy_dev, g_surface, &fmt_count, NULL);
    VkSurfaceFormatKHR *fmts = malloc(sizeof(VkSurfaceFormatKHR) * fmt_count);
    vkGetPhysicalDeviceSurfaceFormatsKHR(g_phy_dev, g_surface, &fmt_count, fmts);
    VkSurfaceFormatKHR chosen_fmt = fmts[0];
    for (uint32_t i = 0; i < fmt_count; i++) {
        if (fmts[i].format == VK_FORMAT_B8G8R8A8_SRGB &&
            fmts[i].colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR) {
            chosen_fmt = fmts[i]; break;
        }
    }
    free(fmts);

    VkSwapchainCreateInfoKHR sc_ci = {
        .sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
        .surface = g_surface,
        .minImageCount = caps.minImageCount + 1,
        .imageFormat = chosen_fmt.format,
        .imageColorSpace = chosen_fmt.colorSpace,
        .imageExtent = { g_width, g_height },
        .imageArrayLayers = 1,
        .imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
        .imageSharingMode = VK_SHARING_MODE_EXCLUSIVE,
        .preTransform = caps.currentTransform,
        .compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
        .presentMode = VK_PRESENT_MODE_FIFO_KHR,
        .clipped = VK_TRUE
    };
    if (vkCreateSwapchainKHR(g_dev, &sc_ci, NULL, &g_swapchain) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateSwapchainKHR failed\n"); return;
    }
    vkGetSwapchainImagesKHR(g_dev, g_swapchain, &g_image_count, NULL);
    VkImage *sw_imgs = malloc(sizeof(VkImage) * g_image_count);
    vkGetSwapchainImagesKHR(g_dev, g_swapchain, &g_image_count, sw_imgs);

    g_swapchain_views = malloc(sizeof(VkImageView) * g_image_count);
    for (uint32_t i = 0; i < g_image_count; i++) {
        VkImageViewCreateInfo iv_ci = {
            .sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
            .image = sw_imgs[i], .viewType = VK_IMAGE_VIEW_TYPE_2D,
            .format = chosen_fmt.format,
            .subresourceRange = { VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1 }
        };
        vkCreateImageView(g_dev, &iv_ci, NULL, &g_swapchain_views[i]);
    }
    free(sw_imgs);
    printf("[VULKAN] Swapchain created with %u images\n", g_image_count);

    VkAttachmentDescription att = {
        .format = chosen_fmt.format, .samples = VK_SAMPLE_COUNT_1_BIT,
        .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
        .storeOp = VK_ATTACHMENT_STORE_OP_STORE,
        .stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
        .stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,
        .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
        .finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
    };
    VkAttachmentReference cref = { .attachment = 0, .layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL };
    VkSubpassDescription sub = {
        .pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS,
        .colorAttachmentCount = 1, .pColorAttachments = &cref
    };
    VkRenderPassCreateInfo rp_ci = {
        .sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
        .attachmentCount = 1, .pAttachments = &att,
        .subpassCount = 1, .pSubpasses = &sub
    };
    if (vkCreateRenderPass(g_dev, &rp_ci, NULL, &g_render_pass) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateRenderPass failed\n"); return;
    }
    printf("[VULKAN] RenderPass created\n");

    g_framebuffers = malloc(sizeof(VkFramebuffer) * g_image_count);
    for (uint32_t i = 0; i < g_image_count; i++) {
        VkFramebufferCreateInfo fb_ci = {
            .sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
            .renderPass = g_render_pass,
            .attachmentCount = 1,
            .pAttachments = &g_swapchain_views[i],
            .width = g_width,
            .height = g_height,
            .layers = 1
        };
        if (vkCreateFramebuffer(g_dev, &fb_ci, NULL, &g_framebuffers[i]) != VK_SUCCESS) {
            fprintf(stderr, "[FATAL] vkCreateFramebuffer failed\n"); return;
        }
    }
    printf("[VULKAN] Framebuffers created\n");

    VkPipelineLayoutCreateInfo pl_ci = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO
    };
    if (vkCreatePipelineLayout(g_dev, &pl_ci, NULL, &g_pipeline_layout) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreatePipelineLayout failed\n"); return;
    }
    printf("[VULKAN] PipelineLayout created\n");

    VkShaderModuleCreateInfo vert_mi = {
        .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
        .codeSize = sizeof(vert_spv), .pCode = vert_spv
    };
    if (vkCreateShaderModule(g_dev, &vert_mi, NULL, &g_vert_mod) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] Vertex shader module creation failed\n"); return;
    }
    VkShaderModuleCreateInfo frag_mi = {
        .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
        .codeSize = sizeof(frag_spv), .pCode = frag_spv
    };
    if (vkCreateShaderModule(g_dev, &frag_mi, NULL, &g_frag_mod) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] Fragment shader module creation failed\n"); return;
    }
    printf("[VULKAN] Shader modules created\n");

    VkPipelineShaderStageCreateInfo stages[2] = {
        { .sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
          .stage = VK_SHADER_STAGE_VERTEX_BIT, .module = g_vert_mod, .pName = "main" },
        { .sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
          .stage = VK_SHADER_STAGE_FRAGMENT_BIT, .module = g_frag_mod, .pName = "main" }
    };
    VkVertexInputBindingDescription bind_desc = {
        .binding = 0, .stride = sizeof(Vertex), .inputRate = VK_VERTEX_INPUT_RATE_VERTEX
    };
    VkVertexInputAttributeDescription attr_descs[2] = {
        { .location = 0, .binding = 0, .format = VK_FORMAT_R32G32_SFLOAT,    .offset = offsetof(Vertex, x) },
        { .location = 1, .binding = 0, .format = VK_FORMAT_R32G32B32_SFLOAT, .offset = offsetof(Vertex, r) }
    };
    VkPipelineVertexInputStateCreateInfo vi = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
        .vertexBindingDescriptionCount = 1, .pVertexBindingDescriptions = &bind_desc,
        .vertexAttributeDescriptionCount = 2, .pVertexAttributeDescriptions = attr_descs
    };
    VkPipelineInputAssemblyStateCreateInfo ia = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
        .topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST
    };
    VkViewport viewport = { 0, 0, (float)g_width, (float)g_height, 0.0f, 1.0f };
    VkRect2D scissor = { {0,0}, {g_width, g_height} };
    VkPipelineViewportStateCreateInfo vp = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
        .viewportCount = 1, .pViewports = &viewport,
        .scissorCount = 1, .pScissors = &scissor
    };
    VkPipelineRasterizationStateCreateInfo rs = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
        .polygonMode = VK_POLYGON_MODE_FILL, .cullMode = VK_CULL_MODE_NONE,
        .frontFace = VK_FRONT_FACE_CLOCKWISE, .lineWidth = 1.0f
    };
    VkPipelineMultisampleStateCreateInfo ms = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
        .rasterizationSamples = VK_SAMPLE_COUNT_1_BIT
    };
    VkPipelineColorBlendAttachmentState cba = {
        .colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT |
                          VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT
    };
    VkPipelineColorBlendStateCreateInfo cb = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
        .attachmentCount = 1, .pAttachments = &cba
    };
    VkGraphicsPipelineCreateInfo pipe_ci = {
        .sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
        .stageCount = 2, .pStages = stages,
        .pVertexInputState = &vi, .pInputAssemblyState = &ia,
        .pViewportState = &vp, .pRasterizationState = &rs,
        .pMultisampleState = &ms, .pColorBlendState = &cb,
        .pDepthStencilState = NULL,
        .pDynamicState = NULL,
        .layout = g_pipeline_layout,
        .renderPass = g_render_pass,
        .subpass = 0
    };
    VkResult res = vkCreateGraphicsPipelines(g_dev, VK_NULL_HANDLE, 1, &pipe_ci, NULL, &g_pipeline);
    if (res != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateGraphicsPipelines failed VkResult=%d\n", (int)res);
        return;
    }
    printf("[VULKAN] Graphics pipeline created\n");

    VkCommandPoolCreateInfo cp_ci = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
        .flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
        .queueFamilyIndex = qfi
    };
    if (vkCreateCommandPool(g_dev, &cp_ci, NULL, &g_cmd_pool) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateCommandPool failed\n"); return;
    }
    VkCommandBufferAllocateInfo cb_ai = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
        .commandPool = g_cmd_pool, .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
        .commandBufferCount = 1
    };
    if (vkAllocateCommandBuffers(g_dev, &cb_ai, &g_cmd_buf) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkAllocateCommandBuffers failed\n"); return;
    }
    VkFenceCreateInfo fence_ci = {
        .sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO,
        .flags = VK_FENCE_CREATE_SIGNALED_BIT
    };
    if (vkCreateFence(g_dev, &fence_ci, NULL, &g_fence) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateFence failed\n"); return;
    }
    printf("[VULKAN] CommandPool, CommandBuffer, Fence created\n");

    VkBufferCreateInfo buf_ci = {
        .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
        .size = sizeof(Vertex) * MAX_VERTICES,
        .usage = VK_BUFFER_USAGE_VERTEX_BUFFER_BIT
    };
    if (vkCreateBuffer(g_dev, &buf_ci, NULL, &g_vertex_buffer) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkCreateBuffer failed\n"); return;
    }

    VkMemoryRequirements mem_req;
    vkGetBufferMemoryRequirements(g_dev, g_vertex_buffer, &mem_req);

    VkPhysicalDeviceMemoryProperties mem_props;
    vkGetPhysicalDeviceMemoryProperties(g_phy_dev, &mem_props);

    uint32_t mem_type_idx = 0;
    for (uint32_t i = 0; i < mem_props.memoryTypeCount; i++) {
        if ((mem_req.memoryTypeBits & (1 << i)) &&
            (mem_props.memoryTypes[i].propertyFlags & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) &&
            (mem_props.memoryTypes[i].propertyFlags & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)) {
            mem_type_idx = i;
            break;
        }
    }

    VkMemoryAllocateInfo alloc_info = {
        .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
        .allocationSize = mem_req.size,
        .memoryTypeIndex = mem_type_idx
    };
    if (vkAllocateMemory(g_dev, &alloc_info, NULL, &g_vertex_memory) != VK_SUCCESS) {
        fprintf(stderr, "[FATAL] vkAllocateMemory failed\n"); return;
    }
    vkBindBufferMemory(g_dev, g_vertex_buffer, g_vertex_memory, 0);
    printf("[VULKAN] Vertex buffer created\n");

    g_is_ready = 1;
    printf("[VULKAN] Render_Init complete, g_is_ready=1\n");
}

void Render_DrawScene(
    const Rect *rects, int rect_count,
    const Circle *circles, int circle_count,
    const LineObj *lines, int line_count)
{
    if (!g_is_ready) return;

    BuildVerticesFromShapes(rects, rect_count, circles, circle_count, lines, line_count);
    if (g_vertex_count == 0) return;

    void *mapped = NULL;
    vkMapMemory(g_dev, g_vertex_memory, 0, sizeof(Vertex) * g_vertex_count, 0, &mapped);
    memcpy(mapped, g_vertices, sizeof(Vertex) * g_vertex_count);
    vkUnmapMemory(g_dev, g_vertex_memory);

    vkWaitForFences(g_dev, 1, &g_fence, VK_TRUE, UINT64_MAX);
    vkResetFences(g_dev, 1, &g_fence);

    uint32_t image_index = 0;
    VkResult acquire_res = vkAcquireNextImageKHR(g_dev, g_swapchain, UINT64_MAX, VK_NULL_HANDLE, g_fence, &image_index);
    if (acquire_res == VK_ERROR_OUT_OF_DATE_KHR || acquire_res == VK_SUBOPTIMAL_KHR) {
        // TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO 
        return;
    }
    vkWaitForFences(g_dev, 1, &g_fence, VK_TRUE, UINT64_MAX);
    vkResetFences(g_dev, 1, &g_fence);

    vkResetCommandBuffer(g_cmd_buf, 0);

    VkCommandBufferBeginInfo begin_info = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
        .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
    };
    vkBeginCommandBuffer(g_cmd_buf, &begin_info);

    VkClearValue clear_color = { .color = {{0.0f, 0.0f, 0.0f, 1.0f}} };
    VkRenderPassBeginInfo rp_begin = {
        .sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
        .renderPass = g_render_pass,
        .framebuffer = g_framebuffers[image_index],
        .renderArea = { .offset = {0, 0}, .extent = {g_width, g_height} },
        .clearValueCount = 1,
        .pClearValues = &clear_color
    };
    vkCmdBeginRenderPass(g_cmd_buf, &rp_begin, VK_SUBPASS_CONTENTS_INLINE);

    vkCmdBindPipeline(g_cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_pipeline);

    VkDeviceSize offset = 0;
    vkCmdBindVertexBuffers(g_cmd_buf, 0, 1, &g_vertex_buffer, &offset);

    vkCmdDraw(g_cmd_buf, g_vertex_count, 1, 0, 0);

    vkCmdEndRenderPass(g_cmd_buf);
    vkEndCommandBuffer(g_cmd_buf);

    VkSubmitInfo submit_info = {
        .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
        .commandBufferCount = 1,
        .pCommandBuffers = &g_cmd_buf
    };
    vkQueueSubmit(g_queue, 1, &submit_info, g_fence);

    VkPresentInfoKHR present_info = {
        .sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
        .waitSemaphoreCount = 0,
        .swapchainCount = 1,
        .pSwapchains = &g_swapchain,
        .pImageIndices = &image_index
    };
    vkQueuePresentKHR(g_queue, &present_info);

    printf("[VULKAN] Drew %u vertices (%u triangles)\n", g_vertex_count, g_vertex_count / 3);
}

void Render_Cleanup(void) {
    g_is_ready = 0;
    if (g_dev != VK_NULL_HANDLE) vkDeviceWaitIdle(g_dev);

    if (g_vertex_memory != VK_NULL_HANDLE)   { vkFreeMemory(g_dev, g_vertex_memory, NULL);           g_vertex_memory = VK_NULL_HANDLE; }
    if (g_vertex_buffer != VK_NULL_HANDLE)   { vkDestroyBuffer(g_dev, g_vertex_buffer, NULL);        g_vertex_buffer = VK_NULL_HANDLE; }
    if (g_fence != VK_NULL_HANDLE)           { vkDestroyFence(g_dev, g_fence, NULL);                 g_fence = VK_NULL_HANDLE; }
    if (g_cmd_pool != VK_NULL_HANDLE)        { vkDestroyCommandPool(g_dev, g_cmd_pool, NULL);        g_cmd_pool = VK_NULL_HANDLE; }
    if (g_pipeline != VK_NULL_HANDLE)        { vkDestroyPipeline(g_dev, g_pipeline, NULL);           g_pipeline = VK_NULL_HANDLE; }
    if (g_pipeline_layout != VK_NULL_HANDLE) { vkDestroyPipelineLayout(g_dev, g_pipeline_layout, NULL); g_pipeline_layout = VK_NULL_HANDLE; }
    if (g_vert_mod != VK_NULL_HANDLE)        { vkDestroyShaderModule(g_dev, g_vert_mod, NULL);       g_vert_mod = VK_NULL_HANDLE; }
    if (g_frag_mod != VK_NULL_HANDLE)        { vkDestroyShaderModule(g_dev, g_frag_mod, NULL);       g_frag_mod = VK_NULL_HANDLE; }

    if (g_framebuffers) {
        for (uint32_t i = 0; i < g_image_count; i++) {
            if (g_framebuffers[i] != VK_NULL_HANDLE)
                vkDestroyFramebuffer(g_dev, g_framebuffers[i], NULL);
        }
        free(g_framebuffers);
        g_framebuffers = NULL;
    }

    if (g_render_pass != VK_NULL_HANDLE)     { vkDestroyRenderPass(g_dev, g_render_pass, NULL);      g_render_pass = VK_NULL_HANDLE; }

    if (g_swapchain_views) {
        for (uint32_t i = 0; i < g_image_count; i++) {
            if (g_swapchain_views[i] != VK_NULL_HANDLE)
                vkDestroyImageView(g_dev, g_swapchain_views[i], NULL);
        }
        free(g_swapchain_views);
        g_swapchain_views = NULL;
    }
    if (g_swapchain != VK_NULL_HANDLE) { vkDestroySwapchainKHR(g_dev, g_swapchain, NULL); g_swapchain = VK_NULL_HANDLE; }
    if (g_dev != VK_NULL_HANDLE)       { vkDestroyDevice(g_dev, NULL);                    g_dev = VK_NULL_HANDLE; }
    if (g_surface != VK_NULL_HANDLE)   { vkDestroySurfaceKHR(g_inst, g_surface, NULL);    g_surface = VK_NULL_HANDLE; }
    if (g_inst != VK_NULL_HANDLE)      { vkDestroyInstance(g_inst, NULL);                 g_inst = VK_NULL_HANDLE; }

    printf("[VULKAN] Shutdown complete\n");
}