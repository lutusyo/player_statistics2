from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError, transaction

from teams_app.models import StaffMember
from players_app.models import Player
from matches_app.models import Match
from perfomance_rating_app.models import StaffPlayerRating, RatingToken, PerformanceRating
from perfomance_rating_app.forms import SingleRatingForm
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count

from django.template.loader import render_to_string
from django.utils.html import strip_tags



def send_rating_links(request, match_id):
    """
    Sends a one-time HTML rating link email to all staff for the match.
    If a link was already used, it is NOT resent.
    """
    match = get_object_or_404(Match, id=match_id)

    staff_list = StaffMember.objects.filter(
        age_group=match.home_team.age_group
    )

    expires_at = timezone.now() + timezone.timedelta(hours=48)

    sent, skipped = [], []

    for staff in staff_list:

        token, created = RatingToken.objects.get_or_create(
            staff=staff,
            match=match,
            defaults={"expires_at": expires_at}
        )

        # 🚫 If token already used → DO NOT resend
        if token.used:
            skipped.append(staff)
            continue

        # ♻ If token exists but expired → refresh it
        if token.is_expired():
            token.refresh(expires_at=expires_at)

        rating_link = request.build_absolute_uri(
            reverse(
                "performance_rating_app:staff_rate_with_token",
                args=[str(token.token)]
            )
        )

        context = {
            "staff_name": staff.name,
            "match": match,
            "rating_link": rating_link,
            "year": timezone.now().year,
        }

        html_message = render_to_string(
            "emails/rating_request.html", context
        )
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=f"Player Rating Request — {match}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[staff.email],
                html_message=html_message,
                fail_silently=False,
            )
            sent.append(staff)

        except Exception as e:
            print("Email error:", e)

    # ✅ Mark match once links are sent
    match.rating_links_sent = True
    match.save()

    return render(
        request,
        "performance_rating_app/links_sent.html",
        {
            "match": match,
            "sent": sent,
            "skipped": skipped,
        },
    )




@require_http_methods(["GET", "POST"])
def staff_rate_with_token(request, token_uuid):
    """
    Staff arrives via unique token link. They rate all players of the match on the page
    (one overall rating per player) and submit. Token is single-use.
    """
    token = get_object_or_404(RatingToken, token=token_uuid)
    # validate
    if not token.is_valid():
        return render(request, "performance_rating_app/token_invalid.html", {"token": token})

    match = token.match
    staff = token.staff

    # players participating in match (home + away)
    players = (match.home_team.players.all() | match.away_team.players.all()).distinct()

    # Build existing ratings map or create blank objects
    existing = StaffPlayerRating.objects.filter(match=match, staff=staff).select_related("player")
    existing_map = {r.player_id: r for r in existing}

    # For GET show form fields
    if request.method == "GET":
        forms = []
        for p in players:
            rating_obj = existing_map.get(p.id)
            if rating_obj:
                form = SingleRatingForm(instance=rating_obj, prefix=str(p.id))
            else:
                # create an unsaved instance for initial form
                form = SingleRatingForm(prefix=str(p.id), initial={})
                form.instance = StaffPlayerRating(staff=staff, match=match, player=p)
            forms.append((p, form))
        return render(request, "performance_rating_app/staff_rate_page.html", {"match": match, "staff": staff, "forms": forms})

    # POST: validate and save all submitted ratings atomically
    if request.method == "POST":
        forms = []
        all_valid = True
        for p in players:
            prefix = str(p.id)
            # determine whether an existing instance exists
            instance = existing_map.get(p.id, StaffPlayerRating(staff=staff, match=match, player=p))
            form = SingleRatingForm(request.POST, instance=instance, prefix=prefix)
            forms.append((p, form))
            if not form.is_valid():
                all_valid = False

        if not all_valid:
            return render(request, "performance_rating_app/staff_rate_page.html", {"match": match, "staff": staff, "forms": forms})

        # Save all forms atomically
        try:
            with transaction.atomic():
                for p, form in forms:
                    rating_obj = form.save(commit=False)
                    rating_obj.staff = staff
                    rating_obj.match = match
                    rating_obj.player = p
                    rating_obj.save()
                # mark token used
                token.mark_used()
        except IntegrityError:
            # This can happen if unique_together violated (concurrent)
            return render(request, "performance_rating_app/error.html", {"msg": "Could not save ratings. Try again."})

        return render(request, "performance_rating_app/thank_you.html", {"match": match, "staff": staff})
    



def match_staff_aggregates(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    qs = StaffPlayerRating.objects.filter(match=match)
    aggregates = qs.values("player__id", "player__name").annotate(
        avg_rating=Avg("rating"),
        count=Count("id")
    ).order_by("-avg_rating")



    # inside some view
    #staff_avg = StaffPlayerRating.objects.filter(match=match, player=player).aggregate(avg=Avg("rating"))["avg"] or None
    #computed_rating = PerformanceRating.objects.filter(match=match, player=player).first()
    #computed_overall = computed_rating.overall() if computed_rating else None

    # combine (example weight: 60% computed, 40% staff)
    #if staff_avg is not None and computed_overall is not None:
    #    final = round((computed_overall * 0.6) + (staff_avg * 0.4), 2)
    #elif staff_avg is not None:
    #    final = staff_avg
    #else:
    #final = computed_overall



    return render(request, "performance_rating_app/match_aggregates.html", {"match": match, "aggregates": aggregates})






