from enum import Enum
from typing import Any, Optional

from langmem import ReflectionExecutor, create_memory_store_manager
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig
from langgraph.config import get_config, get_store

from imind_ai.utils.markdown import json_to_markdown


class MemoryType(Enum):
    TRIPLE = 1
    PROFILE = 2
    EPISODE = 4


class Triple(BaseModel):
    """Store all new facts, preferences, and relationships as triples."""

    subject: str
    predicate: str
    object: str
    context: str | None = None


# Define profile structure
class UserProfile(BaseModel):
    """Represents the full representation of a user."""

    name: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class Episode(BaseModel):
    """Write the episode from the perspective of the agent within it. Use the benefit of hindsight to record the memory, saving the agent's key internal thought process so it can learn over time."""

    observation: str = Field(..., description="The context and setup - what happened")
    thoughts: str = Field(
        ...,
        description="Internal reasoning process and observations of the agent in the episode that let it arrive"
        ' at the correct action and result. "I ..."',
    )
    action: str = Field(
        ...,
        description="What was done, how, and in what format. (Include whatever is salient to the success of the action). I ..",
    )
    result: str = Field(
        ...,
        description="Outcome and retrospective. What did you do well? What could you do better next time? I ...",
    )


class MemoryManager:
    def __init__(self):
        self.triples_manager = create_memory_store_manager(
            "ollama:qwen2.5:14b",
            namespace=("memories", "{user_id}", "triples"),
            schemas=[Triple],
            instructions="Extract all user information and events as triples.",
            enable_inserts=True,
            enable_deletes=True,
        )

        self.profile_manager = create_memory_store_manager(
            "ollama:qwen2.5:14b",
            namespace=("memories", "{user_id}", "profile"),
            schemas=[UserProfile],
            instructions="Extract user profile information",
            enable_inserts=False,
        )

        self.episode_manager = create_memory_store_manager(
            "ollama:qwen2.5:14b",
            namespace=("memories", "{user_id}", "episodes"),
            schemas=[Episode],
            instructions="Extract exceptional examples of noteworthy problem-solving scenarios, including what made them effective.",
            enable_inserts=True,
        )


class MemoryExecutor:
    def __init__(self):
        memory_manager = MemoryManager()

        self.triples_executor = ReflectionExecutor(memory_manager.triples_manager)
        self.profile_executor = ReflectionExecutor(memory_manager.profile_manager)
        self.episode_executor = ReflectionExecutor(memory_manager.episode_manager)

    def submit(
        self,
        payload: dict[str, Any],
        *,
        config: RunnableConfig | None = None,
        after_seconds: int = 0,
    ):
        self.triples_executor.submit(
            payload, config=config, after_seconds=after_seconds
        )
        self.profile_executor.submit(
            payload, config=config, after_seconds=after_seconds
        )
        self.episode_executor.submit(
            payload, config=config, after_seconds=after_seconds
        )


def system_prompt_with_memory(prompt: str, memory_flag: int | None = None) -> str:
    configurable = get_config()["configurable"]
    store = get_store()
    system_prompt = "You are a helpful assistant."

    if memory_flag is not None and memory_flag > 0 and memory_flag < 8:
        if memory_flag & MemoryType.TRIPLE.value:
            results = store.search(("memories", configurable["user_id"], "triples"))
            if results:
                system_prompt = f"""{system_prompt}
\n### TRIPLE MEMORY:
"""
                for result in results:
                    item = result.value
                    content = json_to_markdown(item["content"], 1)

                    system_prompt = f"""{system_prompt}
{content}
"""
                    print("result1", type(result), result)
        if memory_flag & MemoryType.PROFILE.value:
            print("PROFILE")
            results = store.search(("memories", configurable["user_id"], "profile"))
            if results:
                item = results[0].value
                content = json_to_markdown(item["content"], 1)

                system_prompt = f"""{system_prompt}
\n### User Profile:
{content}
"""
        if memory_flag & MemoryType.EPISODE.value:
            results = store.search(("memories", configurable["user_id"], "episodes"))
            if results:
                system_prompt = f"""{system_prompt}
\n### EPISODIC MEMORY:
"""
                for result in results:
                    item = result.value
                    content = json_to_markdown(item["content"], 1)

                    system_prompt = f"""{system_prompt}
{content}
"""
