import requests
from pydantic import BaseModel, ConfigDict

from tests_e2e.test_endpoints.variables import ALFRED_API_URL

SANITY_URL = f"{ALFRED_API_URL}/sanity"


class SanityResponse(BaseModel):
    message: str
    x_requested_from: str | None

    model_config = ConfigDict(extra="forbid")


def test_sanity_ok():
    sanity_request = requests.get(SANITY_URL)
    sanity_response = SanityResponse(**sanity_request.json())
    assert sanity_response.message == "OK"
