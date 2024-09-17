import structlog
from django.core.management.base import BaseCommand

from data.models import Language

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Deletes all data from data_language table."

    def handle(self, *args, **kwargs):
        Language.objects.all().delete()

        logger.info(self.style.SUCCESS("Flushing languages completed!"))
