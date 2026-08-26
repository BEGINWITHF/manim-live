# Manim-Booster (Manteraction)

A **Vulkan-accelerated rendering backend** for [ManimCE](https://www.manim.community/) that replaces the default OpenGL/Cairo renderer with a custom GPU pipeline for real-time mathematical animation rendering on Windows.

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2B-lightgrey.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Rendering Pipeline](#rendering-pipeline)
- [Animation System](#animation-system)
- [Shape Dispatch](#shape-dispatch)
- [Recording System](#recording-system)
- [MathTex Rendering](#mathtex-rendering)
- [Getting Started](#getting-started)
- [Running Demo Scenes](#running-demo-scenes)
- [Building the Native DLL](#building-the-native-dll)
- [Writing Custom Scenes](#writing-custom-scenes)
- [Key Design Decisions](#key-design-decisions)

---

## Overview

Manim-Booster bridges ManimCE's Python-based animation system with a native Vulkan rendering engine. Instead of relying on OpenGL or Cairo for drawing, it:

1. **Translates** Manim mobjects into typed shape commands (rectangles, circles, lines, beziers, text, etc.)
2. **Sends** those commands across a ctypes boundary to a native C/C++ DLL
3. **Renders** them via a Vulkan GPU pipeline at real-time frame rates
4. **Captures** frames as BMP screenshots and encodes them to MP4 via ffmpeg

The result is a fast, windowed renderer that can produce high-quality video output of any Manim scene.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Python Layer                          │
│                                                         │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  Scene    │──▶│ VulkanRender │──▶│  ShapeMixin /  │  │
│  │ (ManimCE) │   │   .play()    │   │  TextMixin     │  │
│  └──────────┘   └──────┬───────┘   └───────┬────────┘  │
│                        │                    │           │
│              ┌─────────▼────────────────────▼─────┐     │
│              │     ctypes FFI (DLL bindings)      │     │
│              └─────────────────┬──────────────────┘     │
├────────────────────────────────┼────────────────────────┤
│                    Native Layer│ (vulkan_core.dll)       │
│              ┌─────────────────▼──────────────────┐     │
│              │   platform.c — Win32 window +      │     │
│              │   shape buffers + command queue     │     │
│              ├────────────────────────────────────┤     │
│              │   vulkan_init.c — Vulkan instance, │     │
│              │   device, swapchain, pipeline       │     │
│              ├────────────────────────────────────┤     │
│              │   vulkan_draw.c — vertex generation│     │
│              │   + GPU submission                  │     │
│              ├────────────────────────────────────┤     │
│              │   draw/ — per-shape vertex builders│     │
│              │   (rect, circle, line, bezier,      │     │
│              │    polygon, arc, text, dashed_line)  │     │
│              └────────────────────────────────────┘     │
│                          │                              │
│                    ┌─────▼─────┐                        │
│                    │  Vulkan   │                        │
│                    │    GPU    │                        │
│                    └───────────┘                        │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
manim-booster/
├── run.py                          # Entry point — demo menu + scene runner
├── requirements.txt                # Python dependencies (manim, numpy)
├── README.md                       # This file
├── DEMO_FEATURES.md                # Detailed parameter reference for all 81 demos
├── LICENSE                         # GPLv3
│
├── core/                           # Python rendering layer
│   ├── __init__.py
│   ├── vulkan_bind.py              # VulkanRender class — main bridge (1740 lines)
│   ├── vulkan_shapes.py            # ShapeMixin — shape-specific senders (626 lines)
│   ├── vulkan_text.py              # TextMixin — text/bezier rendering
│   ├── vulkan_util.py              # Coordinate conversion, color helpers
│   ├── rate_functions.py           # Easing functions (_smooth, _linear, etc.)
│   ├── animations/                 # Custom animation implementations
│   │   ├── __init__.py             # Animation registry + import overrides
│   │   ├── base.py                 # Base Animation class + opacity/rotation tracking
│   │   ├── transform.py            # Transform, ReplacementTransform
│   │   ├── fade_transform.py       # FadeTransform
│   │   ├── create.py               # Create (draw outline)
│   │   ├── write.py                # Write (handwriting simulation)
│   │   ├── fade_in.py / fade_out.py
│   │   ├── ... (30+ animation modules)
│   │   └── wait.py
│   └── utils/
│       └── paths.py
│
├── scenes/
│   └── demo_scene.py               # 81 demo scenes (menu system)
│
├── native/                         # C/C++ Vulkan engine
│   ├── platform.h / platform.c     # Win32 window, DLL entry, shape buffers
│   ├── vulkan_core.h               # Global Vulkan state declarations
│   ├── vulkan_init.c               # Vulkan instance/device/swapchain setup
│   ├── vulkan_render.h             # Render API (DrawCmd, Render_DrawScene)
│   ├── vulkan_draw.c               # Vertex generation + GPU submission
│   ├── shared_types.h              # Shape data structures (Rect, Circle, etc.)
│   ├── draw_common.h               # NDC conversion, vertex push helpers
│   ├── stb_truetype.h              # Font rasterizer (stb library)
│   ├── build.ps1                   # PowerShell build script
│   └── draw/                       # Per-shape vertex builders
│       ├── draw_rect.c
│       ├── draw_circle.c
│       ├── draw_line.c
│       ├── draw_ellipse.c
│       ├── draw_polygon.c
│       ├── draw_arc.c
│       ├── draw_bezier.c
│       ├── draw_text.c
│       ├── draw_dashed_line.c
│       └── draw_point.c
│
├── dist/                           # Compiled DLL output
│   ├── release/vulkan_core.dll
│   └── debug/vulkan_core.dll
│
├── tex_cache/                      # Cached LaTeX SVG output
└── downloaded_videos/              # Generated MP4 files
```

---

## Rendering Pipeline

### Frame Lifecycle

Each frame follows this sequence:

```
1. play(*animations)          — Manim entry point
   │
   ├─ begin()                 — Set start_time on each animation
   │
   └─ Main Loop (per frame):
      │
      ├─ time.step(dt)        — Compute elapsed time
      │
      ├─ interpolate(alpha)   — Each animation updates mobject state
      │   ├─ Transform: morphs points between source → target
      │   ├─ FadeIn/FadeOut: adjusts opacity via _anim_opacity
      │   ├─ Create: advances _vulkan_progress (0→1)
      │   └─ Rotating: accumulates rotation via _anim_rotation
      │
      ├─ tick()               — Process Win32 messages (resize, close)
      │   └─ Returns current window dimensions
      │
      ├─ sync(scene)          — Traverse scene.mobjects recursively
      │   ├─ ClearShapes()    — Reset DLL command buffer
      │   └─ _send(mob)       — Type-dispatch each mobject
      │       ├─ Square/Rectangle → _send_square/_send_polygon
      │       ├─ Circle/Ellipse  → _send_circle/_send_ellipse
      │       ├─ Line/Arrow      → _send_line/_send_arrow
      │       ├─ Polygon/Polygram → _send_polygon
      │       ├─ Text            → _send_text (DLL AddText)
      │       ├─ VGroup/Group    → recurse into submobjects
      │       └─ VMobject        → _send_vmobject (bezier path)
      │
      ├─ [DLL] Render_DrawScene()  — Convert shapes → vertices → GPU
      │   ├─ BuildVerticesFromRects/Circles/Lines/...
      │   ├─ Upload vertex buffer
      │   └─ Vulkan draw call → swapchain present
      │
      └─ [Optional] SaveScreenshot() → BMP → ffmpeg → MP4
```

### Coordinate System

Manim uses a centered coordinate system with Y-up:

```
Manim:  (-7.1 → +7.1, -4.0 → +4.0)     Screen: (0 → 1920, 0 → 1080)
        Y-axis points UP                  Y-axis points DOWN
```

The `manim_to_screen()` function in `vulkan_util.py` performs this conversion:

```python
sx = cx + x * (w / frame_width)     # frame_width = w * 8.0 / h
sy = cy - y * (h / 8.0)             # Manim's default frame height = 8 units
```

### Vertex Format

Each vertex uses 6 floats: `[ndc_x, ndc_y, r, g, b, alpha]`

NDC (Normalized Device Coordinates) maps screen pixels to [-1, +1] range:

```c
ndc_x = (pixel_x / width)  * 2.0 - 1.0
ndc_y = (pixel_y / height) * 2.0 - 1.0
```

---

## Animation System

### Base Animation Class (`core/animations/base.py`)

All animations inherit from `Animation` which provides:

- **`begin(t)`** — Records start time
- **`interpolate(alpha)`** — Calls `interpolate_mobject(rate_func(alpha))`
- **`finish()`** — Marks animation complete, triggers `clean_up_from_scene()`
- **`get_sub_alpha()`** — Stagger calculation for `lag_ratio`

### Opacity & Rotation Tracking

Manim-Booster maintains per-mobject state in module-level dictionaries:

```python
_anim_opacity[id(mob)]    = 0.0..1.0    # Current fade level
_anim_rotation[id(mob)]   = radians     # Accumulated rotation
```

These are propagated through VGroup hierarchies during `sync()`.

### Supported Animations (30+ modules)

| Category | Animations |
|----------|-----------|
| **Transforms** | Transform, ReplacementTransform, FadeTransform, TransformMatchingShapes, TransformMatchingTex |
| **Drawing** | Create, Uncreate, DrawBorderThenFill, ShowIncreasingSubsets, SpiralIn |
| **Fading** | FadeIn, FadeOut, FadeToColor |
| **Movement** | MoveToTarget, MoveAlongPath, ApplyPointwiseFunction |
| **Scaling** | GrowFromCenter, GrowFromEdge, GrowFromPoint, GrowArrow, SpinInFromNothing |
| **Text** | Write, Unwrite, TypeWithCursor, UntypeWithCursor |
| **Effects** | Indicate, Flash, FocusOn, ShowPassingFlash, Wiggle, Circumscribe, ApplyWave, Blink |
| **Rotation** | Rotating, Rotate, ClockwiseTransform, CounterclockwiseTransform |
| **Groups** | AnimationGroup, LaggedStart, LaggedStartMap, Succession |
| **Special** | TracedPath, DissipatingPath, AnimatedBoundary, ChangeSpeed |
| **Math** | Homotopy, WarpSquare, Broadcast, ApplyMatrix |

---

## Shape Dispatch

The `_send()` method in `VulkanRender` recursively traverses the mobject tree and dispatches each leaf to a type-specific sender:

```python
def _send(self, mob, angle, parent_alpha, ...):
    if isinstance(mob, Text):
        # → AddText() via DLL
    elif isinstance(mob, VGroup):
        # → recurse into submobjects
    elif isinstance(mob, Square):
        # → AddRect() for fill + AddLine() for stroke edges
    elif isinstance(mob, Circle):
        # → AddCircle() for fill + tessellated AddLine() for stroke
    elif isinstance(mob, Arrow):
        # → AddLine() shaft + AddPolygon() tip triangle
    elif isinstance(mob, Polygon):
        # → AddPolygon() with vertex array
    elif isinstance(mob, VMobject):
        # → AddBezierPath() with control points
    ...
```

### Shape → DLL Mapping

| Manim Type | DLL Function | Notes |
|------------|-------------|-------|
| `Square`, `Rectangle` | `AddRect` | Fill rect + line edges for stroke |
| `Circle` | `AddCircle` | Fill circle + tessellated stroke segments |
| `Ellipse` | `AddEllipse` | Fill ellipse + tessellated stroke |
| `Line`, `DashedLine` | `AddLine` / `AddDashedLine` | With progress for Create animation |
| `Arrow` | `AddLine` + `AddPolygon` | Shaft line + triangular tip |
| `Polygon`, `Polygram` | `AddPolygon` | Vertex array with close path |
| `Arc` | `AddArc` | Arc segment |
| `Dot`, `Point` | `AddCircle` / `AddPoint` | Small filled circle |
| `Text` | `AddText` | TrueType font rendering via stb_truetype |
| `VMobject` (generic) | `AddBezierPath` | Bezier curve tessellation |

### Transform Handling

When a mobject has `_transforming = True`, the renderer bypasses shape-specific dispatchers and uses `_send_vmobject()` which renders the mobject as a generic bezier path. This is essential for:

- **Transform**: Points morph between source → target shape
- **ApplyMethod**: Pointwise functions warp the geometry
- **ClockwiseTransform**: Rotation + point modification

The exception is axis-aligned quads (Square/Rectangle) during rotation — these use the polygon path for solid fills.

---

## Recording System

### 1. Live GDI Recording

Uses a background thread that captures via Windows GDI `PrintWindow`:

```python
renderer.start_record("output.mp4", fps=60)
scene.construct()                          # Runs with live window
renderer.stop_record()                     # BMP frames → ffmpeg → MP4
```

**Process:**
- Background thread calls `screenshot_printwindow()` at target FPS
- Captures client area via `BitBlt(SRCCOPY)`
- Saves BMP frames to a temp directory
- `stop_record()` encodes frames with ffmpeg at actual capture FPS

### 2. Fast Offline Recording

Renders at maximum speed with simulated time (no window display):

```python
renderer.enable_fast_record("output.mp4", fps=60, hidden=True)
scene.construct()                          # Runs at full speed
renderer._finish_fast_record()             # Pipe BMP → ffmpeg
```

**Two sub-modes:**
- **Pipe mode** (default): `SaveScreenshot()` → parse BMP → pipe raw BGR to ffmpeg stdin
- **BMP mode** (segmented): Individual BMP files per frame, for parallel encoding

### 3. Run.py Integration

`run.py` monkey-patches `VulkanRender` to auto-record:

```python
VulkanRender.__init__ = patched_init    # Calls start_record() after init
VulkanRender.close = patched_close      # Calls stop_record() before shutdown
```

---

## MathTex Rendering

Manim-Booster supports two modes for mathematical typesetting:

### LaTeX Mode (Default)

```python
_USE_NATIVE_MATHTEX = False  # Uses real LaTeX compilation
```

- Compiles TeX → DVI → SVG via Manim's built-in pipeline
- Requires MiKTeX or TeX Live installed
- Full LaTeX fidelity: fractions, matrices, integrals, etc.
- SVG output is cached in `tex_cache/` for reuse

### Native Mode (No LaTeX)

```python
_USE_NATIVE_MATHTEX = True   # Bypasses LaTeX entirely
```

- Converts LaTeX commands → Unicode characters (400+ mappings)
- Renders via `Text` mobjects with TrueType fonts
- Handles superscripts/subscripts with manual positioning
- Fast but limited: no fractions, matrices, or complex layouts

### LaTeX → Unicode Mappings

The system includes comprehensive mappings for:
- Greek letters (α, β, γ, δ, ...)
- Binary operators (±, ×, ÷, ⊕, ...)
- Relations (≤, ≥, ≠, ≈, ...)
- Arrows (←, →, ↔, ⇒, ...)
- Set theory (∪, ∩, ∈, ∅, ...)
- Hebrew (ℵ, ℶ, ℸ)
- Delimiters and structural commands

---

## Getting Started

### Prerequisites

- **Windows 10** (64-bit)
- **Python 3.11+**
- **Vulkan SDK** (for building the native DLL)
- **MiKTeX or TeX Live** (optional, for LaTeX mode)
- **ffmpeg** (for video recording, must be in PATH)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd manim-booster

# Install Python dependencies
pip install -r requirements.txt

# Build the native DLL (requires Vulkan SDK + MSVC)
cd native
.\build.ps1
```

### Quick Test

```bash
# Run demo scene #1 (Create)
python run.py 1

# Run all demos
python run.py
# Then enter the scene number when prompted
```

---

## Running Demo Scenes

`run.py` provides 81 demo scenes covering all supported animations:

```bash
python run.py          # Interactive menu
python run.py 1        # Direct: Create (draw shapes)
python run.py 6        # Direct: FadeTransform (crossfade)
python run.py 13       # Direct: Text rendering
python run.py 80       # Direct: Fourier Transform epicycles
python run.py 81       # Direct: Lorenz Attractor
```

### Scene Categories

| # | Category | Scenes |
|---|----------|--------|
| 1–10 | Basic shapes & transforms | Create, Write, Transform, FadeIn/Out, VGroup, All Shapes |
| 11–20 | Timing & grouping | Succession, LagRatios, AnimatedBoundary, TracedPath |
| 21–30 | Text & effects | LaggedStart, DrawBorderThenFill, TypeWithCursor |
| 31–40 | Fade variants | FadeIn, FadeOut, GrowFromCenter/Edge/Point |
| 41–50 | Special animations | SpinInFromNothing, Blink, Flash, FocusOn |
| 51–60 | Advanced transforms | Wiggle, Homotopy, MoveAlongPath, SpeedModifier |
| 61–70 | Composition | ClockwiseTransform, CyclicReplace, FadeToColor |
| 71–81 | Complex scenes | Restore, ScaleInPlace, Anagram, LaTeX, Fourier, Lorenz |

Output videos are saved to `downloaded_videos/`.

---

## Building the Native DLL

The native C/C++ code compiles to `vulkan_core.dll`:

```powershell
cd native
.\build.ps1
```

**Requirements:**
- Visual Studio 2022 (MSVC compiler)
- Vulkan SDK (headers + libraries)

**Build outputs:**
- `dist/release/vulkan_core.dll` (optimized)
- `dist/debug/vulkan_core.dll` (debug symbols)

### DLL API

The DLL exports these functions via `platform.h`:

```c
// Lifecycle
int  Vulkan_Init(int w, int h);      // Create window + init Vulkan
int  Vulkan_Tick(void);              // Process messages, return dimensions
void Vulkan_Shutdown(void);          // Cleanup

// Shape submission
void AddRect(float x, y, hw, hh, rot, r, g, b, br, bg, bb, bw, progress, alpha);
void AddCircle(float x, y, radius, r, g, b, br, bg, bb, bw, progress, alpha);
void AddLine(float x1, y1, x2, y2, width, r, g, b, alpha);
void AddEllipse(float x, y, rx, ry, ...);
void AddPolygon(float x, y, ..., const float* verts, int count, ...);
void AddDashedLine(float x1, y1, x2, y2, ...);
void AddArc(float x, y, radius, start_angle, angle, ...);
void AddPoint(float x, y, r, g, b, alpha);
void AddText(float x, y, r, g, b, font_size, opacity, const char* text, alpha);
void AddBezierPath(const float* points, int num, ...);

// Font loading
int Text_LoadFont(const unsigned char* data, int len);

// Screenshot
int SaveScreenshot(const char* path);
void ClearShapes(void);
```

---

## Writing Custom Scenes

Create a new scene file in `scenes/` and use standard Manim syntax:

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        # Create a square
        sq = Square(side_length=2, color=BLUE)
        self.play(Create(sq))

        # Transform to circle
        circ = Circle(radius=1, color=RED)
        self.play(Transform(sq, circ))

        # Fade out
        self.play(FadeOut(sq))
```

### Using Manim-Booster's VulkanRender

```python
from core.vulkan_bind import VulkanRender

renderer = VulkanRender(1920, 1080)

# Create a Manim scene
scene = MyScene()
scene.renderer = renderer

# Play animations
renderer.play(Create(my_mobject))
renderer.play(Transform(source, target))
```

### Key Attributes on Mobjects

Manim-Booster sets these attributes during animations:

| Attribute | Type | Description |
|-----------|------|-------------|
| `_vulkan_progress` | float | Draw progress (0→1 for Create) |
| `_transforming` | bool | Use bezier path instead of shape dispatcher |
| `_grow_scale` | float | Scale factor for GrowFrom* animations |
| `_grow_point` | tuple | Origin point for scale animations |
| `_rotation_about_point` | tuple | Rotation pivot |
| `_letter_alphas` | list | Per-character opacity for Write |

---

## Key Design Decisions

### 1. Shape-Specific Dispatch

Each Manim shape type has a dedicated sender that extracts its properties (center, size, color, rotation) and calls the appropriate DLL function. This avoids the overhead of generic bezier tessellation for simple primitives.

### 2. Transform Routing

When `_transforming=True`, the renderer uses `_send_vmobject()` (bezier path) instead of shape-specific dispatchers. This is necessary because transforms modify the mobject's points directly — the shape-specific senders ignore point changes and only read high-level properties.

**Exception:** Axis-aligned quads (Square/Rectangle) during rotation use the polygon path for solid fills, even with `_transforming=True`.

### 3. Per-Frame Rotation Delta

VGroup rotation is tracked as an accumulated angle. Each frame, the delta is computed and applied as a rotation matrix to all submobject points:

```python
delta = current_rotation - previous_rotation
rot_matrix = [[cos(d), -sin(d), 0], [sin(d), cos(d), 0], [0, 0, 1]]
sub.points = (sub.points - pivot) @ rot_matrix.T + pivot
```

### 4. Opacity Isolation

Per-mobject opacity is tracked separately from Manim's internal state via `_anim_opacity`. This prevents interference between concurrent animations and allows clean fade transitions.

### 5. DLL as Rendering Backend

The native DLL handles all GPU interaction:
- Vulkan instance/device/swapchain management
- Vertex buffer management
- Shader compilation (embedded SPIR-V)
- Win32 window creation and message loop

This keeps the Python layer focused on animation logic and mobject state management.

---

## License

This project is licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [ManimCE](https://www.manim.community/) — The mathematical animation engine
- [stb_truetype](https://github.com/nothings/stb) — TrueType font rasterizer
- [Vulkan SDK](https://www.lunarg.com/vulkan-sdk/) — Graphics API
