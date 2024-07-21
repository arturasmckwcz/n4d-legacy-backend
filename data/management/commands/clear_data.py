import structlog
from django.core.management.base import BaseCommand

from data.models import Avatar, Contact, Location, Organization, Person
from users.models import AlfredUser

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Deletes data from tables that used for e2e."

    def handle(self, *args, **kwargs):
        AlfredUser.objects.all().delete()
        Location.objects.all().delete()
        Contact.objects.all().delete()
        Organization.objects.all().delete()
        Person.objects.all().delete()
        Avatar.objects.all().delete()

        logger.info(self.style.SUCCESS("Clearing database completed!"))
