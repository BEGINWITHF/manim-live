import subprocess

def compile_shader(input_path, output_path, stage):
    cmd = [
        "glslc.exe",
        f"-fshader-stage={stage}",  # 正确格式！
        input_path,
        "-o", output_path
    ]
    
    print(f"编译: {input_path}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 成功: {output_path}\n")
    else:
        print("❌ 失败:")
        print(result.stderr)

# 编译顶点着色器
compile_shader("renderer/shaders/vert.glsl", "renderer/shaders/vert.spv", "vertex")

# 编译片段着色器
compile_shader("renderer/shaders/frag.glsl", "renderer/shaders/frag.spv", "fragment")