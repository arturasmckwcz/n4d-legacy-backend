from http import HTTPStatus
from typing import List

import requests
from pydantic import BaseModel, ConfigDict

from tests_e2e.fixtures import structure, users
from tests_e2e.fixtures.data import lichtenberg_opportunity_flattered
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

url_encoded_params = "?search=%7B%22status%22:[%22Volunteers%20Needed%22]%7D&primary_keys=[%22name%22,%22title%22]"

API_LOGIN_URL = f"{ALFRED_API_URL}/api/jwt/create/"
API_OPPORTUNITY_URL = f"{ALFRED_API_URL}/api/opportunity/{url_encoded_params}"


class ApiOpportunityResponse(BaseModel):
    items: List[structure.ApiOpportunityFlattered]
    model_config = ConfigDict(extra="forbid")


class ApiLoginResponse(structure.ApiLogin):
    model_config = ConfigDict(extra="forbid")


def test_api_opportunity():
    login_request = requests.post(url=API_LOGIN_URL, data=users.rac_user)
    login_response = ApiLoginResponse(**login_request.json())

    assert login_request.status_code == HTTPStatus.OK

    headers = {"Authorization": f"Bearer {login_response.access}"}
    api_opportunity_request = requests.get(url=API_OPPORTUNITY_URL, headers=headers)
    response = ApiOpportunityResponse(items=api_opportunity_request.json())
    api_opportunity_response = response.items[0]

    assert api_opportunity_request.status_code == HTTPStatus.OK
    expected_opportunity = structure.ApiOpportunityFlattered(
        **lichtenberg_opportunity_flattered
    )

    assert api_opportunity_response == expected_opportunity
