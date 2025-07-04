from pydantic import BaseModel

from langgraph.store.base import BaseStore


class BaseContext(BaseModel):
    _user_id: str | None = None
    _store: BaseStore | None = None
    _session_id: str | None = None

    def set(self, k, v):
        """Set attribute"""
        self.__dict__[k] = v

    @property
    def user_id(self) -> str | None:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: str):
        self.set("_user_id", user_id)

    @property
    def store(self) -> BaseStore | None:
        return self._store

    @store.setter
    def store(self, store: BaseStore):
        self.set("_store", store)

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: str):
        self.set("_session_id", session_id)
