from pathlib import Path
from turtle import setup
from typing import Dict


from imind_ai.agent.config.base import Config
from imind_ai.agent.workflow.pipeline.context import Context, Phase
from imind_ai.utils.settings import build_settings_from_schema, update_schema


class Parser:

    @classmethod
    def parse(
        cls,
        context: Context,
        *,
        values: Dict | Path | None = None,
        env: Dict | None = None,
        **kwargs,
    ):
        context.phase = Phase.PARSING

        if isinstance(values, dict):
            config = Config.from_dict(values)
        else:
            config = Config.from_file(values)

        schema = config.agent.env
        schema = update_schema(schema, env)

        setting_cls = build_settings_from_schema(schema)

        settings = setting_cls()

        context.config = config
        context.settings = settings
        context.kwargs = kwargs
