import os
from http import HTTPStatus
from typing import List

import requests
from django.core.files.uploadedfile import SimpleUploadedFile
from pydantic import BaseModel, ConfigDict

from tests_e2e.fixtures import structure, users
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

primary_keys_param = "?search=%7B%22status%22%3A%5B%22e2e_test%22%5D%7D"

API_LOGIN_URL = f"{ALFRED_API_URL}/api/jwt/create/"
API_OPPORTUNITY_URL = f"{ALFRED_API_URL}/api/opportunity/{primary_keys_param}"
API_OPPORTUNITIES_JSON_URL = f"{ALFRED_API_URL}/api/opportunities.json/"
FILE_OPPORTUNITIES_JSON_URI = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../fixtures/opportunities.json"
)


class ApiOpportunityResponse(BaseModel):
    items: List[structure.ApiOpportunity]

    model_config = ConfigDict(extra="forbid")


class ApiLoginResponse(structure.ApiLogin):
    model_config = ConfigDict(extra="forbid")


class ApiOpportunitiesJsonResponse(BaseModel):
    message: str


def test_api_opportunities_json():
    login_request = requests.post(url=API_LOGIN_URL, data=users.rac_user)
    login_response = ApiLoginResponse(**login_request.json())

    assert login_request.status_code == HTTPStatus.OK

    headers = {
        "Authorization": f"Bearer {login_response.access}",
    }

    with open(FILE_OPPORTUNITIES_JSON_URI, "rb") as f:
        file_to_upload = SimpleUploadedFile(
            f.name, f.read(), content_type="application/json"
        )

    upload_request = requests.post(
        API_OPPORTUNITIES_JSON_URL, files={"json_file": file_to_upload}, headers=headers
    )

    upload_response = ApiOpportunitiesJsonResponse(**upload_request.json())
    assert (
        upload_response.message
        == "JSON file uploaded and successfully processed 3 items"
    )
    assert upload_request.status_code == HTTPStatus.OK

    api_opportunity_request = requests.get(url=API_OPPORTUNITY_URL, headers=headers)
    assert len(api_opportunity_request.json()) == 3

    response = ApiOpportunityResponse(items=api_opportunity_request.json())

    assert len(response.items) == 3
