// platform_mac.m - macOS native layer for manim-booster
// Uses Objective-C for NSWindow, NSView, CAMetalLayer
// Rest of drawing/command code is plain C

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
// macOS Window Management
// ============================================================
static NSWindow* g_window = nil;
static NSView* g_view = nil;
static CAMetalLayer* g_metal_layer = nil;
static int g_win_w = 0;
static int g_win_h = 0;
static bool g_window_should_close = false;

// We need a delegate to handle window close
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
// Vulkan_Init - Create window with CAMetalLayer
// ============================================================
int Vulkan_Init(int w, int h) {
    // Initialize Cocoa application if not already running
    if (![NSApplication sharedApplication]) {
        [NSApplication sharedApplication];
    }
    [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
    [NSApp activateIgnoringOtherApps:YES];

    g_aspect_ratio = (double)w / (double)h;
    g_min_width = w / 4;
    if (g_min_width < 320) g_min_width = 320;

    // Calculate window size (macOS uses content rect, no AdjustWindowRect needed)
    NSRect frame = NSMakeRect(0, 0, w, h);
    // Center the window
    NSRect screenFrame = [[NSScreen mainScreen] visibleFrame];
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

    [g_window setTitle:@"Manim Vulkan"];
    [g_window setOpaque:YES];
    [g_window setBackgroundColor:[NSColor blackColor]];
    [g_window makeKeyAndOrderFront:nil];

    // Create content view
    g_view = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, w, h)];
    [g_view setWantsLayer:YES];
    [g_window setContentView:g_view];

    // Create CAMetalLayer
    g_metal_layer = [CAMetalLayer layer];
    g_metal_layer.device = MTLCreateSystemDefaultDevice();
    g_metal_layer.pixelFormat = MTLPixelFormatBGRA8Unorm;
    g_metal_layer.framebufferOnly = NO;
    g_metal_layer.frame = g_view.bounds;
    g_metal_layer.opaque = YES;
    g_metal_layer.drawableSize = CGSizeMake(w, h);

    [g_view setLayer:g_metal_layer];
    [g_view setWantsLayer:YES];

    // Set up window delegate for close handling
    g_delegate = [[ManimWindowDelegate alloc] init];
    [g_window setDelegate:g_delegate];

    g_win_w = w;
    g_win_h = h;

    // Initialize Vulkan renderer with the CAMetalLayer
    Render_Init((__bridge void*)g_metal_layer, w, h);

    if (!Render_IsReady()) {
        fprintf(stderr, "[ERROR] Vulkan renderer failed to initialize\n");
        return 0;
    }

    [g_window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];

    return 1;
}

// ============================================================
// Vulkan_Tick - Process events + render
// ============================================================
int Vulkan_Tick(void) {
    // Process pending Cocoa events
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

    if (g_framebuffer_resized) {
        g_framebuffer_resized = false;
        RecreateSwapchain();
    }

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

    // Return window size as packed int (same as Windows version)
    NSRect contentRect = [g_view bounds];
    int cw = (int)contentRect.size.width;
    int ch = (int)contentRect.size.height;
    return (cw << 16) | (ch & 0xFFFF);
}

