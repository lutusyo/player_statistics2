from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from players_app.models import Player
from teams_app.models import Team


def export_team_players_to_excel_view(request, team_id):
    # Get the team
    team = Team.objects.get(id=team_id)

    # Create a new Excel workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"{team.name} Players"

    # Define headers
    headers = [
        "NAME", "JNAME", "AGE GROUP", "BIRTHDATE",
        "POSITION", "HEIGHT (CM)", "WEIGHT (KG)",
        "FOOT PREFERENCE", "JERSEY NUMBER", "FORMER CLUB"
    ]

    # Styles
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")

    # Write headers
    ws.append(headers)
    for cell in ws[1]:  # First row
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    # Get players for the specific team
    players = Player.objects.filter(team=team).select_related("age_group")

    # Write player data rows
    for player in players:
        full_name = f"{player.name} {player.second_name} {player.surname}".upper()

        row = [
            full_name,
            (player.jina_maarufu or "").upper(),
            player.age_group.name.upper() if player.age_group else "",
            player.birthdate.strftime("%Y-%m-%d") if player.birthdate else "",
            (player.position or "").upper(),
            player.height or "",
            player.weight or "",
            (player.foot_preference or "").upper(),
            player.jersey_number or "",
            (player.former_club or "").upper(),
        ]

        ws.append(row)

    # Apply center alignment to all cells
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(headers)):
        for cell in row:
            cell.alignment = center_align

    # Adjust column widths for readability
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    # Prepare HTTP response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"{team.name.replace(' ', '_')}_PLAYERS.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Save workbook to response
    wb.save(response)
    return response
