from typing import Any, Dict, List, Optional, Tuple, Type, Union
from pydantic import BaseModel, ConfigDict, create_model

from imind_ai.agent.config.base import BaseNode


NODE_INPUT_TEMPLATE = "{node_id}_input"
NODE_OUTPUT_TEMPLATE = "{node_id}_output"


class BaseState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_input: Union[str, Tuple[str, dict]]
    workflow_output: Union[str, dict]

    extras: Dict[str, Any] = {}


def new_state_cls(nodes: List[BaseNode]) -> Type[BaseState]:
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
