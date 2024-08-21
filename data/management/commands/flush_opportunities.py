import structlog
from django.core.management.base import BaseCommand

from data.models import Opportunity

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Deletes data from tables that used for e2e."

    def handle(self, *args, **kwargs):
        Opportunity.objects.all().delete()

        logger.info(self.style.SUCCESS("Flushing opportunities completed!"))
