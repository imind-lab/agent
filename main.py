import asyncio
from certifi import contents
from imind_ai.base_agent.agent import BaseAgent
from imind_ai.config.schema import Input

agent = BaseAgent(name="koofox", system_prompt="You are a helpful assistant")
user_input = Input(content="你是谁？")


async def main():
    resp = await agent.achat(user_input)
    print("resp", resp)


if __name__ == "__main__":
    asyncio.run(main())
