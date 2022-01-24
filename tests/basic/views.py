from django.views.generic.base import TemplateView
import jsonpickle


class IndexView(TemplateView):
    template_name = "basic/index.html"


class ContextTestView(TemplateView):
    template_name = "basic/context.html"

    def get_context_json(self):
        context = self.get_context_data(**self.kwargs)
        return jsonpickle.encode(context)


class BlockTestView(TemplateView):
    template_name = "basic/block.html"


class KwargsTestView(ContextTestView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["food_kwarg"] = kwargs["food"]
        return context