import sys
from scenes.demo_scene import (
    DemoCreate, DemoWriteUnwrite, DemoTransform, DemoReplacementTransform,
    DemoFadeInFadeOut, DemoFadeTransform, DemoRotating,
    DemoTransformMatchingShapes, DemoVGroup, DemoAllShapes,
    DemoSuccession, DemoFadeInShift, DemoTextFeatures, DemoCombined,
    DemoDefaultAdd, DemoAddWithRunTime, DemoLagRatios, DemoChangeDefaultAnimation,
    DemoAnimatedBoundary, DemoTracedPath, DemoDissipatingPath, DemoLaggedStart,
    DemoLaggedStartMap, DemoSuccessionDots, DemoCreateSquare,
    DemoDrawBorderThenFill, DemoShowIncreasingSubsets, DemoSpiralIn,
    DemoTypeWithCursor, DemoUncreate,
)

SCENES = [
    ("1",  "Create - draw shapes",                    DemoCreate),
    ("2",  "Write / Unwrite - text",                  DemoWriteUnwrite),
    ("3",  "Transform - morph shapes",                DemoTransform),
    ("4",  "ReplacementTransform - replace in scene", DemoReplacementTransform),
    ("5",  "FadeIn / FadeOut",                        DemoFadeInFadeOut),
    ("6",  "FadeTransform - crossfade shapes",        DemoFadeTransform),
    ("7",  "Rotating / Rotate",                       DemoRotating),
    ("8",  "TransformMatchingShapes",                 DemoTransformMatchingShapes),
    ("9",  "VGroup - grouped animations",             DemoVGroup),
    ("10", "All supported shapes",                    DemoAllShapes),
    ("11", "Succession - chained animations",         DemoSuccession),
    ("12", "FadeIn with shift/scale",                 DemoFadeInShift),
    ("13", "Text rendering - all styles",             DemoTextFeatures),
    ("14", "Combined demo",                           DemoCombined),
    ("15", "Add - DefaultAddScene",                   DemoDefaultAdd),
    ("16", "Add with run_time - grid of circles",     DemoAddWithRunTime),
    ("17", "LagRatios - staggered animations",        DemoLagRatios),
    ("18", "ChangeDefaultAnimation",                   DemoChangeDefaultAnimation),
    ("19", "AnimatedBoundary - shiny text",            DemoAnimatedBoundary),
    ("20", "TracedPath - rolling circle trace",        DemoTracedPath),
    ("21", "DissipatingPath - fading trace",           DemoDissipatingPath),
    ("22", "LaggedStart - staggered dot animation",    DemoLaggedStart),
    ("23", "LaggedStartMap - ripple effect on grid",   DemoLaggedStartMap),
    ("24", "Succession - dots chase each other",       DemoSuccessionDots),
    ("25", "Create(Square) - basic create",            DemoCreateSquare),
    ("26", "DrawBorderThenFill - fill animation",      DemoDrawBorderThenFill),
    ("27", "ShowIncreasingSubsets - reveal submobjects", DemoShowIncreasingSubsets),
    ("28", "SpiralIn - shapes fly in on spiral",          DemoSpiralIn),
    ("29", "TypeWithCursor + Blink - typing effect",       DemoTypeWithCursor),
    ("30", "Uncreate - reverse of Create",                  DemoUncreate),
]


def show_menu():
    print("\n" + "=" * 50)
    print("  Manim Vulkan Renderer - Demo Menu")
    print("=" * 50)
    for num, desc, _ in SCENES:
        print(f"  {num:>3}. {desc}")
    print("=" * 50)


def main():
    if len(sys.argv) > 1:
        num = sys.argv[1]
    else:
        show_menu()
        num = input("\nEnter number: ").strip()

    for n, desc, cls in SCENES:
        if n == num:
            print(f"Running: {desc}")
            scene = cls()
            scene.construct()
            return

    print(f"Invalid option: {num}")
    sys.exit(1)


if __name__ == "__main__":
    main()
