
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from apps.individual_data.forms import (
    TrainingSessionForm,
    SessionTopicForm,
    PlayerParticipationForm,
    PlayerInterventionForm,
    SessionEvaluationForm,
    InterventionCoachingPointForm
)
from apps.individual_data.models.data_collection import (
    TrainingSession,
    SessionTopic,
    PlayerParticipation,
    PlayerIntervention,
    SessionEvaluation,
    TrainingObjective,
    PlayerInterventionCoachingPoint
)






def session_list(request):
    sessions = TrainingSession.objects.select_related(
        "age_group", "team", "coach"
    ).order_by("-date", "-created_at")

    return render(
        request, "individual_data/session_list.html",
        {"sessions": sessions},
    )


def session_create(request):
    form = TrainingSessionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        session = form.save()
        messages.success(request, "Training session created.")
        return redirect(
            "individual_training:session_detail", session_id=session.pk
        )

    return render(
        request, "individual_data/session_form.html", {"form": form}
    )


def session_detail(request, session_id):
    session = get_object_or_404(
        TrainingSession.objects.select_related("age_group", "team", "coach"),
        pk=session_id,
    )

    topics = session.session_topics.select_related(
        "topic", "objective"
    ).order_by("order", "id")

    participations = session.player_participations.select_related(
        "player"
    ).prefetch_related(
        "interventions__session_topic__topic",
        "interventions__session_topic__objective",
    )

    participations = session.player_participations.select_related(
        "player"
    ).prefetch_related(
        "interventions__session_topic__topic",
        "interventions__session_topic__objective",
        "interventions__coaching_points__coaching_point",
    )

    player_rows = []

    for participation in participations:
        intervention_rows = []

        for intervention in participation.interventions.all():
            coaching_point_form = InterventionCoachingPointForm(
                objective=intervention.session_topic.objective,
                position=participation.position,
            )

            intervention_rows.append({
                "intervention": intervention,
                "coaching_point_form": coaching_point_form,
            })

        player_rows.append({
            "participation": participation,
            "intervention_form": PlayerInterventionForm(session=session),
            "intervention_rows": intervention_rows,
        })

    try:
        evaluation = session.evaluation
    except SessionEvaluation.DoesNotExist:
        evaluation = None

    context = {
        "session": session,
        "topics": topics,
        "participations": participations,
        "player_rows": player_rows,
        "topic_form": SessionTopicForm(),
        "participation_form": PlayerParticipationForm(
            age_group=session.age_group
        ),
        "evaluation": evaluation,
        "evaluation_form": SessionEvaluationForm(instance=evaluation),
    }

    return render(
        request, "individual_data/session_detail.html", context
    )


def _session_redirect(session):
    return redirect(
        "individual_training:session_detail", session_id=session.pk
    )


@require_POST
def add_session_topic(request, session_id):
    session = get_object_or_404(TrainingSession, pk=session_id)
    form = SessionTopicForm(request.POST)

    if form.is_valid():
        item = form.save(commit=False)
        item.session = session

        try:
            item.full_clean()
            item.save()
            messages.success(request, "Topic added to the session.")
        except (ValidationError, IntegrityError) as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, "Please check the selected topic and objective.")

    return _session_redirect(session)


@require_POST
def add_participation(request, session_id):
    session = get_object_or_404(TrainingSession, pk=session_id)
    form = PlayerParticipationForm(
        request.POST, age_group=session.age_group
    )

    if form.is_valid():
        item = form.save(commit=False)
        item.session = session

        try:
            item.full_clean()
            item.save()
            messages.success(request, "Player participation recorded.")
        except (ValidationError, IntegrityError) as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, "Please check the player information.")

    return _session_redirect(session)


@require_POST
def add_intervention(request, session_id, participation_id):
    session = get_object_or_404(TrainingSession, pk=session_id)
    participation = get_object_or_404(
        PlayerParticipation, pk=participation_id, session=session
    )

    form = PlayerInterventionForm(request.POST, session=session)

    if form.is_valid():
        item = form.save(commit=False)
        item.player_participation = participation

        try:
            item.full_clean()
            item.save()
            messages.success(request, "Player intervention recorded.")
        except (ValidationError, IntegrityError) as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, "Please check the intervention details.")

    return _session_redirect(session)


@require_POST
def save_evaluation(request, session_id):
    session = get_object_or_404(TrainingSession, pk=session_id)
    evaluation, _ = SessionEvaluation.objects.get_or_create(session=session)
    form = SessionEvaluationForm(request.POST, instance=evaluation)

    if form.is_valid():
        form.save()
        messages.success(request, "Session evaluation saved.")
    else:
        messages.error(request, "Please check the evaluation details.")

    return _session_redirect(session)


@require_GET
def objectives_by_topic(request):
    topic_id = request.GET.get("topic_id")
    objectives = TrainingObjective.objects.none()

    if topic_id and topic_id.isdigit():
        objectives = TrainingObjective.objects.filter(
            topic_id=topic_id, is_active=True
        ).order_by("order", "name")

    return JsonResponse({
        "objectives": [
            {"id": obj.pk, "name": obj.name}
            for obj in objectives
        ]
    })





@require_POST
def add_intervention_coaching_point(
    request, session_id, intervention_id
):
    session = get_object_or_404(
        TrainingSession,
        pk=session_id,
    )

    intervention = get_object_or_404(
        PlayerIntervention,
        pk=intervention_id,
        player_participation__session=session,
    )

    objective = intervention.session_topic.objective
    position = intervention.player_participation.position

    form = InterventionCoachingPointForm(
        request.POST,
        objective=objective,
        position=position,
    )

    if form.is_valid():
        selection = form.save(commit=False)
        selection.intervention = intervention

        try:
            selection.full_clean()
            selection.save()
            messages.success(request, "Coaching point added.")
        except Exception as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, "Please select a valid coaching point.")

    return redirect(
        "individual_training:session_detail",
        session_id=session.id,
    )
