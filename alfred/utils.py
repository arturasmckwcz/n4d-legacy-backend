import ast
from datetime import datetime
from enum import StrEnum, auto
from os import getenv
from typing import Any, List

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


class YesNo(StrEnum):
    YES = auto()
    NO = auto()


def get_yes_no(flag: bool | None) -> str | None:
    """Gets a capitalized "Yes" or "No" string based on a boolean flag.

    Args:
        flag (bool): The boolean flag to convert.

    Returns:
        str | None: A capitalized "Yes" or "No" string, or None if `flag` is None.

    Raises:
        (This function raises no exceptions)
    """
    if flag is None:
        return None
    return YesNo.YES.capitalize() if flag else YesNo.NO.capitalize()


def parse_yes_no(value: str | None) -> bool | None:
    """Parses a string into a boolean value representing a yes or no answer.

    Args:
        value (str | None, optional): The string to parse. Defaults to None.

    Returns:
        bool | None: A boolean representing "yes" (True), "no" (False), or None if the input couldn't be parsed.

    Raises:
        (This function raises no exceptions)
    """
    if isinstance(value, str):
        value = value.lower()

    if value == YesNo.YES:
        return True
    elif value == YesNo.NO:
        return False
    return None


def is_later_than(dt1: datetime, dt2: datetime) -> bool:
    """Checks if the first datetime object is later than the second, ignoring their time zones.

    Args:
        dt1 (datetime): The first datetime object.
        dt2 (datetime): The second datetime object.

    Returns:
        bool: `True` if `dt1` is later than `dt2`, `False` otherwise.
    """
    dt1_naive = dt1.replace(tzinfo=None)
    dt2_naive = dt2.replace(tzinfo=None)
    return dt1_naive > dt2_naive


def get_the_first(maybe_list, should_raise=False):
    """Gets the first element of a list, handling potential errors.

    Args:
        maybe_list: The list to extract the first element from.
        should_raise (bool, optional): Whether to raise an exception if the list is empty. Defaults to False.

    Returns:
        The first element of the list, or None if the list is empty and `should_raise` is False.

    Raises:
        IndexError: If the list is empty and `should_raise` is True.
    """
    if should_raise:
        return maybe_list[0]
    else:
        try:
            return maybe_list[0]
        except Exception:
            return None


def get_key_value(
    source_dict: Any, keys: List[str], should_raise=False, null=None
) -> Any:
    """Recursively retrieves a value from a nested dictionary using a list of keys.

    Args:
        source_dict (Any): The source dictionary to extract the value from.
        keys (List[str]): A list of keys to follow to reach the desired value.
        should_raise (bool, optional): Whether to raise an exception if the value cannot be retrieved.
                                       Defaults to False.
        null (Any, optional): The default value to return if the value cannot be retrieved
                              and `should_raise` is False. Defaults to None.

    Returns:
        Any: The retrieved value, or value of `null` if the value cannot be retrieved and
            `should_raise` is False.

    Raises:
        KeyError: If a key is not found and `should_raise` is True.
        TypeError: If a value is not a dictionary and a key is used to access it.
    """

    def get_value():
        result = source_dict[keys[0]]
        for idx in range(1, len(keys)):
            result = result[keys[idx]]
        return result

    if should_raise:
        return get_value()
    else:
        try:
            return get_value()
        except Exception:
            return null


def get_clean_select_for_notion(content: str | None) -> str | None:
    """Cleans a given string for use as a Notion select option.

    This function sanitizes the input string to ensure compatibility with Notion's
    select field limitations

    Args:
        content: The input string to be cleaned.

    Returns:
        The cleaned string, or `None` if the input is `None`.
    """
    if not content:
        return None

    select = content.strip()
    # notion doesn't let select fields to contain a comma
    select = select.replace(",", " ")
    select = select.replace("  ", " ")
    if len(select) > 100:
        select = select[:100]
    return select


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
