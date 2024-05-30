import json
from os import PathLike, getenv

from .config.defaults import defaults
from .config.globals import BASE_DIR


def get_list_from_str(list_string) -> list[str] | str | None:
    if isinstance(list_string, str):
        value = [item.strip() for item in list_string.split(",")]
        return value[0] if len(value) == 1 else value


def read_local_env(local_env_path: PathLike) -> dict:
    local_env = {}
    try:
        with open(local_env_path, "r") as env_file:
            local_env = json.load(env_file)
            for key, value in local_env.items():
                local_env[key] = get_list_from_str(value)
    except FileNotFoundError:
        pass

    return local_env


dotenv_file = BASE_DIR / ".env.json"
defaults.update(read_local_env(dotenv_file))


def read_env_var(
    name: str, is_mandatory=True
) -> str | int | float | tuple | list | dict | None:
    value = getenv(name)

    if value:
        return get_list_from_str(value)

    if name in defaults:
        return defaults[name]

    if is_mandatory:
        raise BaseException(f"Environment var {name} has to be set!")

    return None
