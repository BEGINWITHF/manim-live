@echo off
setlocal

set VULKAN_SDK=C:\VulkanSDK\1.4.350.0

rmdir /s /q build 2>nul
mkdir build\obj 2>nul
mkdir build\bin 2>nul

set INC=-I"%VULKAN_SDK%\Include" -Inative
set LIB=-L"%VULKAN_SDK%\Lib" -lvulkan-1

gcc -c native\platform.c        %INC% -o build\obj\platform.o      -std=c11 -Wall
gcc -c native\vulkan_render.c   %INC% -o build\obj\vulkan_render.o -std=c11 -Wall
g++ -c native\vulkan_bind.cpp   %INC% -o build\obj\vulkan_bind.o   -std=c++17 -Wall

g++ -shared -o build/bin/native.dll ^
build/obj/platform.o ^
build/obj/vulkan_render.o ^
build/obj/vulkan_bind.o ^
%LIB% -mwindows -Wl,--add-stdcall-alias -Wl,--kill-at

echo done
endlocal