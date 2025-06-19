from typing import Any, Dict, List, Set, Union

from imind_ai.config.schema import AgentInput, AgentOutput


def process_depends(config: Dict) -> List[str]:
    """处理输出依赖"""
    params: Set[str] = set()
    for key, val in config.items():
        if isinstance(val, (AgentInput, AgentOutput)):
            if val.value_type == "Dict" and isinstance(val.value_schema, dict):
                params = params.union(set(process_depends(val.value_schema)))  # type: ignore
            if val.source == "reference" and val.reference is not None:
                infos = val.reference.split(".")
                params.add(infos[0])
    return list(params)


def process_params(config: Dict, **kwargs) -> Dict:
    """处理参数
    1、如果存在引用，使用引用对象的值
    2、如果不存在对象但存在值，直接使用值
    3、如果几步存在引用，也不存在值，使用类型默认值
    """
    params = {}
    for key, val in config.items():
        if isinstance(val, (AgentInput, AgentOutput)):
            if isinstance(val, AgentOutput):
                if val.value_type == "Dict" and isinstance(
                    val.value_schema, (AgentOutput, dict)
                ):
                    params[key] = process_params(val.value_schema, **kwargs)  # type: ignore
                    continue

            if (
                hasattr(val, "source") and val.source == "reference"
            ) and val.reference is not None:
                params[key] = process_reference(val.reference, **kwargs)
                continue

            case_value(key, val, params)
        else:
            params[key] = val
    return params


def process_reference(ref: str, **kwargs) -> Any:
    """取出引用对象的值
    引用对象不存在时抛出异常
    """
    infos = ref.split(".")
    length = len(infos)
    if length < 2 or infos[0] not in kwargs:
        raise ValueError(f"引用的值不正确，请核实{ref}, {str(kwargs)}")

    obj = kwargs[infos[0]]
    for index, info in enumerate(infos):
        if index == 0:
            continue
        elif index == length - 1:
            if hasattr(obj, info):
                return getattr(obj, info)
            elif isinstance(obj, dict) and info in obj:
                return obj[info]
            else:
                raise ValueError(f"引用的值不正确，请核实{ref}")
        else:
            if hasattr(obj, info):
                obj = getattr(obj, info)
            elif info in obj:
                obj = obj[info]
            else:
                raise ValueError(f"引用的值不正确，请核实{ref}")


def case_value(
    key: str,
    value: Union[AgentInput, AgentOutput],
    params: Dict,
) -> None:
    if value.value is None:
        params[key] = value.value_type.default_value()
        return

    if value.value_type == "int":
        if isinstance(value.value, int):
            params[key] = value.value  # type: ignore
        else:
            params[key] = int(value.value)  # type: ignore
    elif value.value_type == "float":
        if isinstance(value.value, float):
            params[key] = value.value  # type: ignore
        else:
            params[key] = float(value.value)  # type: ignore
    elif value.value_type == "bool":
        if isinstance(value.value, bool):
            params[key] = value.value  # type: ignore
        else:
            params[key] = bool(value.value)  # type: ignore
    elif value.value_type == "str":
        if isinstance(value.value, str):
            params[key] = value.value  # type: ignore
        else:
            params[key] = str(value.value)  # type: ignore
    elif value.value_type.startswith("List"):
        if isinstance(value.value, list):
            params[key] = value.value  # type: ignore
        else:
            params[key] = list(value.value)  # type: ignore
    elif value.value_type == "Dict":
        if isinstance(value.value, dict):
            params[key] = value.value  # type: ignore
        else:
            params[key] = dict(value.value)  # type: ignore
    else:
        params[key] = value.value
