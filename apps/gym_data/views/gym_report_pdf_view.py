from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from ..forms import GymReportFilterForm
from ..report_utils import (
    get_report_queryset,
    apply_report_filters,
    add_volume,
)


def gym_report_pdf(request):

    form = GymReportFilterForm(
        request.GET or None
    )

    queryset = get_report_queryset()

    queryset = apply_report_filters(
        queryset,
        form,
    )

    queryset = add_volume(queryset)

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="gym_report.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "GYM TRAINING REPORT",
            styles["Title"],
        )
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            "Group-based gym training data",
            styles["Normal"],
        )
    )

    story.append(
        Spacer(1, 12)
    )

    total_volume = sum(
        (
            item.volume or Decimal("0")
        )
        for item in queryset
    )

    story.append(
        Paragraph(
            f"Total Exercise Records: {queryset.count()}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Total Volume: {total_volume:.2f} kg",
            styles["Normal"],
        )
    )

    story.append(
        Spacer(1, 12)
    )

    data = [
        [
            "Date",
            "Team",
            "Gym Type",
            "Exercise",
            "Category",
            "Weight",
            "Sets",
            "Reps",
            "Volume",
        ]
    ]

    for item in queryset:

        data.append([
            item.gym_group.gym_session.date.strftime(
                "%d %b %Y"
            ),

            str(
                item.gym_group.gym_session.team
            ),

            str(
                item.gym_group.gym_type
            ),

            item.exercise.name,

            item.exercise.category.name,

            f"{item.weight_kg} kg",

            str(item.sets),

            str(item.reps),

            f"{item.volume:.2f} kg",
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            25 * mm,
            30 * mm,
            25 * mm,
            40 * mm,
            30 * mm,
            25 * mm,
            15 * mm,
            15 * mm,
            25 * mm,
        ],
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey,
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black,
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.3,
                colors.grey,
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                6,
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, 0),
                6,
            ),
        ])
    )

    story.append(table)

    document.build(story)

    return response