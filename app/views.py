import httpx
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

import splatnet

from . import forms, models, services, tasks


@login_required
def shifts_index(request):
    summaries = list(
        models.SalmonRunShiftSummaryRaw.objects.filter(
            uploaded_by=request.user
        ).order_by("-uploaded_at")[:50]
    )
    highest_grade_points = max(summary.grade_points for summary in summaries)
    context = {
        "summaries": summaries,
        "highest_grade_points": highest_grade_points,
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

    shifts = []
    summaries = list(
        models.SalmonRunShiftSummaryRaw.objects.filter(
            uploaded_by=request.user
        ).order_by("-uploaded_at")[:50]
    )
    details = {
        detail.shift_id: detail
        for detail in models.SalmonRunShiftDetailRaw.objects.filter(
            shift_id__in=[summary.shift_id for summary in summaries]
        )
    }
    for summary in summaries:
        data = {
            "id": summary.data["id"],
            "rank": summary.data["afterGrade"]["name"],
            "points": summary.data["afterGradePoint"],
            "change": summary.data["gradePointDiff"],
        }
        if detail := details.get(summary.shift_id):
            data["detail"] = {
                "hazard_level": detail.hazard_level,
                "boss_count_individual": detail.boss_count_individual,
                "boss_count_team": detail.boss_count_team,
                "boss_count_percent": detail.boss_count_percent,
                "rescued_count_individual": detail.rescued_count_individual,
                "rescued_count_team": detail.rescued_count_team,
            }
        shifts.append(data)

    context = {
        "nintendo_session_form": nintendo_session_form,
        "splatnet_session": splatnet_session,
        "shifts": shifts,
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
    summaries = services.sync_salmon_run_shift_summaries(request.user)
    tasks.sync_salmon_run_shift_details.delay(
        request.user.id, [summary.id for summary in summaries]
    )
    return redirect("shifts_index")


@login_required
def salmon_run_shift_detail(request, shift_id: str):
    detail = get_object_or_404(models.SalmonRunShiftDetailRaw, shift_id=shift_id)
    return render(request, "app/salmon_run_shift_detail.html", {"detail": detail})
