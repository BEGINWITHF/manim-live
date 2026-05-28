#include "vulkan_core.h"
#include <string.h>
#include <math.h>

#define MAX_VERTICES 65536
static float g_vertices[MAX_VERTICES * 5];
static uint32_t g_vertex_count = 0;

static inline void ToNDC(float px, float py, float *nx, float *ny) {
    *nx = (px / (float)g_swapchain_ext.width) * 2.0f - 1.0f;
    *ny = 1.0f - (py / (float)g_swapchain_ext.height) * 2.0f;
}

static void PushVertex(float px, float py, float r, float g, float b) {
    if (g_vertex_count >= MAX_VERTICES) return;
    float nx, ny;
    ToNDC(px, py, &nx, &ny);
    uint32_t idx = g_vertex_count * 5;
    g_vertices[idx + 0] = nx;
    g_vertices[idx + 1] = ny;
    g_vertices[idx + 2] = r;
    g_vertices[idx + 3] = g;
    g_vertices[idx + 4] = b;
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

void RecordCommandBuffer(VkCommandBuffer cmd_buf, uint32_t img_idx,
                         const Rect *rects, int rect_count,
                         const Circle *circles, int circle_count,
                         const LineObj *lines, int line_count) {
    VkCommandBufferBeginInfo bi = {0};
    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    vkBeginCommandBuffer(cmd_buf, &bi);

    VkClearValue clear = {{{0.05f, 0.05f, 0.05f, 1.0f}}};
    VkRenderPassBeginInfo rpbi = {0};
    rpbi.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
    rpbi.renderPass = g_render_pass;
    rpbi.framebuffer = g_framebuffers[img_idx];
    rpbi.renderArea.offset = (VkOffset2D){0, 0};
    rpbi.renderArea.extent = g_swapchain_ext;
    rpbi.clearValueCount = 1;
    rpbi.pClearValues = &clear;

    vkCmdBeginRenderPass(cmd_buf, &rpbi, VK_SUBPASS_CONTENTS_INLINE);
    vkCmdBindPipeline(cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_pipeline);

    VkBuffer bufs[] = {g_vert_buf};
    VkDeviceSize offsets[] = {0};
    vkCmdBindVertexBuffers(cmd_buf, 0, 1, bufs, offsets);

    uint32_t total_verts = g_vertex_count;

    if (total_verts > 0) {
        vkCmdDraw(cmd_buf, total_verts, 1, 0, 0);
    }

    vkCmdEndRenderPass(cmd_buf);
    vkEndCommandBuffer(cmd_buf);
}

void CleanupSwapchain(void) {
    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroyFramebuffer(g_dev, g_framebuffers[i], NULL);
        vkDestroyImageView(g_dev, g_swapchain_img_views[i], NULL);
    }
    free(g_framebuffers); g_framebuffers = NULL;
    free(g_swapchain_img_views); g_swapchain_img_views = NULL;
    free(g_swapchain_imgs); g_swapchain_imgs = NULL;
    vkDestroySwapchainKHR(g_dev, g_swapchain, NULL);
}

void RecreateSwapchain(void) {
    vkDeviceWaitIdle(g_dev);
    CleanupSwapchain();
    CreateSwapchain();
    CreateImageViews();
    CreateFramebuffers();
}

