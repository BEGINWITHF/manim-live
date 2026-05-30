#include "platform_macos.h"
#include "vulkan_render.h"
#include <stdio.h>
#include <string.h>
#include <Cocoa/Cocoa.h>
#include <pthread.h>

// macOS-specific window management
static NSWindow* g_window = NULL;
static NSView* g_view = NULL;
static NSApplication* g_app = NULL;
static BOOL g_running = YES;

// Shape storage
static ShapeRect g_rects[MAX_SHAPES];
static int g_rect_count = 0;

static ShapeCircle g_circles[MAX_SHAPES];
static int g_circle_count = 0;

static ShapeLine g_lines[MAX_SHAPES];
static int g_line_count = 0;

// Event handling
static pthread_mutex_t g_event_mutex = PTHREAD_MUTEX_INITIALIZER;

@interface VulkanView : NSView
@end

@implementation VulkanView
- (void)drawRect:(NSRect)dirtyRect {
    [[NSColor colorWithCalibratedRed:0.05 green:0.05 blue:0.05 alpha:1.0] setFill];
    NSRectFill(dirtyRect);

    pthread_mutex_lock(&g_event_mutex);

    for (int i = 0; i < g_rect_count; i++) {
        ShapeRect r = g_rects[i];
        [[NSColor colorWithCalibratedRed:r.r / 255.0 green:r.g / 255.0 blue:r.b / 255.0 alpha:1.0] setFill];
        NSAffineTransform *transform = [NSAffineTransform transform];
        [transform translateXBy:r.x yBy:r.y];
        [transform rotateByRadians:r.rot];
        [transform concat];
        NSRectFill(NSMakeRect(-r.hw, -r.hh, r.hw * 2.0, r.hh * 2.0));
        [transform invert];
        [transform concat];
    }

    for (int i = 0; i < g_circle_count; i++) {
        ShapeCircle c = g_circles[i];
        [[NSColor colorWithCalibratedRed:c.r / 255.0 green:c.g / 255.0 blue:c.b / 255.0 alpha:1.0] setFill];
        NSBezierPath *path = [NSBezierPath bezierPathWithOvalInRect:NSMakeRect(c.x - c.radius, c.y - c.radius, c.radius * 2.0, c.radius * 2.0)];
        [path fill];
    }

    for (int i = 0; i < g_line_count; i++) {
        ShapeLine l = g_lines[i];
        [[NSColor colorWithCalibratedRed:l.r / 255.0 green:l.g / 255.0 blue:l.b / 255.0 alpha:1.0] setStroke];
        NSBezierPath *path = [NSBezierPath bezierPath];
        [path setLineWidth:l.width];
        [path moveToPoint:NSMakePoint(l.x1, l.y1)];
        [path lineToPoint:NSMakePoint(l.x2, l.y2)];
        [path stroke];
    }

    pthread_mutex_unlock(&g_event_mutex);
}
@end

@interface VulkanAppDelegate : NSObject <NSApplicationDelegate>
@end

@implementation VulkanAppDelegate
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    // Application finished launching
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES;
}

- (void)applicationWillTerminate:(NSNotification *)notification {
    g_running = NO;
}
@end

