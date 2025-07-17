from typing import Any, Dict, Type

from pydantic import BaseModel, Field, create_model
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

from imind_ai.utils import create_dynamic_model


def build_settings_from_schema(schema: Dict[str, Any]) -> Type[BaseSettings]:
    """Dynamically creates a Settings class from a given schema configuration.

    Args:
        schema: Dictionary defining the configuration structure and validation rules

    Returns:
        Custom Settings class configured to load from multiple sources
    """

    # Create a dynamic Pydantic model based on the provided schema
    DynamicModel: Type[BaseModel] = create_dynamic_model(schema)

    # Create custom Settings class combining BaseSettings and the dynamic model
    class Settings(BaseSettings, DynamicModel):
        """Configuration settings with YAML file support and dynamic field definitions."""

        # Configure settings loading behavior
        model_config = SettingsConfigDict(
            yaml_file="settings.yaml",
            yaml_file_encoding="utf-8",
            extra="allow",
        )

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            """Customize the priority and sources for loading configuration values.

            Determines the order of precedence for configuration sources:
            1. Initialization arguments (highest priority)
            2. Environment variables
            3. YAML configuration file (lowest priority)

            Note: Dotenv and file secret sources are excluded from this configuration.
            """
            return init_settings, env_settings, YamlConfigSettingsSource(settings_cls)

    return Settings


def process_alias_schema(setup: Dict[str, Any]) -> Dict[str, Any]:
    schema: Dict[str, Any] = {}
    for key, value in setup.items():
        if isinstance(value, BaseModel):
            value = value.model_dump()
        alias = value.pop("alias", None)
        if alias and isinstance(alias, str):
            schema[alias] = value

        schema[key] = value
    return schema


def aggregate_schemas(*args) -> Dict[str, Any]:
    schemas = {}
    for schema in args:
        if isinstance(schema, dict):
            schemas.update(process_alias_schema(schema))

    return schemas


def process_re_alias_schema(
    parent: Dict[str, Any], child: Dict[str, Any]
) -> Dict[str, Any]:
    """Processes and merges schema definitions by handling field aliases and default values.

    This function updates a child schema based on a parent schema by:
    1. Propagating alias definitions from parent to child
    2. Synchronizing default values between matching fields
    3. Handling both direct field matches and alias-based matches

    Args:
        parent: Parent schema containing field definitions with potential aliases
        child: Child schema to be updated with parent's aliases and defaults

    Returns:
        Updated child schema with merged alias configurations and default values
    """
    # Start with the child schema as base configuration
    schema = child

    for key, value in parent.items():
        alias = value.get("alias", None)
        if alias is not None:
            for k, v in schema.items():
                # Convert BaseModel fields to dictionaries for uniform processing
                if isinstance(v, BaseModel):
                    v = v.model_dump()
                a = v.get("alias", None)
                if a is None:
                    if k == key:
                        v["alias"] = alias
                        v["value"] = value.default
                else:
                    if key == a:
                        v["alias"] = alias
                        v["value"] = value.default
        else:
            for k, v in schema.items():
                if isinstance(v, BaseModel):
                    v = v.model_dump()
                if key == k:
                    v["value"] = value.default

                else:
                    alias = v.get("alias", None)
                    if alias is not None and alias == key:
                        v["value"] = value.default

    return schema


def update_default(origin: Dict[str, Any], default: Dict[str, Any]) -> Dict[str, Any]:
    if origin is None or default is None:
        return {}

    schema = origin
    for key, value in schema.items():
        if isinstance(value, dict):
            if key in default:
                value["value"] = default[key]
            else:
                alias = value.get("alias", None)
                if alias is not None and alias in default:
                    value["value"] = default[alias]
        elif isinstance(value, BaseModel):
            if key in default.keys():
                value.default = default[key]
            else:
                alias = value.alias
                if alias is not None and alias in default.keys():
                    value.default = default[alias]
    return schema


def update_schema(origin: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    schema = origin
    if isinstance(update, dict):
        for key, value in update.items():
            item = schema.get(key, None)
            if item is None:
                schema[key] = value
            else:
                if isinstance(item, dict):
                    item.update(value)
                elif isinstance(item, BaseModel):
                    item.__dict__.update(value)
    return schema
