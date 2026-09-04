// platform_mac.m - macOS native layer for real-time-manim (manim-booster)
// Objective-C: NSWindow + NSView + CAMetalLayer (MoltenVK renders into it).
// All shape/draw-command code is plain C and shared with Windows.

#import <Cocoa/Cocoa.h>
#import <QuartzCore/CAMetalLayer.h>
#import <Metal/Metal.h>

#include "platform.h"
#include "vulkan_render.h"
#include "vulkan_core.h"
#include "shared_types.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>

// ============================================================
// Shape buffers and draw commands (same as Windows platform.c)
// ============================================================
static RectObj g_rects[MAX_SHAPES];
static int g_rect_count = 0;
static CircleObj g_circles[MAX_SHAPES];
static int g_circle_count = 0;
static LineObj g_lines[MAX_SHAPES];
static int g_line_count = 0;
static EllipseObj g_ellipses[MAX_SHAPES];
static int g_ellipse_count = 0;
static PolygonObj g_polygons[MAX_SHAPES];
static int g_polygon_count = 0;
static DashedLineObj g_dashed_lines[MAX_SHAPES];
static int g_dashed_line_count = 0;
static ArcObj g_arcs[MAX_SHAPES];
static int g_arc_count = 0;
static PointObj g_points[MAX_SHAPES];
static int g_point_count = 0;
static TextObj g_texts[MAX_SHAPES];
static int g_text_count = 0;

#define CMD_RECT 0
#define CMD_CIRCLE 1
#define CMD_LINE 2
#define CMD_ELLIPSE 3
#define CMD_POLYGON 4
#define CMD_DASHED_LINE 5
#define CMD_ARC 6
#define CMD_POINT 7
#define CMD_TEXT 8

#define MAX_DRAW_CMDS 16384
static DrawCmd g_draw_cmds[MAX_DRAW_CMDS];
static int g_draw_cmd_count = 0;

static double g_aspect_ratio = 16.0 / 9.0;
static int g_min_width = 320;

// ============================================================
// macOS window state
// ============================================================
static NSWindow* g_window = nil;
static NSView* g_view = nil;
static CAMetalLayer* g_metal_layer = nil;
static bool g_window_should_close = false;

// Window-close delegate so Vulkan_Tick can report the window is gone.
@interface ManimWindowDelegate : NSObject <NSWindowDelegate>
@end

@implementation ManimWindowDelegate
- (BOOL)windowShouldClose:(NSWindow *)sender {
    g_window_should_close = true;
    return YES;
}
@end

static ManimWindowDelegate* g_delegate = nil;

