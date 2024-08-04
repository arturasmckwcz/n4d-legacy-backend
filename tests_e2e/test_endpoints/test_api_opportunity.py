from http import HTTPStatus
from typing import List

import requests
from pydantic import BaseModel, ConfigDict

from tests_e2e.fixtures import data, structure, users
from tests_e2e.test_endpoints.variables import ALFRED_API_URL

API_LOGIN_URL = f"{ALFRED_API_URL}/api/jwt/create/"
API_ME_URL = f"{ALFRED_API_URL}/api/opportunity/"


class ApiOpportunityRespose(BaseModel):
    items: List[structure.ApiOpportunity]

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

    assert api_opportunity_response.organization.name == data.organization_RAC_name

    assert (
        api_opportunity_response.organization.location.title
        == data.location_Helter_Skelter["title"]
    )
    assert (
        api_opportunity_response.organization.location.street_address
        == data.location_Helter_Skelter["street_address"]
    )
    assert (
        api_opportunity_response.organization.location.post_code
        == data.location_Helter_Skelter["post_code"]
    )
    assert (
        api_opportunity_response.organization.location.city
        == data.location_Helter_Skelter["city"]
    )
    assert (
        api_opportunity_response.organization.location.country
        == data.location_Helter_Skelter["country"]
    )

    assert (
        api_opportunity_response.organization.contact.title
        == data.contact_Helter_Skelter["title"]
    )
    assert (
        api_opportunity_response.organization.contact.phone
        == data.contact_Helter_Skelter["phone"]
    )
    assert api_opportunity_response.organization.contact.email is None
    assert api_opportunity_response.organization.contact.web is None

    assert api_opportunity_response.organization.avatar.pic == data.avatar_RAC["pic"]

    api_organization_person = api_opportunity_response.organization.persons[0]  # type: ignore
    assert api_organization_person.first_name == data.person_RAC["first_name"]
    assert api_organization_person.last_name == data.person_RAC["last_name"]
    assert api_organization_person.middle_name is None
    assert api_organization_person.date_of_birth is None
    assert api_organization_person.avatar.pic == data.avatar_RAC["pic"]

    assert api_organization_person.user.email == users.rac_user["email"]
    assert api_organization_person.user.user_type == users.user_type_rac_user

    assert api_organization_person.contact.title == data.contact_RAC["title"]
    assert api_organization_person.contact.phone == data.contact_RAC["phone"]
    assert api_organization_person.contact.email is None
    assert api_organization_person.contact.web is None

    assert (
        api_organization_person.location.title == data.location_Helter_Skelter["title"]
    )
    assert (
        api_organization_person.location.street_address
        == data.location_Helter_Skelter["street_address"]
    )
    assert (
        api_organization_person.location.post_code
        == data.location_Helter_Skelter["post_code"]
    )
    assert api_organization_person.location.city == data.location_Helter_Skelter["city"]
    assert (
        api_organization_person.location.country
        == data.location_Helter_Skelter["country"]
    )
    assert api_organization_person.location.longitude is None
    assert api_organization_person.location.latitude is None

    api_opportunity_payload = api_opportunity_response.payloads[0]
    assert api_opportunity_payload.payload_type == data.payload_USSR["payload_type"]

    assert api_opportunity_payload.locations[0].title == data.locations[0]["title"]
    assert (
        api_opportunity_payload.locations[0].street_address
        == data.locations[0]["street_address"]
    )
    assert (
        api_opportunity_payload.locations[0].post_code == data.locations[0]["post_code"]
    )
    assert api_opportunity_payload.locations[0].city == data.locations[0]["city"]
    assert api_opportunity_payload.locations[0].country == data.locations[0]["country"]
    assert api_opportunity_payload.locations[0].latitude is None
    assert api_opportunity_payload.locations[0].longitude is None

    assert api_opportunity_payload.locations[1].title == data.locations[1]["title"]
    assert api_opportunity_payload.locations[1].street_address == ""
    assert api_opportunity_payload.locations[1].post_code == ""
    assert api_opportunity_payload.locations[1].city == ""
    assert api_opportunity_payload.locations[1].country == ""
    assert (
        api_opportunity_payload.locations[1].latitude == data.locations[1]["latitude"]
    )
    assert (
        api_opportunity_payload.locations[1].longitude == data.locations[1]["longitude"]
    )

    # for idx in range(len(api_opportunity_payload.timeslots)):
    #     assert (
    #         api_opportunity_payload.timeslots[idx].start == data.timeslots[idx]["start"]
    #     )

    for idx in range(len(api_opportunity_payload.activities)):
        assert (
            api_opportunity_payload.activities[idx].title
            == data.activities[idx]["title"]
        )
        assert api_opportunity_payload.activities[idx].description is None

    for idx in range(len(api_opportunity_payload.languages)):
        assert (
            api_opportunity_payload.languages[idx].iso_code
            == data.languages[idx]["iso_code"]
        )
        assert (
            api_opportunity_payload.languages[idx].level == data.languages[idx]["level"]
        )

    for idx in range(len(api_opportunity_payload.skills)):  # type: ignore
        assert (
            api_opportunity_payload.skills[idx].title  # type: ignore
            == data.skills[idx]["title"]
        )
        assert api_opportunity_payload.skills[idx].description is None  # type: ignore
