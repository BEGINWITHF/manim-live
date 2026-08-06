#include "vulkan_core.h"
#include "vulkan_render.h"
#include "draw_common.h"

float g_vertices[MAX_VERTICES * 6];
uint32_t g_vertex_count = 0;

void BuildVerticesFromRects(const Rect *rects, int count);
void BuildVerticesFromCircles(const Circle *circles, int count);
void BuildVerticesFromLines(const LineObj *lines, int count);
void BuildVerticesFromEllipses(const EllipseObj *ellipses, int count);
void BuildVerticesFromPolygons(const PolygonObj *polygons, int count);
void BuildVerticesFromDashedLines(const DashedLineObj *lines, int count);
void BuildVerticesFromArcs(const ArcObj *arcs, int count);
void BuildVerticesFromPoints(const PointObj *points, int count);
void BuildVerticesFromTexts(const TextObj *texts, int count);
void BuildVerticesFromBezierPaths(void);
void BuildVerticesFromLineStrips(void);

void Render_DrawScene(const Rect* rects, int rect_count,
                      const Circle* circles, int circle_count,
                      const LineObj* lines, int line_count,
                      const EllipseObj* ellipses, int ellipse_count,
                      const PolygonObj* polygons, int polygon_count,
                      const DashedLineObj* dashed_lines, int dashed_line_count,
                      const ArcObj* arcs, int arc_count,
                      const PointObj* points, int point_count,
                      const TextObj* texts, int text_count,
                      const DrawCmd* cmds, int cmd_count) {

    g_vertex_count = 0;

    for (int i = 0; i < cmd_count; i++) {
        int idx = cmds[i].index;
        switch (cmds[i].type) {
            case CMD_RECT:
                if (idx < rect_count) BuildVerticesFromRects(&rects[idx], 1);
                break;
            case CMD_CIRCLE:
                if (idx < circle_count) BuildVerticesFromCircles(&circles[idx], 1);
                break;
            case CMD_LINE:
                if (idx < line_count) BuildVerticesFromLines(&lines[idx], 1);
                break;
            case CMD_ELLIPSE:
                if (idx < ellipse_count) BuildVerticesFromEllipses(&ellipses[idx], 1);
                break;
            case CMD_POLYGON:
                if (idx < polygon_count) BuildVerticesFromPolygons(&polygons[idx], 1);
                break;
            case CMD_DASHED_LINE:
                if (idx < dashed_line_count) BuildVerticesFromDashedLines(&dashed_lines[idx], 1);
                break;
            case CMD_ARC:
                if (idx < arc_count) BuildVerticesFromArcs(&arcs[idx], 1);
                break;
            case CMD_POINT:
                if (idx < point_count) BuildVerticesFromPoints(&points[idx], 1);
                break;
            case CMD_TEXT:
                if (idx < text_count) BuildVerticesFromTexts(&texts[idx], 1);
                break;
        }
    }

    BuildVerticesFromBezierPaths();
    BuildVerticesFromLineStrips();

    if (g_vertex_count > 0) {
        update_vertex_buffer(g_vertices, g_vertex_count * 6 * sizeof(float));
    }
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

    VkViewport vp = {0, 0, (float)g_swapchain_ext.width, (float)g_swapchain_ext.height, 0, 1};
    vkCmdSetViewport(cmd_buf, 0, 1, &vp);

    VkRect2D sc = {{0, 0}, g_swapchain_ext};
    vkCmdSetScissor(cmd_buf, 0, 1, &sc);

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
