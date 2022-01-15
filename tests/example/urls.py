from django.urls import path

from . import views

app_name = "example"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("basic", views.BasicFunctionalityView.as_view(), name="basic"),
]
