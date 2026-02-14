# tagging_app_v2/templatetags/dict_get.py
from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key)
