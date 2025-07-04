from typing import Any
from imind_ai.agent.config.base import ConditionNodeConfig
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.agent.workflow.graph.state import BaseState
from imind_ai.agent.workflow.pipeline.context import Context


class ConditionNode(Node):
    def __init__(self, config: ConditionNodeConfig, ctx: Context):
        super().__init__(config)
        self.prev = config.prev
        self.ctx = ctx

    def __call__(self, state: BaseState):
        if_express = self.config.if_express

        is_meet = True
        for condition in if_express.condition:
            print(condition)
            operand = self.process_reference(condition.operand, state)
            print(operand)
            right_hand = (
                condition.value
                if condition.source == "input"
                else self.process_reference(condition.reference, state)
            )

            logic = self.exec_judgment(condition.operator, operand, right_hand)
            if if_express.logic_operator == "or" and logic:
                return if_express.next
            if if_express.logic_operator == "and" and not logic:
                is_meet = False
                break

        if is_meet:
            return if_express.next

        elif_express = self.config.elif_express

        for elif_condition in elif_express:
            is_meet = True
            for condition in elif_condition.condition:
                print(condition)
                operand = self.process_reference(condition.operand, state)
                print(operand)
                right_hand = (
                    condition.value
                    if condition.source == "input"
                    else self.process_reference(condition.reference, state)
                )

                logic = self.exec_judgment(condition.operator, operand, right_hand)
                if elif_condition.logic_operator == "or" and logic:
                    return elif_condition.next
                if elif_condition.logic_operator == "and" and not logic:
                    is_meet = False
                    break

            if is_meet:
                return elif_condition.next
        return self.config.else_express

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

    def exec_judgment(self, operator: str, operand: Any, right_hand: Any) -> bool:
        print(operator, operand, right_hand, sep=",")
        if operator == "eq":
            return operand == right_hand
        elif operator == "ne":
            return operand != right_hand
        elif operator == "lt":
            return operand < right_hand
        elif operator == "gt":
            return operand > right_hand
        elif operator == "le":
            return operand <= right_hand
        elif operator == "ge":
            return operand >= right_hand
        elif operator == "ct":
            return operand in right_hand
        elif operator == "nc":
            return not operand in right_hand
        elif operator == "sw":
            return str(operand).startswith(right_hand)
        elif operator == "ew":
            return str(operand).endswith(right_hand)
        elif operator == "em":
            return True if operand else False
        elif operator == "nem":
            return False if operand else True
