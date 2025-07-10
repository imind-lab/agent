from pathlib import Path
from typing import List, Literal, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from uuid import uuid4

from imind_ai.agent.config.schema import Input, Output, Env
from imind_ai.utils import read_yaml

from .helper import AgentInput, AgentOutput, process_depends, process_params


class AgentConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default="")
    description: Optional[str] = None
    env: Optional[Dict[str, Env]] = None
    input: Dict[str, AgentInput] = {}
    output: Union[str, Dict[str, AgentOutput]] = ""

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


class BaseNodeConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default="")
    type: Literal["rag", "sdk", "base_agent", "condition", "loop_aggregation"] = Field(
        default="base_agent"
    )


class NodeConfig(BaseNodeConfig):

    next: Optional[Union[str, List[str]]] = None
    next_type: Optional[Literal["condition"]] = None


class MCP(BaseModel):
    transport: Literal["stdio", "streamable_http"] = "streamable_http"


class MCPStdIO(MCP):
    command: str
    args: List[str]
    env: Optional[Dict[str, Any]] = None
    cwd: Optional[str] = None


class MCPStreamableHttp(MCP):
    url: str
    headers: Optional[Dict[str, Any]] = None


class BaseAgentNodeConfig(NodeConfig, AgentConfig):
    system_prompt: Optional[str] = None
    mcp: Optional[Dict[str, Union[MCPStreamableHttp, MCPStdIO]]] = None
    debug: bool = False


class ConditionItem(BaseModel):
    operator: Literal[
        "eq", "ne", "lt", "gt", "ge", "le", "ct", "nc", "sw", "ew", "em", "nem"
    ]
    operand: str
    op_type: str
    source: Literal["input", "reference"]
    value: Optional[Any] = None
    reference: Optional[str] = None


class Condition(BaseModel):
    logic_operator: Literal["and", "or"]
    condition: List[ConditionItem]
    next: Union[str, List[str]]


class ConditionNodeConfig(BaseNodeConfig):
    prev: str
    if_express: Condition = Field(alias="if")
    elif_express: Optional[List[Condition]] = Field(default=None, alias="elif")
    else_express: Optional[Union[str, List[str]]] = Field(default=None, alias="else")


class Aggregation(BaseModel):
    reference: str
    agg_type: str


class LoopAggregationNodeConfig(BaseNodeConfig):
    aggregation: Dict[str, Aggregation]
    next: Union[str, List[str]]


class Config(BaseModel):
    agent: AgentConfig
    nodes: List[Union[BaseAgentNodeConfig, ConditionNodeConfig]]

    @classmethod
    def from_file(cls, path: Path | None = None) -> "Config":
        path = path or Path("config.yaml")
        cfg = read_yaml(path)
        return Config(**cfg)

    @classmethod
    def from_dict(cls, data: Dict):
        return Config(**data)
