from django.contrib import admin
from django.db import models

from version1.reports_app.models.previous_models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "competition_type",
        "venue",
        "home_team",
        "home_score",
        "away_team",
        "away_score",
        "our_team",
        "result",
    )

    list_filter = (
        "competition_type",
        "home_team",
        "away_team",
        "our_team",
        "result",
    )

    search_fields = (
        "home_team__name",
        "away_team__name",
        "competition_type",
        "venue",
    )

    date_hierarchy = "date"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "date",
                    "venue",
                    "competition_type",
                    "home_team",
                    "away_team",
                    ("home_score", "away_score"),
                    "our_team",
                    "goal_scorers",
                    "notes",
                ),
            },
        ),
    )

    formfield_overrides = {
        models.TextField: {
            "widget": admin.widgets.AdminTextareaWidget(
                attrs={
                    "rows": 4,
                    "cols": 50,
                }
            )
        },
    }