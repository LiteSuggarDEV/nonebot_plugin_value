from typing import Any

from pydantic import BaseModel, Field


class BaseData(BaseModel):
    # dict鸭子类型
    id: str = Field(default_factory=str)

    def __getitem__(self, key: str):
        if key not in self.model_dump():
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: str):
        if key not in self.model_dump():
            raise KeyError(key)
        setattr(self, key, value)

    def get(self, key: str, default: Any | None = None):
        return getattr(self, key, default)
