from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import uuid4

from imind_ai.agent.config.schema import Input, Output

from .helper import Env, AgentInput, AgentOutput, process_depends, process_params


class BaseConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default="")
    description: Optional[str] = None
    env: Optional[Dict[str, Env]] = None
    input: Dict[str, AgentInput] = {}
    output: Dict[str, AgentOutput] = {}

    def get_env_schema(self) -> Dict[str, Any]:
        schema: Dict[str, Any] = {}

        if self.env is not None:
            for key, value in self.env.items():
                if isinstance(value, Env):
                    schema[key] = value.model_dump()

        return schema

    def get_input_schema(self) -> Dict[str, Any]:
        schema: Dict[str, Any] = {}
        for key, value in self.input.items():
            if isinstance(value, AgentInput):
                schema[key] = value.model_dump()

        return schema

    def get_output_schema(self) -> Dict[str, Dict[str, Any]]:
        return self._output_schema(self.output)

    def _output_schema(self, entry: Dict) -> Dict[str, Any]:
        schema: Dict[str, Any] = {}
        for key, value in entry.items():
            if isinstance(value, dict):
                value = AgentOutput(**value)

            if isinstance(value, AgentOutput):
                item = value.model_dump()
                if value.value_type == "Dict" and isinstance(value.value_schema, dict):
                    item["value_schema"] = self._output_schema(value.value_schema)  # type: ignore

                schema[key] = item  # type: ignore
        return schema

    def get_input_depends(self) -> List[str]:
        return process_depends(self.input)

    def get_output_depends(self) -> List[str]:
        return process_depends(self.output)

    def build_input(self, **kwargs) -> Input:
        params = process_params(self.input, **kwargs)
        return Input(**params)

    def build_output(self, **kwargs) -> Output:
        params = process_params(self.output, **kwargs)
        return Output(**params)


class AgentConfig(BaseConfig):
    type: str = ""
    structure: bool = Field(default=False)


class Node(BaseModel):
    pass


class Config(BaseConfig):
    agent: AgentConfig
    nodes: List[Node]
