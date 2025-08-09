from django import template

register = template.Library()

@register.filter
def get_item_or(dictionary, key):
    # Returns dictionary[key] if exists, else empty dict or default
    return dictionary.get(key, {})

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)

