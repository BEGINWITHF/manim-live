"""Runner: render one (or all) demo scene(s) through the Vulkan renderer.

Usage:
    env -u PYTHONPATH .venv/bin/python3.12 run.py 1      # scene 1 -> downloaded_videos/
    env -u PYTHONPATH .venv/bin/python3.12 run.py all    # all 82 scenes (in-process sweep)

Each scene's MLWindow is monkey-patched to auto-start recording at 60 fps and
stop before close, so every rendered scene also produces an MP4 download.
"""
import sys
import os
import shutil
from scenes.demo_scene import (
    DemoCreate, DemoWriteUnwrite, DemoTransform, DemoReplacementTransform,
    DemoFadeInFadeOut, DemoFadeTransform, DemoRotating,
    DemoTransformMatchingShapes, DemoVGroup, DemoAllShapes,
    DemoSuccession, DemoFadeInShift, DemoTextFeatures, DemoCombined,
    DemoDefaultAdd, DemoAddWithRunTime, DemoLagRatios, DemoChangeDefaultAnimation,
    DemoAnimatedBoundary, DemoTracedPath, DemoDissipatingPath, DemoLaggedStart,
    DemoLaggedStartMap, DemoSuccessionDots, DemoCreateSquare,
    DemoDrawBorderThenFill, DemoShowIncreasingSubsets, DemoSpiralIn,
    DemoTypeWithCursor, DemoUncreate, DemoUntypeWithCursor,
    DemoUnwriteReverseTrue, DemoUnwriteReverseFalse, DemoShowWrite, DemoShowWriteReversed,
    DemoFadeInExample, DemoFadeOutExample, DemoGrowFromCenter, DemoGrowArrow, DemoGrowFromEdge,
    DemoGrowFromPoint, DemoSpinInFromNothing, DemoApplyingWaves, DemoBlinking, DemoCircumscribe,
    DemoUsingFlash, DemoFlashOnCircle, DemoFocusOn, DemoUsingIndicate,
    DemoTimeWidthValues, DemoWiggle, DemoHomotopy, DemoMoveAlongPath,
    DemoChangeDecimalToValue, DemoChangingDecimal, DemoUsingRotate, DemoRotatingAbout,
    BroadcastExample, SpeedModifierExample, SpeedModifierUpdaterExample,
    SpeedModifierUpdaterExample2, ApplyMatrixExample, WarpSquare, ClockwiseExample,
    CounterclockwiseTransform_vs_Transform, DemoCyclicReplace, DemoFadeToColor,
    DemoDifferentFadeTransforms, DemoFadeTransformPieces,
    DemoMoveToTarget, DemoReplacementTransformOrTransform,
    DemoRestore, DemoScaleInPlace, DemoShrinkToCenter,
    DemoTransformPathArc, DemoAnagram, DemoMatchingEquationParts,
    DemoTangentAnimation, DemoLatexWithoutLatex, DemoFourierTransform,
    DemoLorenzButterfly, DemoWriteLatex,
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
    ("18", "ChangeDefaultAnimation",                  DemoChangeDefaultAnimation),
    ("19", "AnimatedBoundary - shiny text",           DemoAnimatedBoundary),
    ("20", "TracedPath - rolling circle trace",       DemoTracedPath),
    ("21", "DissipatingPath - fading trace",          DemoDissipatingPath),
    ("22", "LaggedStart - staggered dot animation",   DemoLaggedStart),
    ("23", "LaggedStartMap - ripple effect on grid",  DemoLaggedStartMap),
    ("24", "Succession - dots chase each other",      DemoSuccessionDots),
    ("25", "Create(Square) - basic create",           DemoCreateSquare),
    ("26", "DrawBorderThenFill - fill animation",     DemoDrawBorderThenFill),
    ("27", "ShowIncreasingSubsets - reveal",          DemoShowIncreasingSubsets),
    ("28", "SpiralIn - shapes fly in on spiral",      DemoSpiralIn),
    ("29", "TypeWithCursor + Blink - typing effect",  DemoTypeWithCursor),
    ("30", "UntypeWithCursor + Blink - deleting",     DemoUntypeWithCursor),
    ("31", "Uncreate - reverse of Create",            DemoUncreate),
    ("32", "Unwrite reverse=True",                    DemoUnwriteReverseTrue),
    ("33", "Unwrite reverse=False",                   DemoUnwriteReverseFalse),
    ("34", "Write - font_size=144",                   DemoShowWrite),
    ("35", "Write reversed - font_size=144",          DemoShowWriteReversed),
    ("36", "FadeIn with shift/target_position",       DemoFadeInExample),
    ("37", "FadeOut with shift/target_position",      DemoFadeOutExample),
    ("38", "GrowFromCenter",                          DemoGrowFromCenter),
    ("39", "GrowArrow",                               DemoGrowArrow),
    ("40", "GrowFromEdge",                            DemoGrowFromEdge),
    ("41", "GrowFromPoint",                           DemoGrowFromPoint),
    ("42", "SpinInFromNothing",                       DemoSpinInFromNothing),
    ("43", "ApplyWave",                               DemoApplyingWaves),
    ("44", "Blink",                                   DemoBlinking),
    ("45", "Circumscribe",                            DemoCircumscribe),
    ("46", "Flash",                                   DemoUsingFlash),
    ("47", "Flash on Circle",                         DemoFlashOnCircle),
    ("48", "FocusOn",                                 DemoFocusOn),
    ("49", "Indicate",                                DemoUsingIndicate),
    ("50", "ShowPassingFlash",                        DemoTimeWidthValues),
    ("51", "Wiggle",                                  DemoWiggle),
    ("52", "Homotopy",                                DemoHomotopy),
    ("53", "MoveAlongPath",                           DemoMoveAlongPath),
    ("54", "ChangeDecimalToValue",                    DemoChangeDecimalToValue),
    ("55", "ChangingDecimal",                         DemoChangingDecimal),
    ("56", "Rotate",                                  DemoUsingRotate),
    ("57", "Rotating with about_point",               DemoRotatingAbout),
    ("58", "Broadcast",                               BroadcastExample),
    ("59", "SpeedModifier (ChangeSpeed)",             SpeedModifierExample),
    ("60", "SpeedModifier (Updater)",                 SpeedModifierUpdaterExample),
    ("61", "SpeedModifier (Updater 2 - stop)",        SpeedModifierUpdaterExample2),
    ("62", "ApplyMatrix",                             ApplyMatrixExample),
    ("63", "WarpSquare (exp)",                        WarpSquare),
    ("64", "ClockwiseTransform",                      ClockwiseExample),
    ("65", "CounterclockwiseTransform vs Transform",  CounterclockwiseTransform_vs_Transform),
    ("66", "CyclicReplace",                           DemoCyclicReplace),
    ("67", "FadeToColor",                             DemoFadeToColor),
    ("68", "FadeTransform",                           DemoDifferentFadeTransforms),
    ("69", "FadeTransformPieces",                     DemoFadeTransformPieces),
    ("70", "MoveToTarget",                            DemoMoveToTarget),
    ("71", "ReplacementTransform vs Transform",       DemoReplacementTransformOrTransform),
    ("72", "Restore",                                 DemoRestore),
    ("73", "ScaleInPlace",                            DemoScaleInPlace),
    ("74", "ShrinkToCenter",                          DemoShrinkToCenter),
    ("75", "TransformPathArc",                        DemoTransformPathArc),
    ("76", "TransformMatchingShapes Anagram",         DemoAnagram),
    ("77", "TransformMatchingShapes Equations",       DemoMatchingEquationParts),
    ("78", "TangentLine - sliding tangent",           DemoTangentAnimation),
    ("79", "All LaTeX features - without LaTeX",      DemoLatexWithoutLatex),
    ("80", "Fourier Transform - epicycles heart",     DemoFourierTransform),
    ("81", "Lorenz Attractor - butterfly effect",     DemoLorenzButterfly),
    ("82", "Write on LaTeX - progressive reveal",     DemoWriteLatex),
]


