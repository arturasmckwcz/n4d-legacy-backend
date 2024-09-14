import ast
from os import getenv

import structlog
from rest_framework.request import Request
from rest_framework.response import Response

from .config.defaults import defaults

logger = structlog.get_logger(__name__)


def itemize_str(list_string) -> list[str] | str | None:
    if isinstance(list_string, str):
        if len(list_string) == 0:
            return ""
        if list_string[0] == "[":
            return ast.literal_eval(list_string)

        value = [item.strip() for item in list_string.split(",")]
        return value[0] if len(value) == 1 else value


def flatten_list(_list: list) -> list:
    try:
        if not isinstance(_list, list):
            raise TypeError("Input should be a list")

        result = []
        for item in _list:
            result += item if isinstance(item, list) else [item]

        return result
    except TypeError as err:
        logger.error(f"Error {err} at flattening list")
        return []


def bool_string_to_bool(value: str | None) -> str | bool | None:
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
    return value


def read_env_var(
    name: str,
    is_mandatory=True,
) -> str | int | float | tuple | list | dict | None:
    value = getenv(name)

    logger.debug(f"Reading {name} {value} {type(value)}")

    value = bool_string_to_bool(value=value)

    if isinstance(value, bool):
        return value

    if value:
        return itemize_str(value)

    if name in defaults:
        return defaults[name]

    if is_mandatory:
        logger.error(f"Environment var {name} is mandatory")
        raise BaseException(f"Environment var {name} has to be set!")

    return None


class AlfredRequest(Request):
    def __init__(self, request: Request):
        self.__dict__.update(request.__dict__)
        logger.debug(f"Alfred request {request}")

    def set_data_attr(self, key: str, value: str) -> None:
        if isinstance(self.data, dict):
            self.data[key] = value


class AlfredResponse(Response):
    def __init__(self, response: Response):
        self.__dict__.update(response.__dict__)
        logger.debug(f"Alfred response {response}")

    def get_data_attr(self, key: str) -> str:
        if isinstance(self.data, dict):
            return self.data.get(key, "")

        return ""
