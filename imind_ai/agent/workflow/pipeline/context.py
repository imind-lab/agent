from enum import Enum
from typing import Any, Callable, List, Tuple, Dict

from langgraph.graph.state import CompiledStateGraph
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
    __phase: Phase = Phase.INITIAL
    __config: Config | None = None
    __nodes: List[Node] = []
    __edges: List[Tuple[str, str]] = []
    __conditional_edges: List[Dict] = []
    __graph: CompiledStateGraph | None = None
    __settings: BaseSettings | None = None
    __kwargs: Dict[str, Any] | None = None

    @property
    def phase(self) -> Phase:
        return self.__phase

    @phase.setter
    def phase(self, phase: Phase) -> None:
        self.set("__phase", phase)

    @property
    def config(self) -> Config | None:
        return self.__config

    @config.setter
    def config(self, config: Config) -> None:
        self.set("__config", config)

    @property
    def nodes(self) -> List[Node]:
        return self.__nodes

    @nodes.setter
    def nodes(self, nodes: List[Node]) -> None:
        self.set("__nodes", nodes)

    @property
    def edges(self) -> List[Tuple[str, str]]:
        return self.__edges

    @edges.setter
    def edges(self, edges: List[Tuple[str, str]]) -> None:
        self.set("__edges", edges)

    @property
    def conditional_edges(self) -> List[Dict]:
        return self.__conditional_edges

    @conditional_edges.setter
    def conditional_edges(self, conditional_edges: List[Dict]) -> None:
        self.set("__conditional_edges", conditional_edges)

    @property
    def graph(self) -> CompiledStateGraph | None:
        return self.__graph

    @graph.setter
    def graph(self, graph: CompiledStateGraph) -> None:
        self.set("__graph", graph)

    @property
    def settings(self) -> BaseSettings | None:
        return self.__settings

    @settings.setter
    def settings(self, settings: BaseSettings) -> None:
        self.set("__settings", settings)

    @property
    def kwargs(self) -> Dict[str, Any] | None:
        return self.__kwargs

    @kwargs.setter
    def kwargs(self, kwargs: Dict[str, Any]) -> None:
        self.set("__kwargs", kwargs)