PLATFORM_EXPORT int Vulkan_Init(int w, int h) {
    printf("[DEBUG] Vulkan_Init enter w=%d h=%d\n", w, h);
    fflush(stdout);

    // Initialize NSApplication if not already done
    if (!g_app) {
        g_app = [NSApplication sharedApplication];
        [g_app setActivationPolicy:NSApplicationActivationPolicyRegular];
        
        // Set up delegate
        VulkanAppDelegate* delegate = [[VulkanAppDelegate alloc] init];
        [g_app setDelegate:delegate];
    }

    // Create window
    NSRect frame = NSMakeRect(100, 100, w, h);
    NSUInteger styleMask = NSWindowStyleMaskTitled | 
                          NSWindowStyleMaskClosable | 
                          NSWindowStyleMaskMiniaturizable | 
                          NSWindowStyleMaskResizable;
    
    g_window = [[NSWindow alloc] initWithContentRect:frame
                                          styleMask:styleMask
                                            backing:NSBackingStoreBuffered
                                              defer:NO];
    
    [g_window setTitle:@"Manim Vulkan"];
    [g_window center];
    [g_window makeKeyAndOrderFront:nil];
    
    // Create view for Vulkan rendering
    g_view = [[VulkanView alloc] initWithFrame:frame];
    [g_window setContentView:g_view];
    
    // Initialize Vulkan renderer
    Render_Init((__bridge void*)g_view, w, h, NULL);
    
    if (!Render_IsReady()) {
        fprintf(stderr, "[ERROR] Vulkan renderer failed to initialize\n");
        return 0;
    }
    
    printf("[INFO] Vulkan_Init succeeded (%dx%d)\n", w, h);
    fflush(stdout);
    return 1;
}

PLATFORM_EXPORT void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b) {
    pthread_mutex_lock(&g_event_mutex);
    if (g_rect_count < MAX_SHAPES) {
        g_rects[g_rect_count++] = (ShapeRect){ x, y, hw, hh, rot, r, g, b };
        printf("[C] AddRect #%d: pos=(%.2f,%.2f) size=(%.2f,%.2f) rgba=(%d,%d,%d)\n",
               g_rect_count - 1, x, y, hw, hh, r, g, b);
        fflush(stdout);
    }
    pthread_mutex_unlock(&g_event_mutex);
}

PLATFORM_EXPORT void AddCircle(float x, float y, float radius, int r, int g, int b) {
    pthread_mutex_lock(&g_event_mutex);
    if (g_circle_count < MAX_SHAPES) {
        g_circles[g_circle_count++] = (ShapeCircle){ x, y, radius, r, g, b };
    }
    pthread_mutex_unlock(&g_event_mutex);
}

PLATFORM_EXPORT void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b) {
    pthread_mutex_lock(&g_event_mutex);
    if (g_line_count < MAX_SHAPES) {
        g_lines[g_line_count++] = (ShapeLine){ x1, y1, x2, y2, width, r, g, b };
    }
    pthread_mutex_unlock(&g_event_mutex);
}

PLATFORM_EXPORT void AddText(const char* text, float x, float y, int size, int r, int g, int b) {
    // TODO: Implement text rendering for macOS
}

PLATFORM_EXPORT void ClearShapes(void) {
    pthread_mutex_lock(&g_event_mutex);
    g_rect_count = 0;
    g_circle_count = 0;
    g_line_count = 0;
    pthread_mutex_unlock(&g_event_mutex);
}

PLATFORM_EXPORT int Vulkan_Tick(void) {
    if (!g_running) {
        return 0;
    }
    
    // Process Cocoa events
    while (true) {
        NSEvent* event = [g_app nextEventMatchingMask:NSEventMaskAny
                                           untilDate:[NSDate distantPast]
                                              inMode:NSDefaultRunLoopMode
                                             dequeue:YES];
        if (!event) break;
        
        [g_app sendEvent:event];
    }
    
    if (g_window && [g_window isVisible]) {
        pthread_mutex_lock(&g_event_mutex);
        printf("[C] Vulkan_Tick: rects=%d circles=%d lines=%d\n",
               g_rect_count, g_circle_count, g_line_count);
        fflush(stdout);
        
        Render_DrawScene(g_rects, g_rect_count,
                        g_circles, g_circle_count,
                        g_lines, g_line_count);
        [g_view setNeedsDisplay:YES];
        pthread_mutex_unlock(&g_event_mutex);
        return 1;
    }
    
    return 0;
}

PLATFORM_EXPORT void Vulkan_Shutdown(void) {
    Render_Cleanup();
    
    if (g_window) {
        [g_window close];
        g_window = nil;
    }
    
    if (g_view) {
        g_view = nil;
    }
    
    g_running = NO;
}
