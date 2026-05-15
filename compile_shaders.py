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
        print(f"✅{output_path}\n")
    else:
        print("❌")
        print(result.stderr)

compile_shader("renderer/shaders/vert.glsl", "renderer/shaders/vert.spv", "vertex")

compile_shader("renderer/shaders/frag.glsl", "renderer/shaders/frag.spv", "fragment")