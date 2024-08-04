import structlog
from django.core.management.base import BaseCommand

from data.models import (
    Activity,
    Avatar,
    Contact,
    Language,
    Location,
    Opportunity,
    Organization,
    Payload,
    Person,
    Skill,
    TargetGroup,
    Timeslot,
)
from tests_e2e.fixtures import data, users
from users.models import AlfredUser

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Seeds database with sample data for testing and development."

    def handle(self, *args, **kwargs):
        if (
            AlfredUser.objects.count()
            or Contact.objects.count()
            or Location.objects.count()
            or Avatar.objects.count()
            or Person.objects.count()
            or Organization.objects.count()
        ):
            logger.error(self.style.ERROR("Seeding failed! Database is not empty"))
        else:
            superuser = AlfredUser.objects.create_superuser(  # pyright: ignore
                **users.superuser
            )
            superuser.save()

            user = AlfredUser.objects.create_user(**users.rac_user)  # pyright: ignore
            user.active = True
            user.user_type = users.user_type_rac_user
            user.save()

            location_Helter_Skelter = Location(**data.location_Helter_Skelter)
            location_Helter_Skelter.save()

            contact_RAC = Contact(**data.contact_RAC)
            contact_RAC.save()

            avatar_RAC = Avatar(**data.avatar_RAC)
            avatar_RAC.save()

            person_RAC = Person(
                user=user,
                **data.person_RAC,
                location=location_Helter_Skelter,
                contact=contact_RAC,
                avatar=avatar_RAC,
            )

            contact_Helter_Skelter = Contact(**data.contact_Helter_Skelter)
            contact_Helter_Skelter.save()

            avatar_Helter_Skelter = Avatar(**data.avatar_RAC)
            avatar_Helter_Skelter.save()

            organization_RAC = Organization(
                name=data.organization_RAC_name,
                contact=contact_Helter_Skelter,
                location=location_Helter_Skelter,
                avatar=avatar_Helter_Skelter,
            )

            person_RAC.save()
            organization_RAC.save()

            person_RAC.organizations.add(organization_RAC)
            organization_RAC.persons.add(person_RAC)

            person_RAC.save()
            organization_RAC.save()

            payload_USSR = Payload(**data.payload_USSR)
            payload_USSR.save()

            for timeslot in data.timeslots:
                timeslot = Timeslot(**timeslot)
                timeslot.save()
                payload_USSR.timeslots.add(timeslot)

            for location in data.locations:
                location = Location(**location)
                location.save()
                payload_USSR.locations.add(location)

            for location in data.activities:
                location = Activity(**location)
                location.save()
                payload_USSR.activities.add(location)

            for language in data.languages:
                language = Language(**language)
                language.save()
                payload_USSR.languages.add(language)

            for skill in data.skills:
                skill = Skill(**skill)
                skill.save()
                payload_USSR.skills.add(skill)

            opportunity_USSR = Opportunity(
                **data.opportunity, organization=organization_RAC
            )
            opportunity_USSR.save()

            for target_group in data.target_groups:
                target_group = TargetGroup(**target_group)
                target_group.save()
                opportunity_USSR.target_groups.add(target_group)

            opportunity_USSR.payloads.add(payload_USSR)

            opportunity_USSR.save()
            payload_USSR.save()

            logger.info(self.style.SUCCESS("Seeding database completed!"))
