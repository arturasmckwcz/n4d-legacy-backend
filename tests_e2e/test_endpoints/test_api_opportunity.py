from http import HTTPStatus
from typing import List

import requests
from pydantic import BaseModel, ConfigDict

from tests_e2e.fixtures import data, structure, users
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

API_LOGIN_URL = f"{ALFRED_API_URL}/api/jwt/create/"
API_ME_URL = f"{ALFRED_API_URL}/api/opportunity/"


class ApiOpportunityRespose(BaseModel):
    items: List[structure.ApiOpportunityFlattered]

    model_config = ConfigDict(extra="forbid")


class ApiLoginResponse(structure.ApiLogin):
    model_config = ConfigDict(extra="forbid")


def test_api_opportunity():
    login_request = requests.post(url=API_LOGIN_URL, data=users.rac_user)
    login_response = ApiLoginResponse(**login_request.json())

    assert login_request.status_code == HTTPStatus.OK

    headers = {"Authorization": f"Bearer {login_response.access}"}
    api_opportunity_request = requests.get(url=API_ME_URL, headers=headers)
    response = ApiOpportunityRespose(items=api_opportunity_request.json())
    api_opportunity_response = response.items[0]

    assert api_opportunity_request.status_code == HTTPStatus.OK

    assert api_opportunity_response.title == data.opportunity["title"]
    assert (
        api_opportunity_response.volunteers_number
        == data.opportunity["volunteers_number"]
    )

    assert api_opportunity_response.organization == data.organization_RAC_name

    api_opportunity_target_groups = api_opportunity_response.target_groups
    for idx in range(len(api_opportunity_target_groups)):
        assert api_opportunity_target_groups[idx] == data.target_groups[idx]["title"]

    api_opportunity_payload = api_opportunity_response.payloads[0]
    assert api_opportunity_payload.payload_type == data.payload_USSR["payload_type"]

    assert api_opportunity_payload.locations[0] == data.locations[0]["title"]

    assert api_opportunity_payload.locations[1] == data.locations[1]["title"]

    for idx in range(len(api_opportunity_payload.timeslots)):
        assert api_opportunity_payload.timeslots[idx] == data.timeslots[idx]["title"]

    for idx in range(len(api_opportunity_payload.activities)):
        assert api_opportunity_payload.activities[idx] == data.activities[idx]["title"]

    for idx in range(len(api_opportunity_payload.languages)):
        assert api_opportunity_payload.languages[idx] == data.languages[idx]["iso_code"]

    for idx in range(len(api_opportunity_payload.skills)):  # type: ignore
        assert (
            api_opportunity_payload.skills[idx]  # type: ignore
            == data.skills[idx]["title"]
        )
