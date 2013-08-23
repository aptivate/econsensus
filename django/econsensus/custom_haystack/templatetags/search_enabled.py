from django import template
from custom_haystack.backends.disabled_backend import DisabledEngine

import haystack

register = template.Library()

def search_is_disabled():
    return isinstance(haystack.connections["default"], DisabledEngine)

class IfCanSearchNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        if not search_is_disabled():
            return self.nodelist.render(context)
        else:
            return u''

@register.tag
def ifcansearch(parser, token):
    """
    Outputs the contents of the block if search is enabled.
    Search is considered to be enabled _unless_ Haystack has been
    configured to use the "disabled" backend.

    Example::

        {% ifcansearch %}
            ...
        {% endifcansearch %}
    """
    nodelist = parser.parse(('endifcansearch',))
    parser.delete_first_token()
    return IfCanSearchNode(nodelist)
