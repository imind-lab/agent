from typing import Any
from imind_ai.agent.config.base import BaseNodeConfig
from imind_ai.agent.workflow.graph.state import BaseState


class Node:

    def __init__(self, config: BaseNodeConfig):
        self.id = config.id
        self.name = config.name
        self.config = config

    def process_reference(self, ref: str, state: BaseState) -> Any:
        """取出引用对象的值
        引用对象不存在时抛出异常
        """
        infos = ref.split(".")
        entity = infos.pop(0)
        print(entity, state)
        if not hasattr(state, entity):
            raise ValueError(f"引用的值不正确，请核实{ref}, {str(state)}")

        item = getattr(state, entity)

        while len(infos) > 0:
            key = infos.pop(0)
            if isinstance(item, dict):
                item = item.get(key)
                if item is None:
                    raise ValueError(f"引用的值不正确，请核实{ref}")
            else:
                if hasattr(item, key):
                    item = getattr(item, key)
                else:
                    raise ValueError(f"引用的值不正确，请核实{ref}")
        return item
