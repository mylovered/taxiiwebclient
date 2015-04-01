from django.core.management.base import BaseCommand, CommandError
from yeti_client.models import ReceivedFile, Event


class Command(BaseCommand):
    help = 'Cleans the Yeti Web Client database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ReceivedFile.objects.all().delete()
        Event.objects.all().delete()
