from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    return value - arg

# @register.filter
# def add(value, arg):
#     return value + arg