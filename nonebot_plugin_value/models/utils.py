from enum import Enum


class OnDeleteEnum(str, Enum):
    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