// ============================================================
// Vulkan_Init - create the window with a CAMetalLayer
// ============================================================
PLATFORM_EXPORT int Vulkan_Init(int w, int h) {
    if (![NSApplication sharedApplication]) {
        [NSApplication sharedApplication];
    }
    [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
    [NSApp activateIgnoringOtherApps:YES];

    // macOS uses content rects (no AdjustWindowRect). Preserve the REQUESTED
    // aspect ratio: macOS clamps oversized windows to fit the screen
    // non-uniformly (a 1920x1080 request can become ~1710x981 points),
    // which would squish the scene horizontally. Size the window to the
    // largest rect with the requested aspect that fits the visible frame.
    NSRect screenFrame = [[NSScreen mainScreen] visibleFrame];
    double req_aspect = (double)w / (double)h;
    double screen_aspect = screenFrame.size.width / screenFrame.size.height;
    int cw, ch;
    if (screen_aspect > req_aspect) {
        ch = (h < (int)screenFrame.size.height) ? h : (int)screenFrame.size.height;
        cw = (int)(ch * req_aspect + 0.5);
    } else {
        cw = (w < (int)screenFrame.size.width) ? w : (int)screenFrame.size.width;
        ch = (int)(cw / req_aspect + 0.5);
    }
    w = cw;
    h = ch;
    g_aspect_ratio = (double)w / (double)h;
    g_min_width = w / 4;
    if (g_min_width < 320) g_min_width = 320;

    NSRect frame = NSMakeRect(0, 0, w, h);
    frame.origin.x = (screenFrame.size.width - w) / 2;
    frame.origin.y = (screenFrame.size.height - h) / 2;

    NSUInteger styleMask = NSWindowStyleMaskTitled |
                           NSWindowStyleMaskClosable |
                           NSWindowStyleMaskMiniaturizable |
                           NSWindowStyleMaskResizable;

    g_window = [[NSWindow alloc] initWithContentRect:frame
                                           styleMask:styleMask
                                             backing:NSBackingStoreBuffered
                                               defer:NO];
    if (!g_window) {
        fprintf(stderr, "[FATAL] NSWindow creation failed\n");
        return 0;
    }

    [g_window setTitle:@"Real Time Manim"];
    [g_window setOpaque:YES];
    [g_window setBackgroundColor:[NSColor blackColor]];

    g_view = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, w, h)];
    [g_view setWantsLayer:YES];
    [g_window setContentView:g_view];

    g_metal_layer = [CAMetalLayer layer];
    g_metal_layer.device = MTLCreateSystemDefaultDevice();
    // Must match the Vulkan swapchain format (VK_FORMAT_B8G8R8A8_UNORM):
    // MoltenVK renders into the drawable's Metal texture; the sRGB layer
    // encodes shader output on write and the compositor decodes it on
    // display, so net appearance matches the Windows UNORM swapchain.
    g_metal_layer.pixelFormat = MTLPixelFormatBGRA8Unorm_sRGB;
    g_metal_layer.framebufferOnly = NO;
    g_metal_layer.frame = g_view.bounds;
    g_metal_layer.opaque = YES;
    g_metal_layer.contentsScale = [g_window backingScaleFactor];
    // Render at PHYSICAL pixel resolution (points x retina scale) so edges
    // stay crisp; the swapchain must match this exact size (see tick()).
    CGFloat scale = g_metal_layer.contentsScale;
    if (scale < 1.0) scale = 1.0;
    int px_w = (int)(NSWidth([g_view bounds]) * scale + 0.5);
    int px_h = (int)(NSHeight([g_view bounds]) * scale + 0.5);
    g_metal_layer.drawableSize = CGSizeMake(px_w, px_h);

    [g_view setLayer:g_metal_layer];
    [g_view setWantsLayer:YES];

    g_delegate = [[ManimWindowDelegate alloc] init];
    [g_window setDelegate:g_delegate];

    // Initialize the Vulkan renderer with the layer (physical pixel size).
    Render_Init((__bridge void*)g_metal_layer, px_w, px_h);
    if (!Render_IsReady()) {
        fprintf(stderr, "[ERROR] Vulkan renderer failed to initialize\n");
        return 0;
    }

    [g_window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];

    return 1;
}

// ============================================================
// Vulkan_Tick - process Cocoa events, sync size, render a frame
// ============================================================
PLATFORM_EXPORT int Vulkan_Tick(void) {
    NSEvent *event;
    while ((event = [NSApp nextEventMatchingMask:NSEventMaskAny
                                       untilDate:[NSDate distantPast]
                                          inMode:NSDefaultRunLoopMode
                                         dequeue:YES])) {
        [NSApp sendEvent:event];
    }

    if (g_window_should_close || ![g_window isVisible]) {
        return 0;
    }

    // Keep the swapchain in sync with the actual view size in PHYSICAL
    // pixels (view bounds are points; drawableSize is pixels).
    CGFloat scale = [g_window backingScaleFactor];
    if (scale < 1.0) scale = 1.0;
    int dw = (int)(NSWidth([g_view bounds]) * scale + 0.5);
    int dh = (int)(NSHeight([g_view bounds]) * scale + 0.5);
    g_metal_layer.drawableSize = CGSizeMake(dw, dh);
    if (dw != (int)g_swapchain_ext.width || dh != (int)g_swapchain_ext.height) {
        ResizeSwapchain(dw, dh);
    }
    g_framebuffer_resized = false;

    Render_DrawScene(
        g_rects, g_rect_count,
        g_circles, g_circle_count,
        g_lines, g_line_count,
        g_ellipses, g_ellipse_count,
        g_polygons, g_polygon_count,
        g_dashed_lines, g_dashed_line_count,
        g_arcs, g_arc_count,
        g_points, g_point_count,
        g_texts, g_text_count,
        g_draw_cmds, g_draw_cmd_count
    );
    extern uint32_t g_vertex_count;
    Render_DrawFrame(g_vertex_count);

    // Return the SWAPCHAIN size (physical pixels) packed as int — the Python
    // side computes coordinates in that exact space.
    return (((int)g_swapchain_ext.width & 0xFFFF) << 16) |
           ((int)g_swapchain_ext.height & 0xFFFF);
}

