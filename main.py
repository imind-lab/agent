# import asyncio

# from pydantic import BaseModel, Field
# from imind_ai.agent.base.agent import BaseAgent
# from imind_ai.agent.config.schema import Input
# from langchain_mcp_adapters.client import MultiServerMCPClient


# class WeatherResponse(BaseModel):
#     """Respond to the user with this"""

#     temperature: float = Field(description="The temperature in fahrenheit")
#     wind_directon: str = Field(
#         description="The direction of the wind in abbreviated form"
#     )
#     wind_speed: float = Field(description="The speed of the wind in km/h")


# client = MultiServerMCPClient(
#     {
#         "weather": {
#             "url": "http://localhost:8888/echo/mcp/",
#             "transport": "streamable_http",
#         }
#     }
# )


# async def main():
#     tools = await client.get_tools()
#     agent = BaseAgent(
#         name="koofox",
#         system_prompt="You are a helpful assistant",
#         output_schema=WeatherResponse,
#         tools=tools,
#     )
#     user_input = Input(content="what's the weather in SF?")
#     resp = await agent.achat(user_input)
#     print("resp", resp)


# if __name__ == "__main__":
#     asyncio.run(main())

from pathlib import Path
from typing import Any

from pydantic import BaseModel
from imind_ai.agent.config.base import Config


config = Config.from_file(Path("./workflow.yaml"))
# print(config.nodes)

config = config.nodes[0]


class Output(BaseModel):
    status: int
    result: dict


class State(BaseModel):
    user_input: dict
    llm_output: Output


output = Output(status=1, result={"name": "daniel"})

state = State(user_input={"age": 18}, llm_output=output)


def process_reference(ref: str, state: State) -> Any:
    """取出引用对象的值
    引用对象不存在时抛出异常
    """
    infos = ref.split(".")
    entity = infos.pop(0)
    print(entity, state)
    if not hasattr(state, entity):
        raise ValueError(f"引用的值不正确，请核实{ref}, {str(state)}")

    item = getattr(state, entity)

    while len(infos) > 0:
        key = infos.pop(0)
        if isinstance(item, dict):
            item = item.get(key)
            if item is None:
                raise ValueError(f"引用的值不正确，请核实{ref}")
        else:
            if hasattr(item, key):
                item = getattr(item, key)
            else:
                raise ValueError(f"引用的值不正确，请核实{ref}")
    return item


def judge(operator: str, operand: Any, right_hand: Any) -> bool:
    if operator == "lt":
        return operand < right_hand
    elif operand == "eq":
        return operand == right_hand


if_express = config.if_express
if if_express.logic_operator:
    for condition in if_express.condition:
        print(condition)
        operand = process_reference(condition.operand, state)
        print(operand)
        right_hand = (
            condition.value
            if condition.source == "input"
            else process_reference(condition.reference, state)
        )

        logic = judge(condition.operator, operand, right_hand)
        print("logic", logic)
