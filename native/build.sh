#!/bin/bash

# Cross-platform build script for Manim Vulkan

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"

# Parse command line arguments
BUILD_CONFIG="release"
if [ "$1" = "debug" ]; then
    BUILD_CONFIG="debug"
fi

echo "========================================"
echo " Manim Vulkan Native Build"
echo "========================================"
echo "Configuration: $BUILD_CONFIG"
echo "Platform: $(uname -s)"
echo "========================================"

# Detect platform
PLATFORM=$(uname -s)
case "$PLATFORM" in
    Darwin*)
        echo "[INFO] Detected macOS platform"
        cd "$SCRIPT_DIR/macOSX"
        
        # Check if Vulkan SDK is available
        if [ ! -d "/System/Library/Frameworks/Vulkan.framework" ] && [ ! -d "$VULKAN_SDK" ]; then
            echo "[WARNING] Vulkan SDK not found in standard location"
            echo "[INFO] Trying to locate Vulkan SDK..."
            
            # Try common locations
            VULKAN_PATHS=(
                "/usr/local/include/vulkan"
                "/opt/homebrew/include/vulkan"
                "$HOME/VulkanSDK"
                "/usr/local/opt/vulkan"
            )
            
            for path in "${VULKAN_PATHS[@]}"; do
                if [ -d "$path" ] || [ -f "$path/vulkan.h" ]; then
                    echo "[INFO] Found Vulkan headers at: $path"
                    export VULKAN_INCLUDE="$path"
                    break
                fi
            done
        fi
        
        # Build with Makefile
        make clean
        make "$BUILD_CONFIG"
        ;;
        
    Linux*)
        echo "[INFO] Detected Linux platform"
        echo "[ERROR] Linux build not yet implemented"
        exit 1
        ;;
        
    CYGWIN*|MINGW*|MSYS*)
        echo "[INFO] Detected Windows platform"
        echo "[INFO] Please use build.ps1 for Windows builds"
        exit 1
        ;;
        
    *)
        echo "[ERROR] Unsupported platform: $PLATFORM"
        exit 1
        ;;
esac

echo "========================================"
echo " Build Complete"
echo "========================================"
