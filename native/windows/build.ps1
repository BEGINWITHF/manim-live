Set-Location $PSScriptRoot

$BuildConfig = if ($args.Count -gt 0 -and $args[0] -eq "debug") { "debug" } else { "release" }
$Version = "1.0.0"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$BuildDir = Join-Path $ProjectRoot "build"
$DistDir = Join-Path $ProjectRoot "dist"
$ObjDir = Join-Path $BuildDir $BuildConfig
$OutputDir = Join-Path $DistDir $BuildConfig

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
New-Item -ItemType Directory -Force -Path $DistDir | Out-Null
New-Item -ItemType Directory -Force -Path $ObjDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Manim Vulkan Native Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration: $BuildConfig" -ForegroundColor Yellow
Write-Host "Version: $Version" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$vulkanBase = "C:\VulkanSDK"
if (Test-Path $vulkanBase) {
    $latestVersion = Get-ChildItem -Path $vulkanBase -Directory | 
                     Where-Object { $_.Name -match '^\d+(\.\d+){2,3}$' } | 
                     Sort-Object Name -Descending | 
                     Select-Object -First 1
    
    if ($latestVersion) {
        $env:VULKAN_SDK = $latestVersion.FullName
        Write-Host "[SUCCESS] Vulkan SDK: $env:VULKAN_SDK" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] No valid SDK version found under $vulkanBase" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] Vulkan SDK not found at $vulkanBase" -ForegroundColor Red
    exit 1
}

$CommonFlags = "-shared -m64"
if ($BuildConfig -eq "debug") {
    $OptimizationFlags = "-O0 -g -DDEBUG"
    $OutputSuffix = "_debug"
} else {
    $OptimizationFlags = "-O2 -DNDEBUG"
    $OutputSuffix = ""
}

$CompilerFlags = "$CommonFlags $OptimizationFlags"

$OutputName = "vulkan_core${OutputSuffix}.dll"
$OutputPath = Join-Path $OutputDir $OutputName

$SourceFiles = @(
    "platform.c",
    "vulkan_init.c",
    "vulkan_draw.c"
)

Write-Host "[INFO] Compiling source files to object files..." -ForegroundColor Cyan
$ObjectFiles = @()
foreach ($src in $SourceFiles) {
    if (Test-Path $src) {
        $objName = $src -replace '\.c$', '.o'
        $objPath = Join-Path $ObjDir $objName
        $ObjectFiles += $objPath
        
        $CompileCmd = "gcc -c $CompilerFlags -o `"$objPath`" `"$src`" -I`"$env:VULKAN_SDK/Include`""
        Write-Host "[CMD] $CompileCmd" -ForegroundColor DarkGray
        Invoke-Expression $CompileCmd
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Compilation failed for $src" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[ERROR] Source file not found: $src" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[INFO] Linking object files to DLL..." -ForegroundColor Cyan
$LinkCmd = "gcc $CompilerFlags -o `"$OutputPath`""
foreach ($obj in $ObjectFiles) {
    $LinkCmd += " `"$obj`""
}
$LinkCmd += " -L`"$env:VULKAN_SDK/Lib`" -lvulkan-1 -luser32"

Write-Host "[CMD] $LinkCmd" -ForegroundColor DarkGray
Invoke-Expression $LinkCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Compilation successful!" -ForegroundColor Green
    Write-Host "[INFO] Output: $OutputPath" -ForegroundColor Cyan
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " Build Complete" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Compilation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}