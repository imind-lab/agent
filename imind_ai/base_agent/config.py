import os
from pathlib import Path
from typing import Any, Optional, Union
from openai import BaseModel

from imind_ai.utils import read_yaml


class IOOption(BaseModel):
    description: str
    type: str
    default: Any


class EnvOption(BaseModel):
    alias: Optional[str] = None
    description: str
    type: str
    default: Any


class Config(BaseModel):
    input: IOOption
    output: Union[str, IOOption]
    env: Optional[EnvOption] = None

    @classmethod
    def from_file(cls, path: Path | None = None) -> "Config":
        path = path or Path(os.path.join(os.path.dirname(__file__), "agent.yaml"))
        cfg = read_yaml(path)
        return Config(**cfg)

    @classmethod
    def default(cls) -> "Config":
        return cls.from_file()
