from typing import Any, AsyncGenerator, Dict, Optional, Sequence, Type, Tuple
from uuid import uuid4

from openai import base_url
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from langchain.chat_models import init_chat_model
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from imind_ai.agent.base.config import Config
from imind_ai.agent.base.graph import create_base_agent
from imind_ai.agent.base.prompt import DEFAULT_PROMPT_TEMPLATE
from imind_ai.agent.config.schema import Input
from imind_ai.utils.context import BaseContext
from imind_ai.utils.settings import build_settings_from_schema, update_schema


class BaseAgent:
    cfg = Config.default()
    prompt_template: str = DEFAULT_PROMPT_TEMPLATE

    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        env: Dict[str, Any] | None = None,
        output_schema: Type[BaseModel] | None = None,
        system_prompt: str | None = None,
        tools: Optional[Sequence[BaseTool]] = None,
        debug: bool = False,
        **kwargs,
    ):
        self.id = id or str(uuid4())
        self.name = name or ""

        if env is None:
            env = {}
        schema = self.get_env_schema()
        schema = update_schema(schema, env)

        setting_cls = build_settings_from_schema(schema)

        env_values = kwargs.get("env_values", None)

        if env_values is not None and isinstance(env_values, dict):
            settings = setting_cls(**env_values)
        else:
            settings = setting_cls()

        self.settings = settings

        if settings.multi_turn:
            if settings.postgres_dsn:
                checkpointer = None
                self.checkpointer_initialized = False
            else:
                checkpointer = InMemorySaver()
                self.checkpointer_initialized = True
        else:
            checkpointer = None
            self.checkpointer_initialized = True
        llm = init_chat_model(settings.model, base_url=settings.base_url)
        self.agent = create_base_agent(
            llm,
            settings=settings,
            tools=tools,
            output_schema=output_schema,
            system_prompt=system_prompt,
            checkpointer=checkpointer,
            debug=debug,
        )

        self.output_schema = output_schema
        self.pg_pool = None

    @classmethod
    def get_env_schema(cls) -> Dict[str, Any]:
        return cls.cfg.env

    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return cls.cfg.input

    @classmethod
    def get_output_schema(cls) -> Dict[str, Dict[str, Any]]:
        return cls.cfg.output

    @classmethod
    def get_prompt_template(cls) -> str:
        return cls.prompt_template

    def update_prompt_template(self, template: str):
        self.prompt_template = template

    async def achat(self, user_input: Input, ctx: BaseContext = None) -> Dict | str:
        inputs, config = await self.pre_process(user_input, ctx)

        response = await self.agent.ainvoke(inputs, config=config)
        return response.get("llm_output")

    async def achat_stream(
        self, user_input: Input, ctx: BaseContext = None
    ) -> AsyncGenerator[str, None]:
        inputs, config = await self.pre_process(user_input, ctx)

        node_name = "llm_caller" if self.output_schema is None else "post_processor"

        async for message_chunk, metadata in self.agent.astream(
            inputs, config=config, stream_mode="messages"
        ):
            if (
                metadata["langgraph_node"] == node_name
                and isinstance(message_chunk, AIMessageChunk)
                and len(message_chunk.tool_calls) == 0
                and message_chunk.content
            ):
                yield message_chunk.content

    async def pre_process(
        self, user_input: Input, ctx: BaseContext = None
    ) -> Tuple[Dict, Dict]:
        if self.agent is None:
            raise RuntimeError("The agent was not initialized correctly.")

        if not self.checkpointer_initialized:
            connection_kwargs = {
                "autocommit": True,
                "prepare_threshold": 0,
            }

            dsn = f"postgresql://{self.settings.postgres_dsn}"

            self.pg_pool = await AsyncConnectionPool(
                conninfo=dsn,
                max_size=20,
                kwargs=connection_kwargs,
            ).__aenter__()

            checkpointer = AsyncPostgresSaver(self.pg_pool)
            await checkpointer.setup()

            self.agent.checkpointer = checkpointer

            self.checkpointer_initialized = True

        ctx = ctx or BaseContext()
        ctx.session_id = ctx.session_id or str(uuid4())

        thread_id = f"{ctx.session_id}-{self.id}"
        configurable = {"thread_id": thread_id}
        if ctx.user_id:
            configurable["user_id"] = ctx.user_id

        config = {"configurable": configurable}

        self.agent.store = ctx.store

        inputs = {"user_input": self.prompt_template.format(**user_input.dict())}
        return inputs, config

    async def clone(self):
        try:
            if self.pg_pool:
                await self.pg_pool.__aexit__(None, None, None)
        except Exception as e:
            print(f"关闭连接时发生错误: {str(e)}")
