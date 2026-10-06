"""Discovery of user-defined nodes placed in ``src/custom_nodes``.

Every module under ``src/custom_nodes`` (files and sub-packages, recursively) is imported once.
The compute registry and the UI registry each subscribe with ``on_custom_nodes_loaded`` and pick
the classes they need from the imported modules. The callback approach makes the result
independent of which side (compute or UI) happens to import a custom module first.
"""

import importlib
import inspect
import pkgutil
from typing import Callable, List, Optional

_modules: Optional[List] = None
_loading = False
_callbacks: List[Callable] = []


def _load():
    global _loading, _modules
    import src.custom_nodes as custom_nodes

    _loading = True
    try:
        modules = []
        prefix = custom_nodes.__name__ + "."

        def _on_error(name):
            raise RuntimeError(f"Failed to import custom node package '{name}'")

        for _, modname, _ in pkgutil.walk_packages(custom_nodes.__path__, prefix, _on_error):
            try:
                modules.append(importlib.import_module(modname))
            except Exception as e:
                raise RuntimeError(f"Failed to import custom node module '{modname}': {e}") from e
    finally:
        _loading = False
    _modules = modules

    callbacks = list(_callbacks)
    _callbacks.clear()
    for callback in callbacks:
        callback(modules)


def on_custom_nodes_loaded(callback: Callable[[list], None]):
    """Call ``callback(modules)`` once every module in ``src/custom_nodes`` has been imported."""
    if _modules is not None:
        callback(_modules)
        return
    _callbacks.append(callback)
    if not _loading:
        _load()


def get_classes(modules: list, base_cls: type, attr: str) -> list:
    """Classes defined in ``modules`` (not imported into them) that subclass ``base_cls``
    and set ``attr`` to a non-empty value."""
    result = []
    for module in modules:
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
            if not issubclass(obj, base_cls) or obj is base_cls:
                continue
            if not getattr(obj, attr, None):
                continue
            result.append(obj)
    return result
