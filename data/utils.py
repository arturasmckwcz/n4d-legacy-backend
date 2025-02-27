import random
from functools import reduce

import structlog
from django.core.exceptions import ValidationError
from django.db.models import Q

from data.enums import DAY_CHOICES

logger = structlog.get_logger(__name__)


def validate_latitude(latitude: float):
    """Checks if provided latitude is within -90 and +90

    Arg:
        latitude (float): latitude value

    Returns:
        None: None if latitude is okay otherwise raises ValidationError
    """

    if latitude < -90 or latitude > 90:
        raise ValidationError("Latitude must be between -90 and 90 degrees.")


def validate_longitude(longitude: float):
    """Checks if provided longitude is within -180 and +180

    Arg:
        longitude (float): longitude value

    Returns:
        None: None if longitude is okay otherwise raises ValidationError
    """

    if longitude < -180 or longitude > 180:
        raise ValidationError("Longitude must be between -180 and 180 degrees.")


def generate_square_pattern_svg(size: int, granularity: int, color: str) -> str | None:
    """Generates an SVG string representing a square pattern with horizontal symmetry.

    Args:
        size (int): square size in px
        granularity (int): pattern element size in px
        color (str): The color of the squares (e.g., "#FF0000" for red).

    Returns:
        str: svg as html element or
        None: if size or granularity is invalid
    """

    if (size < 16 or size > 128) or (granularity < 2 or granularity > size // 4):
        return None

    def rect_template(x: int, y: int) -> str:
        return f"""
        <rect x='{x}' y='{y}' width='{granularity}' height='{granularity}' fill='{color}' />
        <rect x='{size-granularity-x}' y='{y}' width='{granularity}' height='{granularity}' fill='{color}' />
        """

    def random_rects() -> str:
        rects = ""
        for y in range(0, size, granularity):
            for x in range(0, size // 2, granularity):
                rects += rect_template(x, y) if round(random.random()) else ""

        return rects

    return f"""
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
    {random_rects()}
  </svg>
  """


def flatten_dict(data: dict, primary_keys: list | None = None) -> dict:
    """Flattens a nested dictionary based on specified primary keys.

    Recursively flattens a nested dictionary, preserving list structures.
    If primary keys are provided, the function attempts to extract the value
    of the first primary key found in each nested dictionary and replaces
    the nested dictionary with this value. If no primary key is found, the
    dictionary is flattened recursively.

    Args:
        data: The nested dictionary to flatten.
        primary_keys: A list of keys to prioritize for flattening.
            If None or empty, the entire dictionary is flattened.

    Returns:
        A flattened dictionary.
    """

    if (primary_keys is None) or (len(primary_keys) == 0):
        return data

    def get_primary_key_value(obj):
        for key in obj.keys():
            if key in primary_keys:
                return obj[key]

    def list_value(data: list) -> list:
        result = []
        for item in data:
            if isinstance(item, dict):
                primary_value = get_primary_key_value(item)
                result.append(primary_value if primary_value else flatten(item))
            elif isinstance(item, list):
                result.append(list_value(item))
            else:
                result.append(item)
        return result

    def flatten(obj):
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if isinstance(value, dict):
                    primary_value = get_primary_key_value(value)
                    result[key] = primary_value if primary_value else flatten(value)
                elif isinstance(value, list):
                    result[key] = list_value(value)
                else:
                    result[key] = value
            return result
        return {}

    return flatten(data)


def filter_queryset(queryset, filter_dict):
    """Filters a queryset based on a given filter dictionary.

    Args:
        queryset: The queryset to filter.
        filter_dict: A dictionary where keys are field names and values are lists of allowed values.
            example: {"status":["Volunteers Needed"]}

    Returns:
        The filtered queryset.
    """

    filter_dict_items = filter_dict.items()
    logger.debug(f"filter_dict: {filter_dict}")
    if len(filter_dict_items) == 0:
        return queryset

    filters = []
    for field, values in filter_dict_items:
        q_objects = [Q(**{field: value}) for value in values]
        filters.append(reduce(lambda x, y: x | y, q_objects))

    logger.debug(f"filters: {filters}")

    return queryset.filter(reduce(lambda x, y: x & y, filters))


def is_in_DAY_CHOICES(day: str) -> bool:
    return day in [day_choice[1] for day_choice in DAY_CHOICES]


def get_day_number_from_DAY_CHOICES(day: str) -> int | None:
    for day_choice_number, day_choice_day in DAY_CHOICES:
        if day == day_choice_day:
            return day_choice_number
    return None
