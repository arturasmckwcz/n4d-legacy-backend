from datetime import datetime
from typing import List, Optional, TypeAlias

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


class ApiSkill(BaseModel):
    title: str
    description: Optional[str | None]


class ApiLanguage(BaseModel):
    title: str
    iso_code: str


class ApiTimeslot(BaseModel):
    start: Optional[datetime]
    end: Optional[datetime]
    recurrence: Optional[str | None]


class ApiOpportunity(BaseModel):
    title: str
    organization: ApiOrganization
    berlin_locations: List[ApiLocation]
    timeslots: List[ApiTimeslot]
    activities: List[ApiActivity]
    languages: List[ApiLanguage]
    skills: Optional[List[ApiSkill]]
    status: str
    opportunity_type: str


class ApiOpportunityFlattered(BaseModel):
    id: int
    title: str
    status: str
    berlin_locations: Optional[list]
    schedule_str: Optional[str]
    activities: Optional[list]
    languages: Optional[list]
    skills: Optional[list]
    vo_information: Optional[str]
    opportunity_type: str


ScheduleItem: TypeAlias = tuple[int, str]


class VolunteerFormData(BaseModel):
    schedule: list[ScheduleItem]
    preferred_berlin_locations: list[str]
    activities: list[str]
    full_name: str
    phone: str
    email: str
    postal_code: int
    if_good_conduct_certificate: bool
    if_measles_vaccination: bool
    skills: list[str]
    comments: Optional[str] = None
    native_languages: list[str]
    fluent_languages: Optional[list[str]] = None
    intermediate_languages: Optional[list[str]]
    origin_opportunity: Optional[str] = None
    lead_from: str


class Organization(BaseModel):
    name: str


class BerlinLocation(BaseModel):
    name: str


class Timeslot(BaseModel):
    title: str
    start: Optional[str] = None
    end: Optional[str] = None
    recurrence: Optional[str] = None


class Activity(BaseModel):
    title: str
    description: Optional[str] = None


class Opportunity(BaseModel):
    title: str
    organization: Organization
    berlin_locations: List[BerlinLocation]
    timeslots: List[Timeslot]
    activities: List[Activity]
    languages: List[str] = []
    skills: List[str] = []
    status: str
    vo_information: str
    opportunity_type: str
