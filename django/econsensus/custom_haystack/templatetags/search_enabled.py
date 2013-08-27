from django import template
from custom_haystack.backends.disabled_backend import DisabledEngine

import haystack

register = template.Library()

def search_is_disabled():
    return isinstance(haystack.connections["default"], DisabledEngine)

class IfCanSearchNode(template.Node):
    child_nodelists = ('search_nodelist', 'nosearch_nodelist')

    def __init__(self, search_nodelist, nosearch_nodelist):
        self.search_nodelist = search_nodelist
        self.nosearch_nodelist = nosearch_nodelist

    def render(self, context):
        if search_is_disabled():
            return self.nosearch_nodelist.render(context)
        else:
            return self.search_nodelist.render(context)

@register.tag
def ifcansearch(parser, token):
    """
    Outputs the contents of the block if search is enabled.
    Search is considered to be enabled _unless_ Haystack has been
    configured to use the "disabled" backend.

    Examples::

        {% ifcansearch %}
            ...
        {% endifcansearch %}

        {% ifcansearch %}
            ...
        {% else %}
            ...
        {% endifcansearch %}
    """
    search_nodelist = parser.parse(('else', 'endifcansearch',))
    token = parser.next_token()
    if token.contents == 'else':
        nosearch_nodelist = parser.parse(('endifcansearch',))
        parser.delete_first_token()
    else:
        nosearch_nodelist = NodeList()
    return IfCanSearchNode(search_nodelist, nosearch_nodelist)
