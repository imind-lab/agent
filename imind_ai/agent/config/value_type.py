from enum import Enum


class ValueType(str, Enum):
    NONE = "none"
    INT = "int"
    STR = "str"
    BOOL = "bool"
    FLOAT = "float"
    DICT = "dict"
    OBJECT = "object"
    LIST_INT = "list[int]"
    LIST_STR = "list[str]"
    LIST_BOOL = "list[bool]"
    LIST_FLOAT = "list[float]"
    LIST_DICT = "list[dict]"
    LIST_OBJECT = "list[object]"

    @classmethod
    def map(cls) -> dict:
        return {
            cls.NONE: None,
            cls.INT: int,
            cls.STR: str,
            cls.BOOL: bool,
            cls.FLOAT: float,
            cls.DICT: dict,
            cls.OBJECT: object,
            cls.LIST_INT: list[int],
            cls.LIST_STR: list[str],
            cls.LIST_BOOL: list[bool],
            cls.LIST_FLOAT: list[float],
            cls.LIST_DICT: list[dict],
            cls.LIST_OBJECT: list[object],
        }

    def is_list(self) -> bool:
        return self.name.startswith("list")

    def default_value(self):
        if self.is_list():
            return []
        if self == self.NONE:
            return None
        elif self == self.INT:
            return 0
        elif self == self.STR:
            return ""
        elif self == self.BOOL:
            return False
        elif self == self.FLOAT:
            return 0.0
        elif self == self.DICT:
            return {}
        elif self == self.OBJECT:
            return object()
        else:
            return None
