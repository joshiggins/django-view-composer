from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import Person


class Index(TemplateView):
    template_name = "kitchensink/index.html"


class PersonListView(ListView):
    model = Person


class PersonCreateView(CreateView):
    model = Person
    fields = ["first_name", "last_name"]
    success_url = reverse_lazy("kitchensink:person-list")