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

import bpy

# Import modules
from . import ui

# Registration
def register():
    """Register all addon classes"""
    ui.register()
    print("Non-Orientable UV Unwrapping addon registered")


def unregister():
    """Unregister all addon classes"""
    ui.unregister()
    print("Non-Orientable UV Unwrapping addon unregistered")


if __name__ == "__main__":
    register()
