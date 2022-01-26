# Django View Composer

Extending the Django template system so that you can include a view inside another view

- **Simple view composition** - based on template tags
- **Reusable components** - turn any class based view into a reusable component
- **Lightweight** - no framework, no core Javascript and no additional Python dependencies
- **Reactive, if you want** - integrates nicely with HTMX

```html+django
{% load view_composer %}

<nav>
   {% view 'myapp.views.NavBar' %}
</nav>

{% viewblock 'myapp.views.ListView' %}
   {% view 'myapp.views.ListFilter' %}
{% endviewblock %}
```

## Quick start

Django View Composer is released on PyPi so you can install using Pip:

```sh
pip install django-view-composer
```

or Poetry:

```sh
poetry install django-view-composer
```

Once installed, add to your `INSTALLED_APPS` setting to register the template tags:

```python
INSTALLED_APPS = [
    ...
    "django_view_composer",
    ...
]
```

## Using the `view` tag

The `{% view %}` tag renders a class based view and includes the content in the current template.

It has 1 required argument which is the import string for the view:

```html+django
{% load view_composer %}

{% view 'myapp.views.MyView' %}
```

You can also provide a variable for the import string which will be resolved from the current template's context:

```html+django
{% view view_to_render %}
```

### Context variables

Similar to the `{% include %}` tag which operates on templates, the included view will be provided with the same context variables from the current template it is being rendered into.

These are provided as extra, so they won't replace any context variables the child view might be setting itself.

If any context variable names conflict, whatever the child view sets in it's own `get_context_data` will take precedence.

You can pass additional context from the template tag:

```html+django
{% view 'myapp.views.MyView' with foo='bar' %}
```

Additional variables can be resolved from the current template's context to pass to the included view:

```html+django
{% view 'myapp.views.MyView' with foo=foo %}
```

### Use `only` to limit context

If you want to render the included view only with the variables provided (or even no variables at all), use the only option. No other variables will be provided to the included view.

```html+django
{% view 'myapp.views.MyView' with foo='bar' only %}
```

### View keyword arguments

If your view requires kwargs in the URL, such as a pattern like

```python
url_patterns = [
    path("item/<pk:pk>/edit", ItemEditView.as_view(), name="item-edit-view"),
]
```

you can supply these in the template tag directly after the import string and before the `with` keyword:

```html+django
{% view 'myapp.views.ItemEditView' pk=pk with extra_food="spam" %}
```

or without any extra context variables:

```html+django
{% view 'myapp.views.ItemEditView' pk=pk %}
```

> These kwargs are the ones passed to the view's `setup()`, not to the `__init__` method

## Using the `viewblock` tag

The `{% viewblock %}` tag renders a class based view and includes the content in the current template, but provides a block for additional nodes which are rendered first and made available in the included view’s context.

This tag must be closed with a corresponding endviewblock. It has 1 required argument which is the import string for the view:

```html+django
{% load view_composer %}

{% viewblock 'myapp.views.MyView' %}
    <h2>An excellent view!</h2>
{% endviewblock %}
```

In the template for the `myapp.views.MyView`, you can use the children context variable to decide where to render the block content:

```html+django
<div>
    {{ children }}
</div>
```

Context variables are supported in the same way as the `view` tag.
However, since the block content is rendered _before_ the included view, the additional nodes in the block can only access the current template's context - not the context of the view being included.

## Nesting views

Two different forms of nesting are possible

- you can put a `{% view %}` or a `{% viewblock %}` inside a `{% viewblock %}` in the same template
- you can include a view where its own template includes other views

Views are rendered in the order that the tags appear in the template.

A `{% viewblock %}` renders the block content _first_ and then renders the view being included.

## Handling POST views

Most of the time the views being composed will have GET handlers which return a template response.

One of the powerful features of view composition (compared to template includes) is the ability to bring in additional logic, such as including a view which handles a form.

However, included views are all rendered with the same HTTP request object which originates from the root view - the top most one which was handled by a URL pattern.

If you need to handle a different method in an included view, such as a child view that contains a form POST, you must

- map the included view to a URL pattern as well
- make the request to the view's direct URL, instead of the current URL, when it is submitted

Using the form as an example:

```python
from .views import ItemCreateView

app_name = "myapp"
url_patterns = [
    path("item/create", ItemCreateView.as_view(), name="item-create-view"),
]
```

```html+django
<form method="post" action="{% url 'myapp:item-create-view' %}">
    ...
</form>
```

Now you can include this view inside another one like `{% view 'myapp.views.ItemCreateView' %}` and when the form is POSTed it will send the request to the correct view.

### Modify view dispatch

In some cases you might need to modify how the view is dispatched so it works well when included inside another (or several levels of) view.

For example, the Django generic editing views usually return a redirect response. You might want to return another blank instance of the form in the response to a successful POST, or you might want to return a confirmation with an 'Add another' button to bring up a new form.

Django View Composer will not render anything if the view being included does not return a template response.

## Reactive

An important concept in the view composer is that _the same views can be included via a template tag or rendered normally via a URL pattern_. 

This provides a foundation for reactivity when coupled with [HTMX](https://htmx.org):

- **initial render of the page** - including views via template tags
- **reactive updates of individual views on a page** - calling the view's direct URL pattern and replacing the content in the page

Remember, the view composer is not a framework - its just a template tag that lets you render a view inside another view.
It does not fundamentally change the Django request lifecycle even if you choose to include some reactivity with HTMX.

## Running tests

There is a growing test suite which can be run 

```
$ poetry install
$ poetry shell
$ cd tests
$ ./manage.py test
```

## Contributing

Welcome!