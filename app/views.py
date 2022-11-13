import httpx
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q, Max
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

import splatnet

from . import forms, models, services, tasks


@login_required
def shifts_index(request):
    summaries = list(
        models.SalmonRunShiftSummary.objects.filter(uploaded_by=request.user)
        .select_related("detail")
        .prefetch_related("players")
        .order_by("-played_at")[:50]
    )
    highest_grade_points = max(
        (summary.grade_points for summary in summaries), default=0
    )
    highest_hazard_level = max(
        (
            summary.detail.hazard_level
            for summary in summaries
            if hasattr(summary, "detail")
        ),
        default=0,
    )
    context = {
        "summaries": summaries,
        "highest_grade_points": highest_grade_points,
        "highest_hazard_level": highest_hazard_level,
    }
    return render(request, "app/shifts_index.html", context)


@login_required
def shifts_show(request, shift_id: str):
    try:
        detail = models.SalmonRunShiftDetailRaw.objects.get(
            shift_id=shift_id, uploaded_by=request.user
        )
        loading = False
    except models.SalmonRunShiftDetailRaw.DoesNotExist:
        detail = None
        loading = models.SalmonRunShiftSummaryRaw.objects.filter(
            shift_id=shift_id, uploaded_by=request.user
        ).exists()

    if detail is None and not loading:
        raise Http404()
    context = {
        "detail": detail,
        "loading": loading,
    }
    return render(request, "app/shifts_show.html", context)


@login_required
def profile(request):
    try:
        nintendo_session = models.NintendoSession.objects.get(user=request.user)
        nintendo_session_form = forms.NintendoSessionForm(
            initial={"token": nintendo_session.token}
        )
    except models.NintendoSession.DoesNotExist:
        nintendo_session_form = forms.NintendoSessionForm()

    try:
        splatnet_session = models.SplatnetSession.objects.get(user=request.user)
    except models.SplatnetSession.DoesNotExist:
        splatnet_session = None

    context = {
        "nintendo_session_form": nintendo_session_form,
        "splatnet_session": splatnet_session,
    }
    return render(request, "app/profile.html", context)


def new_nintendo_session(request):
    if request.method == "POST":
        form = forms.NintendoSessionRequestForm(request.POST)
        if not form.is_valid():
            return redirect("new_nintendo_session")
        verifier = request.session["verifier"]
        with httpx.Client() as client:
            token = splatnet.get_session_token(
                client, form.cleaned_data["url"], verifier
            )
        models.NintendoSession.objects.update_or_create(
            user=request.user, defaults={"token": token}
        )
        return redirect("profile")

    with httpx.Client() as client:
        verifier, nintendo_sign_in_url = splatnet.request_session_token(client)
    request.session["verifier"] = verifier
    context = {
        "nintendo_sign_in_url": nintendo_sign_in_url,
        "form": forms.NintendoSessionRequestForm(),
    }
    return render(request, "app/new_nintendo_session.html", context)


@login_required
def nintendo_session(request):
    form = forms.NintendoSessionForm(request.POST)

    if form.is_valid():
        token = form.cleaned_data["token"]
        models.NintendoSession.objects.update_or_create(
            user=request.user, defaults={"token": token}
        )

    return redirect("profile")


@login_required
def salmon_run_sync(request):
    if request.method == "POST":
        summaries = services.sync_salmon_run_shift_summaries(request.user)
        tasks.sync_salmon_run_shift_details.delay(
            request.user.id, [summary.splatnet_id for summary in summaries]
        )
    return redirect("shifts_index")


@login_required
def salmon_run_shift_detail(request, shift_id: str):
    detail = get_object_or_404(models.SalmonRunShiftDetailRaw, shift_id=shift_id)
    return render(request, "app/salmon_run_shift_detail.html", {"detail": detail})


@login_required
def statistics_index(request):
    shifts_all_time = models.SalmonRunShiftSummary.objects.filter(
        uploaded_by=request.user
    )
    waves_all_time = models.SalmonRunWave.objects.all()
    statistics_all_time = services.salmon_run_shift_statistics(
        shifts_all_time, waves_all_time
    )

    latest_rotation = models.SalmonRunShiftSummary.objects.latest("played_at").rotation
    shifts_latest_rotation = models.SalmonRunShiftSummary.objects.filter(
        uploaded_by=request.user, rotation=latest_rotation
    )
    waves_latest_rotation = models.SalmonRunWave.objects.filter(
        shift__rotation=latest_rotation
    )
    statistics_latest_rotation = services.salmon_run_shift_statistics(
        shifts_latest_rotation, waves_latest_rotation
    )

    context = {
        "all_time": statistics_all_time,
        "latest_rotation": statistics_latest_rotation,
    }
    return render(request, "app/statistics_index.html", context)


@login_required
def rotations_index(request):
    rotations = (
        models.SalmonRunRotation.objects.filter(
            shifts__isnull=False,
            shifts__uploaded_by=request.user,
            shifts__players__is_uploader=True,
        )
        .annotate(
            average_waves_cleared=Avg(
                "shifts__waves_cleared", filter=~Q(shifts__waves_cleared=-1)
            ),
            num_shifts=Count("shifts"),
            average_times_rescued=Avg("shifts__players__times_rescued"),
            highest_hazard_level=Max("shifts__detail__hazard_level"),
            highest_grade_points=Max("shifts__grade_points", filter=Q(shifts__grade='Eggsecutive VP')),
        )
        .order_by("-start_end_time")
    )
    context = {
        "rotations": rotations,
    }
    return render(request, "app/rotations_index.html", context)
