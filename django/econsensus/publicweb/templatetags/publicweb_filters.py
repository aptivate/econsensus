from django import template

from publicweb.models import Feedback

register = template.Library()

@register.filter
def get_item(dict, arg):
    """Dictionary lookup when your key is a string"""
    return dict.get(arg)

@register.filter
def get_rating_name(value):
    """Get rating name from rating value/integer"""
    return [name for integer, name in Feedback.RATING_CHOICES if integer==value][0]