def show_menu():
    print("\n" + "=" * 50)
    print("  Real Time Manim Renderer - Demo Menu")
    print("=" * 50)
    for num, desc, _ in SCENES:
        print(f"  {num:>3}. {desc}")
    print("=" * 50)


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TEX_CACHE_DIR = os.path.join(PROJECT_DIR, "tex_cache")


def _restore_tex_cache():
    """Copy cached SVGs into media/Tex/ so manim skips LaTeX compilation."""
    media_tex = os.path.join(PROJECT_DIR, "media", "Tex")
    if not os.path.exists(TEX_CACHE_DIR):
        return
    os.makedirs(media_tex, exist_ok=True)
    for fname in os.listdir(TEX_CACHE_DIR):
        src = os.path.join(TEX_CACHE_DIR, fname)
        dst = os.path.join(media_tex, fname)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    cached = len(os.listdir(media_tex))
    print(f"[Cache] Restored {cached} files from tex_cache/")


def _save_tex_cache():
    """Save new SVGs from media/Tex/ back to tex_cache/."""
    media_tex = os.path.join(PROJECT_DIR, "media", "Tex")
    if not os.path.exists(media_tex):
        return
    os.makedirs(TEX_CACHE_DIR, exist_ok=True)
    new_count = 0
    for fname in os.listdir(media_tex):
        src = os.path.join(media_tex, fname)
        dst = os.path.join(TEX_CACHE_DIR, fname)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            new_count += 1
    if new_count:
        print(f"[Cache] Saved {new_count} new files to tex_cache/")


