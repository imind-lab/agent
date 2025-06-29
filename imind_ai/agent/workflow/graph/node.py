from imind_ai.agent.config.base import BaseNode


class Node:

    def __init__(self, config: BaseNode):
        self.id = config.id
        self.name = config.name
        self.config = config
