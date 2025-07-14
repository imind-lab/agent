from enum import Enum
from typing import Any, Callable, List, Tuple, Dict

from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from imind_ai.agent.config.base import Config
from imind_ai.agent.workflow.graph.node import Node
from imind_ai.utils.context import BaseContext


class Phase(Enum):
    INITIAL = 0
    PARSING = 1
    PARSED = 2
    PLANNING = 3
    PLANNED = 4
    EXECUTING = 5
    EXECUTED = 6
    FINISHED = 7


class Context(BaseContext):
    _phase: Phase = Phase.INITIAL
    _config: Config | None = None
    _nodes: List[Node] = []
    _state: BaseModel | None = None
    _edges: List[Tuple[str, str]] = []
    _conditional_edges: List[Dict] = []
    _graph: CompiledStateGraph | None = None
    _settings: BaseSettings | None = None
    _kwargs: Dict[str, Any] | None = None

    @property
    def phase(self) -> Phase:
        return self._phase

    @phase.setter
    def phase(self, phase: Phase) -> None:
        self.set("_phase", phase)

    @property
    def config(self) -> Config | None:
        return self._config

    @config.setter
    def config(self, config: Config) -> None:
        self.set("_config", config)

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List[Node]) -> None:
        self.set("_nodes", nodes)

    @property
    def state(self) -> BaseModel | None:
        return self._state

    @state.setter
    def state(self, state: BaseModel) -> None:
        self.set("_state", state)

    @property
    def edges(self) -> List[Tuple[str, str]]:
        return self._edges

    @edges.setter
    def edges(self, edges: List[Tuple[str, str]]) -> None:
        self.set("_edges", edges)

    @property
    def conditional_edges(self) -> List[Dict]:
        return self._conditional_edges

    @conditional_edges.setter
    def conditional_edges(self, conditional_edges: List[Dict]) -> None:
        self.set("_conditional_edges", conditional_edges)

    @property
    def graph(self) -> CompiledStateGraph | None:
        return self._graph

    @graph.setter
    def graph(self, graph: CompiledStateGraph) -> None:
        self.set("_graph", graph)

    @property
    def settings(self) -> BaseSettings | None:
        return self._settings

    @settings.setter
    def settings(self, settings: BaseSettings) -> None:
        self.set("_settings", settings)

    @property
    def kwargs(self) -> Dict[str, Any] | None:
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs: Dict[str, Any]) -> None:
        self.set("_kwargs", kwargs)
