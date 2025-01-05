from functools import reduce
from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError
from django.db.models import Q

from data.utils import (  # is_valid_email,
    filter_queryset,
    flatten_dict,
    generate_square_pattern_svg,
    get_day_number_from_DAY_CHOICES,
    is_in_DAY_CHOICES,
    validate_latitude,
    validate_longitude,
)


@pytest.mark.parametrize(
    "size, granularity, color, expected_result",
    [
        (32, 4, "red", False),
        (32, 2, "", False),
        (32, 20, "", True),
        (15, 2, "", True),
        (150, 2, "", True),
    ],
)
def test_generate_square_pattern_svg(size, granularity, color, expected_result):
    square_pattern_svg = generate_square_pattern_svg(size, granularity, color)
    result = square_pattern_svg is None
    assert result is expected_result


@pytest.mark.parametrize(
    "latitude, expected_exception",
    [
        (0.0, None),
        (15.78, None),
        (-89.99, None),
        (90.0, None),
    ],
)
def test_validate_latitude(latitude, expected_exception):
    assert validate_latitude(latitude) is expected_exception


@pytest.mark.parametrize(
    "day, expected_result",
    [
        ("Occasional", True),
        ("Monday", True),
        ("Tuesday", True),
        ("Wednesday", True),
        ("Thursday", True),
        ("Friday", True),
        ("Saturday", True),
        ("Sunday", True),
        ("something_else", False),
        (None, False),
    ],
)
def test_is_in_DAY_CHOICES(day, expected_result):
    assert is_in_DAY_CHOICES(day) is expected_result


@pytest.mark.parametrize(
    "day, expected_result",
    [
        ("Occasional", 0),
        ("Monday", 1),
        ("Tuesday", 2),
        ("Wednesday", 3),
        ("Thursday", 4),
        ("Friday", 5),
        ("Saturday", 6),
        ("Sunday", 7),
        ("something_else", None),
        (None, None),
    ],
)
def test_get_day_number_from_DAY_CHOICES(day, expected_result):
    assert get_day_number_from_DAY_CHOICES(day) is expected_result


@pytest.mark.parametrize(
    "latitude, expected_exception, expected_error_message",
    [
        (-100, ValidationError, "Latitude must be between -90 and 90 degrees."),
        (100.1, ValidationError, "Latitude must be between -90 and 90 degrees."),
        ("hello", TypeError, "'<' not supported between instances of 'str' and 'int'"),
    ],
)
def test_validate_latitude_with_side_effect(
    latitude, expected_exception, expected_error_message
):
    with pytest.raises(expected_exception) as excinfo:
        validate_latitude(latitude)
        assert excinfo.value.args[0] == expected_error_message


@pytest.mark.parametrize(
    "longitude, expected_exception",
    [
        (0.0, None),
        (15.78, None),
        (-179.99, None),
        (180.0, None),
    ],
)
def test_validate_longitude(longitude, expected_exception):
    assert validate_longitude(longitude) is None


@pytest.mark.parametrize(
    "longitude, expected_exception, expected_error_message",
    [
        (-181, ValidationError, "Longitude must be between -180 and 180 degrees."),
        (181.1, ValidationError, "Longitude must be between -180 and 180 degrees."),
        ("hello", TypeError, "'<' not supported between instances of 'str' and 'int'"),
    ],
)
def test_validate_longitude_with_side_effect(
    longitude, expected_exception, expected_error_message
):
    with pytest.raises(expected_exception) as excinfo:
        validate_longitude(longitude)
        assert excinfo.value.args[0] == expected_error_message


@pytest.mark.parametrize(
    "data, primary_keys, expected",
    [
        ([], None, []),
        ({"a": 1, "b": 2}, None, {"a": 1, "b": 2}),
        (
            {"a": 1, "b": [{"c": 3}, {"c": 4}], "e": 5},
            [],
            {"a": 1, "b": [{"c": 3}, {"c": 4}], "e": 5},
        ),
        (
            {"a": 1, "b": [{"c": 3}, {"c": 4}], "e": 5},
            ["c"],
            {"a": 1, "b": [3, 4], "e": 5},
        ),
        (
            {
                "a": 1,
                "b": [{"c": 3}, {"c": 4}],
                "e": [{"f": 5, "g": [{"d": 7}, {"d": 8}]}],
            },
            ["c", "d"],
            {"a": 1, "b": [3, 4], "e": [{"f": 5, "g": [7, 8]}]},
        ),
        (5, [""], {}),
    ],
)
def test_flatten_dict(data, primary_keys, expected):
    result = flatten_dict(data, primary_keys)
    assert result == expected


@pytest.mark.parametrize(
    "queryset, filter_dict, expected_filter_calls",
    [
        (
            MagicMock(),
            {"status": ["Volunteers Needed"]},
            [Q(status="Volunteers Needed")],
        ),
        (
            MagicMock(),
            {"status": ["Volunteers Needed", "Closed"]},
            [Q(status="Volunteers Needed") | Q(status="Closed")],
        ),
        (
            MagicMock(),
            {"status": ["Volunteers Needed", "Closed"], "type": ["Urgent", "Standard"]},
            [
                Q(status="Volunteers Needed") | Q(status="Closed"),
                Q(type="Urgent") | Q(type="Standard"),
            ],
        ),
    ],
)
def test_filter_queryset(queryset, filter_dict, expected_filter_calls):
    queryset.filter = MagicMock(return_value=queryset)

    result = filter_queryset(queryset, filter_dict)

    expected_call = reduce(lambda x, y: x & y, expected_filter_calls)
    queryset.filter.assert_called_once_with(expected_call)

    assert result == queryset


@pytest.mark.parametrize(
    "queryset, filter_dict, expected_filter_calls",
    [(MagicMock(), {}, [])],
)
def test_empty_filter_queryset(queryset, filter_dict, expected_filter_calls):
    queryset.filter = MagicMock(return_value=queryset)

    result = filter_queryset(queryset, filter_dict)

    queryset.filter.assert_not_called()

    assert result == queryset
