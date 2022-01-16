import random

from django.db import transaction
from django.core.management.base import BaseCommand

from kitchensink.models import Person
from kitchensink.factories import PersonFactory

class Command(BaseCommand):
    help = "Generates test data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        Person.objects.all().delete()

        for _ in range(50):
            person = PersonFactory()
