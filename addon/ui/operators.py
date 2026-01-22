"""
Blender operators for non-orientable UV unwrapping.
"""

import bpy
import bmesh
import numpy as np
from typing import Set

from ..core.topology import TopologicalUVAtlas


class NonOrientableUnwrapOperator(bpy.types.Operator):
    """Non-orientable UV unwrapping operator"""

    bl_idname = "uv.non_orientable_unwrap"
    bl_label = "Non-Orientable UV Unwrap"
    bl_description = "Unwrap mesh using non-orientable topology (eliminates seams)"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties
    k_star: bpy.props.FloatProperty(
        name="k* Threshold",
        description="Stitch edge selection threshold (0-1). Higher = more stitch edges",
        default=0.721,
        min=0.0,
        max=1.0,
        step=0.01
    )

    verbose: bpy.props.BoolProperty(
        name="Verbose",
        description="Print progress messages to console",
        default=False
    )

    @classmethod
    def poll(cls, context):
        """Check if operator can run"""
        obj = context.active_object
        return (obj is not None and
                obj.type == 'MESH' and
                obj.mode in {'OBJECT', 'EDIT'})

    def execute(self, context):
        """Execute the unwrapping"""
        obj = context.active_object

        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}

        try:
            # Get mesh data
            mesh = obj.data
            bm = bmesh.new()

            if obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(mesh)
            else:
                bm.from_mesh(mesh)

            # Convert to numpy arrays
            vertices = np.array([v.co for v in bm.verts], dtype=np.float64)
            triangles = []

            for face in bm.faces:
                if len(face.verts) == 3:
                    triangles.append([v.index for v in face.verts])
                elif len(face.verts) == 4:
                    # Triangulate quads
                    verts = [v.index for v in face.verts]
                    triangles.append([verts[0], verts[1], verts[2]])
                    triangles.append([verts[0], verts[2], verts[3]])
                else:
                    # N-gons: simple fan triangulation
                    verts = [v.index for v in face.verts]
                    for i in range(1, len(verts) - 1):
                        triangles.append([verts[0], verts[i], verts[i + 1]])

            triangles = np.array(triangles, dtype=np.int32)

            if self.verbose:
                self.report({'INFO'}, f"Processing {len(vertices)} vertices, {len(triangles)} triangles")

            # Run algorithm
            atlas = TopologicalUVAtlas(
                vertices,
                triangles,
                k_star=self.k_star,
                verbose=self.verbose
            )

            # Create UV layer if not exists
            if not mesh.uv_layers:
                mesh.uv_layers.new(name="UVMap")

            uv_layer = mesh.uv_layers.active

            # Apply UVs to mesh
            bm.faces.ensure_lookup_table()
            bm.verts.ensure_lookup_table()

            for face in bm.faces:
                for loop in face.loops:
                    vert_idx = loop.vert.index
                    uv = atlas.vertex_uvs[vert_idx]
                    loop[uv_layer].uv = uv

            # Store parity as vertex attribute
            if "parity" not in mesh.attributes:
                mesh.attributes.new(name="parity", type='INT', domain='POINT')

            parity_attr = mesh.attributes["parity"]
            for i, parity in enumerate(atlas.vertex_parities):
                parity_attr.data[i].value = int(parity)

            # Update mesh
            if obj.mode == 'EDIT':
                bmesh.update_edit_mesh(mesh)
            else:
                bm.to_mesh(mesh)
                mesh.update()

            bm.free()

            # Report stats
            stats = atlas.get_stats()
            self.report({'INFO'},
                       f"Unwrapping complete: {stats['num_stitch_edges']} stitch edges "
                       f"({stats['stitch_fraction']*100:.1f}%)")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Unwrapping failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


class CreateParityShaderOperator(bpy.types.Operator):
    """Create parity-aware shader for rendering"""

    bl_idname = "uv.create_parity_shader"
    bl_label = "Create Parity-Aware Shader"
    bl_description = "Create shader node tree for parity-aware texture sampling"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Check if operator can run"""
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def execute(self, context):
        """Create shader"""
        obj = context.active_object
        mesh = obj.data

        # Check parity attribute exists
        if "parity" not in mesh.attributes:
            self.report({'WARNING'},
                       "Parity attribute not found. Run Non-Orientable UV Unwrap first.")
            return {'CANCELLED'}

        # Create material if not exists
        if not obj.data.materials:
            mat = bpy.data.materials.new(name="ParityMaterial")
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]

        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Clear existing nodes
        nodes.clear()

        # Create nodes
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (400, 0)

        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (0, 0)

        # Parity attribute node
        parity_node = nodes.new(type='ShaderNodeAttribute')
        parity_node.attribute_name = "parity"
        parity_node.location = (-800, 0)

        # UV Map node
        uv_node = nodes.new(type='ShaderNodeUVMap')
        uv_node.location = (-800, -200)

        # Math node: check if parity < 0
        compare_node = nodes.new(type='ShaderNodeMath')
        compare_node.operation = 'LESS_THAN'
        compare_node.inputs[1].default_value = 0.0
        compare_node.location = (-600, 0)

        # Vector Math: compute (1, 1) - UV
        subtract_node = nodes.new(type='ShaderNodeVectorMath')
        subtract_node.operation = 'SUBTRACT'
        subtract_node.inputs[0].default_value = (1.0, 1.0, 0.0)
        subtract_node.location = (-600, -200)

        # Mix node: select UV based on parity
        mix_node = nodes.new(type='ShaderNodeMix')
        mix_node.data_type = 'VECTOR'
        mix_node.location = (-400, -100)

        # Image texture node
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.location = (-200, -100)

        # Connect nodes
        links.new(parity_node.outputs['Fac'], compare_node.inputs[0])
        links.new(uv_node.outputs['UV'], subtract_node.inputs[1])
        links.new(uv_node.outputs['UV'], mix_node.inputs[4])  # A
        links.new(subtract_node.outputs['Vector'], mix_node.inputs[5])  # B
        links.new(compare_node.outputs['Value'], mix_node.inputs[0])  # Factor
        links.new(mix_node.outputs['Result'], tex_node.inputs['Vector'])
        links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
        links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

        self.report({'INFO'}, "Parity-aware shader created successfully")

        return {'FINISHED'}
