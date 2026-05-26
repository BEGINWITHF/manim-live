import sys

def spv_to_c_array(input_file, array_name):
    with open(input_file, 'rb') as f:
        binary_data = f.read()
    
    # 确保数据长度是4的倍数
    if len(binary_data) % 4 != 0:
        raise ValueError("SPIR-V file size is not a multiple of 4")
        
    words = []
    for i in range(0, len(binary_data), 4):
        word = int.from_bytes(binary_data[i:i+4], byteorder='little')
        words.append(f"0x{word:08x}")
    
    # 每8个元素换一行，生成C数组代码
    formatted_words = []
    for i in range(0, len(words), 8):
        formatted_words.append("    " + ", ".join(words[i:i+8]) + ",")
    
    c_code = f"static const uint32_t {array_name}[] = {{\n"
    c_code += "\n".join(formatted_words)
    c_code += "\n};"
    return c_code

if __name__ == "__main__":
    # 转换顶点着色器
    vert_code = spv_to_c_array("assets/shaders/basic_vert.spv", "vert_spv")
    print("// Vertex Shader SPIR-V")
    print(vert_code)
    print("\n")
    
    # 转换片段着色器
    frag_code = spv_to_c_array("assets/shaders/basic_frag.spv", "frag_spv")
    print("// Fragment Shader SPIR-V")
    print(frag_code)