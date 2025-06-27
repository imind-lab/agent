from pydantic import BaseModel

from langgraph.store.base import BaseStore


class BaseContext(BaseModel):
    __user_id: str | None = None
    __store: BaseStore | None = None
    __session_id: str | None = None

    def set(self, k, v):
        """Set attribute"""
        self.__dict__[k] = v

    @property
    def user_id(self) -> str | None:
        return self.__user_id

    @user_id.setter
    def user_id(self, user_id: str):
        self.set("__user_id", user_id)

    @property
    def store(self) -> BaseStore | None:
        return self.__store

    @store.setter
    def store(self, store: BaseStore):
        self.set("__store", store)

    @property
    def session_id(self) -> str | None:
        return self.__session_id

    @session_id.setter
    def session_id(self, session_id: str):
        self.set("__session_id", session_id)
