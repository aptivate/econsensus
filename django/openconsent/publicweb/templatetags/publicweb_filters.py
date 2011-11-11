from django import template
from django.template.defaultfilters import stringfilter
from publicweb.models import Decision

register = template.Library()

# this filter is a slightly fudgerydoo way of getting hold of
# an instances methods / attribute values in an abstract fashion

@register.filter
@stringfilter
def decision_field(obj,attr):
    try:
        decision = Decision.objects.get(description=obj)
        value = getattr(decision, attr)
        if callable(value):
            return value()
        else:
            return value
    except:
        return None

@register.filter
@stringfilter
def model_name(obj, attr):
    try:
        decision = Decision.objects.get(description=obj)
        value = getattr(decision, attr)
        return value.__name__
    except:
        return None
