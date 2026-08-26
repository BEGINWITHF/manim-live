# Manim-Booster — Complete Feature Showcase

> Every capability of the Vulkan rendering backend, organized by category.

---

## Table of Contents

- [Supported Shapes](#supported-shapes)
- [Drawing Animations](#drawing-animations)
- [Fading Animations](#fading-animations)
- [Transform Animations](#transform-animations)
- [Movement Animations](#movement-animations)
- [Rotation Animations](#rotation-animations)
- [Scale & Grow Animations](#scale--grow-animations)
- [Text & Typing Animations](#text--typing-animations)
- [Visual Effects](#visual-effects)
- [Composition & Grouping](#composition--grouping)
- [Updaters & Continuous Animations](#updaters--continuous-animations)
- [Mathematical Rendering](#mathematical-rendering)
- [Recording & Output](#recording--output)
- [Scene Management](#scene-management)
- [Performance Features](#performance-features)

---

## Supported Shapes

Every shape below renders natively via the Vulkan pipeline with fill, stroke, and animation support.

| Shape | Class | Fill | Stroke | Rotation | Notes |
|-------|-------|------|--------|----------|-------|
| Square | `Square` | ✅ | ✅ | ✅ | `side_length` param |
| Rectangle | `Rectangle` | ✅ | ✅ | ✅ | `width`, `height` params |
| Circle | `Circle` | ✅ | ✅ | ✅ | `radius` param |
| Ellipse | `Ellipse` | ✅ | ✅ | ✅ | `width`, `height` params |
| Line | `Line` | — | ✅ | ✅ | Start/end points |
| DashedLine | `DashedLine` | — | ✅ | ✅ | `dash_length`, `dashed_ratio` |
| Arrow | `Arrow` | — | ✅ | ✅ | Shaft + triangular tip |
| Polygon | `Polygon` | ✅ | ✅ | ✅ | Arbitrary vertex list |
| Polygram | `Polygram` | ✅ | ✅ | ✅ | Star polygons, etc. |
| Triangle | `Triangle` | ✅ | ✅ | ✅ | Regular 3-sided polygon |
| Arc | `Arc` | — | ✅ | ✅ | `start_angle`, `angle` |
| Dot | `Dot` | ✅ | — | — | Small filled circle |
| Point | `Point` | — | — | — | Single pixel |
| Star | `Star` | ✅ | ✅ | ✅ | 5-pointed star |
| RightArrow | `RightArrow` | — | ✅ | ✅ | Pre-built arrow |
| Text | `Text` | ✅ | — | ✅ | TrueType font rendering |
| MathTex | `MathTex` | ✅ | — | ✅ | LaTeX or Unicode math |
| VGroup | `VGroup` | — | — | ✅ | Container for grouped mobjects |
| Group | `Group` | — | — | ✅ | Lightweight container |

### Shape Properties

All shapes support:

- **Fill color** — RGB via `set_fill()`
- **Stroke color** — RGB via `set_stroke()`
- **Stroke width** — Pixels, converted from Manim units
- **Fill opacity** — 0.0 (invisible) to 1.0 (solid)
- **Stroke opacity** — 0.0 (invisible) to 1.0 (solid)
- **Rotation** — Arbitrary angle in radians
- **Scale** — Via `_grow_scale` attribute
- **Position** — Manim coordinate system (centered, Y-up)

---

## Drawing Animations

### Create

Traces the outline of a shape, simulating it being drawn.

```python
sq = Square(side_length=2, color=BLUE)
self.play(Create(sq))                          # Default speed
self.play(Create(circ, run_time=2.0))          # Slower
self.play(Create(vg, lag_ratio=0.3))           # Staggered group
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `run_time` | float | 1.0 | Duration in seconds |
| `lag_ratio` | float | 0.0 | Stagger between submobjects |

**Demos:** 1, 9, 25, 31, 45

---

### Uncreate

Reverse of Create — erases by untracing the outline.

```python
self.play(Uncreate(sq, run_time=1.5))
```

**Demos:** 31

---

### DrawBorderThenFill

Draws the stroke first, then fills in the interior.

```python
self.play(DrawBorderThenFill(sq, run_time=2.0))
```

**Demos:** 26

---

### ShowIncreasingSubsets

Reveals submobjects one at a time.

```python
p = VGroup(Dot(), Square(), Triangle())
self.play(ShowIncreasingSubsets(p, run_time=2.0))
```

**Demos:** 27

---

### SpiralIn

Spirals shapes into position from outside the frame.

```python
shapes = VGroup(circle, square)
self.play(SpiralIn(shapes))
```

**Demos:** 28

---

## Fading Animations

### FadeIn

Fades a mobject into view with optional shift/scale.

```python
self.play(FadeIn(sq))
self.play(FadeIn(sq, shift=UP*2))
self.play(FadeIn(sq, scale=2.0))
self.play(FadeIn(sq, target_position=dot))
self.play(FadeIn(sq, shift=DOWN, scale=0.5))
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `shift` | np.array | Direction to slide from |
| `scale` | float | Initial scale factor |
| `target_position` | np.array/str | Where to fade from |
| `fade_scale` | float | Scale at start |

**Demos:** 5, 12, 36

---

### FadeOut

Fades a mobject out of view with optional shift/scale.

```python
self.play(FadeOut(sq))
self.play(FadeOut(sq, shift=DOWN*2))
self.play(FadeOut(sq, scale=0.0))
self.play(FadeOut(sq, target_position=dot))
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `shift` | np.array | Direction to slide toward |
| `scale` | float | Final scale factor |
| `target_position` | np.array | Where to fade to |

**Demos:** 5, 12, 37

---

### FadeToColor

Fades mobject to a target color.

```python
self.play(FadeToColor(Text("Hello World!"), color=RED))
```

**Demos:** 67

---

### FadeTransform

Cross-fades source into target with optional stretching.

```python
self.play(FadeTransform(sq, circ, run_time=2.0))
self.play(FadeTransform(src, tgt, stretch=True))
self.play(FadeTransform(src, tgt, dim_to_match=0))
self.play(FadeTransform(src, tgt, dim_to_match=1))
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `stretch` | bool | Non-uniform stretch to fit |
| `dim_to_match` | int | Which dimension to match (0 or 1) |

**Demos:** 6, 68, 69

---

### FadeTransformPieces

Cross-fades each submobject individually.

```python
src = VGroup(sq, circ)
tgt = VGroup(tri, star)
self.play(FadeTransformPieces(src, tgt))
```

**Demos:** 69

---

## Transform Animations

### Transform

Morphs source mobject into target in-place (source stays in scene).

```python
sq = Square()
circ = Circle()
self.play(Transform(sq, circ, run_time=1.5))
# sq is now a Circle visually
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `path_arc` | float | Arc angle for interpolation path |

**Demos:** 3, 11, 64, 65, 75

---

### ReplacementTransform

Transforms source into target and replaces source with target in scene.

```python
sq = Square()
tri = Triangle()
self.play(ReplacementTransform(sq, tri, run_time=1.5))
# sq is removed, tri is in scene
```

**Demos:** 4, 71

---

### ClockwiseTransform

Transforms with a clockwise arc path.

```python
self.play(ClockwiseTransform(source, target))
```

**Demos:** 64

---

### CounterclockwiseTransform

Transforms with a counterclockwise arc path.

```python
self.play(CounterclockwiseTransform(source, target))
```

**Demos:** 65

---

### TransformMatchingShapes

Matches submobjects by point similarity for smooth morphing.

```python
src = Text("the morse code")
tgt = Text("here come dots")
self.play(TransformMatchingShapes(src, tgt, path_arc=PI/2))
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `path_arc` | float | Arc path for matched pieces |

**Demos:** 8, 76, 77

---

### TransformMatchingTex

Matches LaTeX submobjects by label for equation transforms.

```python
eq1 = MathTex(r"x^2 + y^2 = r^2")
eq2 = MathTex(r"r^2 = x^2 + y^2")
self.play(TransformMatchingTex(Group(eq1, variables), eq2))
```

**Demos:** 77

---

### CyclicReplace

Cyclically swaps positions of group members.

```python
group = VGroup(Square(), Circle(), Triangle(), Star())
self.play(CyclicReplace(*group))
```

**Demos:** 66

---

## Movement Animations

### MoveToTarget

Moves mobject to its `.target` attribute position.

```python
sq = Square()
sq.target = Circle().shift(RIGHT*3)
self.play(MoveToTarget(sq))
```

**Demos:** 70

---

### MoveAlongPath

Moves mobject along another mobject's path.

```python
circle = Circle()
dot = Dot()
self.play(MoveAlongPath(dot, circle))
```

**Demos:** 53

---

### ApplyMatrix

Applies a 2D matrix transformation to a mobject.

```python
matrix = [[1, 1], [0, 1]]  # Shear
self.play(ApplyMatrix(matrix, sq))
```

**Demos:** 62

---

### WarpSquare

Applies an exponential warp to a square.

```python
self.play(WarpSquare(sq))
```

**Demos:** 63

---

## Rotation Animations

### Rotating

Continuously rotates a mobject over the animation duration.

```python
self.play(Rotating(sq, run_time=3.0))
self.play(Rotating(arrow, 180*DEGREES, about_point=arrow.get_start()))
self.play(Rotating(vg, PI, about_point=RIGHT))
self.play(Rotating(vg, PI, axis=UP, about_point=ORIGIN))
self.play(Rotating(vg, PI, axis=RIGHT, about_edge=UP))
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `angle` | float | Total rotation (radians) |
| `axis` | np.array | Rotation axis (3D) |
| `about_point` | np.array | Center of rotation |
| `about_edge` | np.array | Edge to rotate about |

**Demos:** 7, 57

---

### Rotate

Instantly rotates by a given angle (interpolated).

```python
self.play(Rotate(sq, PI/4))
self.play(Rotate(sq, 90*DEGREES, about_point=ORIGIN))
```

**Demos:** 56, 57

---

## Scale & Grow Animations

### GrowFromCenter

Scales mobject from its center.

```python
self.play(GrowFromCenter(sq))
```

**Demos:** 38

---

### GrowFromEdge

Scales mobject from a specified edge.

```python
self.play(GrowFromEdge(sq, DOWN))
```

**Demos:** 40

---

### GrowFromPoint

Scales mobject from an arbitrary point.

```python
self.play(GrowFromPoint(sq, LEFT*3))
```

**Demos:** 41

---

### GrowArrow

Grows an arrow from its tail to its tip.

```python
arrow = Arrow(LEFT, RIGHT)
self.play(GrowArrow(arrow))
```

**Demos:** 39

---

### SpinInFromNothing

Spirals mobject in while spinning.

```python
self.play(SpinInFromNothing(sq))
```

**Demos:** 42

---

### ScaleInPlace

Scales mobject in place.

```python
self.play(ScaleInPlace(sq, 2.0))
```

**Demos:** 73

---

### ShrinkToCenter

Shrinks mobject to a point at its center.

```python
self.play(ShrinkToCenter(sq))
```

**Demos:** 74

---

## Text & Typing Animations

### Write

Draws text by simulating handwriting (per-character reveal).

```python
t = Text("Hello World", font_size=60)
self.play(Write(t, run_time=2.0))
self.play(Write(t, reverse=True))  # Erase instead
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `reverse` | bool | If True, erases instead |
| `remover` | bool | If True, removes after animation |

**Demos:** 2, 13, 34, 35

---

### Unwrite

Erases text by reversing the Write animation.

```python
self.play(Unwrite(text, reverse=True))
self.play(Unwrite(text, reverse=False))
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `reverse` | bool | Erase direction |

**Demos:** 32, 33

---

### TypeWithCursor

Types text one character at a time with a blinking cursor.

```python
text = Text("Hello")
cursor = Dot(color=WHITE).scale(0.3)
self.play(TypeWithCursor(text, cursor))
self.play(Blink(cursor))  # Cursor blinks after typing
```

**Demos:** 29

---

### UntypeWithCursor

Deletes text one character at a time with a cursor.

```python
self.play(UntypeWithCursor(text, cursor))
```

**Demos:** 30

---

## Visual Effects

### Indicate

Highlights a mobject with a brief scale pulse.

```python
self.play(Indicate(sq))
self.play(Indicate(circ, color=RED))
```

**Demos:** 49

---

### Flash

Creates a flash burst effect at a point.

```python
self.play(Flash(dot))
self.play(Flash(circle.get_center()))
```

**Demos:** 46, 47

---

### FocusOn

Highlights a point with a small expanding dot.

```python
self.play(FocusOn(dot))
```

**Demos:** 48

---

### ShowPassingFlash

Shows a brief flash along a path.

```python
self.play(ShowPassingFlash(circle))
self.play(ShowPassingFlash(arrow))
```

**Demos:** 50

---

### Wiggle

Wiggles a mobject back and forth.

```python
self.play(Wiggle(sq))
```

**Demos:** 51

---

### Circumscribe

Draws a circle/rectangle around a mobject.

```python
self.play(Circumscribe(sq))
self.play(Circumscribe(text, circle=True))
```

**Demos:** 45

---

### Blink

Makes a mobject blink (briefly disappear/reappear).

```python
eye = Dot()
self.play(Blink(eye))
```

**Demos:** 44

---

### ApplyWave

Applies a wave distortion to a mobject.

```python
self.play(ApplyWave(sq))
```

**Demos:** 43

---

### Broadcast

Broadcasts expanding circles from a point.

```python
self.play(Broadcast(dot))
```

**Demos:** 58

---

### TangentLine

Shows a tangent line sliding along a curve.

```python
curve = ParametricFunction(...)
line = TangentLine(curve, alpha=0.5)
self.play(ShowCreation(line))
```

**Demos:** 78

---

## Composition & Grouping

### AnimationGroup

Plays multiple animations simultaneously.

```python
sq = Square()
circ = Circle()
self.play(AnimationGroup(
    Create(sq),
    FadeIn(circ),
    lag_ratio=0.5
))
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `lag_ratio` | float | Stagger between sub-animations |

**Demos:** 9, 15, 17

---

### Succession

Plays animations one after another.

```python
self.play(Succession(
    Create(sq),
    Transform(sq, circ),
    FadeOut(circ),
    run_time=4.0
))
```

**Demos:** 11, 24

---

### LaggedStart

Starts animations with a staggered delay.

```python
dots = VGroup(*[Dot() for _ in range(10)])
self.play(LaggedStart(*[FadeIn(d) for d in dots]))
```

**Demos:** 22

---

### LaggedStartMap

Applies an animation to each submobject with staggered timing.

```python
grid = VGroup(*[Square() for _ in range(25)])
self.play(LaggedStartMap(FadeIn, grid))
```

**Demos:** 23

---

### VGroup

Groups mobjects for batch operations.

```python
squares = VGroup(*[Square() for _ in range(5)])
self.play(Create(squares, lag_ratio=0.3))
self.play(squares.animate.shift(RIGHT*2))
self.play(FadeOut(squares))
```

**Demos:** 9

---

## Updaters & Continuous Animations

### Updaters

Functions that run every frame to update mobject properties.

```python
dot = Dot()
dot.add_updater(lambda m: m.move_to(RIGHT * np.sin(time.time())))
self.add(dot)
self.wait(3)
```

**Supported updater signatures:**
- `updater()` — No arguments
- `updater(mob)` — Mobject argument
- `updater(mob, dt)` — Mobject + delta time

---

### TracedPath

Traces the path of a moving point.

```python
circle = Circle()
dot = Dot()
dot.add_updater(lambda m: m.move_to(circle.get_center()))
self.play(TracedPath(dot.get_center()))
```

**Demos:** 20

---

### DissipatingPath

Like TracedPath but the trace fades over time.

```python
self.play(DissipatingPath(dot.get_center()))
```

**Demos:** 21

---

### AnimatedBoundary

Animated border around a mobject.

```python
text = Text("Shiny!")
self.play(AnimatedBoundary(text))
```

**Demos:** 19

---

### ChangeSpeed (SpeedModifier)

Changes the speed of nested animations.

```python
self.play(
    ChangeSpeed(
        Succession(Create(sq), FadeOut(sq)),
        speedinfo={0.0: 1.0, 0.5: 0.1, 1.0: 1.0}
    )
)
```

**Demos:** 59, 60, 61

---

### Restore

Restores a mobject to its state before an animation.

```python
sq.save_state()
self.play(sq.animate.shift(RIGHT*2).rotate(PI/4))
self.play(Restore(sq))  # Returns to saved state
```

**Demos:** 72

---

### Homotopy

Applies a continuous deformation function.

```python
def homotopy(x, y, z, t):
    return np.array([x + np.sin(t * PI) * y, y, z])

self.play(Homotopy(homotopy, sq))
```

**Demos:** 52

---

### PointwiseTransform

Applies a function to every point.

```python
def transform(point):
    return point + np.array([np.sin(point[1]), 0, 0])

self.play(ApplyPointwiseFunction(transform, sq))
```

---

### ChangingDecimal

Dynamically changes a number display.

```python
decimal = DecimalNumber(0)
self.play(ChangingDecimal(decimal, target_value=3.14))
```

**Demos:** 55

---

### ChangeDecimalToValue

Changes a DecimalNumber to a target value.

```python
self.play(ChangeDecimalToValue(decimal, 42))
```

**Demos:** 54

---

## Mathematical Rendering

### MathTex (LaTeX Mode)

Full LaTeX rendering with MiKTeX/TeX Live.

```python
eq = MathTex(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}")
self.play(Write(eq))
```

**Supported LaTeX features:**
- Fractions: `\frac{a}{b}`
- Integrals: `\int`, `\oint`, `\iint`
- Summations: `\sum`, `\prod`
- Greek letters: `\alpha`, `\beta`, `\gamma`, ... (all lowercase + uppercase)
- Operators: `\pm`, `\times`, `\div`, `\cdot`, `\oplus`, ...
- Relations: `\leq`, `\geq`, `\approx`, `\equiv`, `\neq`, ...
- Arrows: `\rightarrow`, `\leftarrow`, `\Rightarrow`, `\Leftrightarrow`, ...
- Sets: `\cup`, `\cap`, `\in`, `\subset`, `\emptyset`, ...
- Matrices: `\begin{matrix}...\end{matrix}`
- Roots: `\sqrt{x}`, `\sqrt[n]{x}`
- Accents: `\hat{x}`, `\bar{x}`, `\dot{x}`, `\ddot{x}`, ...
- Theorems, alignment, arrays, etc.

---

### MathTex (Native Unicode Mode)

No LaTeX installation required — renders via Unicode characters.

```python
# Enable native mode
import core.vulkan_bind as vb
vb._USE_NATIVE_MATHTEX = True

eq = MathTex(r"\alpha + \beta = \gamma")
self.play(Write(eq))
```

**Supported:**
- All Greek letters (α, β, γ, δ, ε, ...)
- Superscripts/subscripts (x², a₁)
- Binary operators (±, ×, ÷, ...)
- Relations (≤, ≥, ≠, ≈, ...)
- Arrows (→, ←, ↔, ⇒, ...)
- Set theory (∪, ∩, ∈, ∅, ...)
- Hebrew (ℵ, ℶ, ℸ)
- Miscellaneous (∞, ∇, ∂, ∠, ...)

**Limitations:** No fractions, matrices, integrals, or complex layouts.

---

### Text Rendering

TrueType font rendering via stb_truetype.

```python
text = Text("Hello World", font_size=60)
bold = Text("Bold", weight=BOLD)
italic = Text("Italic", slant=ITALIC)
```

**Supported:**
- Font size control
- Bold/italic variants
- Unicode characters
- Color via `set_color()`
- Per-character animation (Write, TypeWithCursor)

---

## Recording & Output

### Live GDI Recording

Captures frames via Windows GDI while the window is visible.

```python
renderer.start_record("output.mp4", fps=60)
scene.construct()
renderer.stop_record()
```

**Features:**
- Background thread capture
- Actual FPS calculation for correct video speed
- BMP → ffmpeg H.264 encoding
- Auto-cleanup of temp frames

---

### Fast Offline Recording

Renders at maximum speed without displaying the window.

```python
renderer.enable_fast_record("output.mp4", fps=60, hidden=True)
scene.construct()
renderer._finish_fast_record()
```

**Two modes:**

| Mode | Method | Use Case |
|------|--------|----------|
| **Pipe mode** | SaveScreenshot → BMP parse → ffmpeg stdin | Single-process, fastest |
| **BMP mode** | Individual BMP files per frame | Multi-segment parallel encoding |

**Features:**
- Simulated time (no sleep between frames)
- Hidden window (no compositing overhead)
- Count-only mode (frame counting without GPU)
- Segment support for parallel rendering

---

### Screenshot Capture

Capture individual frames as BMP files.

```python
renderer.screenshot("frame.bmp")              # Via Vulkan swapchain
renderer.screenshot_printwindow("frame.bmp")  # Via GDI PrintWindow
```

---

### Frame Rate Control

Target 60 FPS with automatic frame pacing.

```python
TARGET_FPS = 60
FRAME_DURATION = 1.0 / TARGET_FPS  # ~16.67ms
```

- Real-time mode: sleeps to maintain target FPS
- Fast record mode: no sleep, renders as fast as possible

---

## Scene Management

### Scene.add / Scene.remove

```python
self.add(sq)        # Add to scene
self.remove(sq)     # Remove from scene
```

---

### Scene.wait

```python
self.wait(2)        # Wait 2 seconds
self.wait()         # Wait 1 second (default)
```

---

### Mobject.animate

ManimCE's method-chaining syntax for property changes.

```python
self.play(sq.animate.shift(RIGHT*2).rotate(PI/4).set_color(RED))
```

---

### State Management

```python
sq.save_state()                    # Save current state
self.play(sq.animate.shift(RIGHT))
self.play(Restore(sq))             # Restore saved state
```

---

## Performance Features

### Native Vulkan Pipeline

- **GPU-accelerated rendering** via Vulkan API
- **Instanced drawing** for repeated shapes
- **Pre-compiled SPIR-V shaders** embedded in DLL
- **Vertex buffer management** with 1M vertex capacity

---

### Efficient Shape Dispatch

- **Type-specific senders** avoid generic bezier overhead
- **Early exit** for invisible mobjects (alpha ≤ 0)
- **Progress-based culling** for Create animations

---

### Memory Management

- **Per-frame shape clearing** via `ClearShapes()`
- **Fixed-size buffers** (4096 shapes per type)
- **Command queue** (16384 draw commands max)

---

### Frame Pacing

- **Real-time mode**: Sleeps to maintain 60 FPS
- **Fast record mode**: No sleep, maximum throughput
- **Delta-time rotation**: Frame-rate-independent animation speed

---

## Demo Scene Index

All 81 demo scenes with quick reference:

| # | Name | Key Feature |
|---|------|-------------|
| 1 | Create | Draw shapes |
| 2 | Write / Unwrite | Text handwriting |
| 3 | Transform | Morph shapes |
| 4 | ReplacementTransform | Replace in scene |
| 5 | FadeIn / FadeOut | Opacity transitions |
| 6 | FadeTransform | Crossfade shapes |
| 7 | Rotating | Continuous rotation |
| 8 | TransformMatchingShapes | Smart morphing |
| 9 | VGroup | Grouped animations |
| 10 | All Shapes | Every shape type |
| 11 | Succession | Chained animations |
| 12 | FadeIn with shift/scale | Position/scale fade |
| 13 | Text rendering | All text styles |
| 14 | Combined demo | Mixed animations |
| 15 | DefaultAdd | Add animations |
| 16 | Add with run_time | Grid of circles |
| 17 | LagRatios | Staggered timing |
| 18 | ChangeDefaultAnimation | Default anim override |
| 19 | AnimatedBoundary | Shiny text border |
| 20 | TracedPath | Rolling circle trace |
| 21 | DissipatingPath | Fading trace |
| 22 | LaggedStart | Staggered dots |
| 23 | LaggedStartMap | Ripple on grid |
| 24 | Succession dots | Chase animation |
| 25 | Create Square | Basic create |
| 26 | DrawBorderThenFill | Fill animation |
| 27 | ShowIncreasingSubsets | Reveal parts |
| 28 | SpiralIn | Spiral entrance |
| 29 | TypeWithCursor | Typing effect |
| 30 | UntypeWithCursor | Deleting text |
| 31 | Uncreate | Reverse create |
| 32 | Unwrite reverse=True | Erase from start |
| 33 | Unwrite reverse=False | Erase from end |
| 34 | Write large | font_size=144 |
| 35 | Write reversed | Reverse write |
| 36 | FadeIn variants | shift/target/scale |
| 37 | FadeOut variants | shift/target/scale |
| 38 | GrowFromCenter | Scale from center |
| 39 | GrowArrow | Arrow grow |
| 40 | GrowFromEdge | Scale from edge |
| 41 | GrowFromPoint | Scale from point |
| 42 | SpinInFromNothing | Spiral + spin |
| 43 | ApplyWave | Wave distortion |
| 44 | Blink | Eye blink |
| 45 | Circumscribe | Circle around |
| 46 | Flash | Burst effect |
| 47 | Flash on Circle | Flash at center |
| 48 | FocusOn | Point highlight |
| 49 | Indicate | Pulse highlight |
| 50 | ShowPassingFlash | Path flash |
| 51 | Wiggle | Back-and-forth |
| 52 | Homotopy | Deformation |
| 53 | MoveAlongPath | Path following |
| 54 | ChangeDecimalToValue | Number change |
| 55 | ChangingDynamic | Dynamic number |
| 56 | Rotate | Instant rotation |
| 57 | Rotating about | Pivot rotation |
| 58 | Broadcast | Expanding rings |
| 59 | SpeedModifier | ChangeSpeed |
| 60 | SpeedModifier Updater | Speed + updater |
| 61 | SpeedModifier Stop | Speed stop |
| 62 | ApplyMatrix | Matrix transform |
| 63 | WarpSquare | Exponential warp |
| 64 | ClockwiseTransform | CW arc path |
| 65 | CounterclockwiseTransform | CCW arc path |
| 66 | CyclicReplace | Position swap |
| 67 | FadeToColor | Color transition |
| 68 | FadeTransform variants | stretch/dim |
| 69 | FadeTransformPieces | Per-piece fade |
| 70 | MoveToTarget | Target position |
| 71 | ReplacementTransform vs Transform | Comparison |
| 72 | Restore | State restore |
| 73 | ScaleInPlace | In-place scale |
| 74 | ShrinkToCenter | Shrink to point |
| 75 | TransformPathArc | Arc angle control |
| 76 | Anagram | Letter rearrange |
| 77 | Matching Equations | LaTeX matching |
| 78 | TangentLine | Sliding tangent |
| 79 | LaTeX Features | Full LaTeX showcase |
| 80 | Fourier Transform | Epicycles heart |
| 81 | Lorenz Attractor | Butterfly effect |

---

## Quick Reference

### Importing

```python
from manim import *
from core.vulkan_bind import VulkanRender
```

### Running

```bash
python run.py <scene_number>
```

### Key Classes

| Class | Purpose |
|-------|---------|
| `VulkanRender` | Main renderer (ShapeMixin + TextMixin) |
| `ShapeMixin` | Shape-specific DLL senders |
| `TextMixin` | Text/bezier DLL senders |
| `Animation` | Base animation class |

### Key Functions

| Function | Purpose |
|----------|---------|
| `manim_to_screen(x, y, w, h)` | Coordinate conversion |
| `get_fill_rgb(mob, alpha)` | Extract fill color |
| `get_stroke_rgb(mob)` | Extract stroke color |
| `get_stroke_w(mob)` | Extract stroke width |
| `set_anim_opacity(mob, val)` | Set fade level |
| `get_anim_opacity(mob)` | Get fade level |
| `set_anim_rotation(mob, val)` | Set rotation angle |
| `get_anim_rotation(mob)` | Get rotation angle |

### Rate Functions

| Function | Effect |
|----------|--------|
| `_smooth(t)` | Ease-in-out (sigmoid) |
| `_linear(t)` | Constant speed |
| `_double_smooth(t)` | Smooth with pause |
| `_there_and_back(t)` | Forward then reverse |
| `_slow_into(t)` | Slow start |
| `_rush_into(t)` | Fast start |
| `_rush_from(t)` | Fast end |
| `_wiggle(t)` | Oscillating |
| `_lingering(t)` | Stays at end |
| `_exponential_decay(t)` | Exponential ease |
