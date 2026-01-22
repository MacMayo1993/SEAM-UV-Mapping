/**
 * Normal Map Correction Shader for Parity-Aware UV Mapping
 *
 * When using parity-aware UV mapping with normal maps, we need to correct
 * the tangent space orientation for negative-parity vertices.
 */

#ifdef FRAGMENT_SHADER

in vec2 fragUV;
in float fragParity;
in vec3 fragNormal;     // Geometric normal
in vec3 fragTangent;    // Tangent vector
in vec3 fragBitangent;  // Bitangent vector

out vec4 fragColor;

uniform sampler2D normalMap;
uniform float normalStrength;

/**
 * Apply antipodal UV correction.
 */
vec2 correctUV(vec2 uv, float parity) {
    if (parity < 0.0) {
        return vec2(1.0, 1.0) - uv;
    }
    return uv;
}

/**
 * Construct TBN (Tangent-Bitangent-Normal) matrix for tangent space.
 *
 * For negative parity, we need to flip the tangent and bitangent
 * to account for the UV transformation.
 */
mat3 constructTBN(vec3 normal, vec3 tangent, vec3 bitangent, float parity) {
    // Normalize vectors
    vec3 N = normalize(normal);
    vec3 T = normalize(tangent);
    vec3 B = normalize(bitangent);

    // Flip tangent space for negative parity
    if (parity < 0.0) {
        T = -T;
        B = -B;
    }

    // Construct TBN matrix (tangent space to world space)
    return mat3(T, B, N);
}

/**
 * Sample and apply normal map with parity correction.
 */
vec3 applyNormalMap(
    sampler2D normalTex,
    vec2 uv,
    float parity,
    vec3 geometricNormal,
    vec3 tangent,
    vec3 bitangent,
    float strength
) {
    // Correct UV coordinates
    vec2 correctedUV = correctUV(uv, parity);

    // Sample normal map
    vec3 normalTS = texture(normalTex, correctedUV).rgb;

    // Convert from [0, 1] to [-1, 1]
    normalTS = normalTS * 2.0 - 1.0;

    // Apply strength
    normalTS.xy *= strength;
    normalTS = normalize(normalTS);

    // Construct TBN matrix with parity correction
    mat3 TBN = constructTBN(geometricNormal, tangent, bitangent, parity);

    // Transform from tangent space to world space
    vec3 worldNormal = TBN * normalTS;

    return normalize(worldNormal);
}

void main() {
    // Apply parity-corrected normal map
    vec3 normal = applyNormalMap(
        normalMap,
        fragUV,
        fragParity,
        fragNormal,
        fragTangent,
        fragBitangent,
        normalStrength
    );

    // Output normal for lighting calculations
    // (In actual use, this would feed into PBR shading)
    fragColor = vec4(normal * 0.5 + 0.5, 1.0);  // Visualize normal
}

#endif

/**
 * OSL version for Cycles normal map correction
 */
#ifdef OSL_SHADER

shader normal_correct(
    vector UV = vector(0, 0, 0),
    float Parity = 1.0,
    normal GeometricNormal = N,
    vector Tangent = dPdu,
    string NormalMap = "",
    float Strength = 1.0,
    output normal Normal = N
) {
    // Correct UV
    vector correctedUV = UV;
    if (Parity < 0.0) {
        correctedUV[0] = 1.0 - UV[0];
        correctedUV[1] = 1.0 - UV[1];
    }

    // Sample normal map
    color normalColor = texture(NormalMap, correctedUV[0], correctedUV[1]);
    vector normalTS = vector(
        normalColor[0] * 2.0 - 1.0,
        normalColor[1] * 2.0 - 1.0,
        normalColor[2] * 2.0 - 1.0
    );

    // Apply strength
    normalTS[0] *= Strength;
    normalTS[1] *= Strength;
    normalTS = normalize(normalTS);

    // Construct TBN
    vector T = Tangent;
    vector N = GeometricNormal;
    vector B = cross(N, T);

    // Flip for negative parity
    if (Parity < 0.0) {
        T = -T;
        B = -B;
    }

    // Transform to world space
    Normal = normalize(
        normalTS[0] * T +
        normalTS[1] * B +
        normalTS[2] * N
    );
}

#endif

/**
 * Additional utility functions
 */

/**
 * Compute tangent space from UV derivatives (automatic tangent generation).
 * Useful when tangent attributes are not available.
 */
#ifdef FRAGMENT_SHADER

vec3 computeTangentFromDerivatives(vec3 position, vec2 uv, vec3 normal) {
    // Compute position derivatives
    vec3 dp1 = dFdx(position);
    vec3 dp2 = dFdy(position);

    // Compute UV derivatives
    vec2 duv1 = dFdx(uv);
    vec2 duv2 = dFdy(uv);

    // Solve for tangent
    vec3 dp2perp = cross(dp2, normal);
    vec3 dp1perp = cross(normal, dp1);

    vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
    vec3 B = dp2perp * duv1.y + dp1perp * duv2.y;

    // Normalize
    float invmax = 1.0 / sqrt(max(dot(T, T), dot(B, B)));
    return T * invmax;
}

#endif
