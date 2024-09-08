from os import environ
from unittest.mock import Mock, patch

import pytest
from django import setup
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.response import Response

from alfred.utils import (
    AlfredRequest,
    AlfredResponse,
    flatten_list,
    itemize_str,
    read_env_var,
)

environ.setdefault("DJANGO_SETTINGS_MODULE", "alfred.settings")
setup()


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("apple,banana,cherry", ["apple", "banana", "cherry"]),
        ("apple", "apple"),
        ("", ""),
        (0, None),
    ],
)
def test_itemize_str(input_str, expected_output):
    result = itemize_str(input_str)
    assert result == expected_output


@pytest.mark.parametrize(
    "input_list, expected_output",
    [
        (
            [[], ["1", "2"], ["3"], 4],
            ["1", "2", "3", 4],
        ),
        ([None, [{}, True]], [None, {}, True]),
        ({"key": "value"}, []),
    ],
)
def test_flatten_list(input_list, expected_output):
    assert flatten_list(input_list) == expected_output


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        123,
        [1, 2, 3],
    ],
)
def test_non_string_input(input_value):
    assert itemize_str(input_value) is None


@pytest.mark.parametrize(
    "env_var_value, itemize_str_value, expected_result",
    [
        (
            "apple,banana,cherry",
            ["apple", "banana", "cherry"],
            ["apple", "banana", "cherry"],
        ),
    ],
)
def test_env_var_set(env_var_value, itemize_str_value, expected_result):
    with patch("alfred.utils.getenv", return_value=env_var_value):
        with patch("alfred.utils.itemize_str", return_value=itemize_str_value):
            result = read_env_var("TEST_ENV_VAR")
            assert result == expected_result


@pytest.mark.parametrize(
    "env_var_value, default_value, expected_result",
    [
        (None, "default_value", "default_value"),
    ],
)
def test_default_value(env_var_value, default_value, expected_result):
    with patch("alfred.utils.getenv", return_value=env_var_value):
        with patch.dict("alfred.utils.defaults", {"TEST_ENV_VAR": default_value}):
            result = read_env_var("TEST_ENV_VAR")
            assert result == expected_result


@pytest.mark.parametrize(
    "env_var_value",
    [
        None,
    ],
)
def test_mandatory_var_not_set(env_var_value):
    with patch("alfred.utils.getenv", return_value=env_var_value):
        with patch.dict("alfred.utils.defaults", {}):
            with pytest.raises(BaseException):
                read_env_var("MANDATORY_ENV_VAR")


@pytest.mark.parametrize(
    "env_var_value, is_mandatory, expected_result",
    [
        (None, False, None),
    ],
)
def test_non_mandatory_var_not_set(env_var_value, is_mandatory, expected_result):
    with patch("alfred.utils.getenv", return_value=env_var_value):
        result = read_env_var("NON_MANDATORY_ENV_VAR", is_mandatory=is_mandatory)
        assert result == expected_result


@pytest.mark.parametrize(
    "initial_data, new_key, new_value, expected_data",
    [
        (
            {"existing_key": "existing_value"},
            "new_key",
            "new_value",
            {"existing_key": "existing_value", "new_key": "new_value"},
        ),
    ],
)
def test_set_data_attr(initial_data, new_key, new_value, expected_data):
    mock_request = Mock(spec=Request)
    mock_request._request = Mock(spec=HttpRequest)
    mock_request._request.data = initial_data

    alfred_request = AlfredRequest(mock_request)
    alfred_request.set_data_attr(new_key, new_value)

    assert isinstance(alfred_request.data, dict)
    assert alfred_request.data == expected_data


@pytest.mark.parametrize(
    "initial_data, new_key, new_value, expected_data",
    [
        (["not", "a", "dict"], "new_key", "new_value", ["not", "a", "dict"]),
    ],
)
def test_set_data_attr_non_dict(initial_data, new_key, new_value, expected_data):
    mock_request = Mock(spec=Request)
    mock_request._request = Mock(spec=HttpRequest)
    mock_request._request.data = initial_data

    alfred_request = AlfredRequest(mock_request)
    alfred_request.set_data_attr(new_key, new_value)

    assert alfred_request.data == expected_data


@pytest.mark.parametrize(
    "response_data, key, expected_value",
    [
        ({"key1": "value1", "key2": "value2"}, "key2", "value2"),
        ({"key": "value"}, "nonexistent_key", ""),
        ("not_a_dict", "any_key", ""),
    ],
)
def test_get_data_attr(response_data, key, expected_value):
    mock_response = Mock(spec=Response)
    mock_response.data = response_data

    alfred_response = AlfredResponse(mock_response)
    value = alfred_response.get_data_attr(key)

    assert value == expected_value
