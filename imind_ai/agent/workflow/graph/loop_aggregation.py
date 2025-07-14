from typing import cast

from pydantic import BaseModel
from imind_ai.agent.config.base import LoopAggregationNodeConfig
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.agent.workflow.graph.node_mixin import NodeMixin
from imind_ai.agent.workflow.pipeline.context import Context


class LoopAggregationNode(Node, NodeMixin):

    def __init__(self, config: LoopAggregationNodeConfig, ctx: Context):
        super().__init__(config)

        self.ctx = ctx

    async def __call__(self, state: BaseModel):

        print("LoopAggregationNode state", type(state))

        la_state = getattr(state, f"{self.id}_output") or {}

        counter = la_state.get("counter", 0)
        agg_items = la_state.get("agg_items")
        if agg_items is None:
            agg_items = {}
        else:
            counter += 1

        aggregation = {}
        for key, value in self.config.aggregation.items():
            agg_type = value.agg_type
            reference = self.process_reference(value.reference, state)
            items = agg_items.get(key, [])
            if reference is not None:
                items.append(reference)
                agg_items[key] = items

            if agg_type == "sum":
                ret = sum(items)
            elif agg_type == "mean":
                ret = sum(items) / len(items)
            elif agg_type == "list":
                ret = items
            aggregation[key] = ret

        return {
            f"{self.id}_output": {
                "counter": counter,
                "agg_items": agg_items,
                "aggregation": aggregation,
            }
        }
