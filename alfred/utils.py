import ast
import json
from os import PathLike, getenv

from rest_framework.request import Request
from rest_framework.response import Response

from .config.defaults import defaults
from .config.globals import BASE_DIR


def itemize_str(list_string) -> list[str] | str | None:
    if list_string[0] == "[":
        return ast.literal_eval(list_string)

    if isinstance(list_string, str):
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
        print(f"TypeError: {err}")
        return []


def read_local_env(local_env_path: PathLike) -> dict:
    local_env = {}
    try:
        with open(local_env_path) as env_file:
            local_env = json.load(env_file)
            for key, value in local_env.items():
                local_env[key] = itemize_str(value)
    except FileNotFoundError:
        pass

    return local_env


dotenv_file = BASE_DIR / ".env.json"
defaults.update(read_local_env(dotenv_file))


def read_env_var(
    name: str,
    is_mandatory=True,
) -> str | int | float | tuple | list | dict | None:
    value = getenv(name)

    if value:
        return itemize_str(value)

    if name in defaults:
        return defaults[name]

    if is_mandatory:
        raise BaseException(f"Environment var {name} has to be set!")

    return None


class AlfredRequest(Request):
    def __init__(self, request: Request):
        self.__dict__.update(request.__dict__)

    def set_data_attr(self, key: str, value: str) -> None:
        if isinstance(self.data, dict):
            self.data[key] = value


class AlfredResponse(Response):
    def __init__(self, response: Response):
        self.__dict__.update(response.__dict__)

    def get_data_attr(self, key: str) -> str:
        if isinstance(self.data, dict):
            return self.data.get(key, "")

        return ""
