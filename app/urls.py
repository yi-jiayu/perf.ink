from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("<username>/shifts/", views.shifts_index, name="shifts_index"),
    path("<username>/rotations/", views.rotations_index, name="rotations_index"),
    path("<username>/shifts/<slug:shift_id>/", views.shifts_show, name="shifts_show"),
    path("<username>/statistics/", views.statistics_index, name="statistics_index"),
    path(
        "<username>/rotations/<int:rotation_id>",
        views.rotations_detail,
        name="rotations_detail",
    ),
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
