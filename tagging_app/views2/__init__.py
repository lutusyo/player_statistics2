# Import aggregation and query utilities from Django ORM
from django.db.models import Count, Q

# Import the render shortcut to render templates
from django.shortcuts import render

# Import the AttemptToGoal model and the DeliveryTypeChoices enumeration
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices


def delivery_summary_view(request, match_id):

    # 🔹 Step 1: Filter only our team's attempts (not opponent’s)
    # Using 'match_id' to get attempts for the specific match
    attempts = AttemptToGoal.objects.filter(match_id=match_id, is_opponent=False)

    # 🔹 Step 2: Group attempts by the player who made the assist (assist_by)
    # and by the type of delivery (e.g., Cross, Pass, Loose Ball)
    # Then count how many of each type per player using annotate(Count('id'))
    # Finally, order results alphabetically by player name
    delivery_summary = (
        attempts.values('assist_by__name', 'delivery_type')
        .annotate(total=Count('id'))
        .order_by('assist_by__name')
    )

    # 🔹 Step 3: Calculate the total number of each delivery type
    # across the whole team for the same match
    # (e.g., total crosses = 10, total passes = 20, etc.)
    total_delivery_types = (
        attempts.values('delivery_type')
        .annotate(total=Count('id'))
        .order_by('delivery_type')
    )

    # 🔹 Step 4: Prepare data to send to the template (context dictionary)
    # 'delivery_summary' → deliveries grouped by player and type
    # 'total_delivery_types' → overall totals for each delivery type
    # 'delivery_types' → all available delivery types defined in choices
    context = {
        'delivery_summary': delivery_summary,
        'total_delivery_types': total_delivery_types,
        'delivery_types': DeliveryTypeChoices.choices,
    }

    # 🔹 Step 5: Render the results using the 'delivery_summary.html' template
    # and pass the context so data can be displayed on the webpage
    return render(request, 'attempts/delivery_summary.html', context)


