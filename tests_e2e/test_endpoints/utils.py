import os


def get_env_variable(name: str) -> str:
    env_variable = os.getenv(name)
    if env_variable is None:
        raise RuntimeError(f"{env_variable} is None")
    return env_variable
