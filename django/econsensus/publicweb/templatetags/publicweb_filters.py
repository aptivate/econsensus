from django import template

from publicweb.models import Feedback
import publicweb.utils

register = template.Library()

@register.filter
def get_item(dict, arg):
    """Dictionary lookup when your key is a string"""
    return dict.get(arg)

@register.filter
def get_rating_name(value):
    """Get rating name from rating value/integer"""
    return [name for integer, name in Feedback.RATING_CHOICES if integer==value][0]

@register.filter
def get_user_name_from_comment(value):
    return (value.user and value.user.username) or value.user_name or "An Anonymous Contributor"

@register.filter
def get_user_name_for_notification(user):
    if user.first_name and user.last_name:
        return user.first_name + " " + user.last_name
    else:
        return user.username

@register.filter
def get_excerpt(value):
    return publicweb.utils.get_excerpt(value)
