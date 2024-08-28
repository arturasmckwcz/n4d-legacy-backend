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
    Person,
    Skill,
    TargetGroup,
    Timeslot,
)
from users.models import AlfredUser

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Deletes data from tables that used for e2e."

    def handle(self, *args, **kwargs):
        AlfredUser.objects.all().delete()
        Location.objects.all().delete()
        Contact.objects.all().delete()
        Language.objects.all().delete()
        Activity.objects.all().delete()
        TargetGroup.objects.all().delete()
        Skill.objects.all().delete()
        Timeslot.objects.all().delete()
        Organization.objects.all().delete()
        Person.objects.all().delete()
        Opportunity.objects.all().delete()
        Avatar.objects.all().delete()

        logger.info(self.style.SUCCESS("Clearing database completed!"))
