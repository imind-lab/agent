from typing import Any, Callable, Optional, Sequence, Type, TypedDict, Union

from pydantic import BaseModel

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.graph.graph import CompiledGraph
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel, _ConfigurableModel
from langchain_core.embeddings import Embeddings
from langchain_core.tools import BaseTool
from langgraph.types import Checkpointer
from langgraph.store.base import BaseStore
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from langmem.short_term import SummarizationNode, RunningSummary


class State(MessagesState):
    summarized_messages: RunningSummary | None
    final_response: Union[str, BaseModel]


# class LLMInputState(TypedDict):
#     summarized_messages: list[AnyMessage]
#     context: dict[str, Any]


def create_base_agent(
    llm: Union[BaseChatModel, _ConfigurableModel],
    embed: Optional[Embeddings] = None,
    tools: Optional[Sequence[Union[BaseTool, Callable]]] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    checkpointer: Optional[Checkpointer] = None,
    store: Optional[BaseStore] = None,
    debug: bool = False,
) -> CompiledGraph:
    summarization_llm = llm.bind(max_tokens=16)

    summarization_node = SummarizationNode(
        token_counter=llm.get_num_tokens_from_messages,
        model=summarization_llm,
        max_tokens=32,
        max_tokens_before_summary=32,
        max_summary_tokens=16,
    )

    def call_model(state: State):
        print("call_model summarized_messages", state["summarized_messages"])
        if tools:
            response = llm.bind_tools(tools).invoke(state["summarized_messages"])
        else:
            response = llm.invoke(state["summarized_messages"])
        print("response", response)
        return {"messages": [response]}

    def respond(state: State):
        structure_output_tool_call = state["messages"][-1].tool_calls[0]
        response = output_schema(**structure_output_tool_call["args"])
        tool_message = {
            "type": "tool",
            "content": "Here is your structured response",
            "tool_call_id": structure_output_tool_call["id"],
        }

        return {"final_response": response, "messages": [tool_message]}

    def should_continue(state: State):
        print("show continue", state)
        messages = state["messages"]
        last_message = messages[-1]
        if (
            len(last_message.tool_calls) == 1
            and last_message.tool_calls[0]["name"] == output_schema.__name__
        ):
            return "respond"
        elif not last_message.tool_calls:
            return END
        else:
            return "tools"

    tools = []
    builder = StateGraph(State)
    builder.add_node("summarize_node", summarization_node)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("respond", respond)
    builder.add_edge(START, "summarize_node")
    builder.add_edge("summarize_node", "call_model")
    builder.add_edge("tools", "summarize_node")
    builder.add_edge("respond", END)
    builder.add_conditional_edges("call_model", should_continue)

    graph = builder.compile(checkpointer=checkpointer, store=store, debug=True)

    return graph


config = {"configurable": {"thread_id": "1"}}

llm = init_chat_model("ollama:qwen2.5:14b")

checkpointer = InMemorySaver()

agent = create_base_agent(llm, checkpointer=checkpointer)

resp = agent.invoke({"messages": "hi, i am bob"}, config)
print("\n\n\n")
# print("resp1", resp)
resp = agent.invoke({"messages": "what's the weather in nyc this weekend"}, config)
# print("resp2", resp)
# resp = agent.invoke({"messages": "what's new on broadway?"}, config)
# print("resp3", resp)
