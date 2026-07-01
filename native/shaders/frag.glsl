#version 450

layout(location = 0) in vec3 fragColor;
layout(location = 1) in float fragAlpha;

layout(location = 0) out vec4 outColor;

void main() {
    outColor = vec4(fragColor, fragAlpha);
}
