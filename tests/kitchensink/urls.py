from django.urls import path

from . import views

app_name = "kitchensink"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("person-list", views.PersonListView.as_view(), name="person-list"),
    path("person-create", views.PersonCreateView.as_view(), name="person-create"),
    path("person-list-modal", views.PersonListViewWithModal.as_view(), name="person-list-modal"),
]