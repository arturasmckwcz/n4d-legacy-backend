import requests
from pydantic import BaseModel, ConfigDict

from tests_e2e.test_endpoints.variables import ALFRED_API_URL

SANITY_URL = f"{ALFRED_API_URL}/sanity/"


class SanityResponse(BaseModel):
    message: str
    x_requested_from: str | None
    last_commit: str | None

    model_config = ConfigDict(extra="forbid")


def test_sanity_ok():
    sanity_request = requests.get(url=SANITY_URL)
    sanity_response = SanityResponse(**sanity_request.json())
    assert sanity_response.message == "OK"


def test_sanity_x_requested_from():
    headers = {"X-Requested-From": "Wayne Manor"}
    sanity_request = requests.get(url=SANITY_URL, headers=headers)
    sanity_response = SanityResponse(**sanity_request.json())
    assert sanity_response.x_requested_from == "Wayne Manor"
    assert sanity_response.last_commit == "I'm the last"
