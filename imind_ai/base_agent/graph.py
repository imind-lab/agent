import asyncio
from collections import deque
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Sequence,
    Type,
    TypedDict,
    Union,
    Tuple,
)

from pydantic import BaseModel, Field

from langchain_core.messages import AnyMessage, HumanMessage
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
from langchain_core.tools import tool


class WeatherResponse(BaseModel):
    """Respond to the user with this"""

    temperature: float = Field(description="The temperature in fahrenheit")
    wind_directon: str = Field(
        description="The direction of the wind in abbreviated form"
    )
    wind_speed: float = Field(description="The speed of the wind in km/h")


@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It is cloudy in NYC, with 5 mph winds in the North-East direction and a temperature of 70 degrees"
    elif city == "sf":
        return "It is 75 degrees and sunny in SF, with 3 mph winds in the South-East direction"
    else:
        raise AssertionError("Unknown city")


class State(MessagesState):
    user_input: Union[str, Tuple[str, dict]]
    summarized_messages: list[AnyMessage]
    llm_output: Union[str, BaseModel]


# class LLMInputState(TypedDict):
#     summarized_messages: list[AnyMessage]
#     context: dict[str, Any]


def create_base_agent(
    llm: Union[BaseChatModel, _ConfigurableModel],
    tools: Optional[Sequence[Union[BaseTool, Callable]]] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    system_prompt: Optional[str] = None,
    checkpointer: Optional[Checkpointer] = None,
    store: Optional[BaseStore] = None,
    debug: bool = False,
) -> CompiledGraph:
    tools = tools or []
    summarization_model = llm.bind(max_tokens=128)

    summarizer = SummarizationNode(
        token_counter=llm.get_num_tokens_from_messages,
        model=summarization_model,
        max_tokens=256,
        max_tokens_before_summary=256,
        max_summary_tokens=128,
    )

    async def pre_processor(state: State):
        user_input = state["user_input"]
        if isinstance(user_input, tuple):
            media = user_input[1]
            if "images" in media:
                images = media["images"]
                if isinstance(images, (list, str)):
                    content = [{"type": "text", "text": user_input[0]}]
                    if isinstance(images, list):
                        for image in images:
                            content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image},
                                }
                            )
                    else:
                        content.append(
                            {
                                "type": "image_url",
                                "image_url": {"url": images},
                            }
                        )
                else:
                    content = user_input[0]
            else:
                content = user_input[0]
        else:
            content = user_input

        return {"messages": HumanMessage(content=content)}

    async def llm_caller(state: State):
        summarized_messages = state["summarized_messages"]
        last_message = summarized_messages[-1]
        new_messages = deque()
        for message in reversed(state["messages"]):
            if message.id == last_message.id:
                break
            else:
                new_messages.appendleft(message)

        summarized_messages.extend(list(new_messages))

        if tools:
            response = llm.bind_tools(tools, tool_choice="any").invoke(
                summarized_messages
            )
        else:
            response = llm.invoke(summarized_messages)

        return {"messages": [response], "summarized_messages": summarized_messages}

    async def post_processor(state: State):
        if output_schema:
            response = llm.with_structured_output(output_schema).invoke(
                [HumanMessage(content=state["messages"][-1].content)]
            )
        else:
            response = state["messages"][-1]
        # We return the final answer
        return {"llm_output": response}

    def should_continue(state: State):
        messages = state["messages"]
        last_message = messages[-1]
        print("last_message", last_message)

        if not last_message.tool_calls:
            return "post_processor"
        else:
            return "tools"

    builder = StateGraph(State)
    builder.add_node("pre_processor", pre_processor)
    builder.add_node("summarizer", summarizer)
    builder.add_node("llm_caller", llm_caller)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("post_processor", post_processor)
    builder.add_edge(START, "pre_processor")
    builder.add_edge("pre_processor", "summarizer")
    builder.add_edge("summarizer", "llm_caller")
    builder.add_edge("tools", "llm_caller")
    builder.add_edge("post_processor", END)
    builder.add_conditional_edges("llm_caller", should_continue)

    graph = builder.compile(checkpointer=checkpointer, store=store, debug=debug)

    return graph


tools = [get_weather]

config = {"configurable": {"thread_id": "1"}}

llm = init_chat_model("ollama:qwen2.5:14b")

checkpointer = InMemorySaver()

agent = create_base_agent(
    llm, tools=tools, checkpointer=checkpointer, output_schema=WeatherResponse
)


async def main():
    # resp = agent.invoke({"messages": "hi, i am bob"}, config)
    # # print("\n\n\n")
    # # print("resp1", resp)
    # resp = agent.invoke({"messages": "what's the weather in nyc this weekend"}, config)
    # # print("\n\n\n")
    # # print("resp2", resp)
    # resp = agent.invoke({"messages": "what's new on broadway?"}, config)
    # print("\n\n\n")
    # print("resp3", resp)

    answer = await agent.ainvoke(
        input={"user_input": "what's the weather in SF?"},
        config=config,
        # input={"messages": [("human", "你是谁？")]},
        # config=config,
    )

    # print(answer)
    for message in answer["messages"]:
        message.pretty_print()
    print("\n\n\n")
    for message in answer["summarized_messages"]:
        message.pretty_print()
    print("\n\n\n")
    print(answer["llm_output"])


if __name__ == "__main__":
    asyncio.run(main())
