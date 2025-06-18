from pydantic import BaseModel, ConfigDict


class State(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
