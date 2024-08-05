import random

from django.core.exceptions import ValidationError


def validate_latitude(latitude: float):
    """Checks if provided latitude is within -90 and +90

    Arg:
        latitude (float): latitude value

    Returns:
        None: None if latidude is okay otherwise raises ValidationError
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
        granularity (int): patern element size in px
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
    if primary_keys is None:
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
        return result

    def flatten(obj):
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if isinstance(value, dict):
                    result[key] = get_primary_key_value(value)
                elif isinstance(value, list):
                    result[key] = list_value(value)
                else:
                    result[key] = value

            return result
        return {}

    return flatten(data)
