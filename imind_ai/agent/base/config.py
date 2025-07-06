import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from openai import BaseModel

from imind_ai.utils import read_yaml


class IOOption(BaseModel):
    description: str
    type: str
    default: Optional[Any] = None


class EnvOption(BaseModel):
    required: Optional[bool] = False
    alias: Optional[str] = None
    description: str
    type: str
    default: Any


class Config(BaseModel):
    input: Dict[str, IOOption]
    output: Union[str, Dict[str, IOOption]]
    env: Optional[Dict[str, EnvOption]] = None

    @classmethod
    def from_file(cls, path: Path | None = None) -> "Config":
        path = path or Path(os.path.join(os.path.dirname(__file__), "agent.yaml"))
        cfg = read_yaml(path)
        return Config(**cfg)

    @classmethod
    def default(cls) -> "Config":
        return cls.from_file()
