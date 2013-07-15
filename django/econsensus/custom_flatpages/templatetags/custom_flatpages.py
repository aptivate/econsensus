from django import template
from django.conf import settings
from django.contrib.flatpages.models import FlatPage


register = template.Library()


class TopFlatpageNode(template.Node):
    def __init__(self, context_name, user):
        self.context_name = context_name
        self.user = template.Variable(user)

    def render(self, context):
        flatpages = FlatPage.objects.filter(sites__id=settings.SITE_ID)
        flatpages = flatpages.filter(url__regex=r'^/[^/]+/$')
        
        user = self.user.resolve(context)
        if not user.is_authenticated():
            flatpages = flatpages.filter(registration_required=False)

        context[self.context_name] = flatpages.order_by('url')
        return ''


@register.tag
def get_topflatpages(parser, token):
    """
    Retrieves all top-level flatpage objects available for the current site.

    Syntax::

        {% get_topflatpages for user as context_name %}

    Example usage::

        {% get_topflatpages for someuser as flatpages %}
    """
    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                       "for user as context_name" %
                       dict(tag_name=bits[0]))
   # Must have at 5 bits in the tag
    if len(bits) != 5 or bits[1] != 'for' or bits[3] != 'as':
            raise template.TemplateSyntaxError(syntax_message)
    user = bits[2]
    context_name = bits[4]
    return TopFlatpageNode(context_name, user)
