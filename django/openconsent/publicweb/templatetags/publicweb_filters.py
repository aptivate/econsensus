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
        decision = Decision.objects.get(excerpt=obj)
        value = getattr(decision, attr)
        if callable(value):
            return value()
        else:
            return value
    except:
        return None

#No need for decision instance in this function
#should be able to pull field names from the class
@register.filter
@stringfilter
def model_name(obj, attr):
    try:
        decision = Decision.objects.get(excerpt=obj)
        value = getattr(decision, attr)
        if callable(value):
            value2 = value.short_description
        else:
            value2 = decision._meta.get_field(attr).verbose_name
        return value2
    except:
        return None
