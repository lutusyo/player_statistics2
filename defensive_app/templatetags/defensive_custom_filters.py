from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, '')



@register.filter
def sum_attr(queryset, attr):
    return sum(getattr(obj, attr, 0) or 0 for obj in queryset)
