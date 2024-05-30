from rest_framework.request import Request
from rest_framework.response import Response


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
        return self.data.get(key, "") if isinstance(self.data, dict) else ""
