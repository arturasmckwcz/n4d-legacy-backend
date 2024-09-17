import structlog
from django.core.management.base import BaseCommand

from data.models import Opportunity

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Deletes all data from data_opportunity table."

    def handle(self, *args, **kwargs):
        Opportunity.objects.all().delete()

        logger.info(self.style.SUCCESS("Flushing opportunities completed!"))
