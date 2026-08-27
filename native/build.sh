#!/bin/bash
# Manim Vulkan Native Build - macOS
# Usage: ./build.sh [debug]
set -e
cd "$(dirname "$0")"

BUILD_CONFIG="release"
if [ "$1" = "debug" ]; then
    BUILD_CONFIG="debug"
fi

PROJECT_ROOT="$(cd .. && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
OBJ_DIR="$BUILD_DIR/$BUILD_CONFIG"
OUTPUT_DIR="$DIST_DIR/$BUILD_CONFIG"

mkdir -p "$OBJ_DIR" "$OUTPUT_DIR"

echo "========================================"
echo " Manim Vulkan Native Build (macOS)"
echo "========================================"
echo "Configuration: $BUILD_CONFIG"
echo "========================================"

# ── Homebrew dependencies ────────────────────────────────────────────
if ! command -v brew >/dev/null 2>&1; then
    echo "[ERROR] Homebrew is required. Install it from https://brew.sh"
    exit 1
fi
BREW_PREFIX="$(brew --prefix)"

MISSING=()
for pkg in glfw molten-vk vulkan-loader vulkan-headers; do
    if [ ! -d "$BREW_PREFIX/opt/$pkg" ]; then
        MISSING+=("$pkg")
    fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
    echo "[INFO] Installing missing dependencies: ${MISSING[*]}"
    brew install "${MISSING[@]}"
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[WARNING] ffmpeg not found - video recording will not work."
    echo "          Install with: brew install ffmpeg"
fi

INCLUDE_FLAGS="-I$BREW_PREFIX/include"
LINK_FLAGS="-L$BREW_PREFIX/lib -lvulkan -lglfw -Wl,-rpath,$BREW_PREFIX/lib"

if [ "$BUILD_CONFIG" = "debug" ]; then
    OPT_FLAGS="-O0 -g -DDEBUG"
    OUTPUT_NAME="libvulkan_core_debug.dylib"
else
    OPT_FLAGS="-O2 -DNDEBUG"
    OUTPUT_NAME="libvulkan_core.dylib"
fi

CFLAGS="-fPIC $OPT_FLAGS $INCLUDE_FLAGS"
OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_NAME"

SOURCE_FILES=(
    "platform.c"
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

echo "[INFO] Compiling source files..."
OBJECT_FILES=()
for src in "${SOURCE_FILES[@]}"; do
    if [ ! -f "$src" ]; then
        echo "[ERROR] Source file not found: $src"
        exit 1
    fi
    obj_name="$(echo "$src" | tr '/' '_' | sed 's/\.c$/.o/')"
    obj_path="$OBJ_DIR/$obj_name"
    OBJECT_FILES+=("$obj_path")
    echo "[CMD] cc -c $CFLAGS -o $obj_path $src"
    cc -c $CFLAGS -o "$obj_path" "$src"
done

echo "[INFO] Linking dynamic library..."
echo "[CMD] cc -dynamiclib -o $OUTPUT_PATH ..."
cc -dynamiclib $OPT_FLAGS -o "$OUTPUT_PATH" "${OBJECT_FILES[@]}" $LINK_FLAGS

echo "========================================"
echo " Build Complete"
echo " Output: $OUTPUT_PATH"
echo "========================================"