def _clean_media():
    """Delete media output directory after each test to keep workspace clean."""
    media_dir = os.path.join(PROJECT_DIR, "media")
    if os.path.exists(media_dir):
        try:
            shutil.rmtree(media_dir)
            print(f"[Clean] Deleted {media_dir}")
        except PermissionError:
            print(f"[Clean] Could not delete {media_dir} (files in use)")
        except Exception as e:
            print(f"[Clean] Error deleting {media_dir}: {e}")


def _safe_name(desc):
    return "".join(c if c.isalnum() or c in "._" else "_" for c in desc)


def run_scene(num, desc, cls):
    import real_time_manim.vulkan_bind as vb
    out_dir = os.path.join(PROJECT_DIR, "downloaded_videos")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{num.zfill(2)}_{_safe_name(desc)}.mp4")

    # Monkey-patch MLWindow to capture instance + auto-start record
    _render_ref = [None]
    _orig_init = vb.MLWindow.__init__
    _orig_close = vb.MLWindow.close

    def _patched_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        _render_ref[0] = self
        self.start_record(out_path, fps=60)

    def _patched_close(self):
        self.stop_record()
        _orig_close(self)

    vb.MLWindow.__init__ = _patched_init
    vb.MLWindow.close = _patched_close

    try:
        print(f"Running: {desc}")
        _restore_tex_cache()
        scene = cls()
        scene.construct()
        # Safety net: scenes that never call render.close() would leave the
        # recorder running and produce no video at all.
        if _render_ref[0] is not None and getattr(_render_ref[0], '_recording', False):
            _render_ref[0].stop_record()
            _render_ref[0].close()
        _save_tex_cache()
        _clean_media()
    finally:
        vb.MLWindow.__init__ = _orig_init
        vb.MLWindow.close = _orig_close


def main():
    if len(sys.argv) > 1:
        num = sys.argv[1]
    else:
        show_menu()
        num = input("\nEnter number: ").strip()

    if num.lower() == "all":
        for n, desc, cls in SCENES:
            print("\n" + "=" * 60)
            run_scene(n, desc, cls)
        return

    for n, desc, cls in SCENES:
        if str(n) == num:
            run_scene(n, desc, cls)
            return

    print(f"Invalid option: {num}")
    sys.exit(1)


if __name__ == "__main__":
    main()
