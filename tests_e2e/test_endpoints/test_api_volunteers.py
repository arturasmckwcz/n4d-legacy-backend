from http import HTTPStatus

import requests

from tests_e2e.fixtures.volunteer_form_data import (
    InvalidVolunteerFormData,
    ValidVolunteerFormData,
)
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

API_VOLUNTEER_FORM_URL = f"{ALFRED_API_URL}/api/volunteer/"


def test_accept_valid_form():
    post_form_response = requests.post(
        API_VOLUNTEER_FORM_URL,
        json=ValidVolunteerFormData.john_doe,
    )
    assert post_form_response.status_code == HTTPStatus.CREATED
    desired_keys_in_response = ["form_id", "created_at"]
    for key in desired_keys_in_response:
        assert key in post_form_response.json()


def test_refuse_invalid_form():
    post_form_response = requests.post(
        API_VOLUNTEER_FORM_URL, json=InvalidVolunteerFormData.robin_hood
    )
    assert post_form_response.status_code == HTTPStatus.BAD_REQUEST
    assert post_form_response.json() == {"email": ["This field is required."]}
