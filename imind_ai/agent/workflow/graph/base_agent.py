from typing import Any, Dict
from imind_ai.agent.base.agent import BaseAgent
from imind_ai.agent.config.base import BaseAgentNodeConfig
from imind_ai.agent.config.schema import Output
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.agent.workflow.graph.state import BaseState
from imind_ai.agent.workflow.pipeline.context import Context
from imind_ai.utils import create_dynamic_model


class BaseAgentNode(Node):

    def __init__(self, config: BaseAgentNodeConfig, ctx: Context):
        super().__init__(config)

        self.ctx = ctx

        output_schema = (
            None
            if config.output_schema is None
            else create_dynamic_model(config.output_schema)
        )

        self.agent = BaseAgent(
            id=config.id,
            name=config.name,
            env=config.env,
            output_schema=output_schema,
            debug=config.debug,
        )

    async def __call__(self, state: BaseState):
        params: Dict[str, Any] = {}
        depends = self.config.get_input_depends()
        for depend in depends:
            param = getattr(state, depend, None)
            if param is not None:
                params[depend] = param

        input = self.config.build_input(**params)
        result = await self.agent.chat(input.dict(), ctx=self.ctx)

        if isinstance(result, dict):
            output = Output(**result)
        else:
            output = Output("_result", result)

        return output
