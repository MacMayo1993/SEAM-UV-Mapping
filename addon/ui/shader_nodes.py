"""
Shader node utilities for parity-aware rendering.
"""

import bpy


def create_parity_aware_material(
    name: str = "ParityMaterial", texture_path: str | None = None
) -> bpy.types.Material:
    """
    Create a complete parity-aware material.

    Args:
        name: Material name
        texture_path: Optional path to texture image

    Returns:
        Created material
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes

    # Clear default nodes
    nodes.clear()

    # Create node tree
    _build_parity_shader_tree(mat.node_tree, texture_path)

    return mat


def _build_parity_shader_tree(node_tree: bpy.types.NodeTree, texture_path: str | None = None):
    """
    Build parity-aware shader node tree.

    Node structure:
        [Parity Attr] -> [Compare < 0] -> [Mix Factor]
        [UV Map] -> [Vector Subtract (1,1) - UV] -> [Mix B]
        [UV Map] -> [Mix A]
        [Mix] -> [Image Texture] -> [Principled BSDF] -> [Output]

    Args:
        node_tree: Node tree to build in
        texture_path: Optional texture image path
    """
    nodes = node_tree.nodes
    links = node_tree.links

    # Output node
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (600, 0)
    output_node.name = "Material Output"

    # Principled BSDF
    bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf_node.location = (300, 0)
    bsdf_node.name = "Principled BSDF"

    # Image Texture
    tex_node = nodes.new(type="ShaderNodeTexImage")
    tex_node.location = (0, 0)
    tex_node.name = "Image Texture"

    if texture_path:
        try:
            img = bpy.data.images.load(texture_path)
            tex_node.image = img
        except Exception:
            pass

    # Mix RGB (for UV selection based on parity)
    mix_node = nodes.new(type="ShaderNodeMix")
    mix_node.data_type = "VECTOR"
    mix_node.location = (-300, 0)
    mix_node.name = "UV Mix"

    # Parity attribute
    parity_node = nodes.new(type="ShaderNodeAttribute")
    parity_node.attribute_name = "parity"
    parity_node.location = (-800, 200)
    parity_node.name = "Parity Attribute"

    # Compare parity < 0
    compare_node = nodes.new(type="ShaderNodeMath")
    compare_node.operation = "LESS_THAN"
    compare_node.inputs[1].default_value = 0.0
    compare_node.location = (-600, 200)
    compare_node.name = "Parity < 0"

    # UV Map
    uv_node = nodes.new(type="ShaderNodeUVMap")
    uv_node.location = (-800, -200)
    uv_node.name = "UV Map"

    # Vector subtract: (1, 1, 0) - UV
    subtract_node = nodes.new(type="ShaderNodeVectorMath")
    subtract_node.operation = "SUBTRACT"
    subtract_node.inputs[0].default_value = (1.0, 1.0, 0.0)
    subtract_node.location = (-600, -200)
    subtract_node.name = "Antipodal UV"

    # Connect nodes
    links.new(parity_node.outputs["Fac"], compare_node.inputs[0])
    links.new(compare_node.outputs["Value"], mix_node.inputs[0])  # Factor
    links.new(uv_node.outputs["UV"], mix_node.inputs[4])  # A (positive parity)
    links.new(uv_node.outputs["UV"], subtract_node.inputs[1])
    links.new(subtract_node.outputs["Vector"], mix_node.inputs[5])  # B (negative parity)
    links.new(mix_node.outputs["Result"], tex_node.inputs["Vector"])
    links.new(tex_node.outputs["Color"], bsdf_node.inputs["Base Color"])
    links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

    # Organize layout
    node_tree.nodes.update()


def add_normal_map_support(material: bpy.types.Material):
    """
    Add normal map support to parity-aware material.

    Args:
        material: Material to modify
    """
    if not material.use_nodes:
        return

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find BSDF node
    bsdf_node = nodes.get("Principled BSDF")
    if not bsdf_node:
        return

    # Find UV Mix node
    mix_node = nodes.get("UV Mix")
    if not mix_node:
        return

    # Create normal map texture
    normal_tex = nodes.new(type="ShaderNodeTexImage")
    normal_tex.location = (0, -400)
    normal_tex.name = "Normal Map Texture"

    # Normal map node
    normal_map = nodes.new(type="ShaderNodeNormalMap")
    normal_map.location = (300, -400)
    normal_map.name = "Normal Map"

    # Connect
    links.new(mix_node.outputs["Result"], normal_tex.inputs["Vector"])
    links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf_node.inputs["Normal"])


def get_parity_statistics(obj: bpy.types.Object) -> dict:
    """
    Get parity statistics for a mesh object.

    Args:
        obj: Mesh object with parity attribute

    Returns:
        Dictionary with parity statistics
    """
    if obj.type != "MESH" or "parity" not in obj.data.attributes:
        return {}

    parity_attr = obj.data.attributes["parity"]
    parities = [v.value for v in parity_attr.data]

    positive = sum(1 for p in parities if p > 0)
    negative = sum(1 for p in parities if p < 0)

    return {
        "total_vertices": len(parities),
        "positive_parity": positive,
        "negative_parity": negative,
        "balance": positive - negative,
        "ratio": positive / len(parities) if parities else 0.0,
    }