// ============================================================
// Vulkan_Shutdown - Clean up
// ============================================================
void Vulkan_Shutdown(void) {
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
// SaveScreenshot - Capture window content via CGImage
// ============================================================
int SaveScreenshot(const char *path) {
    if (!g_window || ![g_window isVisible]) return 0;

    NSView *view = [g_window contentView];
    NSRect bounds = [view bounds];
    NSBitmapImageRep *rep = [view bitmapImageRepForCachingDisplayInRect:bounds];
    if (!rep) return 0;

    [view cacheDisplayInRect:bounds toBitmapImageRep:rep];

    size_t width = (size_t)[rep pixelsWide];
    size_t height = (size_t)[rep pixelsHigh];
    size_t rowBytes = ((width * 3 + 3) & ~3);
    size_t imgSize = rowBytes * height;
    unsigned char *srcData = [rep bitmapData];
    size_t srcRowBytes = [rep bytesPerRow];
    NSUInteger srcBPP = [rep bitsPerPixel] / 8;

    FILE *fp = fopen(path, "wb");
    if (!fp) return 0;

    // Write BMP header
    uint32_t bfType = 0x4D42;
    uint32_t bfOffBits = 54;
    uint32_t bfSize = bfOffBits + (uint32_t)imgSize;
    uint32_t biSize = 40;
    int32_t biWidth = (int32_t)width;
    int32_t biHeight = -(int32_t)height;
    uint16_t biPlanes = 1;
    uint16_t biBitCount = 24;
    uint32_t biCompression = 0;
    uint32_t biSizeImage = (uint32_t)imgSize;
    uint16_t reserved = 0;

    fwrite(&bfType, 2, 1, fp);
    fwrite(&bfSize, 4, 1, fp);
    fwrite(&reserved, 2, 1, fp);
    fwrite(&reserved, 2, 1, fp);
    fwrite(&bfOffBits, 4, 1, fp);
    fwrite(&biSize, 4, 1, fp);
    fwrite(&biWidth, 4, 1, fp);
    fwrite(&biHeight, 4, 1, fp);
    fwrite(&biPlanes, 2, 1, fp);
    fwrite(&biBitCount, 2, 1, fp);
    fwrite(&biCompression, 4, 1, fp);
    fwrite(&biSizeImage, 4, 1, fp);
    uint32_t zero32 = 0;
    fwrite(&zero32, 4, 1, fp);
    fwrite(&zero32, 4, 1, fp);
    fwrite(&zero32, 4, 1, fp);
    fwrite(&zero32, 4, 1, fp);

    // Write pixel data: NSBitmapImageRep is RGBA, BMP expects BGR (bottom-up)
    for (int32_t y = 0; y < (int32_t)height; y++) {
        unsigned char *row = srcData + y * srcRowBytes;
        for (size_t x = 0; x < width; x++) {
            // RGBA -> BGR
            unsigned char *px = row + x * srcBPP;
            uint8_t bgr[3] = { px[2], px[1], px[0] };
            fwrite(bgr, 3, 1, fp);
        }
    }

    fclose(fp);
    return 1;
}

// ============================================================
// Drawing command functions (same as Windows)
// ============================================================

void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_rect_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_rects[g_rect_count] = (RectObj){ x, y, hw, hh, rot, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_RECT, g_rect_count };
        g_rect_count++;
    }
}

void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_circle_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_circles[g_circle_count] = (CircleObj){ x, y, radius, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_CIRCLE, g_circle_count };
        g_circle_count++;
    }
}

void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float alpha) {
    if (g_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_lines[g_line_count] = (LineObj){ x1, y1, x2, y2, width, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_LINE, g_line_count };
        g_line_count++;
    }
}

void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_ellipse_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_ellipses[g_ellipse_count] = (EllipseObj){ x, y, rx, ry, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ELLIPSE, g_ellipse_count };
        g_ellipse_count++;
    }
}

void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts, float stroke_progress, float alpha, int close_path) {
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

void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length, float alpha) {
    if (g_dashed_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_dashed_lines[g_dashed_line_count] = (DashedLineObj){ x1, y1, x2, y2, width, r, g, b, dash_length, gap_length, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_DASHED_LINE, g_dashed_line_count };
        g_dashed_line_count++;
    }
}

void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width, float alpha) {
    if (g_arc_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_arcs[g_arc_count] = (ArcObj){ x, y, radius, start_angle, angle, r, g, b, stroke_width, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ARC, g_arc_count };
        g_arc_count++;
    }
}

void AddPoint(float x, float y, int r, int g, int b, float alpha) {
    if (g_point_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_points[g_point_count] = (PointObj){ x, y, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_POINT, g_point_count };
        g_point_count++;
    }
}

void AddText(float x, float y, int r, int g, int b, float font_size, float opacity, const char* text, float alpha) {
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

void ClearShapes(void) {
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
