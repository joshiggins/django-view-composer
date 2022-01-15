from django import template
from django.utils.module_loading import import_string

register = template.Library()


def parse_view_tag(parser, token):
    try:
        tag_name, view_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )
    if not (view_name[0] == view_name[-1] and view_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )
    return view_name[1:-1]


@register.tag
def view(parser, token):
    view_name = parse_view_tag(parser, token)
    return ViewNode(None, view_name)


@register.tag
def viewblock(parser, token):
    view_name = parse_view_tag(parser, token)
    nodelist = parser.parse(("endviewblock",))
    parser.delete_first_token()
    return ViewNode(nodelist, view_name)


class ViewNode(template.Node):
    def __init__(self, view_name, nodelist=None):
        self.nodelist = nodelist
        self.view_class = import_string(view_name)
        self.view_name = view_name
        self.request = template.Variable("request")

    def render(self, context):
        # the child view gets our context variables
        child_context = context.flatten()
        del child_context["view"]
        # render any nodes in the block first
        if self.nodelist:
            child_context["children"] = self.nodelist.render(context)
        # render it to a response
        request = self.request.resolve(context)
        instance = self.view_class(request=request, extra_context=child_context)
        # if the view class has as_view method use that, otherwise
        # default to get
        if hasattr(instance, "as_view"):
            response = instance.as_view(request)
        else:
            response = instance.get(request)
        # only render if there is something to render
        if hasattr(response, "render"):
            response.render()
            return response.content.decode()
        # any other response
        return ""
