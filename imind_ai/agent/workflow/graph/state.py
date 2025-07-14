from typing import Any, Dict, List, Optional, Tuple, Type, Union
from pydantic import BaseModel, ConfigDict, Field, create_model

from imind_ai.agent.workflow.graph.node import Node


NODE_INPUT_TEMPLATE = "{node_id}_input"
NODE_OUTPUT_TEMPLATE = "{node_id}_output"


def new_state_cls(nodes: List[Node]) -> Type[BaseModel]:
    model_config = ConfigDict(arbitrary_types_allowed=True)

    schema_dict: Dict[str, Tuple] = {
        "workflow_input": (Union[str, Tuple[str, dict], dict], Field()),
        "workflow_output": (Optional[Union[str, dict]], None),
    }

    for node in nodes:

        if node.type == "loop_aggregation":
            schema_dict[NODE_OUTPUT_TEMPLATE.format(node_id=node.id)] = (
                Optional[Dict[str, Any]],
                None,
            )
            # schema_dict[f"{node.id}_counter"] = (int, 0)
            # schema_dict[f"{node.id}_agg_items"] = (Optional[List[Any]], None)
            # schema_dict[f"{node.id}_aggregation"] = (Optional[Any], None)
        else:
            schema_dict[NODE_INPUT_TEMPLATE.format(node_id=node.id)] = (
                Optional[Union[str, Dict[str, Any]]],
                None,
            )
            schema_dict[NODE_OUTPUT_TEMPLATE.format(node_id=node.id)] = (
                Optional[Union[str, Dict[str, Any]]],
                None,
            )
    print(f"{schema_dict=}")
    return create_model("State", __config__=model_config, **schema_dict)
