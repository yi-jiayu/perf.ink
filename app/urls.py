from django.urls import path

from . import views

urlpatterns = [
    path("accounts/profile/", views.profile, name="profile"),
    path("accounts/nintendo_session/", views.nintendo_session, name="nintendo_session"),
    path("salmon_run/sync/", views.salmon_run_sync, name="salmon_run_sync"),
]
