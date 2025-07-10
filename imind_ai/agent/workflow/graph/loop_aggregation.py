from imind_ai.agent.config.base import LoopAggregationNodeConfig
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.agent.workflow.graph.state import BaseState
from imind_ai.agent.workflow.pipeline.context import Context


class LoopAggregationNode(Node):

    def __init__(self, config: LoopAggregationNodeConfig, ctx: Context):
        super().__init__(config)

        self.ctx = ctx

    async def __call__(self, state: BaseState):
        if not hasattr(self, "agent"):
            await self.build_agent()

        counter = getattr(state, f"{self.id}_counter")
        agg_items = getattr(state, f"{self.id}_agg_items")
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
                items.append(value)
                agg_items[key] = items

            if agg_type == "sum":
                ret = sum(items)
            elif agg_type == "mean":
                ret = sum(items) / len(items)
            elif agg_type == "list":
                ret = items
            aggregation[key] = ret

        return {
            f"{self.id}_counter": counter,
            f"{self.id}_agg_items": agg_items,
            f"{self.id}_aggregation": aggregation,
        }
