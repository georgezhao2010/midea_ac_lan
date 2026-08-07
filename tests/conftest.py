"""Configure sys.modules so that midea sub-packages can be imported without
Home Assistant / voluptuous being installed in the test environment."""
import importlib.util
import os
import sys
import types

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_midea = os.path.join(_root, "custom_components", "midea_ac_lan", "midea")


def _make_pkg(name, path=None):
    """Register a namespace package in sys.modules."""
    mod = types.ModuleType(name)
    mod.__package__ = name
    mod.__path__ = [path] if path else []
    sys.modules.setdefault(name, mod)
    return sys.modules[name]


def _load_module(fqn, path):
    """Load a single .py file under its fully-qualified module name."""
    if fqn in sys.modules:
        return sys.modules[fqn]
    spec = importlib.util.spec_from_file_location(fqn, path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = ".".join(fqn.split(".")[:-1])
    sys.modules[fqn] = mod
    spec.loader.exec_module(mod)
    return mod


# Build namespace packages for the midea hierarchy so relative imports resolve.
_make_pkg("custom_components")
_make_pkg("custom_components.midea_ac_lan")
_make_pkg("custom_components.midea_ac_lan.midea", _midea)
_make_pkg("custom_components.midea_ac_lan.midea.core", os.path.join(_midea, "core"))
_make_pkg("custom_components.midea_ac_lan.midea.devices", os.path.join(_midea, "devices"))
_make_pkg(
    "custom_components.midea_ac_lan.midea.devices.ac",
    os.path.join(_midea, "devices", "ac"),
)

# Load the leaf modules that ac/message.py depends on.
_load_module(
    "custom_components.midea_ac_lan.midea.core.crc8",
    os.path.join(_midea, "core", "crc8.py"),
)
_load_module(
    "custom_components.midea_ac_lan.midea.core.message",
    os.path.join(_midea, "core", "message.py"),
)
_load_module(
    "custom_components.midea_ac_lan.midea.devices.ac.message",
    os.path.join(_midea, "devices", "ac", "message.py"),
)