void Render_DrawScene(const Rect *rects, int rect_count,
                      const Circle *circles, int circle_count,
                      const LineObj *lines, int line_count) {
    printf("[DRAW] called: rects=%d circles=%d lines=%d ready=%d\n", 
           rect_count, circle_count, line_count, g_is_ready);
    if (!g_is_ready) return;
    
    vkWaitForFences(g_dev, 1, &g_in_flight_fences[g_current_frame], VK_TRUE, UINT64_MAX);
    vkResetFences(g_dev, 1, &g_in_flight_fences[g_current_frame]);

    uint32_t img_idx;
    VkResult res = vkAcquireNextImageKHR(g_dev, g_swapchain, UINT64_MAX,
                                          g_img_avail_sems[g_current_frame],
                                          VK_NULL_HANDLE, &img_idx);
    if (res == VK_ERROR_OUT_OF_DATE_KHR) { RecreateSwapchain(); return; }

    // Build vertices from shapes
    BuildVerticesFromShapes(rects, rect_count, circles, circle_count, lines, line_count);
    uint32_t total_verts = g_vertex_count;

    if (total_verts > 0) {
        void *mapped;
        vkMapMemory(g_dev, g_vert_buf_mem, 0, total_verts * sizeof(float) * 5, 0, &mapped);
        memcpy(mapped, g_vertices, total_verts * sizeof(float) * 5);
        vkUnmapMemory(g_dev, g_vert_buf_mem);
    }

    RecordCommandBuffer(g_cmd_bufs[img_idx], img_idx,
                        rects, rect_count, circles, circle_count, lines, line_count);

    VkSemaphore wait_sems[] = {g_img_avail_sems[g_current_frame]};
    VkPipelineStageFlags wait_stages[] = {VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT};
    VkSemaphore signal_sems[] = {g_render_done_sems[g_current_frame]};

    VkSubmitInfo si = {0};
    si.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
    si.waitSemaphoreCount = 1;
    si.pWaitSemaphores = wait_sems;
    si.pWaitDstStageMask = wait_stages;
    si.commandBufferCount = 1;
    si.pCommandBuffers = &g_cmd_bufs[img_idx];
    si.signalSemaphoreCount = 1;
    si.pSignalSemaphores = signal_sems;

    vkQueueSubmit(g_gfx_queue, 1, &si, g_in_flight_fences[g_current_frame]);

    VkPresentInfoKHR pi = {0};
    pi.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
    pi.waitSemaphoreCount = 1;
    pi.pWaitSemaphores = signal_sems;
    pi.swapchainCount = 1;
    pi.pSwapchains = &g_swapchain;
    pi.pImageIndices = &img_idx;

    res = vkQueuePresentKHR(g_present_queue, &pi);
    if (res == VK_ERROR_OUT_OF_DATE_KHR || res == VK_SUBOPTIMAL_KHR) {
        RecreateSwapchain();
    }

    g_current_frame = (g_current_frame + 1) % g_swapchain_img_count;
}

void Render_Cleanup(void) {
    if (!g_is_ready) return;
    vkDeviceWaitIdle(g_dev);

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroySemaphore(g_dev, g_img_avail_sems[i], NULL);
        vkDestroySemaphore(g_dev, g_render_done_sems[i], NULL);
        vkDestroyFence(g_dev, g_in_flight_fences[i], NULL);
    }
    free(g_img_avail_sems);     g_img_avail_sems = NULL;
    free(g_render_done_sems);   g_render_done_sems = NULL;
    free(g_in_flight_fences);   g_in_flight_fences = NULL;

    vkDestroyBuffer(g_dev, g_vert_buf, NULL);
    vkFreeMemory(g_dev, g_vert_buf_mem, NULL);

    CleanupSwapchain();

    vkDestroyPipeline(g_dev, g_pipeline, NULL);
    vkDestroyPipelineLayout(g_dev, g_pipeline_layout, NULL);
    vkDestroyRenderPass(g_dev, g_render_pass, NULL);

    if (g_cmd_bufs) {
        vkFreeCommandBuffers(g_dev, g_cmd_pool, g_cmd_buf_count, g_cmd_bufs);
        free(g_cmd_bufs);
        g_cmd_bufs = NULL;
    }

    vkDestroyCommandPool(g_dev, g_cmd_pool, NULL);
    vkDestroyDevice(g_dev, NULL);
    vkDestroySurfaceKHR(g_inst, g_surface, NULL);
    vkDestroyInstance(g_inst, NULL);

    g_is_ready = false;
}