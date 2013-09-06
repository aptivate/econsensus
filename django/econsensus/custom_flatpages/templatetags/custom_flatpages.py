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
    pieces = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                       "for user as context_name" %
                       dict(tag_name=pieces[0]))
    if len(pieces) != 5 or pieces[1] != 'for' or pieces[3] != 'as':
        raise template.TemplateSyntaxError(syntax_message)
    user = pieces[2]
    context_name = pieces[4]
    return TopFlatpageNode(context_name, user)
