from http import HTTPStatus

import requests
from pydantic import ConfigDict

from tests_e2e.fixtures import data, structure, users
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

API_LOGIN_URL = f"{ALFRED_API_URL}/api/jwt/create/"
API_ME_URL = f"{ALFRED_API_URL}/api/me/"


class ApiMeResponse(structure.ApiPerson):
    model_config = ConfigDict(extra="forbid")


class ApiLoginResponse(structure.ApiLogin):
    model_config = ConfigDict(extra="forbid")


def test_api_me():
    login_request = requests.post(url=API_LOGIN_URL, data=users.rac_user)
    login_response = ApiLoginResponse(**login_request.json())

    assert login_request.status_code == HTTPStatus.OK

    headers = {"Authorization": f"Bearer {login_response.access}"}
    api_me_request = requests.get(url=API_ME_URL, headers=headers)
    api_me_response = ApiMeResponse(**api_me_request.json())

    assert api_me_request.status_code == HTTPStatus.OK
    assert api_me_response.first_name == data.person_RAC["first_name"]
    assert api_me_response.last_name == data.person_RAC["last_name"]
    assert api_me_response.middle_name == data.person_RAC["middle_name"]
    assert api_me_response.date_of_birth is None
    assert api_me_response.user.user_type == users.user_type_rac_user
    assert api_me_response.avatar.pic == data.avatar_RAC["pic"]
    assert api_me_response.contact.phone == "+49 30 3009090"
    assert api_me_response.contact.email is None
    assert api_me_response.contact.web is None
    assert (
        api_me_response.location.street_address
        == data.location_Helter_Skelter["street_address"]
    )
    assert (
        api_me_response.location.post_code == data.location_Helter_Skelter["post_code"]
    )
    assert api_me_response.location.city == data.location_Helter_Skelter["city"]
    assert api_me_response.location.country == data.location_Helter_Skelter["country"]
