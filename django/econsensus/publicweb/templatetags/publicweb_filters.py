from django import template

register = template.Library()

@register.filter
def get_item(dict, arg):
    """Dictionary lookup when your key is a string"""
    return dict.get(arg)

