from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ApiLogin(BaseModel):
    access: str
    refresh: str


class ApiUser(BaseModel):
    email: str
    user_type: str


class ApiAvatar(BaseModel):
    pic: str


class ApiContact(BaseModel):
    title: str
    phone: str | None
    email: str | None
    web: str | None


class ApiLocation(BaseModel):
    title: Optional[str | None]
    street_address: Optional[str | None]
    post_code: Optional[str | None]
    city: Optional[str | None]
    country: Optional[str | None]
    latitude: Optional[float | None]
    longitude: Optional[float | None]


class ApiPerson(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str | None]
    name: str
    date_of_birth: Optional[str | None]
    user: ApiUser
    location: ApiLocation
    contact: ApiContact
    avatar: ApiAvatar


class ApiOrganization(BaseModel):
    name: str
    location: ApiLocation
    contact: ApiContact
    avatar: ApiAvatar
    persons: Optional[List[ApiPerson]]


class ApiActivity(BaseModel):
    title: str
    description: Optional[str | None]


class ApiTargetGroup(BaseModel):
    title: str
    description: Optional[str | None]


class ApiSkill(BaseModel):
    title: str
    description: Optional[str | None]


class ApiLanguage(BaseModel):
    title: str
    iso_code: str
    level: str


class ApiTimeslot(BaseModel):
    start: Optional[datetime]
    end: Optional[datetime]
    recurrence: Optional[str | None]


class ApiOpportunity(BaseModel):
    title: str
    organization: ApiOrganization
    target_groups: List[ApiTargetGroup]
    locations: List[ApiLocation]
    timeslots: List[ApiTimeslot]
    activities: List[ApiActivity]
    languages: List[ApiLanguage]
    skills: Optional[List[ApiSkill]]
    status: str


class ApiOpportunityFlattered(BaseModel):
    title: str
    status: str
    target_groups: list
    locations: list
    timeslots: list
    activities: list
    languages: list
    skills: Optional[list]
