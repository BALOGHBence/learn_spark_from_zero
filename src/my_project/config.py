"""
Configuration loader for datapao.experimental.docintel.

Typical usage::

    from datapao.experimental.docintel.config import Config

    cfg = Config()                                    # uses defaults from meta.yaml
    cfg = Config(catalog="my_catalog")                # override catalog only
    cfg = Config(catalog="my_catalog", schema="dev")  # override both

    path  = cfg.asset("wheels_volume")                # resolved path (any type)
    path  = cfg.table("project_assets")               # resolved path, asserts type is table
    value = cfg.setting("CANONICAL_TS_COL")           # typed setting value
"""

from functools import cached_property
from importlib.resources import files
from typing import Any, Literal

import yaml


# Recognised asset types. The YAML entry for an asset must contain exactly one
# of these keys; that key identifies the asset's type and holds its path template.
AssetType = Literal["table", "view", "function", "volume", "folder"]
_ASSET_TYPES: tuple[AssetType, ...] = ("table", "view", "function", "volume", "folder")


class AssetNotFoundError(KeyError):
    """Raised when an unknown asset key is requested."""


class AssetTypeMismatchError(TypeError):
    """Raised when an asset exists but is not of the expected type."""


class SettingNotFoundError(KeyError):
    """Raised when an unknown setting key is requested."""