// ============================================================
// Vulkan_Shutdown
// ============================================================
PLATFORM_EXPORT void Vulkan_Shutdown(void) {
    Render_Cleanup();
    if (g_window) {
        [g_window close];
        g_window = nil;
    }
    g_view = nil;
    g_metal_layer = nil;
    g_delegate = nil;
}

// ============================================================
// SaveScreenshot - exact framebuffer readback to a BMP file
// ============================================================
// Copies the LAST DRAWN frame (captured inside the draw command buffer,
// before present — MoltenVK crashes on reads of presented drawables) into
// a host-visible staging buffer, then writes it as a 24-bit BMP.
//
// Call semantics: when no fresh frame has been drawn since the last call,
// this arms the readback request and returns 0; the NEXT Vulkan_Tick frame
// performs the copy, and a subsequent call returns 1 with the BMP written.
// The record worker calls it once per interval and only advances its frame
// index on success — pending calls are cheap (a flag write, no GPU stall).
PLATFORM_EXPORT int SaveScreenshot(const char *path) {
    if (!g_is_ready || !g_staging_buf || !g_swapchain) return 0;
    int w = (int)g_swapchain_ext.width;
    int h = (int)g_swapchain_ext.height;
    if (w <= 0 || h <= 0) return 0;

    if (!g_readback_available) {
        g_readback_requested = 1;   // next drawn frame is copied into staging
        return 0;
    }

    // Wait only for the frame that performed the copy (its in-flight fence),
    // not the whole device: a full vkDeviceWaitIdle drains the present
    // pipeline every capture and throttles recording to ~10 fps.
    if (g_readback_fence_idx < g_swapchain_img_count) {
        vkWaitForFences(g_dev, 1, &g_in_flight_fences[g_readback_fence_idx],
                        VK_TRUE, UINT64_MAX);
    }
    void *mapped = NULL;
    if (vkMapMemory(g_dev, g_staging_mem, 0, g_staging_size, 0, &mapped) != VK_SUCCESS) return 0;

    int rowBytes = ((w * 3 + 3) & ~3);
    int padN = rowBytes - w * 3;
    FILE *fp = fopen(path, "wb");
    if (!fp) {
        vkUnmapMemory(g_dev, g_staging_mem);
        return 0;
    }
    setvbuf(fp, NULL, _IOFBF, 1 << 20);

    // BMP header. NEGATIVE biHeight = top-down: the readback buffer's row 0
    // is the image TOP row and rows are written in order, so a positive
    // biHeight would flip the video (verified: PIL and ffmpeg both decode
    // positive-height BMPs bottom-up).
    uint32_t imgSize = (uint32_t)rowBytes * (uint32_t)h;
    uint8_t header[54] = {0};
    header[0] = 'B'; header[1] = 'M';
    uint32_t u32;
    u32 = 54 + imgSize;  memcpy(header + 2,  &u32, 4);   // bfSize
    u32 = 54;            memcpy(header + 10, &u32, 4);   // bfOffBits
    u32 = 40;            memcpy(header + 14, &u32, 4);   // biSize
    int32_t i32 = w;     memcpy(header + 18, &i32, 4);   // biWidth
    i32 = -h;            memcpy(header + 22, &i32, 4);   // biHeight (top-down)
    uint16_t u16 = 1;    memcpy(header + 26, &u16, 2);   // biPlanes
    u16 = 24;            memcpy(header + 28, &u16, 2);   // biBitCount
    memcpy(header + 34, &imgSize, 4);                    // biSizeImage
    fwrite(header, 54, 1, fp);

    // BGRA (GPU) -> BGR rows, one fwrite per row (3.7M single-pixel
    // fwrites would take seconds).
    const unsigned char *src = (const unsigned char *)mapped;
    unsigned char *rowbuf = (unsigned char *)malloc((size_t)rowBytes);
    if (rowbuf) {
        static const unsigned char zeros[4] = {0, 0, 0, 0};
        for (int y = 0; y < h; y++) {
            const unsigned char *row = src + (size_t)y * (size_t)w * 4;
            for (int x = 0; x < w; x++) {
                rowbuf[x * 3 + 0] = row[x * 4 + 0];  // B
                rowbuf[x * 3 + 1] = row[x * 4 + 1];  // G
                rowbuf[x * 3 + 2] = row[x * 4 + 2];  // R
            }
            if (padN) memcpy(rowbuf + w * 3, zeros, (size_t)padN);
            fwrite(rowbuf, 1, (size_t)rowBytes, fp);
        }
        free(rowbuf);
    }
    fclose(fp);

    vkUnmapMemory(g_dev, g_staging_mem);
    g_readback_available = 0;
    return 1;
}

