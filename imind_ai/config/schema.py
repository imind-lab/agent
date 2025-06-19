from _collections_abc import dict_items, dict_keys, dict_values

from typing import Any, Dict, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_serializer

from imind_ai.config.value_type import ValueType


class IO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _data: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, **kwargs: Any):
        fields = {}
        private_attrs = {}
        data = {}

        for k, v in kwargs.items():
            if k in self.__class__.model_fields:
                fields[k] = v
            elif k in self.__private_attributes__:
                private_attrs[k] = v
            else:
                data[k] = v

        super().__init__(**fields)

        for private_attr, value in private_attrs.items():
            super().__setattr__(private_attr, value)

        if data:
            self._data.update(data)

    def __getattr__(self, __name: str) -> Any:
        if (
            __name in self.__private_attributes__
            or __name in self.__class__.model_fields
        ):
            return super().__getattr__(__name)
        else:
            try:
                return self._data[__name]
            except KeyError:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{__name}'"
                )

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__private_attributes__ or name in self.__class__.model_fields:
            super().__setattr__(name, value)
        else:
            self._data.__setitem__(name, value)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def keys(self) -> "dict_keys[str, Any]":
        return self._data.keys()

    def values(self) -> "dict_values[str, Any]":
        return self._data.values()

    def items(self) -> "dict_items[str, Any]":
        return self._data.items()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Any:
        return iter(self._data)

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._data

    @model_serializer(mode="wrap")
    def custom_model_dump(self, handler: Any) -> Dict[str, Any]:
        data = handler(self)

        if self._data:
            data["_data"] = self._data
        return data


class Input(IO):
    pass


class Output(IO):
    pass


class Env(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    description: str = Field(default="")
    value_type: ValueType = Field(default="str")
    value: Union[str, int, bool, float, list, dict, object, None] = None
    alias: Optional[str] = None


class AgentInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    required: Optional[bool] = Field(default=None)
    description: str = Field(default="")
    value_type: ValueType = Field(default="str")
    value: Union[str, int, bool, float, list, dict, object, None] = None
    source: Optional[Literal["input", "reference"]] = None
    reference: Optional[str] = None


class AgentOutput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    description: Optional[str] = Field(default="")
    value_type: ValueType = Field(default="str")
    value_schema: Optional[dict[str, "AgentOutput"]] = None
    value: Optional[Union[str, int, bool, float, list, dict, object]] = None
    source: Optional[Literal["input", "reference"]] = None
    reference: Optional[str] = None
