from django.core.management.base import BaseCommand

from data.fixtures.generate_data import load_opportunities


class Command(BaseCommand):
    help = "Load opportunities for test data"

    def handle(self, *args, **options):
        load_opportunities()
