"""Compatibility shim for the pre-rename ``core`` package name.

The demo scenes are fixed reference material (never edited) and import
``from core.vulkan_bind import ...``, which predates the v0.1.3 rename of the
package to ``real_time_manim``.  Alias the submodule so those scenes import
byte-for-byte unchanged.  Nothing here renames or copies the renderer code —
``core.vulkan_bind`` *is* ``real_time_manim.vulkan_bind`` (same module object),
so any monkey-patching of one is visible through the other.
"""
import sys as _sys
import real_time_manim.vulkan_bind as _vb

_sys.modules[__name__ + ".vulkan_bind"] = _vb
