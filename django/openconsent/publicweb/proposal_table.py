import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _

class ProposalTable(tables.Table):
    id = tables.Column(verbose_name=_('ID'))
    description_excerpt = tables.Column(verbose_name=_('Excerpt'))
    unresolvedfeedback = tables.Column(verbose_name=_('Activity'))
    deadline = tables.Column(verbose_name=_('Deadline'))
