#!/bin/bash
# build_mac.sh - build the real-time-manim Vulkan renderer for macOS.
# Uses MoltenVK (Vulkan over Metal), clang, and Cocoa frameworks.
# Output: dist/<config>/vulkan_core.dylib, copied to real_time_manim/ next to
# the packaged vulkan_core.dll so the Python loader finds it.
#
# Usage: ./build_mac.sh [release|debug]

set -e
cd "$(dirname "$0")"

BUILD_CONFIG="${1:-release}"
if [ "$BUILD_CONFIG" = "debug" ]; then
    OPT_FLAGS="-O0 -g -DDEBUG"
    OUTPUT_SUFFIX="_debug"
else
    OPT_FLAGS="-O2 -DNDEBUG"
    OUTPUT_SUFFIX=""
fi

PROJECT_ROOT="$(cd .. && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
OBJ_DIR="$BUILD_DIR/$BUILD_CONFIG"
OUTPUT_DIR="$DIST_DIR/$BUILD_CONFIG"

mkdir -p "$BUILD_DIR" "$DIST_DIR" "$OBJ_DIR" "$OUTPUT_DIR"

echo "========================================"
echo " Real Time Manim Native Build (macOS)"
echo "========================================"
echo "Configuration: $BUILD_CONFIG"
echo "========================================"

# --- Locate MoltenVK + Vulkan headers ---
BREW_PREFIX="$(brew --prefix 2>/dev/null || true)"

MOLTENVK_LIB=""
for lib_path in \
    "$VULKAN_SDK/MoltenVK/dynamic/libMoltenVK.dylib" \
    "$VULKAN_SDK/lib/libMoltenVK.dylib" \
    "$BREW_PREFIX/opt/molten-vk/lib/libMoltenVK.dylib" \
    "$BREW_PREFIX/lib/libMoltenVK.dylib" \
    "/opt/homebrew/opt/molten-vk/lib/libMoltenVK.dylib" \
    "/usr/local/opt/molten-vk/lib/libMoltenVK.dylib"; do
    if [ -f "$lib_path" ]; then
        MOLTENVK_LIB="$lib_path"
        break
    fi
done
if [ -z "$MOLTENVK_LIB" ]; then
    echo "[ERROR] libMoltenVK.dylib not found."
    echo "        Install it with: brew install molten-vk vulkan-headers"
    exit 1
fi
echo "[OK] MoltenVK: $MOLTENVK_LIB"

INCLUDE_FLAGS=""
for inc_dir in \
    "$VULKAN_SDK/include" \
    "$BREW_PREFIX/opt/vulkan-headers/include" \
    "$BREW_PREFIX/include" \
    "/opt/homebrew/include" \
    "/usr/local/include"; do
    if [ -f "$inc_dir/vulkan/vulkan.h" ]; then
        INCLUDE_FLAGS="$INCLUDE_FLAGS -I$inc_dir"
        break
    fi
done
if ! echo '#include <vulkan/vulkan.h>' | cc $INCLUDE_FLAGS -fsyntax-only -x c - >/dev/null 2>&1; then
    echo "[ERROR] Vulkan headers not found."
    echo "        Install them with: brew install vulkan-headers"
    exit 1
fi
echo "[OK] Vulkan headers: $(echo '#include <vulkan/vulkan.h>' | cc $INCLUDE_FLAGS -H -fsyntax-only -x c - 2>&1 | grep 'vulkan.h' | head -1 | awk '{print $NF}')"

# --- Compile ---
OUTPUT_NAME="vulkan_core${OUTPUT_SUFFIX}.dylib"
OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_NAME"

# macOS replaces platform.c (Win32) with platform_mac.m (Cocoa/Metal).
SOURCE_FILES=(
    "platform_mac.m"
    "vulkan_init.c"
    "vulkan_draw.c"
    "draw/draw_rect.c"
    "draw/draw_circle.c"
    "draw/draw_line.c"
    "draw/draw_ellipse.c"
    "draw/draw_polygon.c"
    "draw/draw_dashed_line.c"
    "draw/draw_arc.c"
    "draw/draw_point.c"
    "draw/draw_text.c"
    "draw/draw_bezier.c"
)

COMPILER_FLAGS="-fPIC -fvisibility=hidden $OPT_FLAGS"

echo ""
echo "[INFO] Compiling source files..."
OBJECT_FILES=()
for src in "${SOURCE_FILES[@]}"; do
    if [ ! -f "$src" ]; then
        echo "[ERROR] Source file not found: $src"
        exit 1
    fi
    obj_name="${src//\//_}"
    obj_name="${obj_name%.c}"
    obj_name="${obj_name%.m}"
    obj_name="${obj_name}.o"
    obj_path="$OBJ_DIR/$obj_name"
    OBJECT_FILES+=("$obj_path")

    if [[ "$src" == *.m ]]; then
        LANG_FLAG="-x objective-c"
    else
        LANG_FLAG=""
    fi

    echo "  CC $src"
    clang $LANG_FLAG -c $COMPILER_FLAGS -o "$obj_path" "$src" $INCLUDE_FLAGS -I.
done

echo ""
echo "[INFO] Linking $OUTPUT_NAME..."
clang -dynamiclib -fvisibility=hidden $OPT_FLAGS \
    -o "$OUTPUT_PATH" "${OBJECT_FILES[@]}" \
    -L"$(dirname "$MOLTENVK_LIB")" \
    -lMoltenVK \
    -framework Metal \
    -framework Cocoa \
    -framework QuartzCore \
    -framework AppKit \
    -framework Foundation \
    -Wl,-rpath,"$(dirname "$MOLTENVK_LIB")"

# Bundle the dylib next to the packaged Windows DLL so vulkan_bind.py finds it.
PKG_DIR="$PROJECT_ROOT/real_time_manim"
cp "$OUTPUT_PATH" "$PKG_DIR/vulkan_core.dylib"
echo "[OK] Copied to $PKG_DIR/vulkan_core.dylib"

echo ""
echo "========================================"
echo " Build Complete"
echo "========================================"
echo "Output: $OUTPUT_PATH"
ls -lh "$OUTPUT_PATH" "$PKG_DIR/vulkan_core.dylib"
