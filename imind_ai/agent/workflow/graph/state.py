from typing import Any, Dict, List, Optional, Tuple, Type, Union
from pydantic import BaseModel, ConfigDict, create_model

from imind_ai.agent.workflow.graph.node import Node


NODE_INPUT_TEMPLATE = "{node_id}_input"
NODE_OUTPUT_TEMPLATE = "{node_id}_output"


class BaseState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    workflow_input: Union[str, Tuple[str, dict], dict]
    workflow_output: Optional[Union[str, dict]] = None

    extras: Dict[str, Any] = {}


def new_state_cls(nodes: List[Node]) -> Type[BaseState]:
    schema_dict: Dict[str, Tuple] = {}
    for node in nodes:
        schema_dict[NODE_INPUT_TEMPLATE.format(node_id=node.id)] = (
            Optional[Union[str, Dict[str, Any]]],
            None,
        )
        schema_dict[NODE_OUTPUT_TEMPLATE.format(node_id=node.id)] = (
            Optional[Union[str, Dict[str, Any]]],
            None,
        )
    return create_model("State", __base__=BaseState, **schema_dict)
