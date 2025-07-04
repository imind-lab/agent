from pathlib import Path
from typing import Any, Dict, Type, Union
from pydantic import BaseModel, Field, create_model
import yaml


def json_to_markdown(data, indent_level=0):
    indent = "    " * indent_level  # 当前缩进

    # 处理字典类型
    if isinstance(data, dict):
        if not data:
            return f"{indent}- {{}}"

        lines = []
        for key, value in data.items():
            # 键名加粗显示
            header = f"{indent}- **{key}**:"

            # 处理嵌套结构
            if isinstance(value, (dict, list)):
                lines.append(header)
                lines.append(json_to_markdown(value, indent_level + 1))
            # 处理空值
            elif value is None:
                lines.append(f"{header} `null`")
            # 处理布尔值
            elif isinstance(value, bool):
                lines.append(f"{header} {'`true`' if value else '`false`'}")
            # 处理基本类型
            else:
                lines.append(f"{header} {value}")

        return "\n".join(lines)


def read_yaml(file_path: Path, encoding: str = "utf-8") -> Dict:
    """Read yaml file and return a dict"""
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding=encoding) as file:
        return yaml.safe_load(file)


type_mapping = {
    "none": None,
    "any": Any,
    "int": int,
    "str": str,
    "float": float,
    "list": list,
    "dict": dict,
    "bool": bool,
    "list[str]": list[str],
    "list[int]": list[int],
    "list[bool]": list[bool],
    "list[float]": list[float],
    "list[dict]": list[dict],
}


def create_dynamic_model(schema: Dict[str, Union[BaseModel, Dict]]) -> Type[BaseModel]:
    schema_dict = {}
    for key, value in schema.items():
        if isinstance(value, BaseModel):
            alias = value.alias
            description = value.description
            if value.default is not None:
                schema_dict[key] = (
                    type_mapping[value.type],
                    Field(description=description, default=value.default, alias=alias),
                )
            else:
                schema_dict[key] = (
                    type_mapping[value.type] | None,
                    Field(description=description, default=None, alias=alias),
                )
        else:
            alias = value.get("alias", None)
            description = value.get("description", None)
            if "value" in value and value["value"] is not None:
                schema_dict[key] = (
                    type_mapping[value["type"]],
                    Field(description=description, default=value["value"], alias=alias),
                )
            else:
                schema_dict[key] = (
                    type_mapping[value["type"]] | None,
                    Field(description=description, default=None, alias=alias),
                )

    DynamicModel: Type[BaseModel] = create_model("DynamicModel", **schema_dict)

    return DynamicModel
