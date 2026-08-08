#!/bin/bash
# build_mac.sh - Build manim-booster Vulkan renderer for macOS
# Uses MoltenVK (Vulkan over Metal), clang, and Cocoa frameworks.

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
echo " Manim Vulkan Native Build (macOS)"
echo "========================================"
echo "Configuration: $BUILD_CONFIG"
echo "========================================"

# --- Locate MoltenVK ---
MOLTENVK_PATH=""

# Priority 1: Vulkan SDK
if [ -d "$VULKAN_SDK" ]; then
    MOLTENVK_PATH="$VULKAN_SDK"
    echo "[INFO] Using Vulkan SDK: $VULKAN_SDK"
fi

# Priority 2: Homebrew molten-vk
if [ -z "$MOLTENVK_PATH" ] && [ -d "/opt/homebrew/opt/molten-vk" ]; then
    MOLTENVK_PATH="/opt/homebrew/opt/molten-vk"
    echo "[INFO] Using Homebrew molten-vk: $MOLTENVK_PATH"
elif [ -z "$MOLTENVK_PATH" ] && [ -d "/usr/local/opt/molten-vk" ]; then
    MOLTENVK_PATH="/usr/local/opt/molten-vk"
    echo "[INFO] Using Homebrew molten-vk: $MOLTENVK_PATH"
fi

# Priority 3: Homebrew vulkan-sdk
if [ -z "$MOLTENVK_PATH" ] && [ -d "/opt/homebrew/opt/vulkan-sdk" ]; then
    MOLTENVK_PATH="/opt/homebrew/opt/vulkan-sdk"
    echo "[INFO] Using Homebrew vulkan-sdk: $MOLTENVK_PATH"
elif [ -z "$MOLTENVK_PATH" ] && [ -d "/usr/local/opt/vulkan-sdk" ]; then
    MOLTENVK_PATH="/usr/local/opt/vulkan-sdk"
    echo "[INFO] Using Homebrew vulkan-sdk: $MOLTENVK_PATH"
fi

# Priority 4: System MoltenVK
if [ -z "$MOLTENVK_PATH" ]; then
    # Check common system locations
    for dir in \
        "/usr/local/share/vulkan" \
        "/opt/homebrew/share/vulkan" \
        "/Library/Frameworks/MoltenVK.framework"; do
        if [ -d "$dir" ]; then
            MOLTENVK_PATH="$dir"
            echo "[INFO] Found MoltenVK at: $dir"
            break
        fi
    done
fi

if [ -z "$MOLTENVK_PATH" ]; then
    echo "[ERROR] MoltenVK not found!"
    echo ""
    echo "Install options:"
    echo "  1. brew install molten-vk vulkan-headers"
    echo "  2. Download Vulkan SDK from https://vulkan.lunarg.com/sdk/home"
    echo ""
    exit 1
fi

# Determine include and lib paths
if [ -d "$MOLTENVK_PATH/include" ]; then
    INCLUDE_FLAGS="-I$MOLTENVK_PATH/include"
elif [ -d "$MOLTENVK_PATH/share/vulkan" ]; then
    INCLUDE_FLAGS="-I$MOLTENVK_PATH/share/vulkan"
else
    # Homebrew: headers in include/ but vulkan/ is inside
    INCLUDE_FLAGS="-I$MOLTENVK_PATH/include"
fi

# For Homebrew, find the actual vulkan headers
for inc_dir in \
    "$MOLTENVK_PATH/include/vulkan" \
    "$MOLTENVK_PATH/../vulkan-headers/include" \
    "/opt/homebrew/include" \
    "/usr/local/include"; do
    if [ -f "$inc_dir/vulkan/vulkan.h" ]; then
        INCLUDE_FLAGS="$INCLUDE_FLAGS -I$inc_dir"
        break
    fi
done

# Fallback: if vulkan.h not found, try installing headers
if ! echo '#include <vulkan/vulkan.h>' | cc $INCLUDE_FLAGS -fsyntax-only -x c - 2>/dev/null; then
    echo "[INFO] Vulkan headers not found, checking Homebrew..."
    if [ -f "/opt/homebrew/include/vulkan/vulkan.h" ]; then
        INCLUDE_FLAGS="$INCLUDE_FLAGS -I/opt/homebrew/include"
    elif [ -f "/usr/local/include/vulkan/vulkan.h" ]; then
        INCLUDE_FLAGS="$INCLUDE_FLAGS -I/usr/local/include"
    fi
fi

# Find libMoltenVK
MOLTENVK_LIB=""
for lib_path in \
    "$MOLTENVK_PATH/lib/libMoltenVK.dylib" \
    "$MOLTENVK_PATH/lib/libvulkan.dylib" \
    "$MOLTENVK_PATH/MoltenVK/dynamic/libMoltenVK.dylib" \
    "/opt/homebrew/lib/libMoltenVK.dylib" \
    "/usr/local/lib/libMoltenVK.dylib"; do
    if [ -f "$lib_path" ]; then
        MOLTENVK_LIB="$lib_path"
        break
    fi
done

if [ -z "$MOLTENVK_LIB" ]; then
    echo "[ERROR] libMoltenVK.dylib not found"
    exit 1
fi
echo "[INFO] MoltenVK library: $MOLTENVK_LIB"

# --- Compile ---
OUTPUT_NAME="vulkan_core${OUTPUT_SUFFIX}.dylib"
OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_NAME"

# Source files (replace platform.c with platform_mac.m on macOS)
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

COMPILER_FLAGS="-dynamiclib -fvisibility=hidden $OPT_FLAGS"
# Note: platform_mac.m is Objective-C, other .c files are plain C

echo ""
echo "[INFO] Compiling source files..."

OBJECT_FILES=()
for src in "${SOURCE_FILES[@]}"; do
    if [ ! -f "$src" ]; then
        echo "[ERROR] Source file not found: $src"
        continue
    fi
    
    obj_name="${src//\//_}"
    obj_name="${obj_name%.c}"
    obj_name="${obj_name%.m}"
    obj_name="${obj_name}.o"
    obj_path="$OBJ_DIR/$obj_name"
    OBJECT_FILES+=("$obj_path")
    
    # Use -x objective-c for .m files
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

# Link against MoltenVK and required macOS frameworks
clang $COMPILER_FLAGS -o "$OUTPUT_PATH" "${OBJECT_FILES[@]}" \
    -L"$(dirname "$MOLTENVK_LIB")" \
    -lMoltenVK \
    -framework Metal \
    -framework Cocoa \
    -framework QuartzCore \
    -framework AppKit \
    -framework Foundation \
    -rpath "@loader_path"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo " Build Complete!"
    echo "========================================"
    echo "Output: $OUTPUT_PATH"
    ls -lh "$OUTPUT_PATH"
else
    echo "[ERROR] Link failed"
    exit 1
fi
