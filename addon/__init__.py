"""
Non-Orientable UV Unwrapping Blender Addon

A novel UV parameterization method that eliminates visible texture seams
by representing surface coordinates on non-orientable quotient domains.
"""

bl_info = {
    "name": "Non-Orientable UV Unwrapping",
    "author": "MacMayo1993",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "UV Editor > Sidebar > Non-Orientable",
    "description": "Seamless UV unwrapping via non-orientable topology",
    "warning": "",
    "doc_url": "https://github.com/MacMayo1993/SEAM-UV-Mapping",
    "category": "UV",
}

try:
    import bpy

    # Import modules (only when running in Blender)
    from . import ui

    _HAS_BLENDER = True
except ImportError:
    # Allow importing core modules without Blender for testing/benchmarking
    _HAS_BLENDER = False
    bpy = None


# Registration
def register():
    """Register all addon classes"""
    if not _HAS_BLENDER:
        raise RuntimeError("Blender (bpy) is required for addon registration")
    ui.register()
    print("Non-Orientable UV Unwrapping addon registered")


def unregister():
    """Unregister all addon classes"""
    if not _HAS_BLENDER:
        raise RuntimeError("Blender (bpy) is required for addon unregistration")
    ui.unregister()
    print("Non-Orientable UV Unwrapping addon unregistered")


if __name__ == "__main__":
    register()
