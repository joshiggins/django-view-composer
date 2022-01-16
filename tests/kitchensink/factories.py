import factory
from factory.django import DjangoModelFactory
from .models import Person


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")