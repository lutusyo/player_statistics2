import csv
import random
from django.http import HttpResponse
from tagging_app.models import AttemptToGoal
from tagging_app.utils.coords_config import LOCATION_COORDS


def random_xy(location):
    area = LOCATION_COORDS.get(location, LOCATION_COORDS["Other"])
    x = round(random.uniform(area["x"][0], area["x"][1]), 2)
    y = round(random.uniform(area["y"][0], area["y"][1]), 2)
    return x, y


def download_attempts_csv(request, match_id, team_type):
    # team_type = "our" or "opponent"

    if team_type == "our":
        attempts = AttemptToGoal.objects.filter(
            match_id=match_id,
            team__team_type="OUR_TEAM"
        )
        filename = f"attempts_our_team_match_{match_id}.csv"

    elif team_type == "opponent":
        attempts = AttemptToGoal.objects.filter(
            match_id=match_id,
            team__team_type="OPPONENT"
        )
        filename = f"attempts_opponent_team_match_{match_id}.csv"

    else:
        return HttpResponse("Invalid team type", status=400)

    # Create CSV
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["minute", "second", "team", "x", "y", "outcome", "choice", "player_name"])

    for obj in attempts:
        x, y = random_xy(obj.location_tag)

        writer.writerow([
            obj.minute,
            obj.second,
            obj.team.name,
            x,
            y,
            obj.outcome,
            obj.delivery_type,
            obj.player.name if obj.player else "Unknown",
        ])

    return response
