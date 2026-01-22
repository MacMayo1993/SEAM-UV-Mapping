"""
Blender UI panels for non-orientable UV unwrapping.
"""

import bpy


class NonOrientablePanel(bpy.types.Panel):
    """Panel in UV Editor sidebar"""

    bl_label = "Non-Orientable UV"
    bl_idname = "UV_PT_non_orientable"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Non-Orientable'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # Title
        layout.label(text="Seamless UV Unwrapping", icon='UV')

        # Info box
        box = layout.box()
        box.label(text="Eliminates seams via", icon='INFO')
        box.label(text="non-orientable topology")

        layout.separator()

        # Unwrap section
        col = layout.column(align=True)
        col.label(text="Unwrap:")

        # Unwrap operator
        unwrap_op = col.operator("uv.non_orientable_unwrap",
                                  text="Non-Orientable Unwrap",
                                  icon='UV')

        # Parameters
        row = col.row(align=True)
        row.label(text="k* Threshold:")

        # Settings box
        box = layout.box()
        box.label(text="Settings:")
        box.prop(context.scene, "non_orientable_k_star",
                text="k*", slider=True)
        box.prop(context.scene, "non_orientable_verbose",
                text="Verbose Output")

        layout.separator()

        # Shader section
        col = layout.column(align=True)
        col.label(text="Rendering:")
        col.operator("uv.create_parity_shader",
                    text="Create Parity Shader",
                    icon='SHADING_TEXTURE')

        layout.separator()

        # Info section
        if obj and obj.type == 'MESH' and "parity" in obj.data.attributes:
            box = layout.box()
            box.label(text="Parity Info:", icon='CHECKMARK')
            mesh = obj.data
            parity_attr = mesh.attributes["parity"]

            # Count parities
            positive = sum(1 for v in parity_attr.data if v.value > 0)
            negative = len(parity_attr.data) - positive

            box.label(text=f"Positive: {positive}")
            box.label(text=f"Negative: {negative}")
            box.label(text=f"Balance: {positive - negative}")

        # Help section
        layout.separator()
        box = layout.box()
        box.label(text="Help:", icon='QUESTION')
        box.label(text="1. Unwrap mesh")
        box.label(text="2. Create parity shader")
        box.label(text="3. Load textures")
        box.label(text="4. Render (Cycles/EEVEE)")


# Scene properties
def register_properties():
    """Register scene properties"""
    bpy.types.Scene.non_orientable_k_star = bpy.props.FloatProperty(
        name="k* Threshold",
        description="Stitch edge selection threshold",
        default=0.721,
        min=0.0,
        max=1.0,
        step=0.01
    )

    bpy.types.Scene.non_orientable_verbose = bpy.props.BoolProperty(
        name="Verbose",
        description="Print progress to console",
        default=False
    )


def unregister_properties():
    """Unregister scene properties"""
    del bpy.types.Scene.non_orientable_k_star
    del bpy.types.Scene.non_orientable_verbose


# Auto-register properties
register_properties()
