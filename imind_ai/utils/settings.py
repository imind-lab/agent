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

    DynamicModel: Type[BaseModel] = create_dynamic_model(schema)

    class Settings(BaseSettings, DynamicModel):
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
    schema = child
    for key, value in parent.items():
        alias = value.get("alias", None)
        if alias is not None:
            for k, v in schema.items():
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
