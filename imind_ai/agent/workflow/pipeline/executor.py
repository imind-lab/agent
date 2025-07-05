from typing import Any, Dict
from uuid import uuid4
from imind_ai.agent.workflow.pipeline.context import Context, Phase
from imind_ai.agent.workflow.graph.state import new_state_cls
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from imind_ai.agent.config.schema import Input, Output


class Executor:
    @classmethod
    async def execute(cls, context: Context, input: Input):
        context.phase = Phase.EXECUTING

        cls.build_graph(context)

        context.session_id = context.session_id or str(uuid4())

        config = {
            "configurable": {
                "thread_id": context.session_id,
                "checkpoint_ns": context.config.agent.id,
            }
        }

        inputs = {
            "workflow_input": input.dict(),
        }

        state = await context.graph.ainvoke(inputs, config)
        print(f"{state=}")

        params: Dict[str, Any] = {}
        agent = context.config.agent
        depends = agent.get_output_depends()
        for depend in depends:
            param = state.get(depend)
            if param is not None:
                params[depend] = param

        output = agent.build_output(**params)

        context.phase = Phase.EXECUTED

        return output

    @classmethod
    def build_graph(cls, context: Context):
        State = new_state_cls(context.nodes)
        print("State=", State.model_fields)

        builder = StateGraph(State)

        for node in context.nodes:
            builder.add_node(node.name, node)

        for edge in context.edges:
            builder.add_edge(edge[0], edge[1])

        for edge in context.conditional_edges:
            builder.add_conditional_edges(**edge)

        memory = MemorySaver()
        context.graph = builder.compile(checkpointer=memory)
