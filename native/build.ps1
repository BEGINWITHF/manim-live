Set-Location $PSScriptRoot

$vulkanBase = "C:\VulkanSDK"

if (Test-Path $vulkanBase) {
    $latestVersion = Get-ChildItem -Path $vulkanBase -Directory | 
                     Where-Object { $_.Name -match '^\d+(\.\d+){2,3}$' } | 
                     Sort-Object Name -Descending | 
                     Select-Object -First 1
    
    if ($latestVersion) {
        $env:VULKAN_SDK = $latestVersion.FullName
        Write-Host "[SUCCESS] Auto-detected Vulkan SDK path: $env:VULKAN_SDK" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] No valid SDK version folder found under $vulkanBase." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] $vulkanBase not found. Please make sure Vulkan SDK is installed." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Compiling vulkan_core.dll..." -ForegroundColor Cyan

gcc -shared -m64 -o "../vulkan_core.dll" `
    "platform.c" `
    "vulkan_init.c" `
    "vulkan_draw.c" `
    -I"$env:VULKAN_SDK/Include" `
    -L"$env:VULKAN_SDK/Lib" `
    -lvulkan-1 `
    -luser32

if ($LASTEXITCODE -eq 0) {
    Write-Host "[DONE] vulkan_core.dll compiled successfully!" -ForegroundColor Green
} else {
    Write-Host "[FAILED] Compilation errors occurred. Please check the messages above." -ForegroundColor Red
}