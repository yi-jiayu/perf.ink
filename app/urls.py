from django.urls import path

from . import views

urlpatterns = [
    path("accounts/profile/", views.profile, name="profile"),
    path("accounts/nintendo_session/", views.nintendo_session, name="nintendo_session"),
    path("salmon_run/sync/", views.salmon_run_sync, name="salmon_run_sync"),
    path(
        "accounts/nintendo_session/new/",
        views.new_nintendo_session,
        name="new_nintendo_session",
    ),
    path(
        "salmon_run/<slug:shift_id>/",
        views.salmon_run_shift_detail,
        name="salmon_run_shift_detail",
    ),
]
