from django import template

register = template.Library()


@register.simple_tag
def match_exists(past_matches, team, competition):
    """
    Returns True if a match exists for a given team & competition
    """

    if not hasattr(past_matches, "filter"):
        return False

    return past_matches.filter(
        team=team,
        competition=competition
    ).exists()
