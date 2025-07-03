from imind_ai.agent.config.base import ConditionNodeConfig
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.agent.workflow.graph.state import BaseState
from imind_ai.agent.workflow.pipeline.context import Context


class ConditionNode(Node):
    def __init__(self, config: ConditionNodeConfig, ctx: Context):
        super().__init__(config)
        self.ctx = ctx
