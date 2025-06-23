from typing import Any, Optional, TypedDict, Union

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.graph.graph import CompiledGraph
from langchain.chat_models.base import BaseChatModel, _ConfigurableModel
from langchain_core.embeddings import Embeddings
from langgraph.types import Checkpointer
from langgraph.store.base import BaseStore
from langgraph.prebuilt import ToolNode
from langmem.short_term import SummarizationNode, RunningSummary


class State(MessagesState):
    context: dict[str, Any]


class LLMInputState(TypedDict):
    summarized_messages: list[AnyMessage]
    context: dict[str, Any]


def create_base_agent(
    llm: Union[BaseChatModel, _ConfigurableModel],
    embed: Optional[Embeddings] = None,
    checkpointer: Optional[Checkpointer] = None,
    store: Optional[BaseStore] = None,
    debug: bool = False,
) -> CompiledGraph:
    summarization_llm = llm.bind(max_tokens=128)

    summarization_node = SummarizationNode(
        token_counter=llm.get_num_tokens_from_messages,
        model=summarization_llm,
        max_tokens=256,
        max_tokens_before_summary=256,
        max_summary_tokens=128,
    )
    pass
