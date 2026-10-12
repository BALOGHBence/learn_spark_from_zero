# This file's sole purpose is to make `_config` a Python package, which is required
# for `importlib.resources.files()` to locate files inside it.
#
# `importlib.resources.files()` anchors lookups to a Python package identified by its
# dotted import name.  Without this `__init__.py`, `_config` is a plain directory and
# the lookup raises ModuleNotFoundError:
#
#   >>> from importlib.resources import files
#   >>> files("my_project._config")   # fails without __init__.py
#   ModuleNotFoundError: No module named 'my_project._config'
#
# With it, the lookup succeeds across all install modes (editable, wheel, zip archive):
#
#   >>> resource = files("my_project._config").joinpath("config.yaml")
#   >>> resource.read_text(encoding="utf-8")
#   '_meta:\n  default_environment: "dev"\n  ...'
