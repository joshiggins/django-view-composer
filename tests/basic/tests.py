from django.test import TestCase
from django.template import Context, Template
from django.test.client import RequestFactory
import jsonpickle


class ViewTagTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def get_with_context(self, template, context):
        request = self.factory.get("/")
        t = Template(template)
        c = Context({"request": request, **context})
        return t.render(c)

    def test_single_view(self):
        res = self.get_with_context(
            "{% load view_composer %}{% view 'basic.views.IndexView' %}", {}
        )
        self.assertEqual(res, "<h1>Test</h1>")

    def test_all_context(self):
        res = self.get_with_context(
            "{% load view_composer %}{% view 'basic.views.ContextTestView' %}",
            {"food": "spam"},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertEqual(test_ctx["food"], "spam")

    def test_no_context(self):
        res = self.get_with_context(
            "{% load view_composer %}{% view 'basic.views.ContextTestView' with only %}",
            {"food": "spam"},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertFalse("food" in test_ctx)

    def test_extra_context(self):
        res = self.get_with_context(
            "{% load view_composer %}"
            "{% view 'basic.views.ContextTestView' with food='spam' %}",
            {},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertEqual(test_ctx["food"], "spam")

    def test_extra_context_override(self):
        res = self.get_with_context(
            "{% load view_composer %}"
            "{% view 'basic.views.ContextTestView' with food='eggs' %}",
            {"food": "spam"},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertEqual(test_ctx["food"], "eggs")

    def test_extra_context_only(self):
        res = self.get_with_context(
            "{% load view_composer %}"
            "{% view 'basic.views.ContextTestView' with ham=1 only %}",
            {"food": "spam"},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertEqual(test_ctx["ham"], 1)
        self.assertFalse("food" in test_ctx)

    def test_extra_context_resolved(self):
        res = self.get_with_context(
            "{% load view_composer %}"
            "{% view 'basic.views.ContextTestView' with food=spam %}",
            {"spam": "eggs"},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertEqual(test_ctx["food"], "eggs")

    def test_block_view(self):
        res = self.get_with_context(
            "{% load view_composer %}"
            "{% viewblock 'basic.views.BlockTestView' %}"
            "   {% view 'basic.views.ContextTestView' %}"
            "{% endviewblock %}",
            {"food": "spam"},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertEqual(test_ctx["food"], "spam")

    def test_nested_block_views(self):
        res = self.get_with_context(
            "{% load view_composer %}"
            "{% viewblock 'basic.views.BlockTestView' %}"
            "   {% viewblock 'basic.views.BlockTestView' %}"
            "       {% viewblock 'basic.views.BlockTestView' %}"
            "           {% view 'basic.views.ContextTestView' %}"
            "       {% endviewblock %}"
            "   {% endviewblock %}"
            "{% endviewblock %}",
            {"food": "spam"},
        )
        test_ctx = jsonpickle.decode(res)
        self.assertEqual(test_ctx["food"], "spam")