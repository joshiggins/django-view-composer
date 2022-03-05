from django import template
from django.template.base import token_kwargs
from django.utils.module_loading import import_string
import itertools

register = template.Library()


def parse_view_tag(parser, token):
    # dict to hold parsed options from the tag
    options = {}

    # split and check args
    tag_name, *bits = token.split_contents()
    if len(bits) == 0:
        raise template.TemplateSyntaxError(
            "%r tag requires at least 1 argument (the view import string)" % tag_name
        )

    # parse view name
    view_name = bits[0]
    if view_name[0] == view_name[-1] and view_name[0] in ('"', "'"):
        # name is an import string
        options["view"] = import_string(view_name[1:-1])
    else:
        # resolve the view from context
        options["resolve_view"] = view_name

    # parse the with variables
    arg_group = [list(g) for _, g in itertools.groupby(bits, "with".__ne__)]
    if len(arg_group) == 3:
        if arg_group[2][-1] == "only":
            arg_group[2].pop()
            options["no_parent_ctx"] = True
        options["vars"] = token_kwargs(arg_group[2], parser)

    # kwargs for the view should preceed the 'with' bit
    arg_group[0].pop(0)
    if len(arg_group[0]) > 0:
        options["kwargs"] = token_kwargs(arg_group[0], parser)

    return options


@register.tag
def view(parser, token):
    options = parse_view_tag(parser, token)
    return ViewNode(options)


@register.tag
def viewblock(parser, token):
    options = parse_view_tag(parser, token)
    nodelist = parser.parse(("endviewblock",))
    parser.delete_first_token()
    return ViewNode(options, nodelist)


class ViewNode(template.Node):
    def __init__(self, options, nodelist=None):
        self.options = options
        self.nodelist = nodelist

    def render(self, context):
        # get the view from template tag options
        if "resolve_view" in self.options:
            # view needs to be resolved from the template context
            try:
                resolved = template.Variable(self.options["resolve_view"]).resolve(context)
                view_class = import_string(resolved)
            except:
                # finally try and import without string, e.g., unquoted module name
                view_class = import_string(self.options["resolve_view"])
        else:
            view_class = self.options["view"]

        # get the request object
        request = template.Variable("request").resolve(context)

        # this child view gets our context variables unless the template
        # tag specifies "with ..."
        child_context = {}
        if not "no_parent_ctx" in self.options:
            child_context = context.flatten()
            if "view" in child_context:
                del child_context["view"]
        if "vars" in self.options:
            for k in self.options["vars"]:
                child_context[k] = self.options["vars"][k].resolve(context)

        # resolve the kwargs
        resolved_kwargs = {}
        if "kwargs" in self.options:
            for k in self.options["kwargs"]:
                resolved_kwargs[k] = self.options["kwargs"][k].resolve(context)

        # render any nodes in the block first and add these to the child
        # view context
        if self.nodelist:
            child_context["children"] = self.nodelist.render(context)

        # render the view to a response
        instance = view_class(request=request, extra_context=child_context)

        # call setup on the view
        instance.setup(request, **resolved_kwargs)

        # if the view class has a compose method use that, otherwise
        # default to get method
        if hasattr(instance, "compose"):
            response = instance.compose(request, **resolved_kwargs)
        else:
            response = instance.get(request, **resolved_kwargs)

        # only render if there is something to render
        if hasattr(response, "render"):
            response.render()
            return response.content.decode()

        # any other response
        return ""
