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


from imind_ai.agent.workflow.pipeline.context import Context
from imind_ai.agent.workflow.pipeline.parser import Parser


context = Context()

config = Parser.parse(context)
print(config)
