/**
 * Parity-Aware Texture Sampling Shader
 *
 * This GLSL shader implements parity-aware texture sampling for non-orientable
 * UV parameterizations. It checks the vertex parity attribute and applies
 * antipodal correction when needed.
 *
 * Usage in Blender Cycles/EEVEE:
 *   - Input: UV coordinates (vec2)
 *   - Input: Parity attribute (float, ±1)
 *   - Output: Corrected UV coordinates (vec2)
 */

// Vertex shader
#ifdef VERTEX_SHADER

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uv;
layout(location = 2) in float parity;  // Vertex attribute: ±1

out vec2 fragUV;
out float fragParity;

uniform mat4 modelViewProjection;

void main() {
    gl_Position = modelViewProjection * vec4(position, 1.0);
    fragUV = uv;
    fragParity = parity;
}

#endif

// Fragment shader
#ifdef FRAGMENT_SHADER

in vec2 fragUV;
in float fragParity;

out vec4 fragColor;

uniform sampler2D baseColorTexture;
uniform sampler2D normalTexture;
uniform bool useNormalMap;

/**
 * Apply antipodal correction to UV coordinates based on parity.
 *
 * For negative parity (σ = -1), we apply the transformation:
 *   UV' = (1, 1) - UV
 *
 * This implements the quotient identification:
 *   (u, v, +1) ≡ (1-u, 1-v, -1)
 */
vec2 correctUV(vec2 uv, float parity) {
    if (parity < 0.0) {
        return vec2(1.0, 1.0) - uv;
    }
    return uv;
}

/**
 * Sample texture with parity-aware UV correction.
 */
vec4 sampleTexture(sampler2D tex, vec2 uv, float parity) {
    vec2 correctedUV = correctUV(uv, parity);
    return texture(tex, correctedUV);
}

/**
 * Sample normal map with parity-aware correction.
 *
 * For negative parity, we also need to flip the normal map
 * to maintain consistency with the UV transformation.
 */
vec3 sampleNormal(sampler2D normalTex, vec2 uv, float parity) {
    vec2 correctedUV = correctUV(uv, parity);
    vec3 normal = texture(normalTex, correctedUV).rgb;

    // Convert from [0, 1] to [-1, 1]
    normal = normal * 2.0 - 1.0;

    // Flip normal for negative parity
    if (parity < 0.0) {
        normal.xy = -normal.xy;  // Flip tangent space X and Y
    }

    return normal;
}

void main() {
    // Sample base color with parity correction
    vec4 baseColor = sampleTexture(baseColorTexture, fragUV, fragParity);

    // Simple shading (can be extended with full PBR)
    fragColor = baseColor;

    // Optional: Sample normal map
    if (useNormalMap) {
        vec3 normal = sampleNormal(normalTexture, fragUV, fragParity);
        // Apply normal to lighting calculations...
        // (This is a simplified example)
    }
}

#endif

/**
 * OSL (Open Shading Language) version for Cycles
 *
 * This can be used in Blender Cycles via Script nodes.
 */
#ifdef OSL_SHADER

shader parity_aware_sample(
    vector UV = vector(0, 0, 0),
    float Parity = 1.0,
    string Filename = "",
    output color Color = 0.0
) {
    // Apply antipodal correction
    vector correctedUV = UV;
    if (Parity < 0.0) {
        correctedUV[0] = 1.0 - UV[0];
        correctedUV[1] = 1.0 - UV[1];
    }

    // Sample texture
    Color = texture(Filename, correctedUV[0], correctedUV[1]);
}

#endif
