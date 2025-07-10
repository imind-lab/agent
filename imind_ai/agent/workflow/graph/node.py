from imind_ai.agent.config.base import BaseNodeConfig


class Node:

    def __init__(self, config: BaseNodeConfig):
        self.id = config.id
        self.name = config.name
        self.type = config.type
        self.config = config
