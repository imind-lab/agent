from typing import Any, Dict

from pydantic import BaseModel
from imind_ai.agent.base.agent import BaseAgent
from imind_ai.agent.config.base import BaseAgentNodeConfig
from imind_ai.agent.config.schema import Output
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.agent.workflow.pipeline.context import Context
from imind_ai.utils import create_dynamic_model

from langchain_mcp_adapters.client import MultiServerMCPClient


class BaseAgentNode(Node):

    def __init__(self, config: BaseAgentNodeConfig, ctx: Context):
        super().__init__(config)

        self.ctx = ctx

        if config.mcp is None:
            output_schema = (
                create_dynamic_model(config.output)
                if isinstance(config.output, dict)
                else None
            )

            self.agent = BaseAgent(
                id=config.id,
                name=config.name,
                env=config.env,
                output_schema=output_schema,
                debug=config.debug,
            )

    async def __call__(self, state: BaseModel):
        print("BaseAgentNode state", type(state), self.ctx.state)

        if not hasattr(self, "agent"):
            await self.build_agent()

        params: Dict[str, Any] = {}
        depends = self.config.get_input_depends()

        for depend in depends:
            param = getattr(state, depend, None)
            if param is not None:
                params[depend] = param

        input = self.config.build_input(**params)
        print("input", type(input), input.dict())

        result = await self.agent.achat(input, ctx=self.ctx)
        print(f"{result=}")
        print(type(result))

        if isinstance(result, dict):
            output = Output(**result)
        elif isinstance(result, BaseModel):
            data = result.model_dump()
            print(f"{data=}")
            output = Output(**data)
        else:
            output = Output(_result=result.content)

        print("output", output.dict())

        return {f"{self.id}_input": input.dict(), f"{self.id}_output": output.dict()}

    async def build_agent(self):
        tools = None
        if self.config.mcp is not None:
            print("mcp", self.config.mcp)
            mcp_client = MultiServerMCPClient(
                self.config.model_dump(exclude_none=True)["mcp"]
            )
            tools = await mcp_client.get_tools()

        output_schema = (
            create_dynamic_model(self.config.output)
            if isinstance(self.config.output, dict)
            else None
        )

        self.agent = BaseAgent(
            id=self.config.id,
            name=self.config.name,
            env=self.config.env,
            output_schema=output_schema,
            tools=tools,
            debug=self.config.debug,
        )
