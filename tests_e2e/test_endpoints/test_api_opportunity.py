from http import HTTPStatus
from typing import List

import requests
from pydantic import BaseModel, ConfigDict

from tests_e2e.fixtures import structure, users
from tests_e2e.fixtures.data import lichtenberg_opportunity_flattered
from tests_e2e.fixtures.opportunity_form_data import (
    InvalidOpportunityFormData,
    ValidOpportunityFormData,
)
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

url_encoded_params = "?search=%7B%22status%22:[%22Volunteers%20Needed%22]%7D&primary_keys=[%22name%22,%22title%22]"

API_LOGIN_URL = f"{ALFRED_API_URL}/api/jwt/create/"
API_OPPORTUNITY_POST_URL = f"{ALFRED_API_URL}/api/opportunity/"
API_OPPORTUNITY_GET_URL = f"{ALFRED_API_URL}/api/opportunity/{url_encoded_params}"


class ApiOpportunityResponse(BaseModel):
    items: List[structure.ApiOpportunityFlattered]
    model_config = ConfigDict(extra="forbid")


class ApiLoginResponse(structure.ApiLogin):
    model_config = ConfigDict(extra="forbid")


def test_get_opportunity():
    login_request = requests.post(url=API_LOGIN_URL, data=users.rac_user)
    login_response = ApiLoginResponse(**login_request.json())

    assert login_request.status_code == HTTPStatus.OK

    headers = {"Authorization": f"Bearer {login_response.access}"}
    api_opportunity_request = requests.get(url=API_OPPORTUNITY_GET_URL, headers=headers)
    response = ApiOpportunityResponse(items=api_opportunity_request.json())
    api_opportunity_response = response.items[0]

    assert api_opportunity_request.status_code == HTTPStatus.OK
    expected_opportunity = structure.ApiOpportunityFlattered(
        **lichtenberg_opportunity_flattered
    )

    assert api_opportunity_response == expected_opportunity


def test_post_valid_form_volunteer():
    post_form_response = requests.post(
        API_OPPORTUNITY_POST_URL,
        json=ValidOpportunityFormData.good_samaritan,
    )
    assert post_form_response.status_code == HTTPStatus.CREATED
    desired_keys_in_response = ["id", "created_at"]
    for key in desired_keys_in_response:
        assert key in post_form_response.json()


def test_post_valid_form_accompanying():
    post_form_response = requests.post(
        API_OPPORTUNITY_POST_URL,
        json=ValidOpportunityFormData.jeremiah,
    )
    assert post_form_response.status_code == HTTPStatus.CREATED
    desired_keys_in_response = ["id", "created_at"]
    for key in desired_keys_in_response:
        assert key in post_form_response.json()


def test_post_invalid_form_volunteer():
    post_form_response = requests.post(
        API_OPPORTUNITY_POST_URL, json=InvalidOpportunityFormData.judas_iscariot
    )
    assert post_form_response.status_code == HTTPStatus.BAD_REQUEST
    assert post_form_response.json() == {"rac_email": ["Enter a valid email address."]}
