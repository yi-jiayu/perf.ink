from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from . import forms, models, services


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
    for shift in models.SalmonRunShiftSummaryRaw.objects.filter(
        uploaded_by=request.user
    ).order_by("-uploaded_at"):
        data = shift.data
        shifts.append(
            {
                "rank": data["afterGrade"]["name"],
                "points": data["afterGradePoint"],
                "change": data["gradePointDiff"],
            }
        )

    context = {
        "nintendo_session_form": nintendo_session_form,
        "splatnet_session": splatnet_session,
        "shifts": shifts,
    }
    return render(request, "app/profile.html", context)


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
    services.sync_salmon_run_shifts(request.user)
    return redirect("profile")
