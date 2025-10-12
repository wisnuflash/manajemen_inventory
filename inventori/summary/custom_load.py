from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, arg):
    """
    Usage: {{ value|replace:"old,new" }}
    """
    old, new = arg.split(',')
    return value.replace(old, new)