class Config:
    """
    Loads the bundled YAML configuration files and resolves asset paths for a
    given Unity Catalog location.

    All ``*.yaml`` files inside the ``_config/`` package are loaded and merged
    at instantiation time.  When ``catalog`` or ``schema`` are omitted, the
    defaults declared in ``meta.yaml`` are used.

    Parameters
    ----------
    catalog:
        Unity Catalog catalog name.  Overrides ``meta.default_catalog``.
    schema:
        Unity Catalog schema name.  Overrides ``meta.default_schema``.
    """

    def __init__(
        self,
        catalog: str | None = None,
        schema: str | None = None,
    ) -> None:
        self._explicit_catalog = catalog
        self._explicit_schema = schema

    # ------------------------------------------------------------------
    # Internal: raw YAML data, loaded and merged once per Config instance
    # ------------------------------------------------------------------

    @cached_property
    def _raw(self) -> dict[str, Any]:
        pkg = files("datapao.experimental.docintel._config")
        merged: dict[str, Any] = {}
        for resource in sorted(pkg.iterdir(), key=lambda r: r.name):
            if resource.name.endswith(".yaml"):
                data = yaml.safe_load(resource.read_text(encoding="utf-8")) or {}
                for key, value in data.items():
                    if key in merged and isinstance(merged[key], dict):
                        merged[key].update(value)
                    else:
                        merged[key] = value
        return merged

    @cached_property
    def _meta(self) -> dict[str, Any]:
        return self._raw.get("meta", {})  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Catalog / schema resolution
    # ------------------------------------------------------------------

    @cached_property
    def catalog(self) -> str:
        """The resolved catalog name."""
        return self._explicit_catalog or self._meta.get("default_catalog", "")

    @cached_property
    def schema(self) -> str:
        """The resolved schema name."""
        return self._explicit_schema or self._meta.get("default_schema", "")

    # ------------------------------------------------------------------
    # Internal asset helpers
    # ------------------------------------------------------------------

    def _asset_entry(self, key: str) -> dict[str, Any]:
        assets: dict[str, Any] = self._raw.get("assets", {})
        if key not in assets:
            raise AssetNotFoundError(
                f"Asset {key!r} not found. Available assets: {sorted(assets)}"
            )
        return assets[key]

    def _asset_type(self, entry: dict[str, Any]) -> AssetType:
        for t in _ASSET_TYPES:
            if t in entry:
                return t
        raise AssetNotFoundError(
            f"Asset entry has no recognised type key. Expected one of: {_ASSET_TYPES}"
        )

    def _resolve_path(self, template: str) -> str:
        return template.format_map({"catalog": self.catalog, "schema": self.schema})

    def _resolve_asset(self, key: str, asset_type: AssetType | None = None) -> str:
        entry = self._asset_entry(key)
        if asset_type is not None:
            if asset_type not in entry:
                actual = self._asset_type(entry)
                raise AssetTypeMismatchError(
                    f"Asset {key!r} is a {actual!r}, not a {asset_type!r}."
                )
            return self._resolve_path(entry[asset_type])
        return self._resolve_path(entry[self._asset_type(entry)])

    def _list_by_type(self, asset_type: AssetType) -> list[str]:
        return sorted(
            k for k, v in self._raw.get("assets", {}).items() if asset_type in v
        )

    # ------------------------------------------------------------------
    # Generic asset access
    # ------------------------------------------------------------------

    def asset(self, key: str) -> str:
        """
        Return the resolved path for *key*, regardless of its type.

        Parameters
        ----------
        key:
            Asset name as defined in the YAML (e.g. ``"documents"``).

        Raises
        ------
        AssetNotFoundError
            When *key* is not defined or has no recognised type key.
        """
        return self._resolve_asset(key)

    def asset_metadata(self, key: str) -> dict[str, Any]:
        """Return the full asset entry with the path placeholder resolved."""
        entry = dict(self._asset_entry(key))
        asset_type = self._asset_type(entry)
        entry[asset_type] = self._resolve_path(entry[asset_type])
        return entry

    def list_assets(self) -> list[str]:
        """Return all asset keys regardless of type, sorted alphabetically."""
        return sorted(self._raw.get("assets", {}).keys())

    # ------------------------------------------------------------------
    # Type-specific asset access
    # ------------------------------------------------------------------

    def table(self, key: str) -> str:
        """Return the resolved path for table *key*.

        Raises :exc:`AssetTypeMismatchError` if the asset exists but is not a table.
        """
        return self._resolve_asset(key, "table")

    def view(self, key: str) -> str:
        """Return the resolved path for view *key*.

        Raises :exc:`AssetTypeMismatchError` if the asset exists but is not a view.
        """
        return self._resolve_asset(key, "view")

    def function(self, key: str) -> str:
        """Return the resolved path for function *key*.

        Raises :exc:`AssetTypeMismatchError` if the asset exists but is not a function.
        """
        return self._resolve_asset(key, "function")

    def volume(self, key: str) -> str:
        """Return the resolved path for volume *key*.

        Raises :exc:`AssetTypeMismatchError` if the asset exists but is not a volume.
        """
        return self._resolve_asset(key, "volume")

    def folder(self, key: str) -> str:
        """Return the resolved path for folder *key*.

        Raises :exc:`AssetTypeMismatchError` if the asset exists but is not a folder.
        """
        return self._resolve_asset(key, "folder")

    def list_tables(self) -> list[str]:
        """Return all table asset keys, sorted alphabetically."""
        return self._list_by_type("table")

    def list_views(self) -> list[str]:
        """Return all view asset keys, sorted alphabetically."""
        return self._list_by_type("view")

    def list_functions(self) -> list[str]:
        """Return all function asset keys, sorted alphabetically."""
        return self._list_by_type("function")

    def list_volumes(self) -> list[str]:
        """Return all volume asset keys, sorted alphabetically."""
        return self._list_by_type("volume")

    def list_folders(self) -> list[str]:
        """Return all folder asset keys, sorted alphabetically."""
        return self._list_by_type("folder")

    # ------------------------------------------------------------------
    # Setting access
    # ------------------------------------------------------------------

    def setting(self, key: str) -> Any:
        """
        Return the value for setting *key*.

        Parameters
        ----------
        key:
            Setting name as defined in the YAML
            (e.g. ``"min_parse_character_length"``).

        Raises
        ------
        SettingNotFoundError
            When *key* is not defined in the YAML.
        """
        settings: dict[str, Any] = self._raw.get("settings", {})
        if key not in settings:
            raise SettingNotFoundError(
                f"Setting {key!r} not found. Available settings: {sorted(settings)}"
            )
        return settings[key]["value"]

    def setting_metadata(self, key: str) -> dict[str, Any]:
        """Return the full setting entry (value + description + any other fields)."""
        settings: dict[str, Any] = self._raw.get("settings", {})
        if key not in settings:
            raise SettingNotFoundError(
                f"Setting {key!r} not found. Available settings: {sorted(settings)}"
            )
        return dict(settings[key])

    def list_settings(self) -> list[str]:
        """Return all defined setting keys, sorted alphabetically."""
        return sorted(self._raw.get("settings", {}).keys())

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def get_volume_name_of_folder(self, folder:str) -> str:
        catalog_index = self.folder(folder).split("/").index(self.catalog)
        schema_index = self.folder(folder).split("/").index(self.schema)
        assert schema_index == catalog_index + 1, "Schema must be a direct child of catalog"
        return self.folder(folder).split("/")[schema_index + 1]

    def list_all_volume_names(self) -> list[str]:
        """Returns all volume names, considering assets registered as
        volumes and folders too.
        
        Notes
        -----
        It might be, that an asset is registered as a folder, but the volume
        the folder is in is not registered as a volume. In this case, just by
        listing the volumes, you woundn't find the volume. This method will
        return all volumes, including the ones that are not registered as
        volumes, but are roots of registered folders.
        """

        volumes = [self.volume(v).split("/")[-2] for v in self.list_volumes()]
        volumes_of_folders = [self.get_volume_name_of_folder(f) for f in self.list_folders()]
        return list(set(volumes + volumes_of_folders))

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Config(catalog={self.catalog!r}, schema={self.schema!r})"
