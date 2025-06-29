from ast import Dict
from enum import Enum
from typing import Callable, List, Tuple

from langgraph.graph.state import CompiledStateGraph

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
    _edges: List[Tuple[str, str]] = []
    _conditional_edges: List[Dict] = []
    _graph: CompiledStateGraph | None = None

    @property
    def phase(self) -> Phase:
        return self._phase

    @phase.setter
    def phase(self, phase: Phase) -> None:
        self.set("_phase", phase, override=True)

    @property
    def config(self) -> Config | None:
        return self._config

    @config.setter
    def config(self, config: Config) -> None:
        self.set("_config", config, override=True)

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List[Node]) -> None:
        self.set("_nodes", nodes, override=True)

    @property
    def edges(self) -> List[Tuple[str, str]]:
        return self._edges

    @edges.setter
    def edges(self, edges: List[Tuple[str, str]]) -> None:
        self.set("_edges", edges, override=True)

    @property
    def conditional_edges(self) -> List[Dict]:
        return self._conditional_edges

    @conditional_edges.setter
    def conditional_edges(self, conditional_edges: List[Dict]) -> None:
        self.set("_conditional_edges", conditional_edges, override=True)

    @property
    def graph(self) -> CompiledStateGraph | None:
        return self._graph

    @graph.setter
    def graph(self, graph: CompiledStateGraph) -> None:
        self.set("_graph", graph, override=True)
