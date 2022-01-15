from django.views.generic.base import TemplateView


class Index(TemplateView):
    template_name = "example/index.html"


class Navigation(TemplateView):
    template_name = "example/nav.html"


class TestView(TemplateView):
    template_name = "example/test.html"


class BasicFunctionalityView(TemplateView):
    template_name = "example/basic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["test_view_str"] = 'example.views.TestView'
        return context