# actions_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(list, index):
    try:
        return list[index]
    except:
        return None

@register.filter
def underscore_to_space(value):
    """Replace underscores with spaces and capitalize the first letter."""
    return value.replace('_', ' ').capitalize()



@register.filter(name='get_item_or')
def get_item_or(dictionary, key):
    return dictionary.get(key, {})

