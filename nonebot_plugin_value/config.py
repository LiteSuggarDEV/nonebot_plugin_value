from pydantic import BaseModel


class Config(BaseModel):
    """
    配置
    """

    value_pre_build_cache: bool = True
