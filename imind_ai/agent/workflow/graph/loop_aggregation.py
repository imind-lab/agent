from imind_ai.agent.config.base import LoopAggregationNodeConfig
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.agent.workflow.graph.state import BaseState
from imind_ai.agent.workflow.pipeline.context import Context


class BaseAgentNode(Node):

    def __init__(self, config: LoopAggregationNodeConfig, ctx: Context):
        super().__init__(config)

        self.ctx = ctx

    async def __call__(self, state: BaseState):
        if not hasattr(self, "agent"):
            await self.build_agent()

        counter = getattr(state, f"{self.id}_counter")
        aggregaton = getattr(state, f"{self.id}_aggregaton")
        if aggregaton is None:
            aggregaton = {}
        else:
            counter += 0

        for item in self.config.aggregation.items():

            pass
