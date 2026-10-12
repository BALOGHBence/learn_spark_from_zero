from importlib.metadata import metadata

__pkg_name__ = "my_project"
__pkg_metadata__ = metadata(__pkg_name__)
__version__ = __pkg_metadata__["version"]
del __pkg_metadata__
