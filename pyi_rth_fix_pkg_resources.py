"""
Runtime hook to fix pkg_resources issues with PyInstaller
"""
import sys

# Patch pkg_resources if it's causing issues
try:
    import pkg_resources
    # If NullProvider doesn't exist, create a dummy
    if not hasattr(pkg_resources, 'NullProvider'):
        class NullProvider:
            def __init__(self, module):
                self.module = module
            def get_resource_filename(self, manager, resource_name):
                return None
        pkg_resources.NullProvider = NullProvider
except ImportError:
    pass  # pkg_resources not available, that's fine
