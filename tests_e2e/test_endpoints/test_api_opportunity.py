from http import HTTPStatus
from typing import List

import requests
from pydantic import BaseModel, ConfigDict

from tests_e2e.fixtures import data, structure, users
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

primary_keys_param = "?primary_keys=%5B%22name%22%2C%22title%22%2C%22iso_code%22%5D"

API_LOGIN_URL = f"{ALFRED_API_URL}/api/jwt/create/"
API_OPPORTUNITY_URL = f"{ALFRED_API_URL}/api/opportunity/{primary_keys_param}"


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

    assert api_opportunity_response.title == data.opportunity["title"]

    api_opportunity_target_groups = api_opportunity_response.target_groups
    for idx in range(len(api_opportunity_target_groups)):
        assert api_opportunity_target_groups[idx] == data.target_groups[idx]["title"]

    assert api_opportunity_response.locations[0] == data.locations[0]["title"]
    assert api_opportunity_response.locations[1] == data.locations[1]["title"]

    assert len(api_opportunity_response.timeslots) > 0
    for idx in range(len(api_opportunity_response.timeslots)):
        assert api_opportunity_response.timeslots[idx] == data.timeslots[idx]["title"]

    assert len(api_opportunity_response.activities) > 0
    for idx in range(len(api_opportunity_response.activities)):
        assert api_opportunity_response.activities[idx] == data.activities[idx]["title"]

    assert len(api_opportunity_response.languages) > 0
    for idx in range(len(api_opportunity_response.languages)):
        assert (
            api_opportunity_response.languages[idx] == data.languages[idx]["iso_code"]
        )

    assert len(api_opportunity_response.skills) > 0
    for idx in range(len(api_opportunity_response.skills)):  # type: ignore
        assert (
            api_opportunity_response.skills[idx]  # type: ignore
            == data.skills[idx]["title"]
        )
