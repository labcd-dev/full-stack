"""Compatibility shim: redirects legacy backend_core imports to backend_api."""

import importlib.abc
import importlib.util
import sys


class _BackendCoreRedirect(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("backend_core"):
            return None
        redirected = "backend_api" + fullname[len("backend_core") :]
        return importlib.util.find_spec(redirected)


if not any(isinstance(finder, _BackendCoreRedirect) for finder in sys.meta_path):
    sys.meta_path.insert(0, _BackendCoreRedirect())
