# Import aggregation and query utilities from Django ORM
from django.db.models import Count, Q
# Import the render shortcut to render templates
from django.shortcuts import render, get_object_or_404
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices
from matches_app.models import Match


def delivery_summary_view(request, match_id):

    attempts = AttemptToGoal.objects.filter(match_id=match_id, is_opponent=False)

    # Group by player and delivery type
    delivery_summary = (attempts.values('assist_by__name', 'delivery_type')
        .annotate(total=Count('id'))
        .order_by('assist_by__name')
    )

    # Convert queryset into a nested dictionary:
    # { "Player 1": {"cross": 2, "corner": 1, ...}, ... }
    summary_dict = {}
    for item in delivery_summary:
        player = item['assist_by__name'] or 'Unknown'
        dtype = item['delivery_type']
        total = item['total']
        if player not in summary_dict:
            summary_dict[player] = {}
        summary_dict[player][dtype] = total

    # Get totals for each delivery type
    total_delivery_types = (
        attempts.values('delivery_type')
        .annotate(total=Count('id'))
        .order_by('delivery_type')
    )

    context = {
        'summary_dict': summary_dict,
        'total_delivery_types': total_delivery_types,
        'delivery_types': DeliveryTypeChoices.choices,
    }

    return render(request, 'tagging_app/output/delivery_types.html', context)







