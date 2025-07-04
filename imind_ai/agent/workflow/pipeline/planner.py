from imind_ai.agent.workflow.pipeline.context import Context, Phase
from imind_ai.agent.workflow.graph.condition import ConditionNode
from imind_ai.agent.workflow.graph.base_agent import BaseAgentNode

from langgraph.graph import START


class Planner:

    @classmethod
    def plan(cls, context: Context):
        context.phase = Phase.PLANNING

        config = context.config

        for idx, item in enumerate(config.nodes):
            if idx == 0:
                context.edges.append((START, item.name))

            if item.type == "sdk":
                node = BaseAgentNode(item, context)
                context.nodes.append(node)
                if item.next_type is None or item.next_type != "condition":
                    next = item.get_next()
                    if isinstance(next, list):
                        for n in next:
                            context.edges.append((item.name, n))
                    elif isinstance(next, str):
                        context.edges.append((item.name, next))

            elif item.type == "condition":
                node = ConditionNode(item, context)
                print(node)
                context.conditional_edges.append({"source": node.prev, "path": node})
