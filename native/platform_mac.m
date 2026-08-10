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

    // Calculate window size (macOS uses content rect, no AdjustWindowRect needed).
    // Preserve the REQUESTED aspect ratio: macOS clamps oversized windows to
    // fit the screen, which would distort the aspect (e.g. a 1920x1080 window
    // on a 1366x1024-pt screen becomes ~1710x981) and squish the scene
    // horizontally. Instead, size the window to the largest rect with the
    // requested aspect that fits the visible screen frame.
    NSRect screenFrame = [[NSScreen mainScreen] visibleFrame];
    double req_aspect = (double)w / (double)h;
    double screen_aspect = screenFrame.size.width / screenFrame.size.height;
    int cw, ch;
    if (screen_aspect > req_aspect) {
        // Screen is wider: window height = min(requested, screen height)
        ch = (h < (int)screenFrame.size.height) ? h : (int)screenFrame.size.height;
        cw = (int)(ch * req_aspect + 0.5);
    } else {
        // Screen is narrower: window width = min(requested, screen width)
        cw = (w < (int)screenFrame.size.width) ? w : (int)screenFrame.size.width;
        ch = (int)(cw / req_aspect + 0.5);
    }
    w = cw;
    h = ch;
    g_aspect_ratio = (double)w / (double)h;
    g_min_width = w / 4;
    if (g_min_width < 320) g_min_width = 320;

    NSRect frame = NSMakeRect(0, 0, w, h);
    // Center the window
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
    // Must match the Vulkan swapchain format (VK_FORMAT_B8G8R8A8_SRGB)
    // or sRGB-encoded colors are displayed as linear -> washed out.
    g_metal_layer.pixelFormat = MTLPixelFormatBGRA8Unorm_sRGB;
    g_metal_layer.framebufferOnly = NO;
    g_metal_layer.frame = g_view.bounds;
    g_metal_layer.opaque = YES;
    g_metal_layer.contentsScale = [g_window backingScaleFactor];
    // Render at physical pixel resolution (points x retina scale) so edges
    // stay crisp instead of being upscaled.
    CGFloat scale = g_metal_layer.contentsScale;
    if (scale < 1.0) scale = 1.0;
    int px_w = (int)(NSWidth([g_view bounds]) * scale + 0.5);
    int px_h = (int)(NSHeight([g_view bounds]) * scale + 0.5);
    g_metal_layer.drawableSize = CGSizeMake(px_w, px_h);

    [g_view setLayer:g_metal_layer];
    [g_view setWantsLayer:YES];

    // Set up window delegate for close handling
    g_delegate = [[ManimWindowDelegate alloc] init];
    [g_window setDelegate:g_delegate];

    g_win_w = px_w;
    g_win_h = px_h;

    // Initialize Vulkan renderer with the CAMetalLayer (physical pixel size)
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

    // Keep the swapchain in sync with the actual view size (physical pixels).
    // On Retina the view is in points; the layer's drawableSize is pixels.
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

    // Return the swapchain size (physical pixels) packed as int, so the
    // Python side computes coordinates in the same space as the viewport.
    return (((int)g_swapchain_ext.width & 0xFFFF) << 16) |
           ((int)g_swapchain_ext.height & 0xFFFF);
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

    // CGWindowListCreateImage is deprecated (unavailable) in the macOS 15 SDK
    // but still present at runtime; call it via dlsym to capture the
    // CAMetalLayer window contents (NSView cacheDisplay does NOT capture
    // Metal layer content).
    CGImageRef image = NULL;
    typedef CGImageRef (*CGWindowListCreateImageFn)(CGRect, CGWindowListOption, CGWindowID, CGWindowImageOption);
    CGWindowListCreateImageFn fn = (CGWindowListCreateImageFn)dlsym(RTLD_DEFAULT, "CGWindowListCreateImage");
    if (fn) {
        CGWindowID windowID = (CGWindowID)[g_window windowNumber];
        // Retry: the window may still be appearing / not yet presented.
        for (int attempt = 0; attempt < 6 && !image; attempt++) {
            image = fn(CGRectNull,
                       kCGWindowListOptionIncludingWindow,
                       windowID,
                       kCGWindowImageBoundsIgnoreFraming);
            if (!image) usleep(50 * 1000);
        }
        // Black-frame guard: if the captured image is entirely black the
        // window was likely not presented yet — retry a couple of times.
        // Only active until the first frame with real content has been seen;
        // otherwise legitimately mostly-black frames (e.g. the early frames
        // of a Write animation on a black background) would be discarded.
        static int saw_content = 0;
        for (int attempt = 0; image && !saw_content && attempt < 4; attempt++) {
            CGDataProviderRef prov = CGImageGetDataProvider(image);
            CFDataRef cf = prov ? CGDataProviderCopyData(prov) : NULL;
            bool allBlack = true;
            if (cf) {
                const uint8_t *p = CFDataGetBytePtr(cf);
                size_t n = CFDataGetLength(cf) / 4;  // 32bpp
                for (size_t i = 0; i < n; i += 199) {  // sparse sample
                    if (p[i*4+0] || p[i*4+1] || p[i*4+2]) { allBlack = false; break; }
                }
                CFRelease(cf);
            }
            if (!allBlack) { saw_content = 1; break; }
            CFRelease(image); image = NULL;
            usleep(50 * 1000);
            image = fn(CGRectNull,
                       kCGWindowListOptionIncludingWindow,
                       windowID,
                       kCGWindowImageBoundsIgnoreFraming);
        }
    }
    if (!image) return 0;

    size_t width = CGImageGetWidth(image);
    size_t height = CGImageGetHeight(image);
    size_t bmpRowBytes = width * 4;          // 32-bit RGBA context rows
    size_t outRowBytes = ((width * 3 + 3) & ~3);  // 24-bit BMP rows
    size_t imgSize = outRowBytes * height;

    // Read the CGImage's raw pixel data via its data provider.
    // The CGImage from CGWindowListCreateImage is typically 32bpp
    // premultiplied; get the native bytes and channel layout.
    CGDataProviderRef provider = CGImageGetDataProvider(image);
    CFDataRef cfData = CGDataProviderCopyData(provider);
    if (!cfData) return 0;
    const uint8_t *raw = CFDataGetBytePtr(cfData);
    size_t rawBytesPerRow = CGImageGetBytesPerRow(image);
    size_t bitsPerPixel = CGImageGetBitsPerPixel(image);
    size_t bytesPerPixel = bitsPerPixel / 8;
    CGBitmapInfo bitmapInfo = CGImageGetBitmapInfo(image);
    // Determine channel order from byte-order flags
    bool littleEndian = (bitmapInfo & kCGBitmapByteOrder32Little) != 0;

    FILE *fp = fopen(path, "wb");
    if (!fp) {
        CFRelease(cfData);
        CGImageRelease(image);
        return 0;
    }

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
    uint32_t rowPad = (4 - (uint32_t)(width * 3 % 4)) % 4;
    uint8_t padBytes[3] = {0, 0, 0};

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

    // Write pixel rows: raw data is premultiplied; byte order flags decide
    // whether it is RGBA or BGRA. BMP wants BGR.
    // The BMP header declares biHeight = -height (bottom-up), so the FIRST
    // row written must be the BOTTOM row of the image. CGImage row 0 is the
    // TOP row — iterate the raw rows in reverse or the recording comes out
    // vertically flipped (upside-down videos).
    if (bytesPerPixel < 3) bytesPerPixel = 4;
    for (size_t y = height; y > 0; y--) {
        const uint8_t *row = raw + (y - 1) * rawBytesPerRow;
        for (size_t x = 0; x < width; x++) {
            const uint8_t *px = row + x * bytesPerPixel;
            uint8_t bgr[3];
            if (littleEndian) {      // BGRA storage
                bgr[0] = px[0]; bgr[1] = px[1]; bgr[2] = px[2];
            } else {                 // RGBA storage
                bgr[0] = px[2]; bgr[1] = px[1]; bgr[2] = px[0];
            }
            fwrite(bgr, 3, 1, fp);
        }
        if (rowPad) fwrite(padBytes, rowPad, 1, fp);
    }

    fclose(fp);
    CFRelease(cfData);
    CGImageRelease(image);
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

// Direct framebuffer readback (RGBA, exact rendered pixels)
int Vulkan_ReadPixels(unsigned char *out, int *w, int *h) {
    return Render_ReadPixels(out, w, h);
}
