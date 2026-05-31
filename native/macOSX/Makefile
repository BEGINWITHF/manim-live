# Makefile for macOS Vulkan library
CC = clang
CFLAGS = -shared -fPIC -O2 -DNDEBUG
DEBUG_CFLAGS = -shared -fPIC -O0 -g -DDEBUG

# Vulkan SDK detection
VULKAN_SDK ?= $(shell xcrun --show-sdk-path)/System/Library/Frameworks/Vulkan.framework
VULKAN_INCLUDE = $(VULKAN_SDK)/Headers
VULKAN_LIB = $(VULKAN_SDK)/Libraries

# Check if Vulkan headers are available, fallback to system paths
ifeq ($(wildcard $(VULKAN_INCLUDE)/vulkan/vulkan.h),)
    VULKAN_INCLUDE = /usr/local/include
    ifeq ($(wildcard $(VULKAN_INCLUDE)/vulkan/vulkan.h),)
        VULKAN_INCLUDE = /opt/homebrew/include
        ifeq ($(wildcard $(VULKAN_INCLUDE)/vulkan/vulkan.h),)
            # Mock mode - create minimal implementation
            CFLAGS += -DMOCK_VULKAN
            $(error 错误：未找到 Vulkan SDK！请安装 Vulkan SDK 以使用完整的 Vulkan 渲染功能。)
        endif
    endif
endif

# Directories (this Makefile lives in native/macOSX)
BUILD_DIR = ../../build
DIST_DIR = ../../dist
OBJ_DIR = $(BUILD_DIR)/$(CONFIG)
OUTPUT_DIR = $(DIST_DIR)/$(CONFIG)

# Shared sources/headers directory (relative to native/macOSX)
SHARED_DIR = ../shared

# Search path for source files (mock sources live in ../shared)
VPATH = $(SHARED_DIR)

# Header include path (platform headers are local, shared headers in ../shared)
INCLUDES = -I. -I$(SHARED_DIR) -I$(VULKAN_INCLUDE)

# Source files
ifeq ($(wildcard $(VULKAN_INCLUDE)/vulkan/vulkan.h),)
    # Mock mode - create minimal implementation
    C_SOURCES = vulkan_init_mock.c vulkan_draw_mock.c
else
    # Real Vulkan implementation (platform-specific)
    C_SOURCES = vulkan_init_macos.c vulkan_draw_macos.c
endif
M_SOURCES = platform_macos.m
OBJECTS = $(C_SOURCES:%.c=$(OBJ_DIR)/%.o) $(M_SOURCES:%.m=$(OBJ_DIR)/%.o)

# Output
CONFIG ?= release
OUTPUT_NAME = libvulkan_core.dylib
OUTPUT_PATH = $(OUTPUT_DIR)/$(OUTPUT_NAME)

# Frameworks for macOS
ifeq ($(wildcard $(VULKAN_INCLUDE)/vulkan/vulkan.h),)
    # Mock mode - no Vulkan framework
    FRAMEWORKS = -framework Cocoa -framework Foundation -framework AppKit
else
    # Real Vulkan implementation - use Vulkan Loader only for now
    FRAMEWORKS = -framework Cocoa -framework Foundation -framework AppKit \
                 -F/opt/homebrew/Cellar/vulkan-loader/1.4.335.0/loader \
                 -framework Vulkan
endif

.PHONY: all clean debug release

all: $(OUTPUT_PATH)

debug: CONFIG = debug
debug: $(OUTPUT_PATH)

release: CONFIG = release
release: $(OUTPUT_PATH)

$(OUTPUT_PATH): $(OBJECTS) | $(OUTPUT_DIR)
	@echo "[INFO] Linking $(OUTPUT_NAME)..."
	$(CC) $(CFLAGS) -o $@ $(OBJECTS) $(FRAMEWORKS)
	@echo "[SUCCESS] Built $(OUTPUT_PATH)"

$(OBJ_DIR)/%.o: %.c | $(OBJ_DIR)
	@echo "[INFO] Compiling $<..."
	@if [ "$(CONFIG)" = "debug" ]; then \
		$(CC) $(DEBUG_CFLAGS) -c $< -o $@ $(INCLUDES); \
	else \
		$(CC) $(CFLAGS) -c $< -o $@ $(INCLUDES); \
	fi

$(OBJ_DIR)/%.o: %.m | $(OBJ_DIR)
	@echo "[INFO] Compiling Objective-C $<..."
	@if [ "$(CONFIG)" = "debug" ]; then \
		$(CC) $(DEBUG_CFLAGS) -c $< -o $@ $(INCLUDES); \
	else \
		$(CC) $(CFLAGS) -c $< -o $@ $(INCLUDES); \
	fi

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(DIST_DIR):
	mkdir -p $(DIST_DIR)

$(OBJ_DIR): | $(BUILD_DIR)
	mkdir -p $(OBJ_DIR)

$(OUTPUT_DIR): | $(DIST_DIR)
	mkdir -p $(OUTPUT_DIR)

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR)

install: $(OUTPUT_PATH)
	@echo "[INFO] Installing to $(OUTPUT_DIR)"
	cp $(OUTPUT_PATH) $(OUTPUT_DIR)/

help:
	@echo "Usage: make [debug|release|clean|install]"
	@echo "  debug   - Build debug version"
	@echo "  release - Build release version (default)"
	@echo "  clean   - Clean build artifacts"
	@echo "  install - Install to dist directory"
