from django.views.generic.base import TemplateView


class Index(TemplateView):
    template_name = "example/index.html"


class Navigation(TemplateView):
    template_name = "example/nav.html"