// ============================================================
// Vulkan_ReadPixels - exact framebuffer readback (two-phase)
// ============================================================
// Phase 1 requests the copy of the NEXT drawn frame (returns 0); the caller
// ticks the renderer and calls again; phase 2 returns the RGBA pixels.
PLATFORM_EXPORT int Vulkan_ReadPixels(unsigned char *out, int *w, int *h) {
    return Render_ReadPixels(out, w, h);
}

// ============================================================
// Drawing command functions (same as Windows)
// ============================================================
PLATFORM_EXPORT void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_rect_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_rects[g_rect_count] = (RectObj){ x, y, hw, hh, rot, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_RECT, g_rect_count };
        g_rect_count++;
    }
}

PLATFORM_EXPORT void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_circle_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_circles[g_circle_count] = (CircleObj){ x, y, radius, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_CIRCLE, g_circle_count };
        g_circle_count++;
    }
}

PLATFORM_EXPORT void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float alpha) {
    if (g_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_lines[g_line_count] = (LineObj){ x1, y1, x2, y2, width, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_LINE, g_line_count };
        g_line_count++;
    }
}

PLATFORM_EXPORT void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_ellipse_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_ellipses[g_ellipse_count] = (EllipseObj){ x, y, rx, ry, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ELLIPSE, g_ellipse_count };
        g_ellipse_count++;
    }
}

PLATFORM_EXPORT void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts, float stroke_progress, float alpha, int close_path) {
    if (g_polygon_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS && vert_count <= MAX_POLYGON_VERTS) {
        PolygonObj* p = &g_polygons[g_polygon_count];
        p->x = x; p->y = y;
        p->r = r; p->g = g; p->b = b;
        p->border_r = border_r; p->border_g = border_g; p->border_b = border_b;
        p->border_width = border_width;
        p->vert_count = vert_count;
        p->stroke_progress = stroke_progress;
        p->alpha = alpha;
        p->close_path = close_path;
        memcpy(p->verts, verts, sizeof(float) * vert_count * 2);
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_POLYGON, g_polygon_count };
        g_polygon_count++;
    }
}

PLATFORM_EXPORT void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length, float alpha) {
    if (g_dashed_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_dashed_lines[g_dashed_line_count] = (DashedLineObj){ x1, y1, x2, y2, width, r, g, b, dash_length, gap_length, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_DASHED_LINE, g_dashed_line_count };
        g_dashed_line_count++;
    }
}

PLATFORM_EXPORT void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width, float alpha) {
    if (g_arc_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_arcs[g_arc_count] = (ArcObj){ x, y, radius, start_angle, angle, r, g, b, stroke_width, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ARC, g_arc_count };
        g_arc_count++;
    }
}

PLATFORM_EXPORT void AddPoint(float x, float y, int r, int g, int b, float alpha) {
    if (g_point_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_points[g_point_count] = (PointObj){ x, y, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_POINT, g_point_count };
        g_point_count++;
    }
}

PLATFORM_EXPORT void AddText(float x, float y, int r, int g, int b, float font_size, float opacity, const char* text, float alpha) {
    if (g_text_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS && text) {
        TextObj* t = &g_texts[g_text_count];
        t->x = x; t->y = y;
        t->r = r; t->g = g; t->b = b;
        t->font_size = font_size;
        t->opacity = opacity;
        t->alpha = alpha;
        int len = 0;
        while (text[len] && len < MAX_TEXT_LEN - 1) {
            t->text[len] = text[len];
            len++;
        }
        t->text[len] = '\0';
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_TEXT, g_text_count };
        g_text_count++;
    }
}

PLATFORM_EXPORT void ClearShapes(void) {
    g_rect_count = 0;
    g_circle_count = 0;
    g_line_count = 0;
    g_ellipse_count = 0;
    g_polygon_count = 0;
    g_dashed_line_count = 0;
    g_arc_count = 0;
    g_point_count = 0;
    g_text_count = 0;
    g_draw_cmd_count = 0;
}
