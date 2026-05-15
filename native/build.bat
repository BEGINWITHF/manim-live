@echo off
pushd %~dp0
gcc -shared -m64 -o ../vulkan_core.dll platform.c -luser32 -lgdi32
echo 编译完成
pause
popd