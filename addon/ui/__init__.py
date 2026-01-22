"""
Blender UI integration for non-orientable UV unwrapping.
"""

import bpy

from . import operators
from . import panels
from . import shader_nodes

# List of classes to register
classes = (
    operators.NonOrientableUnwrapOperator,
    operators.CreateParityShaderOperator,
    panels.NonOrientablePanel,
)


def register():
    """Register all UI classes"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all UI classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
